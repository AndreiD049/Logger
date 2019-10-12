"""
    This is a simple GUI for my package for live logging.
"""

__author__ = "Andrei Dimitrascu"

import wx 
import wx.lib.agw.flatnotebook as FlatNotebook
import wx.lib.mixins.listctrl as listctrl
import time
from log.server import Server, ServerJSON, ExecFile
from threading import Thread, main_thread, Lock
import queue
import json

EVT_NEW_PAGE = wx.NewIdRef()
EVT_NEW_DATA = wx.NewIdRef()
LOCK = Lock()

class LoggerApp(wx.App):

    def OnInit(self, *args, **kwargs):
        self.queue = queue.Queue()
        self.main_frame = LoggerFrame(None, wx.ID_ANY, "ePyLog", size=(500, 500))
        self.server = ServerJSON((ExecFile("test.py", []), ))
        self.server_thread = ServerThread(self.main_frame.notebook)
        # inspection.InspectionTool().Show(self.main_frame)
        self.main_frame.Show()
        return True


class LoggerFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(LoggerFrame, self).__init__(*args, **kwargs)
        self.main_panel = MainPanel(self, wx.ID_ANY)
        self.notebook = self.main_panel.notebook

    def process_message(self, message):
        mapping = json.loads(message)
        for key in mapping.keys():
            if not self.check_label_exists(key):
                print("adding %s" % list(self.page_mapping.keys()))
                wx.CallAfter(self.main_panel.add_new_page, key)
                self.page_mapping.setdefault(key, 0)
                self.Refresh()
        print("Processing")

    def check_label_exists(self, label):
        return label in self.page_mapping


class MainPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(MainPanel, self).__init__(*args, **kwargs)
        self.doLayout()
        self.Layout()


    def doLayout(self):
        """
        Creates the sizers for the main frame.
        The minimal version consists of one vertical sizer of 3 slots, each slot
        is a sizer itself (horizontal).
        """
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.title_sizer = wx.BoxSizer()
        self.content_sizer = wx.BoxSizer()
        self.button_sizer = wx.BoxSizer()
        self.main_sizer.Add(self.title_sizer, wx.SizerFlags(0).Expand().Border(wx.ALL, 10))
        self.main_sizer.Add(self.content_sizer, wx.SizerFlags(1).Expand())
        self.main_sizer.Add(self.button_sizer, wx.SizerFlags(0).Expand())

        # make title
        self.title_sizer.Add((10, 10), wx.SizerFlags(1))
        text = wx.StaticText(self, label="ePyLog")
        self.title_sizer.Add(text, wx.SizerFlags(0).Center())
        self.title_sizer.Add((10, 10), wx.SizerFlags(1))

        # make notebook that will have the text control
        panel_txt = wx.Panel(self)
        panel_txt.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))
        panel_txt_sizer = wx.BoxSizer()
        panel_txt.SetSizer(panel_txt_sizer)
        self.notebook = LogNotebook(panel_txt)
        panel_txt_sizer.Add(self.notebook, wx.SizerFlags(1).Expand().Border(wx.ALL, 10))
        self.content_sizer.Add(panel_txt, wx.SizerFlags(1).Expand())

        # add a button panel
        buttons_panel = ButtonPanel(self)
        self.button_sizer.Add(buttons_panel, wx.SizerFlags(1).Expand())

        self.SetSizer(self.main_sizer)

            
class LogNotebook(FlatNotebook.FlatNotebook):

    def __init__(self, *args, **kwargs):
        super(LogNotebook, self).__init__(*args, **kwargs)
        self.pages = {}
        self._register_events()
        # set the type of window where the messages will be displayed, either TextCtrlPanel or ListCtrlPanel
        self.displayType = ListCtrlPanel
        ProcessQueueThread(self, wx.GetApp().queue)

    def AddPage(self, page, text):
        self.pages.setdefault(text, page)
        return super(LogNotebook, self).AddPage(page, text)

    def AddCtrl(self, text):
        self.Freeze()
        page = self.displayType(self)
        self.Thaw()
        return self.AddPage(page, text)

    def AddText(self, label, text):
        """
            Append text to the TextCtrl on the Page specified by @label
        """
        if label in self.pages:
            self.pages[label].control.AppendText(text)

    def _register_events(self):
        self.Connect(-1, -1, EVT_NEW_PAGE, self.onNewPage)


    def onNewPage(self, evt):
        # with LOCK:
        if not evt.data in self.pages:
                self.AddCtrl(evt.data)


class GenericPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(GenericPanel, self).__init__(*args, **kwargs)
        self.control = None
        self.do_layout()

    def do_layout(self):
        raise NotImplementedError("This method should be overriden in children")


