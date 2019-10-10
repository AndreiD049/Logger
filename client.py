import os
from time import sleep
import datetime

if __name__ == "__main__":
    from utils import _log_path
    from logfile import LoggingFile
else:
    from .utils import _log_path
    from .logfile import LoggingFile

class ClientLogger:

    __log_path__ = "logs"

    def __init__(self, label, executable, **kwargs):
        # Double check if the logging folder exists
        if not os.path.exists(os.path.abspath(_log_path)): os.mkdir(os.path.abspath(_log_path))
        self.logging_file = LoggingFile(_log_path, label, executable, 'w')
        self.fd = self.logging_file.fd
        self.delete = kwargs.get("delete", False)

    def __del__(self):
        if self.delete: os.remove(self.fd.name)

    def log(self, message):
        self.fd.write(message + '\n')
        self.fd.flush()
    
    def logif(self, expression, message, else_message=None, seconds=0):
        if expression:
            self.log(message)
            if seconds: sleep(seconds)
        elif else_message:
            self.log(else_message)
            if seconds: sleep(seconds)

    def log_n_wait(self, message, seconds):
        self.log(message)
        sleep(seconds)

class ClientLoggerJSON(ClientLogger):

    def log(self, message):
        import json

        new_message = {
            "time": datetime.datetime.now().strftime("%H:%M:%S.%f"),
            "message": message
        }
        self.fd.write(json.dumps(new_message) + '\n')
        self.fd.flush()


if __name__ == "__main__":
    l = ClientLoggerJSON("Main2", __file__, delete=False)
    # time.sleep(5)
    for i in range(1000):
        l.logif( i % 2 == 0, "Value %s is even" % i, "Value %s is odd" % i, .01)
        l.logif(i == 500, "i is 500", seconds=5)