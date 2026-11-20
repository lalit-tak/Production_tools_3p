import wx
import wx.lib.scrolledpanel as scrolled

class TMainForm(wx.Frame):

    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.Splitter = wx.SplitterWindow(self, -1)

        self.Panel1 = wx.Panel(self.Splitter, -1)          
        self.Panel3 = wx.Panel(self.Splitter, -1)

        self.Splitter.SplitVertically(self.Panel1,self.Panel3,350)

        self.Notebook2 = wx.Notebook(self.Panel1, -1)

        self.Notebook3 = wx.Notebook(self.Panel3, -1)
        self.OptPane = scrolled.ScrolledPanel(self.Notebook3, -1)
        self.OptPane.SetupScrolling()

        self.Opt_Info = wx.Panel(self.OptPane,-1, style=wx.NO_BORDER)
        self.Opt_Middle = wx.Panel(self.OptPane,-1, style=wx.RAISED_BORDER)
        self.Opt_Buttons = wx.Panel(self.OptPane,-1, style=wx.NO_BORDER)

        self.Button1 = wx.Button(self.Opt_Buttons,-1,'Button1',size=(-1,-1))
        self.Button2 = wx.Button(self.Opt_Buttons,-1,'Button2',size=(-1,-1))
        self.Button3 = wx.Button(self.Opt_Buttons,-1,'Button3',size=(-1,-1))

        self.MainMenu = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.FileOpenItem = wx.MenuItem(self.FileMenu, 103, "&Open\tCtrl+O", "Open a Previous Session", wx.ITEM_NORMAL)
        self.FileMenu.AppendItem(self.FileOpenItem)
        self.FileSaveItem = wx.MenuItem(self.FileMenu, 102, "&Save\tCtrl+S", "Save the data", wx.ITEM_NORMAL)
        self.FileMenu.AppendItem(self.FileSaveItem)
        self.FileQuitItem = wx.MenuItem(self.FileMenu, wx.ID_EXIT, "&Quit\tCtrl+Q", "Quit the program", wx.ITEM_NORMAL)
        self.FileMenu.AppendItem(self.FileQuitItem)  
        self.MainMenu.Append(self.FileMenu, "&File")
        self.SetMenuBar(self.MainMenu)

        self.__set_properties()
        self.__do_layout()

        print self.Button1.GetScreenPosition()
        testtext = wx.StaticText(self.Notebook3, -1, 'X marks spot',pos=(240,840))

    def __set_properties(self): 

        self.SetTitle("My Program")

        screen_x = 95 * wx.GetDisplaySize()[0]/100
        screen_y = 90 * wx.GetDisplaySize()[1]/100
        self.SetSize((screen_x, screen_y))
        self.SetFocus()

    def __do_layout(self , call_fit = True, set_sizer = True): 

        vbox  = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        hbox1.Add(self.Opt_Info, 1, wx.EXPAND|wx.ALL, 3)
        hbox2.Add(self.Opt_Middle, 1, wx.EXPAND|wx.ALL, 3)
        hbox3.Add(self.Opt_Buttons, 1, wx.EXPAND|wx.ALL, 3)

        box_bot = wx.GridSizer(1,3,2,2)

        box_bot.Add(self.Button1, 1, wx.ALIGN_CENTER| wx.LEFT | wx.RIGHT, 55)    
        box_bot.Add(self.Button2, 1, wx.ALIGN_CENTER| wx.LEFT | wx.RIGHT, 55)
        box_bot.Add(self.Button3, 1, wx.ALIGN_CENTER| wx.LEFT | wx.RIGHT, 55)

        self.Opt_Buttons.SetSizer(box_bot)

        vbox.Add(hbox1, 0, wx.EXPAND|wx.TOP, 20)
        vbox.Add(hbox2, 1, wx.EXPAND|wx.TOP, 50)
        vbox.Add(hbox3, 0, wx.EXPAND|wx.ALL, 20)
        self.OptPane.SetSizer(vbox)

        self.Notebook3.AddPage(self.OptPane,"Page1")

        #Sizer for Panel 2
        sizer_P2 = wx.BoxSizer(wx.VERTICAL)
        sizer_P2.Add(self.Notebook2, 1, wx.EXPAND, 0)
        self.Panel1.SetSizer(sizer_P2)

        #Sizer for Panel 3
        sizer_P3 = wx.BoxSizer(wx.VERTICAL)
        sizer_P3.Add(self.Notebook3, 1, wx.EXPAND, 0)
        self.Panel3.SetSizer(sizer_P3)

        # Split Panel Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.Splitter,1,wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()
        self.Centre()

# Code to Execute File
class TApplication(wx.App):
    def OnInit(self):

            wx.InitAllImageHandlers()
            MainForm = TMainForm(None, -1,"")
            self.SetTopWindow(MainForm)

            MainForm.Show()
            return 1

if __name__ == "__main__":
    Application = TApplication(0)
    Application.MainLoop()