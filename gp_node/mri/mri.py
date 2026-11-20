import wx
from initialise_gui import InitialisePanel
from config_gui import ConfigPanel
from monitor_gui import MonitorPanel


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="MRI GramPower India Ltd", size=(
            1100, 600), style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.TAB_TRAVERSAL)

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        nb = wx.Notebook(p)
        nb.SetBackgroundColour('#B0C4DE')

        # create the page windows as children of the notebook
        page2 = ConfigPanel(nb)
        page1 = InitialisePanel(nb)
        page3 = MonitorPanel(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "Initialization")
        nb.AddPage(page2, "Settings")
        nb.AddPage(page3, "Data Monitor")

        def Test(check):
            print "EVT_NOTEBOOK_PAGE_CHANGED"
            print nb.GetSelection()

        def Test2(check):
            print "EVT_NOTEBOOK_PAGE_CHANGING"
            print nb.GetSelection()

        #nb.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, Test )
        #nb.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGING, Test2 )
        #page2.Enable( False )
        page3.Enable(False)
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


def run():
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()


if __name__ == "__main__":
    run()
