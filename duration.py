import wave
import contextlib


def duration(fname):
    with contextlib.closing(wave.open(f'music\\{fname}', 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        dur = frames / float(rate)
        return dur


def minutes(sec=0):
    m, s = divmod(sec, 60)
    min = str(int(m)) if int(m) > 9 else f'0{m}'
    sec = str(int(s)) if int(s) > 9 else f'0{s}'
    return f'{min}:{sec}'
