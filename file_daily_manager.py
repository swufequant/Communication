# author='lwz'
# coding:utf-8
# !/usr/bin/env python3
import os
import time
from warnings import warn


def file_daily_manager(fn):
    if isinstance(fn, str):
        choose_def(fn)
        return
    for f in fn:
        if isinstance(f, str):
            choose_def(f)
        else:
            warn(UserWarning, "file suffix warning" + f)


def choose_def(fn):
    if fn[-4:] == '.txt':
        file_txt(fn)
    elif fn[-4:] == '.log':
        file_txt(fn)
    elif fn[-4:] == '.pkl':
        file_pkl(fn)
    else:
        warn(UserWarning, "file suffix warning" + fn)


def file_pkl(fn):
    if not os.path.exists(fn):
        print("we dont find file: ", fn)
        return

    work_start_time = time.time() - time.time() % 86400
    # 每日上午8点
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fn)))
    print("file : {}\nupdate time: {}".format(fn, timestr))
    if os.path.getmtime(fn) < work_start_time:
        remove(fn)


def file_txt(fn):
    if not os.path.exists(fn):
        print("we dont find file: ", fn)
        rewrite_file(fn)
        return

    work_start_time = time.time() - time.time() % 86400
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fn)))
    print("file : {}\nupdate time: {}".format(fn, timestr))
    # 每日上午8点
    if os.path.getmtime(fn) < work_start_time:
        rewrite_file(fn)


def remove(fn):
    os.remove(fn)
    print("we remove file: ", fn)


def rewrite_file(fn):
    with open(fn, 'w') as f:
        f.write('')
        print("we rewrite file: ", fn)