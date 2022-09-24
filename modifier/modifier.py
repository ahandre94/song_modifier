import os
import shutil
import logging

import librosa
import pyrubberband as pyrb
import soundfile as sf
from spleeter.separator import Separator
from ffmpy import FFmpeg, FFExecutableNotFoundError, FFRuntimeError

from .config import BITRATE_WEBM, BITRATE_MP3, BITRATE_AAC


log = logging.getLogger(__name__)


class Modifier:
    def __init__(self, audio_path, output_folder):
        self.audio_path = audio_path
        self.in_file = audio_path
        self.out_file, _ = os.path.splitext(os.path.basename(self.audio_path))
        self.output_folder = output_folder
        self.to_be_removed = set()

    def change_pitch(self, semitones):
        """Change pitch to a song.
        Save the output song in wav format.
        :param float semitones: how many semitones the song has to be shifted
        """
        if semitones == 0:
            return

        out_file = os.path.join(self.output_folder, f'{self.out_file}_{semitones}.wav')

        log.info('%s: Changing pitch of %s semitones', self.audio_path, semitones)
        try:
            song, samplerate = librosa.load(self.in_file, sr=None)
        except:
            raise ValueError

        song_shifted = pyrb.pitch_shift(song, samplerate, semitones)
        sf.write(out_file, song_shifted, samplerate, 'PCM_24')
        self.in_file = out_file

    def split_song(self, semitones):
        """Create two different tracks for the song.
        The first track is the vocal track (vocal.wav), the second is the instrumental
        track (accompaniment.wav).
        """
        try:
            song, samplerate = librosa.load(self.in_file, sr=None)
        except:
            raise ValueError
        length = librosa.get_duration(song, samplerate) or 600

        log.info('%s: Performing source separation using Spleeter', self.in_file)
        separator = Separator('spleeter:2stems', multiprocess=False)
        separator.separate_to_file(self.in_file, self.output_folder, duration=length)

        if semitones:
            self.to_be_removed.update([self.in_file, os.path.splitext(self.in_file)[0]])
        else:
            self.to_be_removed.add(os.path.join(self.output_folder, self.out_file))

    def transcode(self, output_format, semitones, type=None):
        """Transcode the song in the ouput format.
        :param str output_format: the extension of the ouput song.
            Supported output format are: wav, webm, mp3, m4a, flac
        :raise: `RuntimeError` in case the output format is not valid
                `FFRuntimeError` in case FFmpeg command exits with a non-zero code;
                `FFExecutableNotFoundError` in case the executable path passed was not valid
        """
        base_file = os.path.join(self.output_folder, self.out_file)
        out_file_pitch, _ = os.path.splitext(self.in_file)
        out_file = f'{out_file_pitch}.{output_format}' if semitones else f'{base_file}.{output_format}'

        if type is not None:
            self.in_file = os.path.join(out_file_pitch, f'{type}.wav') if semitones else os.path.join(base_file, f'{type}.wav')
            out_file = os.path.join(out_file_pitch, f'{type}.{output_format}') if semitones else os.path.join(base_file, f'{type}.{output_format}')

        if f'.{output_format}' == os.path.splitext(self.in_file)[1]:
            return

        channels = 2
        default_options = f'-ac {channels} -vn -map_metadata -1'
        global_options = '-y'

        output_options = {
            'wav': default_options,
            'webm': f'-b:a {BITRATE_WEBM}k -acodec libvorbis {default_options}',
            'mp3': f'-b:a {BITRATE_MP3}k -acodec libmp3lame {default_options}',
            'm4a': f'-b:a {BITRATE_AAC}k -acodec aac {default_options}',
            'flac': f'-acodec flac {default_options}'
        }.get(output_format)

        if output_options is None:
            raise RuntimeError('Invalid output format')

        log.info('Transcoding "%s" to "%s"', self.in_file, output_format)
        ff = FFmpeg(
            global_options=global_options,
            inputs={self.in_file: None},
            outputs={out_file: output_options}
        )
        ff.run()

        if semitones:
            self.to_be_removed.add(self.in_file)

        if type is not None:
            self.in_file = os.path.dirname(self.in_file)

    def delete_split_tmp_files(self, type, semitones, output_format):
        """Delete the split temporary files in case of transcoding."""
        if output_format == 'wav':
            return
        os.remove(os.path.join(self.in_file, f'{type}.wav'))

    def make_zip(self, semitones):
        """Zip the vocal and accompaniment audio files."""
        log.debug('%s: Creating zip archive', self.in_file)

        base_file = os.path.join(self.output_folder, self.out_file)
        dir_to_zip = f'{base_file}_{semitones}' if semitones else base_file
        zip_file = dir_to_zip
        shutil.make_archive(zip_file, 'zip', dir_to_zip)

    def clear_tmp_files(self):
        """Remove temporary jobs file."""
        for item in self.to_be_removed:
            if os.path.isdir(item):
                shutil.rmtree(item)
                continue
            if os.path.exists(item):
                os.remove(item)

    def complete_modify_song(self, semitones, split, output_format):
        """Perform a complete modifying song process.
        Retrieve the song from the storage server, change the pitch, if requested
        split the song in vocal and accompaniment tracks, transcode to
        the desired output format. Upload the song to the storage server.
        Delete all the local temporary files.
        :param float semitones: how many semitones the song has to be shifted
        :param str output_format: the extension of the ouput song
        :param bool split: if True, split the pitched song in two different audio
            files: vocal and accompainement
        """
        log.info('%s: Modifying song job started', self.audio_path)

        try:
            if semitones is not None:
                self.change_pitch(semitones)

            if split:
                self.split_song(semitones)
                if output_format is not None:
                    for output_type in ['vocals', 'accompaniment']:
                        self.transcode(output_format, semitones, output_type)
                        self.delete_split_tmp_files(output_type, semitones, output_format)
                self.make_zip(semitones)

            if output_format is not None and not split:
                self.transcode(output_format, semitones)

            log.info('%s: Modifying song job finished', self.audio_path)

        except ValueError:
            log.error('Invalid input format: %s', os.path.splitext(self.audio_path)[1])
        except RuntimeError:
            log.error('Invalid output format: %s', output_format)
        except FFExecutableNotFoundError:
            log.error('Executable path not valid')
        except FFRuntimeError as e:
            log.exception('FFRuntimeError: %s', e)
        except Exception as e:
            log.exception('%s(%s)', type(e).__name__, e)
        finally:
            self.clear_tmp_files()
