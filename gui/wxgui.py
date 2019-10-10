import wx 
import wx.html2 
import multiprocessing
import time
from .main import run

def startserver():
    proc = multiprocessing.Process(target=run, daemon=True)
    proc.start()

def startapp():
    startserver()
    app = wx.App() 
    frame = wx.Frame(None, wx.ID_ANY, "test", size=(500, 500))
    dialog = wx.html2.WebView.New(frame)
    dialog.LoadURL("http://localhost:64322") 
    frame.Center()
    frame.Show()
    app.MainLoop()    

if __name__ == '__main__':
    startserver()
    app = wx.App() 
    frame = wx.Frame(None, wx.ID_ANY, "test()", size=(500, 500))
    dialog = wx.html2.WebView.New(frame)
    dialog.LoadURL("http://localhost:64322") 
    frame.Center()
    frame.Show()
    app.MainLoop()