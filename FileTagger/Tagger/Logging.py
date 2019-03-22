import sys
from enum import IntEnum
class LogLevel (IntEnum):
    INFO = 3
    WARNING = 2
    ERROR = 1

    

class Log():
    level = 3

    def writeLog(msg, msgLevel):
        if (msgLevel <= Log.level):
            if msgLevel == LogLevel.ERROR:
                print(msg,file=sys.stderr)
            else:
                print(msg)

    def writeError(msg):
        Log.writeLog(msg, LogLevel.ERROR)

    def writeInfo(msg):
        Log.writeLog(msg, LogLevel.INFO)