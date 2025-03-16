import sys
import time
from utils.class_dict import *

_total, _curr = 0, 0
_program_time1, _program_time2 = 0, 0
_start_time = 0


def Init_Progress_Bar(total: int):
    global _curr, _total, _program_time1
    _curr = 1
    _total = total
    _program_time1 = time.perf_counter()


def Next_Progress_Bar(evtSize: int, config: ConfigDict):
    global _curr, _start_time
    temp_time = time.perf_counter()
    print(
        f"[{config.name}] Total:{temp_time - _start_time:.1f}s | Current:{temp_time - _program_time1:.1f}s | PNG:{_program_time2 - _program_time1:.1f}s | EVT:{temp_time - _program_time2:.1f}s ({evtSize})\033[K"
    )
    _curr += 1


def Progress_Bar_Show(completed: float, config: ConfigDict):
    if completed == 0:
        global _start_time
        _start_time = time.perf_counter()

    progress = int(20 * completed / config.piv_img_total + 0.5)
    bar = "PNG format data: [" + "=" * progress + "·" * (20 - progress) + "]"
    sys.stdout.write(
        f"-> {bar} {completed/config.piv_img_total*100 : 2.1f}%  > {_curr}/{_total} | {config.name} <\r"
    )
    sys.stdout.flush()


def Progress_Bar_Show_String(string: str, config: ConfigDict):
    global _program_time2

    _program_time2 = time.perf_counter()

    sys.stdout.write(
        f"-> {string}  > {_curr}/{_total} | {config.name} <                              \r"
    )
    sys.stdout.flush()
