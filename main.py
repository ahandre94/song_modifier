import os
import sys
import argparse
import logging

from modifier import Modifier
import log_util


log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--audio', dest='audio', type=str,
                        help='Path to audio file')
    parser.add_argument('-p', '--pitch', dest='pitch', type=int,
                        help='Number of semitones by which the trace will be altered (+1, -1, ...)')
    parser.add_argument('-s', '--split', dest='split', action='store_true',
                        help='Whether to split audio file')
    parser.add_argument('-f', '--format', dest='format', type=str,
                        help='Output format of the audio file if you want to transcode it')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help='Output path (default: /output)')
    parser.set_defaults(output='output')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Debug mode')
    return parser.parse_args()


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def main(audio, pitch, split, format, output):
    make_dir(output)
    modifier = Modifier(audio, output)
    modifier.complete_modify_song(pitch, split, format)


if __name__ == '__main__':
    args = parse_args()

    log_util.configure_logging(__package__, logging.DEBUG if args.debug else None)

    if args.audio is None:
        print('Use: python -h')
        sys.exit()

    main(args.audio, args.pitch, args.split, args.format, args.output)
