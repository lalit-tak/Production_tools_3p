# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrame2
###########################################################################

#class MyFrame1 ( wx.Frame ):
    
class MonitorPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        gbSizerMonitor = wx.GridBagSizer( 0, 0 )
        gbSizerMonitor.SetFlexibleDirection( wx.BOTH )
        gbSizerMonitor.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        gbSizerMonitor.SetEmptyCellSize( wx.Size( 25,25 ) )

        x = 2
        y = 2

        ########################################################################################################################
        ##################################  Instantaneous Parameters Section ###################################################
        ########################################################################################################################
        self.m_staticTextInstantaniousParams = wx.StaticText( self, wx.ID_ANY, u"Instantaneous Parameters", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextInstantaniousParams.Wrap( -1 )
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.m_staticTextInstantaniousParams.SetFont(font)
        gbSizerMonitor.Add( self.m_staticTextInstantaniousParams, wx.GBPosition( x, y ), wx.GBSpan( 1, 2 ), wx.ALL|wx.ALIGN_CENTER, 5 )

        

        self.m_staticTextDateTime = wx.StaticText( self, wx.ID_ANY, u"Date Time", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextDateTime.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextDateTime, wx.GBPosition( x+1,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlDateTime = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlDateTime, wx.GBPosition( x+1, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextSerialNo = wx.StaticText( self, wx.ID_ANY, u"Serial No", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextSerialNo.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextSerialNo, wx.GBPosition( x+2,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlSerialNo = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlSerialNo, wx.GBPosition( x+2, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextRVoltage = wx.StaticText( self, wx.ID_ANY, u"R Voltage(V)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextRVoltage.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextRVoltage, wx.GBPosition( x+3,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlRVoltage = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlRVoltage, wx.GBPosition( x+3, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextYVoltage = wx.StaticText( self, wx.ID_ANY, u"Y Voltage(V)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextYVoltage.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextYVoltage, wx.GBPosition( x+4,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlYVoltage = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlYVoltage, wx.GBPosition( x+4, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        self.m_staticTextBVoltage = wx.StaticText( self, wx.ID_ANY, u"B Voltage(V)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextBVoltage.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextBVoltage, wx.GBPosition( x+5,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlBVoltage = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlBVoltage, wx.GBPosition( x+5, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextRCurrent = wx.StaticText( self, wx.ID_ANY, u"R Current(A)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextRCurrent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextRCurrent, wx.GBPosition( x+6,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlRCurrent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlRCurrent, wx.GBPosition( x+6, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextYCurrent = wx.StaticText( self, wx.ID_ANY, u"Y Current(A)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextYCurrent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextYCurrent, wx.GBPosition( x+7,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlYCurrent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlYCurrent, wx.GBPosition( x+7, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        self.m_staticTextBCurrent = wx.StaticText( self, wx.ID_ANY, u"B Current(A)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextBCurrent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextBCurrent, wx.GBPosition( x+8,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlBCurrent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlBCurrent, wx.GBPosition( x+8, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextRPF = wx.StaticText( self, wx.ID_ANY, u"R P.F", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextRPF.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextRPF, wx.GBPosition( x+9,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlRPF = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlRPF, wx.GBPosition( x+9, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextYPF = wx.StaticText( self, wx.ID_ANY, u"Y P.F", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextYPF.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextYPF, wx.GBPosition( x+10,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlYPF = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlYPF, wx.GBPosition( x+10, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        self.m_staticTextBPF = wx.StaticText( self, wx.ID_ANY, u"B P.F", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextBPF.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextBPF, wx.GBPosition( x+11,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlBPF = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlBPF, wx.GBPosition( x+11, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTotalPf = wx.StaticText( self, wx.ID_ANY, u"Total P.F", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTotalPf.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTotalPf, wx.GBPosition( x+12,y+0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTotalPf = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTotalPf, wx.GBPosition( x+12, y+1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        ########################################################################################################################
        ##################################  Energy  Section ####################################################################
        ########################################################################################################################
        self.m_staticTextEnergy = wx.StaticText( self, wx.ID_ANY, u"Energy Reading", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextEnergy.Wrap( -1 )
        self.m_staticTextEnergy.SetFont(font)
        gbSizerMonitor.Add( self.m_staticTextEnergy, wx.GBPosition( x+0, y+2 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.ALIGN_CENTER, 5 )

        self.m_staticTextTotalRealEnergy = wx.StaticText( self, wx.ID_ANY, u"Total Real Energy", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTotalRealEnergy.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTotalRealEnergy, wx.GBPosition(x+1, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTotalRealEnergy = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTotalRealEnergy, wx.GBPosition( x+1, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTotalApparentEnergy = wx.StaticText( self, wx.ID_ANY, u"Total Apparent Energy", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTotalApparentEnergy.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTotalApparentEnergy, wx.GBPosition( x+2, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTotalApparentEnergy = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTotalApparentEnergy, wx.GBPosition( x+2, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTotalReactiveEnergy = wx.StaticText( self, wx.ID_ANY, u"Total Reactive Energy", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTotalReactiveEnergy.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTotalReactiveEnergy, wx.GBPosition( x+3, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTotalReactiveEnergy = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTotalReactiveEnergy, wx.GBPosition( x+3, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTotalLagReactiveEnergy = wx.StaticText( self, wx.ID_ANY, u"Lag Only Reactive Energy", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTotalLagReactiveEnergy.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTotalLagReactiveEnergy, wx.GBPosition( x+4, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTotalLagReactiveEnergy = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTotalLagReactiveEnergy, wx.GBPosition( x+4, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTotalLeadReactiveEnergy = wx.StaticText( self, wx.ID_ANY, u"Lead Only Reactive Energy", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTotalLeadReactiveEnergy.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTotalLeadReactiveEnergy, wx.GBPosition( x+5, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTotalLeadReactiveEnergy = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTotalLeadReactiveEnergy, wx.GBPosition( x+5, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        ########################################################################################################################
        ##################################  Configuration Parameters Section ###################################################
        ########################################################################################################################
        self.m_staticTextConfParams = wx.StaticText( self, wx.ID_ANY, u"Configuration Parameters", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextConfParams.Wrap( -1 )
        self.m_staticTextConfParams.SetFont(font)
        gbSizerMonitor.Add( self.m_staticTextConfParams, wx.GBPosition( x+6, y+2 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.ALIGN_CENTER, 5 )


        self.m_staticTextSIP = wx.StaticText( self, wx.ID_ANY, u"Survey Integration Period", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextSIP.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextSIP, wx.GBPosition( x+7, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlSIP = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlSIP, wx.GBPosition( x+7, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextDIP = wx.StaticText( self, wx.ID_ANY, u"Demand Integration Period", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextDIP.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextDIP, wx.GBPosition( x+8, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlDIP = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlDIP, wx.GBPosition( x+8, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextPtime = wx.StaticText( self, wx.ID_ANY, u"P Time (Occurrence,Restoration)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextPtime.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextPtime, wx.GBPosition( x+9, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlPtime = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlPtime, wx.GBPosition( x+9, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextOverPowerLimit = wx.StaticText( self, wx.ID_ANY, u"Over Power Limit", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextOverPowerLimit.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextOverPowerLimit, wx.GBPosition( x+10, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlOverPowerLimit = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlOverPowerLimit, wx.GBPosition( x+10, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextNxtBillingDate = wx.StaticText( self, wx.ID_ANY, u"Next Billing Date", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNxtBillingDate.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextNxtBillingDate, wx.GBPosition( x+11, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlNxtBillingDate = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlNxtBillingDate, wx.GBPosition( x+11, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextResetDate = wx.StaticText( self, wx.ID_ANY, u"Initialization Date", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextResetDate.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextResetDate, wx.GBPosition( x+12, y+2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlResetDate = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlResetDate, wx.GBPosition( x+12, y+3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        ########################################################################################################################
        ##################################  No Of Entries Section ##############################################################
        ########################################################################################################################
        self.m_staticTextprofile = wx.StaticText( self, wx.ID_ANY, u"No of Entries", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextprofile.Wrap( -1 )
        self.m_staticTextprofile.SetFont(font)
        gbSizerMonitor.Add( self.m_staticTextprofile, wx.GBPosition( x+0, y+5 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.ALIGN_CENTER, 5 )

        self.m_staticTextLoadProfile = wx.StaticText( self, wx.ID_ANY, u"Load Profile", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextLoadProfile.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextLoadProfile, wx.GBPosition( x+1,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlLoadProfile = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlLoadProfile, wx.GBPosition( x+1, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextDailyProfile = wx.StaticText( self, wx.ID_ANY, u"Daily Profile", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextDailyProfile.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextDailyProfile, wx.GBPosition( x+2,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlDailyProfile = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlDailyProfile, wx.GBPosition( x+2, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextBillingProfile = wx.StaticText( self, wx.ID_ANY, u"Billing Profile", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextBillingProfile.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextBillingProfile, wx.GBPosition( x+3,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlBillingProfile = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlBillingProfile, wx.GBPosition( x+3, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextVoltageEvent = wx.StaticText( self, wx.ID_ANY, u"Voltage  Event", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextVoltageEvent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextVoltageEvent, wx.GBPosition( x+4,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlVoltageEvent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlVoltageEvent, wx.GBPosition( x+4, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextCurrentEvent = wx.StaticText( self, wx.ID_ANY, u"Current  Event", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextCurrentEvent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextCurrentEvent, wx.GBPosition( x+5,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlCurrentEvent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlCurrentEvent, wx.GBPosition( x+5, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextPowerEvent = wx.StaticText( self, wx.ID_ANY, u"Power  Event", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextPowerEvent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextPowerEvent, wx.GBPosition( x+6,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlPowerEvent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlPowerEvent, wx.GBPosition( x+6, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTransEvent = wx.StaticText( self, wx.ID_ANY, u"Transaction  Event", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTransEvent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTransEvent, wx.GBPosition( x+7,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTransEvent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTransEvent, wx.GBPosition( x+7, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextNonRollEvent = wx.StaticText( self, wx.ID_ANY, u"Non roll Over Event", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextNonRollEvent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextNonRollEvent, wx.GBPosition( x+8,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlNonRollEvent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlNonRollEvent, wx.GBPosition( x+8, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextOtherEvent = wx.StaticText( self, wx.ID_ANY, u"Other Event", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextOtherEvent.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextOtherEvent, wx.GBPosition( x+9,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlOtherEvent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlOtherEvent, wx.GBPosition( x+9, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextTamperCount = wx.StaticText( self, wx.ID_ANY, u"Tamper Count", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextTamperCount.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextTamperCount, wx.GBPosition( x+10,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlTamperCount = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlTamperCount, wx.GBPosition( x+10, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextRelayCount = wx.StaticText( self, wx.ID_ANY, u"Relay Count", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextRelayCount.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextRelayCount, wx.GBPosition( x+11,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlRelayCount = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlRelayCount, wx.GBPosition( x+11, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticTextLastUpdated = wx.StaticText( self, wx.ID_ANY, u"Last Updated", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextLastUpdated.Wrap( -1 )
        gbSizerMonitor.Add( self.m_staticTextLastUpdated, wx.GBPosition( x+12,y+5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrlLastUpdated = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizerMonitor.Add( self.m_textCtrlLastUpdated, wx.GBPosition( x+12, y+6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.SetSizer( gbSizerMonitor )
        self.Layout()
        
        self.Centre( wx.BOTH )
    
    def __del__( self ):
        pass
    

