from initialise_api import InitializeApi
from gp_node.network.network_api import NetworkAPI
from gp_node.network.protocols.common.tap import TAPHandler, TAPPacket, TAPError
from gp_node.network.protocols._3p.flash_io import FlashIOMaster_3P, FlashIOError_3P
from gp_node.utils.address import Address
import gp_node.utils.serialize as serialize
import wx
from config import MAX_CURRENT, MIN_CURRENT, SOFTWARE_VERSION, ENERGY_TRIES, \
    OVERPOWER_LIMIT, TOTAL_ENERGY,ALLOWED_ENERGY, MAPPING_LOG, LOG_PATH, TIME_DRIFT,FACTORY_TRIES,SERIAL_NO_TRIES
import serial
import datetime
import wx.lib.platebtn as platebtn
import time
import os.path
import thread
import json

class InitialisePanel(wx.Panel):
    def __init__(self, parent):
        self.temp_meter_data = {}
        self.meter_time = ''
        self.meter_init_time = ''
        wx.Panel.__init__(self, parent)
        #--------------------------------------
        #ser = serial.Serial(args.device, args.baud_rate, timeout=args.timeout)
        #testHandler = RequestHandler_3P(network_api)
        #--------------------------------------
        self.network_api = InitializeApi()
        self.gbSizerInitialize = wx.GridBagSizer( 0, 0 )
        self.gbSizerInitialize.SetFlexibleDirection( wx.BOTH )
        self.gbSizerInitialize.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        self.gbSizerInitialize.SetEmptyCellSize( wx.Size( 20,20 ) )

        x = 2
        y = 2

        m_radioBox1Choices = [ u"Single Phase ", u"Three Phase" ]
        self.m_radioBoxMeterType = wx.RadioBox( self, wx.ID_ANY, u"Meter Type", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_ROWS )
        self.m_radioBoxMeterType.SetSelection( 0 )
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.m_radioBoxMeterType.SetFont(font)
        self.m_radioBoxMeterType.Enable( True )
        self.gbSizerInitialize.Add( self.m_radioBoxMeterType, wx.GBPosition( x+1,y+0), wx.GBSpan( 2, 2 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_serialNo = wx.StaticText( self, wx.ID_ANY, u"Serial No", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_serialNo.Wrap( -1 )
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.m_staticText_serialNo.SetFont(font)
        self.gbSizerInitialize.Add( self.m_staticText_serialNo, wx.GBPosition( x+3,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl_serialNo = wx.TextCtrl( self, wx.ID_ANY, u"500322", wx.DefaultPosition, (200,-1), 0 )
        self.m_textCtrl_serialNo.SetFont(font)
        self.m_textCtrl_serialNo.SetMaxLength( 6 ) 
        self.gbSizerInitialize.Add( self.m_textCtrl_serialNo, wx.GBPosition( x+3,y+1 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_address = wx.StaticText( self, wx.ID_ANY, u"Address", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_address.Wrap( -1 )
        self.m_staticText_address.SetFont(font)
        self.gbSizerInitialize.Add( self.m_staticText_address, wx.GBPosition( x+4,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrl_address = wx.TextCtrl( self, wx.ID_ANY, u"1.2.3.4", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl_address.SetFont(font)
        self.m_textCtrl_address.SetMaxLength( 15 ) 
        self.gbSizerInitialize.Add( self.m_textCtrl_address, wx.GBPosition( x+4,y+1 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )


        self.m_button_initialise = wx.Button( self, wx.ID_ANY, u"I N I T I A L I Z E", wx.DefaultPosition, wx.DefaultSize, 0 )
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.m_button_initialise.SetFont(font)
        self.gbSizerInitialize.Add( self.m_button_initialise, wx.GBPosition( x+5,y+0 ), wx.GBSpan( 1, 3 ), wx.ALL|wx.EXPAND, 5 )

        self.m_gauge_progress = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.m_gauge_progress.SetValue( 0 ) 
        #self.m_gauge_progress.Hide( )
        self.pos_gauge_x = x+6
        self.pos_gauge_y = y+0
        self.gbSizerInitialize.Add( self.m_gauge_progress, wx.GBPosition( self.pos_gauge_x, self.pos_gauge_y ), wx.GBSpan( 1, 3 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticTextLiveResult = wx.StaticText( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextLiveResult.Wrap( -1 )
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.m_staticTextLiveResult.SetFont(font)
        self.gbSizerInitialize.Add( self.m_staticTextLiveResult, wx.GBPosition( x+7,y+0 ), wx.GBSpan( 1, 3 ), wx.ALL|wx.EXPAND, 5 )

        # gp_logo = os.path.join(os.path.join(os.path.expanduser('~')), 'grampower/gp_node/gp_node/mri/images/gp_logo.png')
        # self.m_bitmap_logo = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( gp_logo, wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        # self.gbSizerInitialize.Add( self.m_bitmap_logo, wx.GBPosition( x+10,  y+0), wx.GBSpan( 3, 3 ), wx.ALL|wx.RIGHT, 5 )

        gp_text = os.path.join(os.path.join(os.path.expanduser('~')), 'grampower/gp_node/gp_node/mri/images/gp_logo_text.png')
        self.m_bitmap_logo = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( gp_text, wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.gbSizerInitialize.Add( self.m_bitmap_logo, wx.GBPosition( x+11,  y+0), wx.GBSpan( 2, 2 ), wx.ALL, 5 )

        self.m_staticTextmoto = wx.StaticText( self, wx.ID_ANY, u"Electrifying Planet Intelligently!!", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextmoto.Wrap( -1 )
        #self.m_staticTextmoto.SetFont(font)
        self.gbSizerInitialize.Add( self.m_staticTextmoto, wx.GBPosition( x+13,y+0 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )
        ########################################################################################################################
        ##################################  Last Initialization section - 1#####################################################
        ########################################################################################################################
        x_sec_offset = 1
        y_sec_offset = 1
        self.m_staticText_serialNoProcess = wx.StaticText( self, wx.ID_ANY, u"Serial No", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_serialNoProcess.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticText_serialNoProcess, wx.GBPosition( x+x_sec_offset+0,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrl_serialNoProcess = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition,  (150,-1), wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrl_serialNoProcess, wx.GBPosition( x+x_sec_offset+0,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND,5 )
        

        self.m_staticTextIP = wx.StaticText( self, wx.ID_ANY, u"IP", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextIP.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextIP, wx.GBPosition( x+x_sec_offset+1,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlIP = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlIP, wx.GBPosition( x+x_sec_offset+1,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)
        
        self.m_staticTextStatus = wx.StaticText( self, wx.ID_ANY, u"Status", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextStatus.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextStatus, wx.GBPosition( x+x_sec_offset+2,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlStatus = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlStatus, wx.GBPosition( x+x_sec_offset+2,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        self.m_staticTextReason = wx.StaticText( self, wx.ID_ANY, u"Reason", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextReason.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextReason, wx.GBPosition( x+x_sec_offset+3,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlReason = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlReason, wx.GBPosition( x+x_sec_offset+3,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ),wx.ALL|wx.EXPAND, 5)

        self.m_staticTextStage = wx.StaticText( self, wx.ID_ANY, u"Stage", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextStage.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextStage, wx.GBPosition( x+x_sec_offset+4,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlStage = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlStage, wx.GBPosition( x+x_sec_offset+4,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        self.m_staticTextDuration = wx.StaticText( self, wx.ID_ANY, u"Duration", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextDuration.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextDuration, wx.GBPosition( x+x_sec_offset+5,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlDuration = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlDuration, wx.GBPosition( x+x_sec_offset+5,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        self.m_staticTextVersion = wx.StaticText( self, wx.ID_ANY, u"Software Version", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextVersion.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextVersion, wx.GBPosition( x+x_sec_offset+6,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlVersion = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlVersion, wx.GBPosition( x+x_sec_offset+6,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)


        self.m_staticTextTime = wx.StaticText( self, wx.ID_ANY, u"Meter Time", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTime.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextTime, wx.GBPosition( x+x_sec_offset+7,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlTime = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTime, wx.GBPosition( x+x_sec_offset+7,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        self.m_staticTextNxtBillingDate = wx.StaticText( self, wx.ID_ANY, u"Next Billing Date", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNxtBillingDate.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextNxtBillingDate, wx.GBPosition( x+x_sec_offset+8,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlTimeNxtBillingDate = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTimeNxtBillingDate, wx.GBPosition( x+x_sec_offset+8,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        self.m_staticTextInitDate = wx.StaticText( self, wx.ID_ANY, u"Initialization Time", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextInitDate.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextInitDate, wx.GBPosition( x+x_sec_offset+9,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlTimeInitDate = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTimeInitDate, wx.GBPosition( x+x_sec_offset+9,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        self.m_staticTextOverPowerLimit = wx.StaticText( self, wx.ID_ANY, u"Over Power Limit", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextOverPowerLimit.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextOverPowerLimit, wx.GBPosition( x+x_sec_offset+10,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlTimeOverPowerLimit = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTimeOverPowerLimit, wx.GBPosition( x+x_sec_offset+10,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5)

        ########################################################################################################################
        ##################################  Last Initialization section - 1#####################################################
        ########################################################################################################################
        x_sec_offset = 1
        y_sec_offset = 6

        self.m_staticTextSurveyInterval = wx.StaticText( self, wx.ID_ANY, u"LSIP", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextSurveyInterval.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextSurveyInterval, wx.GBPosition( x+x_sec_offset+0,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlSurveyInterval = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlSurveyInterval, wx.GBPosition( x+x_sec_offset+0,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )

        self.m_staticTextMDInterval = wx.StaticText( self, wx.ID_ANY, u"MDIP", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextMDInterval.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextMDInterval, wx.GBPosition( x+x_sec_offset+1,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlMDInterval = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlMDInterval, wx.GBPosition( x+x_sec_offset+1,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )


        self.m_staticTextNoSurvey = wx.StaticText( self, wx.ID_ANY, u"No Of Survey", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNoSurvey.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextNoSurvey, wx.GBPosition( x+x_sec_offset+2,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlNoSurvey = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlNoSurvey, wx.GBPosition( x+x_sec_offset+2,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )


        self.m_staticTextNoDailyProfile = wx.StaticText( self, wx.ID_ANY, u"No Of Daily Profile", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNoDailyProfile.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextNoDailyProfile, wx.GBPosition( x+x_sec_offset+3,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlNoDailyProfile = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlNoDailyProfile, wx.GBPosition( x+x_sec_offset+3,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )

        self.m_staticTextNoEvents = wx.StaticText( self, wx.ID_ANY, u"No Of Events", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNoEvents.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextNoEvents, wx.GBPosition( x+x_sec_offset+4,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlNoEvents = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlNoEvents, wx.GBPosition( x+x_sec_offset+4,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )

        self.m_staticTextNoBillingHistory = wx.StaticText( self, wx.ID_ANY, u"No Of Billing History", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNoBillingHistory.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextNoBillingHistory, wx.GBPosition( x+x_sec_offset+5,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlNoBillingHistory = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlNoBillingHistory, wx.GBPosition( x+x_sec_offset+5,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )

        self.m_staticTexTotRealEnergy = wx.StaticText( self, wx.ID_ANY, u"Total Real Energy", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTexTotRealEnergy.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTexTotRealEnergy, wx.GBPosition( x+x_sec_offset+6,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlTotRealEnergy = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTotRealEnergy, wx.GBPosition( x+x_sec_offset+6,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL,5 )

        self.m_staticTextTimeDrift = wx.StaticText( self, wx.ID_ANY, u"Time Drift", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTimeDrift.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextTimeDrift, wx.GBPosition( x+x_sec_offset+7,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_textCtrlTimeDrift = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTimeDrift, wx.GBPosition( x+x_sec_offset+7,y+y_sec_offset+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5)

        self.m_staticTextTampers = wx.StaticText( self, wx.ID_ANY, u"Live Tampers", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTampers.Wrap( -1 )
        self.gbSizerInitialize.Add( self.m_staticTextTampers, wx.GBPosition( x+x_sec_offset+8,y+y_sec_offset+5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_textCtrlTampers = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        self.gbSizerInitialize.Add( self.m_textCtrlTampers, wx.GBPosition( x+x_sec_offset+8,y+y_sec_offset+6 ), wx.GBSpan( 3, 1 ), wx.ALL|wx.EXPAND,5 )

        self.SetSizer( self.gbSizerInitialize )

        #self.m_button_initialise.Bind( wx.EVT_BUTTON, self.node_shell_api.send_meter_dlms_to_tap )
        self.m_button_initialise.Bind( wx.EVT_BUTTON, self.do_factory_init)

        self.m_textCtrl_serialNo.Bind( wx.EVT_TEXT, self.validate_serial_no )
        self.m_textCtrl_address.Bind( wx.EVT_TEXT, self.validate_ip_address )

        self.check_pre_log_file_exist()
        self.load_ser_no_n_ip()


    def updateProgressBar(self,progress):
        current_progress = self.m_gauge_progress.GetValue()
        current_span = progress - current_progress
        for i in range(0,int(current_span)):
            self.m_gauge_progress.SetValue(int(current_progress+i))
            time.sleep(.1)
            wx.Yield()

    def updateLiveResult(self, msg):
        self.m_staticTextLiveResult.SetLabel(str(msg))
        time.sleep(.1)
        wx.Yield()

    def clearTextBox(self):
        self.m_textCtrlIP.SetValue("")
        self.m_textCtrlStage.SetValue("")
        self.m_textCtrlReason.SetValue("")
        self.m_textCtrlDuration.SetValue("")

        self.m_textCtrl_serialNoProcess.SetValue("")
        self.m_textCtrl_serialNoProcess.SetBackgroundColour("White")
        self.m_textCtrl_serialNoProcess.Refresh()

        self.m_textCtrlStatus.SetValue("")
        self.m_textCtrlStatus.SetBackgroundColour("White")
        self.m_textCtrlStatus.Refresh()

        self.m_textCtrlVersion.SetValue("")
        self.m_textCtrlVersion.SetBackgroundColour("White")
        self.m_textCtrlVersion.Refresh()

        self.m_textCtrlTime.SetValue("")
        self.m_textCtrlTime.SetBackgroundColour("White")
        self.m_textCtrlTime.Refresh()

        self.m_textCtrlTimeDrift.SetValue("")
        self.m_textCtrlTimeDrift.SetBackgroundColour("White")
        self.m_textCtrlTimeDrift.Refresh()

        self.m_textCtrlTimeNxtBillingDate.SetValue("")
        self.m_textCtrlTimeNxtBillingDate.SetBackgroundColour("White")
        self.m_textCtrlTimeNxtBillingDate.Refresh()

        self.m_textCtrlTimeInitDate.SetValue("")
        self.m_textCtrlTimeInitDate.SetBackgroundColour("White")
        self.m_textCtrlTimeInitDate.Refresh()

        self.m_textCtrlTimeOverPowerLimit.SetValue("")
        self.m_textCtrlTimeOverPowerLimit.SetBackgroundColour("White")
        self.m_textCtrlTimeOverPowerLimit.Refresh()

        self.m_textCtrlSurveyInterval.SetValue("")
        self.m_textCtrlSurveyInterval.SetBackgroundColour("White")
        self.m_textCtrlSurveyInterval.Refresh()

        self.m_textCtrlMDInterval.SetValue("")
        self.m_textCtrlMDInterval.SetBackgroundColour("White")
        self.m_textCtrlMDInterval.Refresh()

        self.m_textCtrlNoSurvey.SetValue("")
        self.m_textCtrlNoSurvey.SetBackgroundColour("White")
        self.m_textCtrlNoSurvey.Refresh()

        self.m_textCtrlNoDailyProfile.SetValue("")
        self.m_textCtrlNoDailyProfile.SetBackgroundColour("White")
        self.m_textCtrlNoDailyProfile.Refresh()

        self.m_textCtrlNoEvents.SetValue("")
        self.m_textCtrlNoEvents.SetBackgroundColour("White")
        self.m_textCtrlNoEvents.Refresh()

        self.m_textCtrlNoBillingHistory.SetValue("")
        self.m_textCtrlNoBillingHistory.SetBackgroundColour("White")
        self.m_textCtrlNoBillingHistory.Refresh()

        self.m_textCtrlTotRealEnergy.SetValue("")
        self.m_textCtrlTotRealEnergy.SetBackgroundColour("White")
        self.m_textCtrlTotRealEnergy.Refresh()

        self.m_textCtrlTampers.SetValue("")
        self.m_textCtrlTampers.SetBackgroundColour("White")
        self.m_textCtrlTampers.Refresh()

    def populateTextBoxwithData(self, ip, serial_num, result):

        duration = result.split(",")[0]
        stage = result.split(",")[1]
        stage_val = int(stage.split(":")[1])
        msg = result.split(",")[2]

        self.m_textCtrlIP.SetValue(str(ip))
        self.m_textCtrlStage.SetValue(stage)
        self.m_textCtrlReason.SetValue(msg)
        self.m_textCtrlDuration.SetValue(duration)
        self.m_textCtrl_serialNoProcess.SetValue(serial_num)
        data = self.network_api.get_result_data()

        if(stage_val == 27):            

            self.m_textCtrlStatus.SetValue("SUCCESS")

            print 'dict : ', data

            try:
                self.m_textCtrl_serialNoProcess.SetValue(str(data['serial_no']))
            except Exception:
                pass

            try:
                self.m_textCtrlVersion.SetValue(str(data['soft_ver']))
            except Exception:
                pass

            #times = str(self.timer_on.strftime('%Y-%m-%d %H:%M:%S'))

            #self.m_textCtrlTime.SetValue(str(times[-8:]))

            try:
                self.m_textCtrlTime.SetValue(str(self.meter_init_time))
            except Exception:
                pass

            try:
                self.m_textCtrlTimeDrift.SetValue(str(data['Drift']))
            except Exception:
                pass

            try:
                self.m_textCtrlTimeNxtBillingDate.SetValue(str(data['next_billing_date']))
                # self.m_textCtrlTimeNxtBillingDate.SetValue(str(data['next_billing_date'][:11]))
            except Exception:
                pass

            try:
                self.m_textCtrlTimeInitDate.SetValue(str(data['factory_init_time']))
            except Exception:
                pass

            try:
                self.m_textCtrlTimeOverPowerLimit.SetValue(str(OVERPOWER_LIMIT)+' watts')
            except Exception:
                pass

            try:
                self.m_textCtrlSurveyInterval.SetValue(str(data['SIP']))
            except Exception:
                pass

            try:
                self.m_textCtrlMDInterval.SetValue(str(data['DIP']))
            except Exception:
                pass

            try:
                self.m_textCtrlTotRealEnergy.SetValue(str(data['real_energy']))
            except Exception:
                pass

            try:
                self.m_textCtrlNoSurvey.SetValue(str(data['NoOfSurveysGenerated']))
            except Exception:
                pass

            try:
                self.m_textCtrlNoDailyProfile.SetValue(str(data['num_profile']))
            except Exception:
                pass

            try:
                self.m_textCtrlNoEvents.SetValue(str(data['num_event_record']))
            except Exception:
                pass

            try:
                self.m_textCtrlNoBillingHistory.SetValue(str(data['cu_billing_cnt']))
            except Exception:
                pass

            try:
                self.m_textCtrlTampers.SetValue(str(data['live_tampers']))
            except Exception:
                pass

        else:
            self.m_textCtrlStatus.SetValue("FAILED")
            self.m_textCtrlStatus.SetBackgroundColour("Red")
            self.m_textCtrlStatus.Refresh()
            self.m_staticTextReason.SetBackgroundColour("Red")
            self.m_staticTextReason.Refresh()
            # duration
            # time Drift             24
            
                
            if(stage_val >=26  ):
                if(stage_val ==26 ):   # need to varify 
                    self.m_textCtrlTimeInitDate.SetBackgroundColour("Red")                   
                self.m_textCtrlTimeInitDate.SetValue("")
                self.m_textCtrlTimeInitDate.SetValue(str(data['factory_init_time']))
                self.m_textCtrlTimeInitDate.Refresh()                    
                self.m_textCtrlTime.SetValue("")
                self.m_textCtrlTime.SetValue(str(self.meter_init_time))
                self.m_textCtrlTime.Refresh()
            if(stage_val >= 25):
                if(stage_val == 25):
                    self.m_textCtrlTime.SetBackgroundColour("Red")                    
                self.m_textCtrlTime.SetValue("")
                self.m_textCtrlVersion.SetValue(str(data['soft_ver']))
                self.m_textCtrlTime.Refresh()
            # Address               19,20
            if(stage_val >=  22):
                if(stage_val == 22):
                    self.m_textCtrlNoSurvey.SetBackgroundColour("Red")                    
                self.m_textCtrlNoSurvey.SetValue("")
                self.m_textCtrlNoSurvey.SetValue(str(data['NoOfSurveysGenerated']))
                self.m_textCtrlNoSurvey.Refresh()
            if(stage_val >=  22):
                if(stage_val ==22 ):
                    self.m_textCtrlNoDailyProfile.SetBackgroundColour("Red")                   
                self.m_textCtrlNoDailyProfile.SetValue("")
                self.m_textCtrlNoDailyProfile.SetValue(str(data['num_profile']))
                self.m_textCtrlNoDailyProfile.Refresh()
            if(stage_val >=  21):
                if(stage_val ==21 ):
                    self.m_textCtrlTimeNxtBillingDate.SetBackgroundColour("Red")
                    self.m_textCtrlMDInterval.SetBackgroundColour("Red")
                    self.m_textCtrlNoBillingHistory.SetBackgroundColour("Red")
                    self.m_textCtrlSurveyInterval.SetBackgroundColour("Red")
                    
                self.m_textCtrlTimeNxtBillingDate.SetValue("")
                self.m_textCtrlTimeNxtBillingDate.SetValue(str(data['next_billing_date']))                

                self.m_textCtrlNoBillingHistory.SetValue("")
                self.m_textCtrlNoBillingHistory.SetValue(str(data['cu_billing_cnt']))                
                    
                self.m_textCtrlSurveyInterval.SetValue("")
                self.m_textCtrlSurveyInterval.SetValue(str(data['SIP']))                
                    
                self.m_textCtrlMDInterval.SetValue("")
                self.m_textCtrlMDInterval.SetValue(str(data['DIP']))

                self.m_textCtrlNoBillingHistory.Refresh()
                self.m_textCtrlSurveyInterval.Refresh()
                self.m_textCtrlTimeNxtBillingDate.Refresh()
                self.m_textCtrlMDInterval.Refresh()
            if(stage_val >= 20 ):
                if(stage_val == 20):
                    self.m_textCtrlNoEvents.SetBackgroundColour("Red")                    
                self.m_textCtrlNoEvents.SetValue("")
                self.m_textCtrlNoEvents.SetValue(str(data['num_event_record']))
                self.m_textCtrlNoEvents.Refresh()
            if(stage_val >= 19 ):
                if(stage_val ==19 ):
                    self.m_textCtrlTampers.SetBackgroundColour("Red")                   
                self.m_textCtrlTampers.SetValue("")
                self.m_textCtrlTampers.SetValue(str(data['live_tampers']))
                self.m_textCtrlTampers.Refresh()
            if(stage_val >= 18 ):
                if(stage_val == 18):
                    self.m_textCtrlTimeOverPowerLimit.SetBackgroundColour("Red")                    
                self.m_textCtrlTimeOverPowerLimit.SetValue("")
                self.m_textCtrlTimeOverPowerLimit.SetValue(str(OVERPOWER_LIMIT)+' watts')
                self.m_textCtrlTimeOverPowerLimit.Refresh()  

            if(stage_val >= 12 ):
                if(stage_val == 12):
                    self.m_textCtrlTimeDrift.SetBackgroundColour("Red")                   
                self.m_textCtrlTimeDrift.SetValue("")
                self.m_textCtrlTimeDrift.SetValue(str(data['Drift']))
                self.m_textCtrlTimeDrift.Refresh()          

            if(stage_val >= 7 ):
                if((stage_val ==7) or (stage_val ==8)):
                    self.m_textCtrlTime.SetBackgroundColour("Red")                      
                self.m_textCtrlTime.SetValue("")
                self.m_textCtrl_serialNoProcess.SetValue(str(data['serial_no']))
                self.m_textCtrlTime.Refresh()
            if(stage_val >= 4 ):
                if(stage_val ==6  or stage_val ==5  or stage_val ==4 ):
                    self.m_textCtrlTotRealEnergy.SetBackgroundColour("Red")                    
                self.m_textCtrlTotRealEnergy.SetValue("")
                self.m_textCtrlTotRealEnergy.SetValue(str(data['real_energy']))
                self.m_textCtrlTotRealEnergy.Refresh()
            if(stage_val >= 2 ):
                if(stage_val ==2 ):
                    self.m_textCtrlTampers.SetBackgroundColour("Red")                   
                self.m_textCtrlTampers.SetValue("")
                self.m_textCtrlTampers.SetValue(str(data['live_tampers']))
                self.m_textCtrlTampers.Refresh()

            

            

    def find_dict_element(self, items, dicts):
        for i in dicts:
            if items in i:
                return True
            else:
                pass


    def data_dict_cw(self, tserial, tadd, msg_w, chk):

        with open(MAPPING_LOG, 'r') as f:
            self.c = json.loads(f.read())

        dict_keys = self.c.keys()
        dict_values = self.c.values()

        print 'Keys : ', dict_keys
        print 'Values : ', dict_values

        flag = False

        if chk == True:
            if (tadd in dict_keys):
                if tserial in self.c[tadd]:
                    c = 1
                    print 'Start search : ',tadd + str('_') + str(c)
                    while (tadd + str('_') + str(c)) in dict_keys:
                        print 'follow : ',tadd + str('_') + str(c)
                        c = c + 1

                    print 'Settled with search : ',tadd + str('_') + str(c)
                    tadd = tadd + str('_') + str(c)
                    flag = True
                else:
                    return True

            elif self.find_dict_element(tserial, dict_values):
                print 'Its present already'
                return True
            else:
                pass


        times_now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        self.c[tadd] = [tserial, msg_w, times_now]

        with open(MAPPING_LOG, 'rw+') as f:
            json.dump(self.c, f, sort_keys=True, indent=4, separators=(',', ': '))

        if chk == True:
            if flag == True:
                return tadd
            else:
                return False

    def ShowMessage(self, msg):
        wx.MessageBox(msg, 'Error During Environment Setup', wx.OK | wx.ICON_ERROR)

    def ShowSuccessMessage(self, serial_no, ip_address,time ):
        message = (
            "Details of Meter \n\n"
            "Serial No                : {} \n"
            "Address                  : {} \n"
            "Time for Completion      : {} \n").format(serial_no,ip_address,time)
        wx.MessageBox(message, 'Initialization of meter completed', wx.OK | wx.ICON_INFORMATION)

    def ShowSuccessMessageCustom(self, serial_no, ip_address,msg ):
        duration = msg.split(",")[0]
        stage = msg.split(",")[1]
        reason = msg.split(",")[2]
        message = (
            "Details of Meter \n\n"
            "Serial No               : {}\n"
            "Address                 : {}\n"
            "Durarion                : {}\n"
            "Status                     : {}\n"
            "Stage                      : {}\n"
            "Reason                   : {}\n ").format(serial_no,ip_address,duration,'FAILED',stage,reason)
        wx.MessageBox(message, 'Error During Initialistion', wx.OK | wx.ICON_ERROR)

    def ShowInputErrorMessage(self, serial_no, ip_address, specs=True): 
        
        if specs==True:
            msg1=''
            if(not serial_no):
                msg1 += "\n\nSerail No should not be blank\n\n"
            else:
                serial_no = int(serial_no)
                if((serial_no<100000)or(serial_no>999999)):
                    msg1 += "\n\ninvalid Serail No !\n range (100000 to 999999)\n"
            ip_valid = self.check_for_valid_ip(ip_address)
            if(ip_valid == False):
                msg1 += "Address range (0.0.0.1 to 253.253.253.253)\n\n"

            message = (
                "Your Inputs are below:- \n"
                "Serial No                : {} \n"
                "Address                  : {} \n").format(serial_no,ip_address)
            message = msg1 + message
            wx.MessageBox(message, 'Input Error', wx.OK | wx.ICON_ERROR)
        else:
            message = 'Serial Number or Address has been used before' 
            wx.MessageBox(message, 'Input Error', wx.OK | wx.ICON_ERROR)

    def ShowInputErrorMessage_same_meter(self, serial_no, ip_address):
        msg1 = ''
        ip = []
        serial_n = []

        try:
            with open(os.path.join(os.path.join(os.path.expanduser('~')),'.grampower/mri/log/output_init_1.csv')) as az:
                serial_ip = az.readlines()
            for i in serial_ip[1:]:
                temp = i.split(',')
                ip.append(temp[2])
                serial_n.append(temp[1])
            self.serial_ip_map = dict(zip(ip,serial_n))
            print self.serial_ip_map
        except Exception as e:
            pass

        try:
            if int(self.serial_ip_map[ip_address]) == serial_num:
                return False
        except Exception:
            pass

        message = (
            "Your Inputs are below:- \n"
            "Serial No                : {} \n"
            "Address                  : {} \n").format(serial_no,ip_address)
        message = msg1 + message
        wx.MessageBox(message, 'Input Error', wx.OK | wx.ICON_ERROR)

    def do_factory_init(self, check):

        temp_radio_btn = self.m_radioBoxMeterType.GetSelection()
        print 'Radio :', temp_radio_btn
        check.Skip()
        if temp_radio_btn == 1:
            ip_address = self.m_textCtrl_address.GetValue()
            ip_address = self.format_ip(ip_address)
            self.m_textCtrl_address.SetValue(str(ip_address))
            serial_num = self.m_textCtrl_serialNo.GetValue()
            validate = self.log_file_open()
            if(validate == False):
                self.ShowMessage("Please Close Log File!!!!")
                return
            validate = self.network_api.configure_environment()
            if(validate != True):
                self.ShowMessage(validate)
                return
            result = self.process_factory_init()
            self.updateLiveResult('')
            if(result == False):
                self.network_api.close_serial_port()
                return

            duration = result.split(",")[0]
            stage = result.split(",")[1]

            self.network_api.populate_result()
            if (stage != "Stage:23"):
                self.ShowSuccessMessageCustom(serial_num, ip_address, result)
            else:
                self.ShowSuccessMessage(serial_num, ip_address, duration)

            self.dump_prefactory_init_log(serial_num, ip_address, result)
            self.m_button_initialise.Enable(True)
            self.network_api.close_serial_port()
            self.m_gauge_progress.SetValue(0)
            self.clearTextBox()
            self.populateTextBoxwithData(ip_address,serial_num,result)

        elif temp_radio_btn == 0:

            print MAX_CURRENT, SOFTWARE_VERSION, \
                OVERPOWER_LIMIT, TOTAL_ENERGY, \
                TIME_DRIFT

            ip_address = self.m_textCtrl_address.GetValue()
            ip_address = self.format_ip(ip_address)
            self.m_textCtrl_address.SetValue(str(ip_address))
            serial_num = self.m_textCtrl_serialNo.GetValue()

            validate = self.log_file_open()

            if(validate == False):
                self.ShowMessage("Please Close Log File!!!!")
                return

            validate = self.network_api.configure_environment()

            if(validate != True):
                self.ShowMessage(validate)
                return

            tadds = self.data_dict_cw(serial_num, ip_address, 'FAIL', True)

            if tadds== True:
                self.ShowInputErrorMessage(serial_num,ip_address,False)
            else:
                result = self.process_factory_init_1p()

            self.data_json = self.network_api.get_data_json()

            if(result == False):
                self.network_api.close_serial_port()
                return
            print 'Done'

            duration = result.split(",")[0]

            print result

            stage = result.split(",")[1]

            self.network_api.populate_result()

            if (stage != "Stage:27"):
                self.ShowSuccessMessageCustom(serial_num, ip_address, result)
                if tadds == False:
                    self.dump_prefactory_init_log(serial_num, ip_address, result)
                else:
                    self.dump_prefactory_init_log(serial_num, tadds, result)
            else:
                if tadds == False:
                    self.data_dict_cw(serial_num, ip_address, 'PASS', False)
                    self.dump_prefactory_init_log(serial_num, ip_address, result)
                else:
                    self.data_dict_cw(serial_num, tadds, 'PASS', False)
                    self.dump_prefactory_init_log(serial_num, tadds, result)
                self.ShowSuccessMessage(serial_num, ip_address, duration)
            self.m_button_initialise.Enable(True)
            self.network_api.close_serial_port()
            self.m_gauge_progress.SetValue(0)
            self.clearTextBox()
            self.populateTextBoxwithData(ip_address, serial_num, result)
        else:
            pass


    def process_factory_init_1p(self):

        # self.timer_on = datetime.datetime.now()
        starttime = datetime.datetime.now()

        ip_address = self.m_textCtrl_address.GetValue()
        serial_num = self.m_textCtrl_serialNo.GetValue()
        validate = self.validate_inputs(serial_num,ip_address)

        if(validate == False):
            self.ShowInputErrorMessage(serial_num,ip_address)
            return False

        self.last_ser_num_n_ip_log(serial_num,ip_address)
        self.m_button_initialise.Enable( False )
        self.updateLiveResult('Sending DLMS to TAP')
        self.network_api.send_meter_dlms_to_tap()
        self.network_api.send_dongle_dlms_to_tap()
        self.network_api.send_meter_dlms_to_tap()
        self.updateProgressBar(10)        

        ##############################################################################
        ######################### Checking relay #############################
        ##############################################################################
        self.updateLiveResult('Sending relay_manual_control')
        flag = self.network_api.send_relay_manual_control_1p()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:1,relay_manual_control command failed"
            return error_message
        self.updateProgressBar(10)
        self.updateLiveResult('checking live tamper')
        tamper = self.network_api.check_live_tamper()
        if(tamper == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            self.updateLiveResult('live tamper present')
            error_message += ",Stage:2,live tamper present"
            return error_message
        self.updateProgressBar(15)
        # wx.Yield()
        self.updateLiveResult('Sending turn_relay_off')
        flag = self.network_api.send_turn_relay_off_1p()
        if(flag == False):
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:3,Turn Relay OFF Failed"
            return error_message
        self.updateProgressBar(20)       
        # ##############################################################################
        # ######################### Clear Energy  ######################################
        # ##############################################################################
        # """
        # 1.Maxwell clear 2
        # 2.Check energy is cleared or not
        # 3.If Energy is not cleared, Try one more time
        # """
        self.updateLiveResult('Checking Energy !!!')
        Retry_for_clear_Energy = 0
        flag = self.network_api.verify_energy_reset_1p()
        if(flag == False):
            if ((self.network_api.meter_data['real_energy'] <= ALLOWED_ENERGY) \
            and (self.network_api.meter_data['reactive_energy'] <= ALLOWED_ENERGY)\
            and (self.network_api.meter_data['apparant_energy'] <= ALLOWED_ENERGY)):
                print "energy is in allowed limit ,allowed energy : ",ALLOWED_ENERGY
                pass
            else:
                self.updateLiveResult('Clearing Energy !!!')
                result_max_clear = self.network_api.send_clear_2_cmd()
                if(result_max_clear == True):
                    retry_count = ENERGY_TRIES
                    while retry_count:
                        retry_count = retry_count -1
                        self.network_api.my_delay(2)
                        wx.Yield()
                        self.network_api.my_delay(2)
                        wx.Yield()
                        self.network_api.my_delay(2)
                        wx.Yield()
                        self.network_api.my_delay(2)
                        wx.Yield()
                        self.network_api.my_delay(2)
                        wx.Yield()
                        self.updateLiveResult('verifying cleared Energy !!!')
                        flag = self.network_api.verify_energy_reset_1p()
                        if (flag == True):
                            break
                    if((flag == False) and (retry_count == 0)):
                        self.updateLiveResult('retrying Clearing Energy !!!')
                        print "Retrying Maxwell clear 2"
                        Retry_for_clear_Energy += 1
                        result_max_clear = self.network_api.send_clear_2_cmd()
                        self.network_api.my_delay(0.5)
                        result_max_clear = self.network_api.send_clear_2_cmd()
                        self.network_api.my_delay(10)
                        if(result_max_clear == True):
                            retry_count = 8
                            while retry_count:
                                retry_count = retry_count -1
                                self.network_api.my_delay(1)
                                wx.Yield()
                                self.network_api.my_delay(1)
                                wx.Yield()
                                self.network_api.my_delay(1)
                                wx.Yield()
                                self.network_api.my_delay(1)
                                wx.Yield()
                                self.network_api.my_delay(1)
                                wx.Yield()
                                self.updateLiveResult('Verifying Cleared Energy !!!')
                                flag = self.network_api.verify_energy_reset_1p()
                                if (flag == True):
                                    self.network_api.my_delay(2)
                                    wx.Yield()
                                    self.network_api.my_delay(3)
                                    wx.Yield()
                                    break
                            print "clear enegry Retry Count :", retry_count
                            if((flag == False) and (retry_count == 0)):
                                # Exit Memory is not clearing
                                Endtime = datetime.datetime.now()
                                duration = int((Endtime-starttime).total_seconds())
                                error_message = str(duration)
                                self.updateLiveResult('clear energy verification failed')
                                error_message += ",Stage:4,clear energy verification failed"                                
                                return error_message
                        else:
                            # Not communicating
                            Endtime = datetime.datetime.now()
                            duration = int((Endtime-starttime).total_seconds())
                            error_message = str(duration)
                            self.updateLiveResult('clear_energy failed')
                            error_message += ",Stage:5,clear_energy failed"
                            return error_message
                else:
                    #5. Memeory not clearing or not communicating
                    Endtime = datetime.datetime.now()
                    duration = int((Endtime-starttime).total_seconds())
                    error_message = str(duration)
                    self.updateLiveResult('clear energy not executed')
                    error_message += ",Stage:6,clear energy not executed"
                    return error_message
        self.updateProgressBar(30)

        # # ##############################################################################
        # # ######################### Setting Serial No. ####################################
        # # ##############################################################################
        # # """
        # # 1.Set meter serial No
        # # 2.Verify Serial no
        # # 3.If serial no is not set, Set again
        # # """
        self.updateLiveResult('Setting Serial No')
        global_retry_cnt = 0
        # self.updateLiveResult('Setting serial number to >>'+serial_num)
        flag = self.network_api.send_set_meter_ser_no_3p(serial_num)
        if(flag == False):
            # Exit Not communicating
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            self.updateLiveResult('Setting Serial No failed due to communication')
            error_message += ",Stage:7,Set Serial No Not Communicating"
            return error_message
        self.updateLiveResult('verify Serial No')
        flag = self.network_api.verify_meter_ser_no_1p(serial_num)
        if(flag == False):
            result_set_ser_no = self.network_api.send_set_meter_ser_no_3p(serial_num)
            time.sleep(0.5)
            flag = self.network_api.verify_meter_ser_no_1p(serial_num)
            if(False==result_set_ser_no):
                global_retry_cnt = global_retry_cnt + 1
                # 1. Exit Point - Means No communication
                Endtime = datetime.datetime.now()
                duration = int((Endtime-starttime).total_seconds())
                error_message = str(duration)
                self.updateLiveResult('set Serial No Not Communicating in retry')
                error_message += ",Stage:8,retry set Serial No Not Communicating"
                return error_message
        self.updateLiveResult('Setting Serial No Completed')
        self.updateProgressBar(40)

        # # ##############################################################################
        # # ######################### No Load Current Verify #############################
        # # ##############################################################################
        # # '''
        # # Wait till realy off
        # # '''
        self.updateLiveResult('Starting No Load Test')
        # self.m_gauge_progress.SetValue(60)            #??????????????
        retry_count = 3
        while retry_count:
            retry_count = retry_count - 1
            wx.Yield()
            self.network_api.my_delay(1)
        flag = self.network_api.verify_no_load_current_1p()
        if(False == flag):
            #No load test failed or communication Error
            Endtime = datetime.datetime.now()
            duration = int((Endtime - starttime).total_seconds())
            error_message = str(duration)
            self.updateLiveResult('metering command execution failed')
            error_message += ",Stage:9,No Load Test Failed/Not Communicating"
            return error_message

        # self.updateLiveResult('No Load Test Completed')

        # # ##############################################################################
        # # ######################### Factory Init ######################################
        # # ##############################################################################
        # # '''
        # # 1.Turn Relay On
        # # 2.Check for Data Valid
        # # 3.Do factoy init
        # # '''
        self.updateLiveResult('Turning relay on')
        flag = self.network_api.send_turn_relay_on_1p()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            self.updateLiveResult('command execution failed')
            error_message += ",Stage:10,Turning Relay ON Failed/Not Communicating"
            return error_message
        
        time.sleep(2)    # delay for load test
        self.updateLiveResult('Load Test started')
        flag = self.network_api.verify_load_presence_1p()
        if(flag == False):
            print 'ERROR'
            # Exit Load test failed, communication failure
            Endtime = datetime.datetime.now()
            duration = int((Endtime - starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:11,Load Test Failed/Not Communicating"

            return error_message
        else:
            self.updateLiveResult('Load Test Completed')
        self.updateProgressBar(50)

        ###########
        self.updateLiveResult('time drift test started')
        flag = self.network_api.send_get_drift_time()
        if(flag == False):
            print 'ERROR'
            # Exit Load test failed, communication failure
            Endtime = datetime.datetime.now()
            duration = int((Endtime - starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:12,Time Drift Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('time drift completed')        
            self.updateProgressBar(55)
        #############################################
        factory_done=False
        for i in range(FACTORY_TRIES):
            if factory_done is False:
                self.updateLiveResult('sending factory_init_1 command')
                flag = self.network_api.send_factory_init_1_1p()
                if(flag == True):
                    print 'Factory init Done'
                    # 3. Exit Point - Address is not setting
                    Endtime = datetime.datetime.now()
                    self.updateLiveResult('sending factory_init_2 command')
                    for i in range(2):
                        flag = self.network_api.send_factory_init_2_1p()
                        if(flag == 'ok'):
                            self.updateLiveResult('factory_init command executed sucessfully')
                            print 'Factory init Check Done'
                            factory_done=True
                            self.network_api.my_delay(5)
                            self.updateLiveResult('resetting meter')
                            self.network_api.send_reset()
                            self.network_api.my_delay(15)
                            self.network_api.send_dongle_dlms_to_tap()
                            self.network_api.send_meter_dlms_to_tap()
                            Endtime = datetime.datetime.now()
                            self.updateLiveResult('reading factory init time from meter')
                            self.network_api.update_fatcory_init_time()
                            break
                        else:
                            print "it will be retried after 1 second...."
                            time.sleep(1)
        if(factory_done is False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            self.updateLiveResult('factory_init command execution failed')
            error_message += ",Stage:13,Factory Init 2 Failed/Not Communicating"
            return error_message
#            else:
#                flag = self.network_api.send_factory_init_1_1p()

        self.updateLiveResult('Factory Reset Completed')
        self.updateProgressBar(60)

        # ##############################################################################
        # ######################### Verifying Factory Init ####################################
        # ##############################################################################

        self.updateLiveResult('Validating Factory Init')
        # reason = ''
        self.network_api.my_delay(10)

        flag = self.network_api.verify_tariff_slab()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime - starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:14,Tariff Slab Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified tariff slab')
            self.updateProgressBar(61)


        flag = self.network_api.verify_fixed_deduction()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:15,Fixed Deduction Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified fd')
            self.updateProgressBar(62)

        flag = self.network_api.verify_prepaid()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:16,Prepaid Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified prepaid')
            self.updateProgressBar(63)

        flag = self.network_api.verify_recharge()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:17,Recharge Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified recharge')
            self.updateProgressBar(64)

        flag = self.network_api.verify_power_limiter()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:18,Power Limiter Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified power limit')
            self.updateProgressBar(65)

        flag = self.network_api.verify_tamper_record()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:19,Tamper Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified tamper records')
            self.updateProgressBar(66)

        flag = self.network_api.verify_event_record()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:20,Event Record Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified event records')
            self.updateProgressBar(67)

        flag = self.network_api.verify_billing()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:21,Billing Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified billing')
            self.updateProgressBar(68)

        flag = self.network_api.verify_block_load_profile()
        if(flag == False):
            # Exit Not communication
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:22,Block Load Verification Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verified block load profile')
            self.updateProgressBar(69)

        # ###############()###############################################################
        # ######################### Setting Address ####################################
        # ##############################################################################
        self.updateLiveResult('setting address')
        flag = self.network_api.send_set_address_1p(ip_address)
        if(flag == False):
            # Exit Not communicating
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:23,Setting Address Failed/Not Communicating"
            return error_message
        self.updateLiveResult('Verified address')
        flag = self.network_api.verify_address_1p(ip_address)
        if(flag == False ):
            # Exit Either not communicating or address is not set
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:24,Verifying Address Failed/Not Communicating"
            return error_message
        self.updateLiveResult('Setting Address Completed')
        self.updateProgressBar(70)

        # ##############################################################################
        # ######################### Verifying  Soft_version####################################
        # ##############################################################################
        self.updateLiveResult('setting software version')
        flag = self.network_api.send_get_soft_version_1p()
        if(flag == False):
            # Exit Not communicating
            Endtime = datetime.datetime.now()
            duration = int((Endtime-starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:25,Getting Soft Version Failed/Not Communicating"
            return error_message
        else:
            self.updateLiveResult('Verifying Soft Version Completed')
            self.updateProgressBar(80)

        # ##############################################################################
        # ######################### Extra Commands #########################################
        # ##############################################################################

        self.network_api.send_extra_ones()

        # ##############################################################################
        # ######################### Init time test #########################################
        # ##############################################################################
        self.updateLiveResult('getting meter_init_time')
        flag = str(self.network_api.send_get_time())
        self.meter_init_time = datetime.datetime.strptime(flag, '%Y-%m-%d %H:%M:%S')
        duration = int((self.meter_init_time - self.network_api.meter_data['factory_init_time']).total_seconds()) 
        self.updateLiveResult('getting meter_init_time')
        print 'time for meter now :',self.meter_init_time
        print 'time for factory meter init :',self.network_api.meter_data['factory_init_time']
        print 'diff : ',duration
        self.updateProgressBar(90)
        if duration > 300:      
            flag = False
        else:
            flag = True
            pass

        if(flag == False):
            print 'ERROR'
            # Exit Load test failed, communication failure
            Endtime = datetime.datetime.now()
            duration = int((Endtime - starttime).total_seconds())
            error_message = str(duration)
            error_message += ",Stage:26,Init time diff Failed/Not Communicating"
            return error_message  
        else:
            self.updateLiveResult('meter time read successfull')
        self.timer_on = str(self.network_api.send_get_time())
        Endtime = datetime.datetime.now()
        duration = int((Endtime - starttime).total_seconds())
        error_message = str(duration)
        error_message += ",Stage:27,completed"
        self.updateLiveResult('Completed')
        self.updateProgressBar(100)
        return error_message     
        


    def validate_inputs(self,serial_num,ip_address):
        if(not serial_num):
            return False
        serial_num = int(serial_num)
        if((serial_num < 100000)or(serial_num > 999999)):
            return False
        ip_valid = self.check_for_valid_ip(ip_address)
        #print ip_valid

        if((ip_address == "0.0.0.0") or (ip_address == "0.0.0.12")):
            return False
        if(ip_valid):
            return True
        else:
            return False

    def validate_serial_no(self, check):
        val = self.m_textCtrl_serialNo.GetValue()
        if(len(val) == 0):
            return
        if(val.isdigit()):
            return
        formatted_string = []
        if not val.isdigit():
            for s in val:
                if s.isdigit():
                    formatted_string.append(s)
            str1 = ''.join(str(e) for e in formatted_string)
            self.m_textCtrl_serialNo.SetValue(str1)
            self.m_textCtrl_serialNo.SetInsertionPointEnd()
        else:
            value = int(val)
            check.Skip()

    def validate_ip_address(self, check):
        check.Skip()
        val = self.m_textCtrl_address.GetValue()
        flag = self.check_for_valid_running_ip(val)
        if(flag == True):
            return
        format_ip = self.format_ip(val)
        print "EXP -IP", format_ip
        self.m_textCtrl_address.SetValue(str(format_ip))
        self.m_textCtrl_address.Refresh()
        wx.Yield()
        self.m_textCtrl_address.SetInsertionPointEnd()
        wx.Yield()


    def check_for_valid_running_ip(self,ip):
        val = str(ip)
        if(len(val)==0):
            return True

        if(val[0]=='.'):
            return False
        if not val[0].isdigit():
            #print "IP should not be alphabet"
            return False
        
        formatted_string = ''

        if val.isdigit():
            if (int(val)>99):
                #print "Value greater than 99"
                return False
            else:
                return True

        if not val.isdigit():
            for s in val:
                if ((s.isdigit()) or (s == '.')):
                    formatted_string += s
                else:
                    return False
        str1 = ''.join(str(e) for e in formatted_string)
        #print "str1",str1

        string_found = str1.find("..")
        if(string_found != -1):
            return False

        ip = str1.split(".")
        if(len(ip)>4):
            return False
        for i in range(len(ip)):
            if(ip[i].isdigit()):
                if(int(ip[i]) > 254):
                    #print "Greater than 99"
                    return False
        return True

    def format_ip(self,ip_add):
        ip = str(ip_add)
        if(ip[0]=='.'):
            ip = ip.replace(".", "0", 1)

        if not ip[0].isdigit():
            return ''

        if ip.isdigit():
            ip = int(ip)
            if(int(ip) > 254):
                ip = int(ip) /10
            return ip

        #print "Raw IP", ip,len(ip)
        ip = ip.replace("..", '.')
        #print "Replaced IP", ip,len(ip)
        no_of_dot = ip.count('.')
        chipped_ip = ''
        if(no_of_dot>3):
            for n in range(len(ip),0,-1):
                if(ip[(n-1)]=='.'):
                    chipped_ip = ip[0:(n-1)]
                    break
        else:
            chipped_ip = ip

        #print "Chipped IP", chipped_ip,len(chipped_ip)
        formatted_string = ''
        if not chipped_ip.isdigit():
            for s in chipped_ip:
                if ((s.isdigit()) or (s == '.')):
                    formatted_string += s
        str1 = ''.join(str(e) for e in formatted_string)
        #print "string1",str1,formatted_string
        chipped_ip = str1.split(".")

        ip_new = chipped_ip
        ip_new = filter(None, ip_new)
        for i in range(0,len(ip_new)):
            print hex(int(ip_new[i]))
            ip_new[i] = int(ip_new[i])
            if(int(ip_new[i])> 254):
                ip_new[i] = int(ip_new[i]) /10

        #print "Length of after",len(ip_new),ip_new

        ip_string = ''
        for i in range(len(ip_new)):
            ip_string += str(ip_new[i])
            ip_string += '.'

        if ((int((ip_new[len(ip_new)-1]))>99) and (len(ip_new)<4)):
            ip_string += '.'

        #print "Last IP",ip_string[:-1]
        return ip_string[:-1]

    def check_for_valid_ip(self,ip):
        val = str(ip)
        if(len(val)==0):
            return False
        formatted_string = ''
        if not val.isdigit():
            for s in val:
                if ((s.isdigit()) or (s == '.')):
                    formatted_string += s
                else:
                    return False
        str1 = ''.join(str(e) for e in formatted_string)

        string_found = str1.find("..")
        if(string_found != -1):
            return False

        ip = str1.split(".")
        if(len(ip) != 4):
            return False
        if(not ip[3]):
            return False
        for i in range(len(ip)):
            if(ip[i].isdigit()):
                ip[i] = int(ip[i])
                if(int(ip[i]) > 254):
                    return False
        return True

    def json_creation(self):
        pass

    def dump_prefactory_init_log(self,ser_num, ip, msg):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = str(current_date) +','
        data += str(ser_num) + ','
        data += str(ip) + ','
        duration = msg.split(",")[0]
        stage = msg.split(",")[1]
        msg = msg.split(",")[2]
        data += str(duration) + ','
        if(stage == 'Stage:27'):
            data += "SUCCESS,"
            #data += "Reason:Born to Win,"
        else:
            data += "FAILED,"
        data += str(msg) + ','

        # if(stage == 'Stage:25'):
        #     #Process data and log
        #     # temp = self.network_api.populate_result()
        #     data += temp + '\n'
        #     pass
        # else:
        #     data += "\n"
        #     pass

        data_to_write = self.network_api.get_data_json()

        data_to_write['status'] = data

        todays = str(datetime.datetime.now().date())

        if os.path.isdir(LOG_PATH):
            pass
        else:
            os.mkdir(LOG_PATH)

        os.chdir(LOG_PATH)


        log_file = (str(ip)).replace('.','_')+'.json'
        print 'Log_file : ', log_file
        with open(log_file, 'w') as fp:
            json.dump(data_to_write, fp, sort_keys=True, indent=4, separators=(',', ': '))

        return data

        self.result_data = result
        print result
        return self.result_data

    def log_file_open(self):
        self.check_log_file_exist()

        try:
            f = open(MAPPING_LOG, 'r')
            f.close()
        except:
            return False
        return True

    def check_log_file_exist(self):
        log_path = os.path.join(os.path.join(os.path.expanduser('~')), '.grampower')
        flag = os.path.exists(log_path)
        if(flag == False):
            os.makedirs(log_path)
            print ".grampower created"

        log_path = os.path.join(log_path, 'mri')
        print log_path
        flag = os.path.exists(log_path)
        if(flag == False):
            os.makedirs(log_path)
            print "mri created"

        log_path = os.path.join(log_path, 'log')
        print log_path
        flag = os.path.exists(log_path)
        if(flag == False):
            os.makedirs(log_path)
            print "log created"

        log_file = MAPPING_LOG
        print 'log_file : ', log_file
        flag = os.path.exists(log_file)
        if(flag == False):
            print "Creating Log File 2"
            f = open(log_file, 'w')
            f.write('{}')
            f.close()

    def check_pre_log_file_exist(self):
        log_file = os.path.join(os.path.join(os.path.expanduser('~')), 'grampower/gp_node/gp_node/mri/config/last_ser_no_ip.csv')
        flag = os.path.exists(log_file)
        csv_header = "023456,0.0.0.255\n"


        if(flag == False):
            print "Creating Last serial no log file"
            f = open(log_file, 'w')
            f.write(csv_header)
            f.close()

    def last_ser_num_n_ip_log(self, ser_num, ip):
        log_file = os.path.join(os.path.join(os.path.expanduser('~')), 'grampower/gp_node/gp_node/mri/config/last_ser_no_ip.csv')
        flag = os.path.exists(log_file)
        csv_header = ''
        csv_header += ser_num + ',' + ip + '\n'

        f = open(log_file, 'w')
        f.write(csv_header)
        f.close()

    def load_ser_no_n_ip(self):
        log_file = os.path.join(os.path.join(os.path.expanduser('~')), 'grampower/gp_node/gp_node/mri/config/last_ser_no_ip.csv')
        f = open(log_file, 'r')
        data = f.read()
        f.close()
        serial_num = data.split(',')[0]
        ip_address = data.split(',')[1]

        self.m_textCtrl_address.SetValue(ip_address)
        self.m_textCtrl_serialNo.SetValue(serial_num)
