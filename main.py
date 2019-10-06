import sys
import os
import time
from log.utils import _log_path

class Logger:

    __log_path__ = "logs"

    def __init__(self, name, exec_name, **kwargs):
        if not os.path.exists(_log_path): os.mkdir(_log_path)
        self.name = name
        self.exec_name = exec_name
        self.fd = None
        self.context = False
        self.delete = kwargs.get("delete", False)

    def __enter__(self):
        self.context = True
        self.fd = self.__open_desc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()
        if self.delete: os.remove(self.fd.name)

    def __del__(self):
        if not self.context:
            self.fd.close()
            if self.delete: os.remove(self.fd.name)

    def start(self):
        if self.fd is None:
            self.fd = self.__open_desc()

    def log(self, message):
        self.fd.write(message.encode("utf-8"))
        self.fd.flush()
    
    def logif(self, expression, message, else_message=None, seconds=0):
        if expression:
            self.log(message)
            if seconds: time.sleep(seconds)
        elif else_message:
            self.log(else_message)
            if seconds: time.sleep(seconds)

    def log_n_wait(self, message, seconds):
        self.log(message)
        time.sleep(seconds)

    def __open_desc(self):
        fd = open(os.path.join(_log_path, "%s - %s" % (os.path.split(self.exec_name)[1], self.name)), 'wb')
        import uuid
        fd.write(f"{uuid.uuid4().hex}{os.linesep}".encode("utf-8")) # 32 characters + linesep
        return fd

if __name__ == "__main__":
    l = Logger("Test-Log-Test", "main.py", delete=False)
    l.start()
    # time.sleep(5)
    for i in range(1000):
        l.logif( i % 2 == 0, "Value %s is even\n" % i, "Value %s is odd\n" % i, .01)
        l.logif(i == 500, "i is 500\n", seconds=5)