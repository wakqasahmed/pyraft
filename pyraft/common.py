import sys, threading

import select
import socket

CONF_LOG_MAX = 100000
CONF_LOG_FILE_MAX = 10000

CONF_VOTING_TIME = 1.0
CONF_PING_TIMEOUT = 5  # re-elect leader after CONF_PING_TIMEOUT

g_log_level = 0
g_log_handle = sys.stdout

def log_write(log):
    global g_log_handle
    g_log_handle.write(log)

def set_log_level(level):  # debug, info, warn, error
    global g_log_level

    if level.lower().startswith('debug'):
        g_log_level = 0
    elif level.lower().startswith('info'):
        g_log_level = 1
    elif level.lower().startswith('warn'):
        g_log_level = 2
    elif level.lower().startswith('err'):
        g_log_level = 3

def get_log_level():
    global g_log_level
    return g_log_level

def intcast(src):
    if isinstance(src, int):
        return src

    if src.isdigit() == False:
        return None

    return int(src)


ERROR_CAST = Exception('number format error')
ERROR_APPEND_ENTRY = Exception('append entry failed')
ERROR_TYPE = Exception('invalid data type')
ERROR_NOT_EXISTS = Exception('not exists')
ERROR_INVALID_PARAM = Exception('invalid parameter')


class Future(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.value = None
        self.cond = threading.Condition()

    def get(self, timeout=None):
        if self.value != None:
            return self.value

        try:
            with self.cond:
                self.cond.wait(timeout)
        except RuntimeError:
            return None

        return self.value

    def set(self, value):
        with self.cond:
            self.value = value
            self.cond.notify()
