import glob
import os
import threading
import time

if __name__ == "__main__":
    from utils import _log_path
    from logfile import LoggingFile, _MODE_READ
else:
    from .utils import _log_path
    from .logfile import LoggingFile, _MODE_READ


class Server:

    def __init__(self, exec_files=[]):
        self.exec_files = exec_files
        t = threading.Thread(target=self.file_monitor, daemon=True)
        t.start()

    def file_monitor(self):
        while True:
            for exec_file in self.exec_files:
                exec_file.check_new_logfiles()
            time.sleep(1)

    def get_messages(self):
        result = ""
        for exec_file in self.exec_files:
            for log_file in exec_file.logfiles:
                lines = log_file.readlines()
                if lines:
                    result += "".join(lines)
        return result
        

class ServerJSON(Server):

    def get_messages(self):
        import json
        result = {}
        for exec_file in self.exec_files:
            for log_file in exec_file.logfiles:
                lines = log_file.readlines()
                if lines:
                    result.setdefault(log_file.label, [json.loads(line) for line in lines])
        return json.dumps(result) if result != {} else ""

class ExecFile:

    def __init__(self, executable, labels):
        self.executable = executable
        self.basename = os.path.split(executable)[1]
        self.logfiles = [LoggingFile(_log_path, label, executable, _MODE_READ) for label in labels]
        self._logset = set([os.path.split(logfile.path)[1] for logfile in self.logfiles])

    def check_new_logfiles(self):
        for logfile in glob.glob(os.path.join(_log_path, f"{self.basename}*")):
            logfile_base = os.path.split(logfile)[1]
            logfile_label = logfile.split(f"{self.basename}-")[1]
            if not logfile_base in self._logset:
                self.logfiles.append(LoggingFile(_log_path, logfile_label, self.executable, _MODE_READ))
                self._logset.add(logfile_base)

if __name__ == "__main__":
    s = ServerJSON((ExecFile(r"C:\Users\User\Documents\Py\testlog.py", ["Main"]), ExecFile(r"client.py", ["Label"])))
    
    while True:
        result = s.get_messages()
        print(result, end='')
        import sys
        sys.stdout.flush()