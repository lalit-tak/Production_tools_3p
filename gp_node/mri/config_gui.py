# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################
import os
import wx
import wx.xrc
import xml.etree.cElementTree as ET
###########################################################################
# Class MyFrame2
###########################################################################


class ConfigPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

    # def __init__( self, parent ):
        #wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        gbSizerConfig = wx.GridBagSizer(1, 0)
        gbSizerConfig.SetFlexibleDirection(wx.BOTH)
        gbSizerConfig.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        gbSizerConfig.SetEmptyCellSize(wx.Size(40, 40))

        x = 2
        y = 4

        #######################################################################
        ##################################  Misc Settings  ####################
        #######################################################################
        self.m_staticTextSerialCaption = wx.StaticText(
            self, wx.ID_ANY, u"Misc Settings", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextSerialCaption.Wrap(-1)
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.m_staticTextSerialCaption.SetFont(font)
        gbSizerConfig.Add(
            self.m_staticTextSerialCaption, wx.GBPosition(
                x, y), wx.GBSpan(
                1, 2), wx.ALL | wx.ALIGN_CENTER, 5)

        m_radioBoxMeterTypeChoices = [u"Single Phase ", u"Three Phase"]
        self.m_radioBoxMeterType = wx.RadioBox(
            self,
            wx.ID_ANY,
            u"Meter Type",
            wx.DefaultPosition,
            wx.DefaultSize,
            m_radioBoxMeterTypeChoices,
            1,
            wx.RA_SPECIFY_ROWS)
        self.m_radioBoxMeterType.SetSelection(1)
        self.m_radioBoxMeterType.Enable(False)
        gbSizerConfig.Add(self.m_radioBoxMeterType, wx.GBPosition(
            x + 1, y + 0), wx.GBSpan(2, 2), wx.ALL | wx.EXPAND, 5)

        self.m_staticTextPort = wx.StaticText(
            self,
            wx.ID_ANY,
            u"Serial Port",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTextPort.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextPort,
            wx.GBPosition(
                x + 3,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        m_comboBoxPortChoices = [u"/dev/gp-gateway"]
        self.m_comboBoxPort = wx.ComboBox(
            self,
            wx.ID_ANY,
            u"/dev/gp-gateway",
            wx.DefaultPosition,
            wx.DefaultSize,
            m_comboBoxPortChoices,
            wx.CB_READONLY)
        self.m_comboBoxPort.SetSelection(0)
        gbSizerConfig.Add(
            self.m_comboBoxPort,
            wx.GBPosition(
                x + 3,
                y + 1),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextBaudRate = wx.StaticText(
            self, wx.ID_ANY, u"Baud Rate", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextBaudRate.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextBaudRate,
            wx.GBPosition(
                x + 4,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        m_comboBoxBaudRateChoices = [u"9600"]
        self.m_comboBoxBaudRate = wx.ComboBox(
            self,
            wx.ID_ANY,
            u"9600",
            wx.DefaultPosition,
            wx.DefaultSize,
            m_comboBoxBaudRateChoices,
            wx.CB_READONLY)
        self.m_comboBoxBaudRate.SetSelection(0)
        gbSizerConfig.Add(
            self.m_comboBoxBaudRate,
            wx.GBPosition(
                x + 4,
                y + 1),
            wx.GBSpan(
                1,
                1),
            wx.EXPAND | wx.ALL,
            5)

        self.m_staticTimeDrift = wx.StaticText(
            self,
            wx.ID_ANY,
            u"Drift in Time",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTimeDrift.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTimeDrift,
            wx.GBPosition(
                x + 5,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlTimeDrift = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlTimeDrift,
            wx.GBPosition(
                x + 5,
                y + 1),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        #######################################################################
        ##################################  No Load Current Settings Section ##
        #######################################################################
        self.m_staticTextNoLoad = wx.StaticText(
            self,
            wx.ID_ANY,
            u"No Load Current Settings",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTextNoLoad.Wrap(-1)
        self.m_staticTextNoLoad.SetFont(font)
        gbSizerConfig.Add(
            self.m_staticTextNoLoad,
            wx.GBPosition(
                x + 6,
                y + 0),
            wx.GBSpan(
                1,
                2),
            wx.ALL | wx.ALIGN_CENTER,
            5)

        self.m_staticTextRPhaseNoLoad = wx.StaticText(
            self, wx.ID_ANY, u"R Phase(mA)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextRPhaseNoLoad.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextRPhaseNoLoad,
            wx.GBPosition(
                x + 7,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlRPhaseNoLoad = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlRPhaseNoLoad,
            wx.GBPosition(
                x + 7,
                y + 1),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextYPhaseNoLoad = wx.StaticText(
            self, wx.ID_ANY, u"Y Phase(mA)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextYPhaseNoLoad.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextYPhaseNoLoad,
            wx.GBPosition(
                x + 8,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlYPhaseNoLoad = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlYPhaseNoLoad,
            wx.GBPosition(
                x + 8,
                y + 1),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextBPhaseNoLoad = wx.StaticText(
            self, wx.ID_ANY, u"B Phase(mA)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextBPhaseNoLoad.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextBPhaseNoLoad,
            wx.GBPosition(
                x + 9,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlBPhaseNoLoad = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlBPhaseNoLoad,
            wx.GBPosition(
                x + 9,
                y + 1),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        #######################################################################
        ##################################  Energy Settings Section ###########
        #######################################################################
        self.m_staticTextEnergy = wx.StaticText(
            self,
            wx.ID_ANY,
            u"Energy offset Settings",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTextEnergy.Wrap(-1)
        self.m_staticTextEnergy.SetFont(font)
        gbSizerConfig.Add(
            self.m_staticTextEnergy,
            wx.GBPosition(
                x + 0,
                y + 4),
            wx.GBSpan(
                1,
                2),
            wx.ALL | wx.ALIGN_CENTER,
            5)

        self.m_staticTextTotalRealEnergy = wx.StaticText(
            self, wx.ID_ANY, u"Total Real Energy", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextTotalRealEnergy.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextTotalRealEnergy,
            wx.GBPosition(
                x + 1,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlTotalRealEnergy = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlTotalRealEnergy,
            wx.GBPosition(
                x + 1,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextTotalApparentEnergy = wx.StaticText(
            self, wx.ID_ANY, u"Total Apparent Energy", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextTotalApparentEnergy.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextTotalApparentEnergy,
            wx.GBPosition(
                x + 2,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlTotalApparentEnergy = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlTotalApparentEnergy,
            wx.GBPosition(
                x + 2,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextTotalReactiveEnergy = wx.StaticText(
            self, wx.ID_ANY, u"Total Reactive Energy", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextTotalReactiveEnergy.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextTotalReactiveEnergy,
            wx.GBPosition(
                x + 3,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlTotalReactiveEnergy = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlTotalReactiveEnergy,
            wx.GBPosition(
                x + 3,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextTotalLagReactiveEnergy = wx.StaticText(
            self,
            wx.ID_ANY,
            u"Lag Only Reactive Energy",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTextTotalLagReactiveEnergy.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextTotalLagReactiveEnergy,
            wx.GBPosition(
                x + 4,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlTotalLagReactiveEnergy = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlTotalLagReactiveEnergy,
            wx.GBPosition(
                x + 4,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextTotalLeadReactiveEnergy = wx.StaticText(
            self,
            wx.ID_ANY,
            u"Lead Only Reactive Energy",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTextTotalLeadReactiveEnergy.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextTotalLeadReactiveEnergy,
            wx.GBPosition(
                x + 5,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlTotalLeadReactiveEnergy = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlTotalLeadReactiveEnergy,
            wx.GBPosition(
                x + 5,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        #######################################################################
        ##################################  Load Current Settings Section #####
        #######################################################################

        self.m_staticTextLoad = wx.StaticText(
            self,
            wx.ID_ANY,
            u"Load Current Settings",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_staticTextLoad.Wrap(-1)
        self.m_staticTextLoad.SetFont(font)
        gbSizerConfig.Add(
            self.m_staticTextLoad,
            wx.GBPosition(
                x + 6,
                y + 4),
            wx.GBSpan(
                1,
                2),
            wx.ALL | wx.ALIGN_CENTER,
            5)

        self.m_staticTextRPhaseNoLoad = wx.StaticText(
            self, wx.ID_ANY, u"R Phase(mA)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextRPhaseNoLoad.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextRPhaseNoLoad,
            wx.GBPosition(
                x + 7,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlRPhaseLoad = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlRPhaseLoad,
            wx.GBPosition(
                x + 7,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextYPhaseNoLoad = wx.StaticText(
            self, wx.ID_ANY, u"Y Phase(mA)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextYPhaseNoLoad.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextYPhaseNoLoad,
            wx.GBPosition(
                x + 8,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlYPhaseLoad = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlYPhaseLoad,
            wx.GBPosition(
                x + 8,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_staticTextBPhaseNoLoad = wx.StaticText(
            self, wx.ID_ANY, u"B Phase(mA)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextBPhaseNoLoad.Wrap(-1)
        gbSizerConfig.Add(
            self.m_staticTextBPhaseNoLoad,
            wx.GBPosition(
                x + 9,
                y + 4),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_textCtrlBPhaseLoad = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_READONLY)
        gbSizerConfig.Add(
            self.m_textCtrlBPhaseLoad,
            wx.GBPosition(
                x + 9,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.ALL,
            5)

        self.m_button_edit = wx.Button(
            self,
            wx.ID_ANY,
            u"Edit",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_button_edit.Enable(False)
        gbSizerConfig.Add(
            self.m_button_edit,
            wx.GBPosition(
                x + 10,
                y + 0),
            wx.GBSpan(
                1,
                1),
            wx.EXPAND | wx.ALL,
            5)

        self.m_button_set = wx.Button(
            self,
            wx.ID_ANY,
            u"Set",
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.m_button_set.Enable(False)
        gbSizerConfig.Add(
            self.m_button_set,
            wx.GBPosition(
                x + 10,
                y + 5),
            wx.GBSpan(
                1,
                1),
            wx.EXPAND | wx.ALL,
            5)

        # self.m_button_exit = wx.Button( self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0 )
        # gbSizerConfig.Add( self.m_button_exit, wx.GBPosition( x+10, y+6 ), wx.GBSpan( 1, 1 ), wx.EXPAND |wx.ALL, 5 )
        self.load_config_from_xml()
        self.update_config_to_ui()

        self.SetSizer(gbSizerConfig)
        self.Layout()

        self.Centre(wx.BOTH)

    def load_config_from_xml(self):
        config_file = os.path.join(
            os.path.join(
                os.path.expanduser('~')),
            'grampower/gp_node/gp_node/mri/config/config.xml')
        print config_file
        try:
            f = open(config_file, 'r')
            f.close()
        except BaseException:
            print "Not Able to open"
        #tree = ET.ElementTree(file=config_file)
        tree = ET.parse(config_file)
        root = tree.getroot()
        print tree
        print root
        print "----------------------------------------"
        # Misc Settings
        for elem in tree.iter(tag='PortNo'):
            self.SERIAL_PORT = str(elem.text)

        for elem in tree.iter(tag='BaudRate'):
            self.BAUD_RATE = int(elem.text)

        for elem in tree.iter(tag='TimeOut'):
            self.TIME_OUT = int(elem.text)

        for elem in tree.iter(tag='TimeDrift'):
            self.TIME_DRIFT = int(elem.text)

        # Three Phase settings
        for elem in tree.iter(tag='NoLoadCurrentRPhase'):
            self.MAX_NO_LOAD_CURRENT_R_PHASE_3P = int(elem.text)
        for elem in tree.iter(tag='NoLoadCurrentYPhase'):
            self.MAX_NO_LOAD_CURRENT_Y_PHASE_3P = int(elem.text)
        for elem in tree.iter(tag='NoLoadCurrentBPhase'):
            self.MAX_NO_LOAD_CURRENT_B_PHASE_3P = int(elem.text)

        for elem in tree.iter(tag='LoadCurrentRPhase'):
            self.MIN_LOAD_CURRENT_R_PHASE_3P = int(elem.text)
        for elem in tree.iter(tag='LoadCurrentYPhase'):
            self.MIN_LOAD_CURRENT_Y_PHASE_3P = int(elem.text)
        for elem in tree.iter(tag='LoadCurrentBPhase'):
            self.MIN_LOAD_CURRENT_B_PHASE_3P = int(elem.text)

        for elem in tree.iter(tag='TotalRealEnergy'):
            self.MAX_TOTAL_REAL_ENERGY_3P = int(elem.text)
        for elem in tree.iter(tag='TotalApparentEnergy'):
            self.MAX_TOTAL_APPARENT_ENERGY_3P = int(elem.text)
        for elem in tree.iter(tag='TotalReactiveEnergy'):
            self.MAX_TOTAL_REACTIVE_ENERGY_3P = int(elem.text)
        for elem in tree.iter(tag='LagOnlyReactiveEnergy'):
            self.MAX_LAG_ONLY_REACTIVE_ENERGY_3P = int(elem.text)
        for elem in tree.iter(tag='LeadOnlyReactiveEnergy'):
            self.MAX_LEAD_ONLY_REACTIVE_ENERGY_3P = int(elem.text)

        # Single Phase settings
        for elem in tree.iter(tag='NoLoadCurrent'):
            self.MAX_NO_LOAD_CURRENT_1P = int(elem.text)
        for elem in tree.iter(tag='LoadCurrent'):
            self.MIN_LOAD_CURRENT_1P = int(elem.text)
        for elem in tree.iter(tag='TotalRealEnergy_1p'):
            self.MAX_TOTAL_REAL_ENERGY_1P = int(elem.text)

    def update_config_to_ui(self):
        self.m_comboBoxPort.SetString(0, str(self.SERIAL_PORT))
        self.m_comboBoxBaudRate.SetString(0, str(self.BAUD_RATE))
        self.m_textCtrlTimeDrift.SetValue(str(self.TIME_DRIFT))
        self.m_textCtrlRPhaseNoLoad.SetValue(
            str(self.MAX_NO_LOAD_CURRENT_R_PHASE_3P))
        self.m_textCtrlYPhaseNoLoad.SetValue(
            str(self.MAX_NO_LOAD_CURRENT_Y_PHASE_3P))
        self.m_textCtrlBPhaseNoLoad.SetValue(
            str(self.MAX_NO_LOAD_CURRENT_B_PHASE_3P))
        self.m_textCtrlTotalRealEnergy.SetValue(
            str(self.MAX_TOTAL_REAL_ENERGY_3P))
        self.m_textCtrlTotalApparentEnergy.SetValue(
            str(self.MAX_TOTAL_APPARENT_ENERGY_3P))
        self.m_textCtrlTotalReactiveEnergy.SetValue(
            str(self.MAX_TOTAL_REACTIVE_ENERGY_3P))
        self.m_textCtrlTotalLagReactiveEnergy.SetValue(
            str(self.MAX_LAG_ONLY_REACTIVE_ENERGY_3P))
        self.m_textCtrlTotalLeadReactiveEnergy.SetValue(
            str(self.MAX_LEAD_ONLY_REACTIVE_ENERGY_3P))
        self.m_textCtrlRPhaseLoad.SetValue(
            str(self.MIN_LOAD_CURRENT_R_PHASE_3P))
        self.m_textCtrlYPhaseLoad.SetValue(
            str(self.MIN_LOAD_CURRENT_Y_PHASE_3P))
        self.m_textCtrlBPhaseLoad.SetValue(
            str(self.MIN_LOAD_CURRENT_B_PHASE_3P))

    def __del__(self):
        pass
