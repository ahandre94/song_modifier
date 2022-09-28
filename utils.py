import os
import logging

from modifier import Modifier


log = logging.getLogger(__name__)


def make_dir(path):
    if not os.path.isdir(path):
        if os.path.exists(path):
            path = f'{path}_'
        os.makedirs(path)
    return path


def main(audio, pitch, split, format, output):
    output = make_dir(output)
    modifier = Modifier(audio, output)
    modifier.complete_modify_song(pitch, split, format)