class TextCtrlPanel(GenericPanel):

    def do_layout(self):
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        sizer.Add(self.control, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        self.control.SetBackgroundColour(wx.BLACK)
        self.control.SetForegroundColour(wx.Colour(102, 185, 51))

    def processMessage(self, msg):
        self.control.AppendText(f"{msg['time']} - {msg['type']} - {msg['context']} - {msg['message']}\n")

class ListCtrlPanel(GenericPanel):

    def do_layout(self):
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        self.control = LogListCtrl(self, style=wx.LC_REPORT)

        # set columns
        self.control.InsertColumn(0, "timestamp")
        self.control.InsertColumn(1, "type")
        self.control.InsertColumn(2, "context")
        self.control.InsertColumn(3, "message")

        self.control.SetBackgroundColour(wx.BLACK)
        self.control.SetForegroundColour(wx.Colour(102, 185, 51))

        sizer.Add(self.control, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))

    def processMessage(self, msg):
        index = self.control.InsertItem(self.control.GetItemCount(), msg["time"])
        self.control.SetItem(index, 1, msg["type"])
        self.control.SetItem(index, 2, msg["context"])
        self.control.SetItem(index, 3, msg["message"])
        self.control.EnsureVisible(self.control.GetItemCount() - 1)

class LogListCtrl(wx.ListCtrl, listctrl.ListCtrlAutoWidthMixin):

    def __init__(self, *args, **kwargs):
        super(wx.ListCtrl, self).__init__(*args, **kwargs)
        listctrl.ListCtrlAutoWidthMixin.__init__(self)
        self.do_layout()

    def Clear(self):
        return self.DeleteAllItems()

    def do_layout(self):
        # self.SetBackgroundColour(wx.BLACK)
        pass


class ButtonPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(ButtonPanel, self).__init__(*args, **kwargs)
        self.buttons = {}
        self.do_layout()
        self._init_buttons()
        self._init_event_handlers()

    def do_layout(self):
        # start by adding a sizer to self
        self._sizer = wx.BoxSizer()
        self.SetSizer(self._sizer)
        self._sizer.Add((10, 10), wx.SizerFlags(1))
        self._sizer.Add((10, 10), wx.SizerFlags(1))

    def AddButton(self, button):
        """
        Add a button to the sizer
        """
        self.buttons[button.Label] = button
        self._sizer.Insert(self._sizer.ItemCount-1, button, wx.SizerFlags(0).Center().Border(wx.ALL, 5))

    def clearCurrentPage(self, evt):
        notebook = self.GetParent().notebook
        page = notebook.GetSelection()
        if page != wx.NOT_FOUND:
            page_window = notebook.GetPage(page)
            page_window.control.Clear()

    def addExecutable(self, evt):
        print("Add Executable")

    def _init_buttons(self):
        self.AddButton(LogButton(self, label="Add Executable"))
        self.AddButton(LogButton(self, label="Clear"))

    def _init_event_handlers(self):
        self.buttons["Clear"].Bind(wx.EVT_BUTTON, self.clearCurrentPage)
        self.buttons["Add Executable"].Bind(wx.EVT_BUTTON, self.addExecutable)


class LogButton(wx.Button):
    """
        Added in case we ever need to customize out buttons.
        Just add a layout method in case.
    """
    def __init__(self, *args, **kwargs):
        super(LogButton, self).__init__(*args, **kwargs)


class CustomEvent(wx.PyEvent):
    """
        Event that will hold data either about new data added,
        or new labels added to the logger.
    """
    
    def __init__(self, evt_type, data):
        super(CustomEvent, self).__init__()
        self.SetEventType(evt_type)
        self.data = data


class ServerThread(Thread):

    def __init__(self, target):
        super(ServerThread, self).__init__()
        self.target = target
        self.start()

    def run(self):
        app = wx.GetApp()
        while True:
            response = app.server.get_messages()
            if response:
                response_obj = json.loads(response)
                # Check for new labels
                for label in response_obj.keys():
                    if not label in self.target.pages:
                        wx.PostEvent(self.target, CustomEvent(EVT_NEW_PAGE, label))
                app.queue.put(response_obj)
                # wx.PostEvent(self.target, CustomEvent(EVT_NEW_DATA, response_obj))
            time.sleep(.1)
            if not main_thread().is_alive():
                break

class ProcessQueueThread(Thread):

    def __init__(self, notebook, queue):
        super(ProcessQueueThread, self).__init__()
        self.notebook = notebook
        self.queue = queue
        self.start()

    def run(self):
        while True:
            with LOCK:
                while not self.queue.empty():
                    item = self.queue.get(True)
                    for (label, messages) in item.items():
                        for message in messages:
                            self.notebook.pages[label].processMessage(message)
                if not main_thread().is_alive():
                    break
            time.sleep(.1)


if __name__ == '__main__':
    app = LoggerApp(False)
    app.MainLoop()