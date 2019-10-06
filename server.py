import glob
import os
import threading
import time

from utils import _log_path


class Server:

    def __init__(self, exec_names):
        self.exec_names = exec_names
        self.fds = {}
        self.check_create_files()
        t = threading.Thread(target=self.file_monitor, daemon=True)
        t.start()

    def file_monitor(self):
        while True:
            for exec_name in self.exec_names:
                for path in glob.glob(os.path.join(_log_path, "%s*" % os.path.split(exec_name.exec_name)[1])):
                    basename = os.path.split(path)[1]
                    if not basename in self.fds:
                        print("Opening %s" % path)
                        self.fds[basename] = LogFile(self.__open_desc(path))
            time.sleep(1)

    def check_create_files(self):
        for exec_file in self.exec_names:
            for log_name in exec_file.names:
                name = self._get_base_name(exec_file.exec_name, log_name)
                if not os.path.exists(name):
                    tmp = open(name, 'x')
                    tmp.close()

    def __open_desc(self, path):
        return open(path, 'r')

    @staticmethod
    def _get_base_name(exec_file, log_name):
        return os.path.join(_log_path, f"{os.path.split(exec_file)[1]} - {log_name}")


class LogFile:

    def __init__(self, fd):
        self.size = os.path.getsize(fd.name)
        self.fd = fd
        self.uuid = fd.read(32)
        fd.seek(0, os.SEEK_END)
        # self.seek_pos = fd.tell()

    def readline(self):
        result = self.fd.readline()
        if not result.strip():
            self.check_uuid()
        return result

    def check_uuid(self):
        current_pos = self.fd.tell()
        self.fd.seek(0)
        current_uuid = self.fd.read(32)
        if current_uuid != self.uuid:
            self.uuid = current_uuid
            self.fd.seek(32)
            return False
        else:
            self.fd.seek(current_pos)
            return True
        

class ExecFile:

    def __init__(self, name, *args):
        self._logfile = [name, *args]

    @property
    def exec_name(self):
        return self._logfile[0]

    @exec_name.setter
    def exec_name(self, value):
        self._logfile[0] = value

    @property
    def names(self):
        return self._logfile[1:]
    
    def add_name(self, name):
        self._logfile.append(name)
    
    def remove_name(self, name):
        self._logfile.remove(name)

if __name__ == "__main__":
    s = Server((ExecFile("G:\pyth\log\main.py", "Main", "Test-Log-Test"), ExecFile("G:\pyth\main-test.py", "Test2")))
    while True:
        k = list(s.fds.keys())
        for fdk in k:
            message = s.fds[fdk].readline()
            if message.strip(): print(message, end='')