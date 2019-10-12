import os
import uuid

_UUID_LENGTH = 32
_MODE_WRITE = 'w'
_MODE_READ = 'r'
_MODE_CREATE = 'x'

class LoggingFile:

    def __init__(self, path, label, executable, mode, existing=True):
        """
            @path: path to the log folder (./logs)
            @label: label of the log file (ex: Main, Secondary etc)
            @executable: the fullpath to the executable program, or just the name (usually the __file__)
            @mode: mode to open the file (read/write/create)
            @existing: boolean, representing whether this is a new file or an existing one remaining from past executions.
                If it's an existing file, it's file pointer will be moved to the end of the file, else it will be read from the beggining
        """
        self.label = label
        self.executable = executable
        self.basename = os.path.split(executable)[1]
        self.mode = mode
        self.uuid = ''
        self.existing = existing
        self.path = os.path.join(path, f"{self.basename}-{self.label}")
        self.fd = self.open_file()

    def check_create(self):
        if not os.path.exists(self.path):
            tmp = open(self.path, _MODE_CREATE)
            tmp.close()

    def remove(self):
        os.remove(self.path)

    def readline(self):
        result = self.fd.readline()
        if not result.strip():
            self.check_uuid()
        elif self.uuid == '':
            result = ''
            self.check_uuid()
            self.readline()
        return result

    def readlines(self):
        result = self.fd.readlines()
        if len(result) == 0:
            self.check_uuid()
        elif self.uuid == '':
            result = ''
            self.check_uuid()
            self.readlines()
        return result

    def check_uuid(self):
        current_pos = self.fd.tell()
        self.fd.seek(0)
        current_uuid = self.fd.read(_UUID_LENGTH)
        if current_uuid != self.uuid:
            self.uuid = current_uuid
            self.fd.seek(_UUID_LENGTH + 2)
            return False
        else:
            self.fd.seek(current_pos)
            return True
    
    def open_file(self):
        if self.mode != _MODE_WRITE: self.check_create()
        fd = open(self.path, self.mode)
        if self.mode == _MODE_WRITE:
            self.uuid = f"{uuid.uuid4().hex}\n"
            fd.write(self.uuid)
        else:
            self.uuid = fd.read(_UUID_LENGTH)
            if self.existing:
                fd.seek(0, os.SEEK_END)
            else:
                fd.seek(_UUID_LENGTH + 2)
        return fd
