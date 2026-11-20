import time
from engine import procedure_keys
from tap import TAPPacket
from tap import TAPHandler


######RELAY IN MANUAL#######
RELAY_MANUAL = 59907
MANUAL_RELAY_ON = 61187
MANUAL_RELAY_OFF = 61699 
TURN_OFF = 60163
TURN_ON = 60675
######RELAY IN AUTO#######
RELAY_AUTO = 59651
AUTO_RELAY_ON = 60931
AUTO_RELAY_OFF = 61443
##########################




class procedure_test:
    
    def __init__(self, eng):
        self.eng=eng
        self.width=165
    def prepaid_101(self):   
        list=[]
        print 'TEST NAME = CHECK DEFAULT VALUE'.center(self.width,'-')
        self.eng.startcase()
        self.eng.dlms_tap()
        list.append(self.eng.set_time("now")) 
        time.sleep(3)       
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        for i in range(0,2):
            list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,0",        ## prepaid disable
                                        change_prepaid_mode_timestamp =True,
                                        account_balance="equal_to,0",
                                        energy_start_of_month=False,
                                        last_prepaid_billing_timestamp=True,
                                        new_tariff_timestamp=True,
                                        current_active_tariff="equal_to,1",
                                        net_positive_recharge="equal_to,0",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,0",
                                        current_account_balance="equal_to,0",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,0",
                                        status="equal_to,5"        ## Acc Prepaid disable
                                ))
            list.append(self.eng.verify_dg_tariff_data(  fd_type = "equal_to,1",
                                    fd_telescopic ="equal_to,0",
                                    mmc_application = "equal_to,1",
                                    friendlyHoursAM= "equal_to,0",
                                    friendlyHoursPM= "equal_to,0",
                                    alert_limit="equal_to,10",
                                    emergency_credit="equal_to,0",
                                    topup_limit= "equal_to,10",
                                    mmc="equal_to,0",
                                    fd_price="equal_to,[0, 0, 0, 0, 0, 0]",
                                    energy_price= "equal_to, [100, 0, 0, 0, 0,0]",
                                    energy_slab="equal_to, [0, 0, 0, 0, 0]",
                                    tariff_type= "equal_to,0"
                                    ))
            list.append(self.eng.verify_eg_tariff_data(  fd_type = "equal_to,1",
                                    fd_telescopic ="equal_to,0",
                                    mmc_application = "equal_to,1",
                                    friendlyHoursAM= "equal_to,0",
                                    friendlyHoursPM= "equal_to,0",
                                    alert_limit="equal_to,10",
                                    emergency_credit="equal_to,0",
                                    topup_limit= "equal_to,10",
                                    mmc="equal_to,0",
                                    fd_price="equal_to,[0, 0, 0, 0, 0, 0]",
                                    energy_price= "equal_to, [100, 0, 0, 0, 0,0]",
                                    energy_slab="equal_to, [0, 0, 0, 0, 0]",
                                    tariff_type= "equal_to,1"
                                    ))
            time.sleep(5)
            list.append(self.eng.verify_time())
            if i==1:
                pass
            else:
                print "Power cycle of meter"
                user_input=input("enter ok here: ")
                self.eng.dlms_tap()
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()

        


    def prepaid_102(self):
        print 'TEST NAME = set and verify value of dg,recharge,prepaid with power cycle'.center(self.width,'-')
        self.eng.startcase()
        self.eng.dlms_tap()
        list=[]
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.verify_prepaid_data(
                                    prepaid_status="equal_to,1,",
                                    change_prepaid_mode_timestamp =True,
                                    account_balance="equal_to,0",
                                    energy_start_of_month=False,
                                    last_prepaid_billing_timestamp=True,
                                    new_tariff_timestamp=True,
                                    current_active_tariff="equal_to,1",
                                    net_positive_recharge="equal_to,0",
                                    net_negative_recharge="equal_to,0",
                                    net_recharge="equal_to,0",
                                    current_account_balance="equal_to,0",
                                    current_FD_cost="equal_to,0",
                                    current_energy_cost="equal_to,0",
                                    status="equal_to,3"
                            ))
        list.append(self.eng.verify_time())
        # eng.verify_time_p("2018-12-27 18:52" )
        list.append(self.eng.recharge(
                        recharge  = ",10000,22222"
                        ))
        list.append(self.eng.set_dg_tariff(
                                fd_type = 1,
                                fd_telescopic = 0 ,
                                mmc_application = 1,
                                friendlyHoursAM= 0,
                                friendlyHoursPM= 0,
                                alert_limit=0,
                                emergency_credit=0,
                                topup_limit= 35,
                                mmc=0,
                                fd_price=[10,20,30,40,50,60],
                                energy_price= [10000,10000,0,0,0,0],
                                energy_slab=[1,2,3,0,0],
                                tariff_type= 0
                                )) 
        time.sleep(7)
        list.append(self.eng.enable_dg_tariff())
        list.append(self.eng.verify_dg_tariff_data(  fd_type = "equal_to,1",
                                    fd_telescopic ="equal_to,0",
                                    mmc_application = "equal_to,1",
                                    friendlyHoursAM= "equal_to,6",
                                    friendlyHoursPM= "equal_to,0",
                                    alert_limit="equal_to,0",
                                    emergency_credit="equal_to,0",
                                    topup_limit= "equal_to,35",
                                    mmc="equal_to,0",
                                    fd_price="equal_to,[1,2,3,4,5,6]",
                                    energy_price= "equal_to,[100,200,0,0,0,0]",
                                    energy_slab="equal_to,[1,2,0,0,0]",
                                    tariff_type= "equal_to,0"
                                    ))
        
        time.sleep(5)
        for i in range(0,2):           
            list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,1,",
                                        change_prepaid_mode_timestamp =False,
                                        account_balance="equal_to,10000",
                                        energy_start_of_month=False,
                                        last_prepaid_billing_timestamp=False,
                                        new_tariff_timestamp=False,
                                        current_active_tariff="equal_to,0",
                                        net_positive_recharge="equal_to,10000",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,10000",
                                        current_account_balance="equal_to,10000",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,0",
                                        status="equal_to,4"
                                ))
            if i==1:
                pass
            else:
                print "Power cycle of meter"
                user_input=input("enter ok here: ")
                self.eng.dlms_tap()
        if False in list:
            print list
            test_result=False
            return test_result
        else:
            print list
            test_result=True
            return test_result
            self.eng.endcase()
    def prepaid_103(self):
        print 'TEST NAME = check eg tariff set and prepaid info'.center(self.width,'-')
        self.eng.startcase()
        self.eng.dlms_tap()
        list=[]
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        self.eng.dlms_tap()
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge=",100000,6767"))
        time.sleep(3)
        for i in range(0,2):
            list.append(self.eng.set_eg_tariff(
                                        fd_type = 1, 
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 0,
                                        friendlyHoursPM= 0,
                                        alert_limit=90,
                                        emergency_credit=0,
                                        topup_limit= 35,
                                        mmc=0,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [10000,20000,0,0,0,0],
                                        energy_slab=[1,2,0,0,0],
                                        tariff_type= 1
                                        ))
            time.sleep(3)
            list.append(self.eng.enable_eg_tariff())   
            list.append(self.eng.verify_eg_tariff_data(  fd_type = "equal_to,1",
                                        fd_telescopic ="equal_to,0",
                                        mmc_application = "equal_to,1",
                                        friendlyHoursAM= "equal_to,0",
                                        friendlyHoursPM= "equal_to,0",
                                        alert_limit="equal_to,90",
                                        emergency_credit="equal_to,0",
                                        topup_limit= "equal_to,35",
                                        mmc="equal_to,0",
                                        fd_price="equal_to,[10000,0,0,0,0,0]",
                                        energy_price= "equal_to,[10000,20000,0,0,0,0]",
                                        energy_slab="equal_to,[1,2,0,0,0]",
                                        tariff_type= "equal_to,1"
                                        ))
            time.sleep(3)

            list.append(self.eng.verify_prepaid_data(
                                       
                                        prepaid_status="equal_to,1",
                                        change_prepaid_mode_timestamp =False,
                                        account_balance="equal_to,100000",
                                        energy_start_of_month=False,
                                        last_prepaid_billing_timestamp=False,
                                        new_tariff_timestamp=False,
                                        current_active_tariff="equal_to,1",
                                        net_positive_recharge="equal_to,100000",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,100000",
                                        current_account_balance="equal_to,100000",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,0",
                                        status="equal_to,4"
                                ))
            if i==1:
                pass
            else:
                print "Power cycle of meter"
                user_input=input("enter ok here: ")
                self.eng.dlms_tap()
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_104(self):
        print 'TEST NAME = tariff set above case data with energy deduction with load '.center(self.width,'-')
        self.eng.startcase()
        list=[]
        list.append(self.eng.verify_energy_data(
                                current_account_balance="equal_to,100000",
                                energy_diffrence=0))
        time.sleep(5)
        print 'connect load for incresing energy '.center(self.width,'-')
        list.append(self.eng.verify_energy_data(current_account_balance="equal_to,900000",
                             energy_diffrence=1000))
        list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,1")) 

        time.sleep(7)
        self.eng.dlms_tap()
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
    def prepaid_105(self):
        print 'TEST NAME = recharge with multiple transaction id '.center(self.width,'-')
        self.eng.dlms_tap()
        self.eng.startcase()
        list=[]

        list.append(self.eng.recharge(
                            recharge  = ",10000,22223"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22224"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22225"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22226"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22227"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22227"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22228"
                            ))
        list.append(self.eng.recharge(
                            recharge  = ",10000,22223"
                            ))
        if False in list:
            print list
            test_result=False
            return test_result
        else:
            test_result=True
            print list
            return test_result
        self.eng.endcase()
    def prepaid_106(self):
        print 'TEST NAME =  check credit deduction with only energy cost  and emergency credit'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.set_time("now"))
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        self.eng.dlms_tap()
        list.append(self.eng.enable_prepaid())
        time.sleep(3)
        list.append(self.eng.recharge(recharge=",10000,5555"))
        time.sleep(7)

        list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,1",        ## prepaid disable
                                        change_prepaid_mode_timestamp =False,
                                        account_balance="equal_to,10000",
                                        energy_start_of_month=False,
                                        last_prepaid_billing_timestamp=False,
                                        new_tariff_timestamp=False,
                                        current_active_tariff="equal_to,0",
                                        net_positive_recharge="equal_to,10000",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,100000",
                                        current_account_balance="equal_to,10000",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,0",
                                        status="equal_to,4"        ## Acc Prepaid disable
                                ))

        list.append(self.eng.set_dg_tariff(
                                        fd_type = 1,
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 0,
                                        friendlyHoursPM= 0,
                                        alert_limit=0,
                                        emergency_credit=20,
                                        topup_limit= 35,
                                        mmc=0,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [30000,0,0,0,0,0],
                                        energy_slab=[1,0,0,0,0],
                                        tariff_type= 0
                                        ))
        time.sleep(6)
        list.append(self.eng.enable_dg_tariff())
        time.sleep(5)

        list.append(self.eng.verify_energy_data(current_account_balance="equal_to,100000",
                                    energy_diffrence=0))
        print 'connect load for increasing energy'.center(self.width,'-')
        time.sleep(7)

        list.append(self.eng.verify_energy_data(              
                                current_account_balance="equal_to,-20000",
                                energy_diffrence=1000))
        time.sleep(7)
        list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,1",        ## prepaid disable
                                        change_prepaid_mode_timestamp =False,
                                        account_balance="equal_to,-20000",
                                        energy_start_of_month=False,
                                        last_prepaid_billing_timestamp=False,
                                        new_tariff_timestamp=False,
                                        current_active_tariff="equal_to,1",
                                        net_positive_recharge="equal_to,10000",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,800",
                                        current_account_balance="equal_to,-20000",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,30000",
                                        status="equal_to,2"        ## Acc Prepaid disable
                                ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_107(self): 
        print 'TEST NAME = disable prepaid and verify_relay_state'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        for i in range(0,2):
            list.append(self.eng.disable_prepaid())
            list.appned(self.eng.verify_prepaid_data(
                                            prepaid_status="equal_to,0",        ## prepaid disable
                                            change_prepaid_mode_timestamp =False,
                                            account_balance="equal_to,0",
                                            energy_start_of_month=False,
                                            last_prepaid_billing_timestamp=False,
                                            new_tariff_timestamp=False,
                                            current_active_tariff=False,
                                            net_positive_recharge="equal_to,0",
                                            net_negative_recharge="equal_to,0",
                                            net_recharge="equal_to,0",
                                            current_account_balance="equal_to,0",
                                            current_FD_cost="equal_to,0",
                                            current_energy_cost="equal_to,0",
                                            status="equal_to,5"        ## Acc Prepaid disable
                                    ))
            time.sleep(4)

            # list.append(self.eng.verify_relay_state())
            if i==1:
                pass
            else:
                print "Power cycle of meter"
                user_input=input("enter ok here: ")
                self.eng.dlms_tap()
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()

        time.sleep(5)
    def prepaid_108(self):
        print 'TEST NAME = Test with mmc and fd monthly no energy deduction'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge="70000,6960"))
        time.sleep(7)
        list.append(self.eng.set_dg_tariff(
                                        fd_type = 1,
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 6,
                                        friendlyHoursPM= 0,
                                        alert_limit=0,
                                        emergency_credit=20,
                                        topup_limit= 35,
                                        mmc=100,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [10000,10000,0,0,0,0],
                                        energy_slab=[1,2,3,0,0],
                                        tariff_type= 0
                                        ))
        time.sleep(3)
        list.append(self.eng.enable_dg_tariff())
        time.sleep(5)
        # for i in range(0,4):
        list.append(self.eng.set_time_month())
        
        time.sleep(5)
        list.append(self.eng.verify_time())
        list.append(self.eng.verify_prepaid_data(
                                            prepaid_status="equal_to,1",        ## prepaid disable
                                            change_prepaid_mode_timestamp =False,
                                            account_balance="equal_to,50000",
                                            energy_start_of_month=False,
                                            last_prepaid_billing_timestamp=False,
                                            new_tariff_timestamp=False,
                                            current_active_tariff="equal_to,0",
                                            net_positive_recharge="equal_to,70000",
                                            net_negative_recharge="equal_to,0",
                                            net_recharge="equal_to,70000",
                                            current_account_balance="equal_to,50000",
                                            current_FD_cost="equal_to,10000",
                                            current_energy_cost="equal_to,0",
                                            status="equal_to,5"        ## Acc Prepaid disable
                                    ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_109(self):
        print 'TEST NAME = disable prepaid, do recharge,check prepaid data'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.disable_prepaid())
        time.sleep(3)
        list.append(self.eng.verify_prepaid_data(
                                    prepaid_status="equal_to,0",        ## prepaid disable
                                    change_prepaid_mode_timestamp =False,
                                    account_balance="equal_to,0",
                                    energy_start_of_month=False,
                                    last_prepaid_billing_timestamp=True,
                                    new_tariff_timestamp=True,
                                    current_active_tariff="equal_to,0",
                                    net_positive_recharge="equal_to,0",
                                    net_negative_recharge="equal_to,0",
                                    net_recharge="equal_to,0",
                                    current_account_balance="equal_to,0",
                                    current_FD_cost="equal_to,0",
                                    current_energy_cost="equal_to,0",
                                    status="equal_to,5"        ## Acc Prepaid disable
                            ))
        time.sleep(3)
        list.append(self.eng.recharge(recharge=",60000,3333"))
        time.sleep(7)
        list.append(self.eng.verify_prepaid_data(
                                    prepaid_status="equal_to,0",        ## prepaid disable
                                    change_prepaid_mode_timestamp =False,
                                    account_balance="equal_to,0",
                                    energy_start_of_month=False,
                                    last_prepaid_billing_timestamp=False,
                                    new_tariff_timestamp=False,
                                    current_active_tariff=False,
                                    net_positive_recharge="equal_to,0",
                                    net_negative_recharge="equal_to,0",
                                    net_recharge="equal_to,0",
                                    current_account_balance="equal_to,0",
                                    current_FD_cost="equal_to,0",
                                    current_energy_cost="equal_to,0",
                                    status="equal_to,5"        ## Acc Prepaid disable
                            ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_110(self):
        print 'TEST NAME = energy deduction with FD and MMC Monthly'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.set_time("now"))
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge=",70000,4444"))
        list.append(self.eng.set_eg_tariff(
                                        fd_type = 1, 
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 18,
                                        friendlyHoursPM= 0,
                                        alert_limit=90,
                                        emergency_credit=0,
                                        topup_limit= 35,
                                        mmc=100,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [10000,20000,0,0,0,0],
                                        energy_slab=[1,2,0,0,0],
                                        tariff_type= 1
                                        ))
        time.sleep(3)
        list.append(self.eng.enable_eg_tariff()) 
        time.sleep(3) 
        list.append(self.eng.verify_eg_tariff_data(  fd_type = "equal_to,1",
                                        fd_telescopic ="equal_to,0",
                                        mmc_application = "equal_to,1",
                                        friendlyHoursAM= "equal_to,18",
                                        friendlyHoursPM= "equal_to,0",
                                        alert_limit="equal_to,90",
                                        emergency_credit="equal_to,0",
                                        topup_limit= "equal_to,35",
                                        mmc="equal_to,100",
                                        fd_price="equal_to,[10000,0,0,0,0,0]",
                                        energy_price= "equal_to,[10000,10000,0,0,0,0]",
                                        energy_slab="equal_to,[1,2,0,0,0]",
                                        tariff_type= "equal_to,1"
                                        )) 
        print 'connect load for increasing energy'.center(self.width,'-')
        list.append(self.eng.verify_energy_data(              
                            current_account_balance="equal_to,70000",
                            energy_difference=2000))
        time.sleep(7)
        list.append(self.eng.set_time_month())
        time.sleep(30)
        self.eng.dlms_tap()
        list.append(self.eng.verify_prepaid_data(
                                    prepaid_status="equal_to,1",        ## prepaid disable
                                    account_balance="equal_to,30000",
                                    next_tariff_to_activate="equal_to,1",
                                    current_active_tariff=1,
                                    net_positive_recharge="equal_to,70000",
                                    net_negative_recharge="equal_to,0",
                                    net_recharge="equal_to,700",
                                    current_account_balance="equal_to,30000",
                                    current_FD_cost="equal_to,100",
                                    current_energy_cost="equal_to,30000"        ## Acc Prepaid disable
                            ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_111(self):
        print 'TEST NAME = Using eg_tariff check credit deduction with only energy cost  and emergency credit'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        self.eng.dlms_tap()
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge=",100000,5555"))
        time.sleep(7)

        list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,0",        ## prepaid disable
                                        change_prepaid_mode_timestamp =False,
                                        account_balance="equal_to,1000",
                                        energy_start_of_month="equal_to,429",
                                        last_prepaid_billing_timestamp=False,
                                        new_tariff_timestamp=False,
                                        next_tariff_to_activate="equal_to,1",
                                        current_active_tariff=False,
                                        net_positive_recharge="equal_to,1000",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,800",
                                        current_account_balance="equal_to,1000",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,300",
                                        status="equal_to,4"        ## Acc Prepaid disable
                                ))

        list.append(self.eng.set_eg_tariff(
                                        fd_type = 1,
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 6,
                                        friendlyHoursPM= 0,
                                        alert_limit=0,
                                        emergency_credit=20,
                                        topup_limit= 35,
                                        mmc=0,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [20000,30000,50000,20000,0,0],
                                        energy_slab=[1,2,3,0,0],
                                        tariff_type= 1
                                        ))
        time.sleep(6)
        list.append(self.eng.enable_eg_tariff())
        time.sleep(5)

        list.append(self.eng.verify_energy_data(current_account_balance="equal_to,100000",
                                    energy_diffrence=0))
        print 'connect load for increasing energy'.center(self.width,'-')
        time.sleep(7)
        list.append(self.eng.verify_relay_state())

        list.append(self.eng.verify_energy_data(              
                                current_account_balance="equal_to,800",
                                energy_diffrence=1000))
        time.sleep(7)
        list.append(self.eng.verify_prepaid_data(
                                        prepaid_status="equal_to,1",        ## prepaid disable
                                        change_prepaid_mode_timestamp =False,
                                        account_balance="equal_to,-200",
                                        energy_start_of_month="equal_to,429",
                                        last_prepaid_billing_timestamp=False,
                                        new_tariff_timestamp=False,
                                        next_tariff_to_activate="equal_to,1",
                                        current_active_tariff=False,
                                        net_positive_recharge="equal_to,800",
                                        net_negative_recharge="equal_to,0",
                                        net_recharge="equal_to,800",
                                        current_account_balance="equal_to,-200",
                                        current_FD_cost="equal_to,0",
                                        current_energy_cost="equal_to,0",
                                        status="equal_to,5"        ## Acc Prepaid disable
                                ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_112(self):
        print 'TEST NAME = EG tariff energy with mmc and fd monthly no energy deduction'.center(self.width,'-')

        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.set_time("now"))
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge=",70000,6960"))
        time.sleep(7)
        list.append(self.eng.set_eg_tariff(
                                        fd_type = 1,
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 6,
                                        friendlyHoursPM= 0,
                                        alert_limit=0,
                                        emergency_credit=20,
                                        topup_limit= 35,
                                        mmc=100,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [10000,10000,0,0,0,0],
                                        energy_slab=[1,2,3,0,0],
                                        tariff_type= 1
                                        ))
        time.sleep(3)
        list.append(self.eng.enable_eg_tariff())
        time.sleep(5)
        
        list.append(self.eng.set_time_month())
        
        time.sleep(15)
        list.append(self.eng.verify_prepaid_data(
                                            prepaid_status="equal_to,1",        
                                            change_prepaid_mode_timestamp =False,
                                            account_balance="equal_to,50000",
                                            energy_start_of_month=False,
                                            last_prepaid_billing_timestamp=False,
                                            new_tariff_timestamp=False,
                                            next_tariff_to_activate="equal_to,1",
                                            current_active_tariff=False,
                                            net_positive_recharge="equal_to,70000",
                                            net_negative_recharge="equal_to,0",
                                            net_recharge="equal_to,70000",
                                            current_account_balance="equal_to,50000",
                                            current_FD_cost="equal_to,10000",
                                            current_energy_cost="equal_to,0",
                                            status="equal_to,4"       
                                    ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_113(self):
        print 'TEST NAME = recharge with same transaction id'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge="70000,6960"))
        time.sleep(7)
        list.append(self.eng.recharge(recharge="70000,6960"))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()

    def prepaid_114(self):
        print 'TEST NAME = Fd monthly with year jump'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.set_time("now"))
        time.sleep(7)
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        list.append(self.eng.enable_prepaid())
        time.sleep(3)
        list.append(self.eng.recharge(recharge=",70000,99900"))
        time.sleep(7)
        list.append(self.eng.set_eg_tariff(
                                        fd_type = 1,
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 0,
                                        friendlyHoursPM= 0,
                                        alert_limit=0,
                                        emergency_credit=20,
                                        topup_limit= 35,
                                        mmc=0,
                                        fd_price=[1000,0,0,0,0,0],
                                        energy_price= [10000,10000,0,0,0,0],
                                        energy_slab=[1,2,3,0,0],
                                        tariff_type= 1
                                        ))
        list.append(self.eng.verify_eg_tariff_data(  fd_type = "equal_to,1",
                                        fd_telescopic ="equal_to,0",
                                        mmc_application = "equal_to,1",
                                        friendlyHoursAM= "equal_to,0",
                                        friendlyHoursPM= "equal_to,0",
                                        alert_limit="equal_to,0",
                                        emergency_credit="equal_to,0",
                                        topup_limit= "equal_to,35",
                                        mmc="equal_to,0",
                                        fd_price="equal_to,[1000,0,0,0,0,0]",
                                        energy_price= "equal_to,[10000,20000,0,0,0,0]",
                                        energy_slab="equal_to,[1,2,0,0,0]",
                                        tariff_type= "equal_to,1"
         
                                       ))
        list.append(self.eng.set_time_year())
        time.sleep(20)

        list.append(self.eng.verify_prepaid_data(
                                            prepaid_status="equal_to,1",        
                                            change_prepaid_mode_timestamp =False,
                                            account_balance="equal_to,58000",
                                            energy_start_of_month=False,
                                            last_prepaid_billing_timestamp=False,
                                            new_tariff_timestamp=False,
                                            next_tariff_to_activate="equal_to,1",
                                            current_active_tariff=False,
                                            net_positive_recharge="equal_to,0",
                                            net_negative_recharge="equal_to,0",
                                            net_recharge="equal_to,70000",
                                            current_account_balance="equal_to,58000",
                                            current_FD_cost="equal_to,120",
                                            current_energy_cost="equal_to,0",
                                            status="equal_to,4"        
                                    ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()
    def prepaid_115(self):
        print 'TEST NAME = energy deduction with FD slabwise and MMC Monthly'.center(self.width,'-')
        self.eng.startcase()
        list=[]
        self.eng.dlms_tap()
        list.append(self.eng.set_time("now"))
        list.append(self.eng.factory_init_1())
        time.sleep(10)
        self.eng.dlms_tap()
        list.append(self.eng.enable_prepaid())
        list.append(self.eng.recharge(recharge=",70000,4444"))
        list.append(self.eng.set_dg_tariff(
                                        fd_type = 2, 
                                        fd_telescopic = 0 ,
                                        mmc_application = 1,
                                        friendlyHoursAM= 18,
                                        friendlyHoursPM= 0,
                                        alert_limit=90,
                                        emergency_credit=0,
                                        topup_limit= 35,
                                        mmc=100,
                                        fd_price=[10000,0,0,0,0,0],
                                        energy_price= [10000,20000,0,0,0,0],
                                        energy_slab=[1,2,0,0,0],
                                        tariff_type= 0
                                        ))
        time.sleep(3)
        list.append(self.eng.enable_dg_tariff()) 
        time.sleep(3) 
        list.append(self.eng.verify_dg_tariff_data(  fd_type = "equal_to,2",
                                        fd_telescopic ="equal_to,0",
                                        mmc_application = "equal_to,1",
                                        friendlyHoursAM= "equal_to,18",
                                        friendlyHoursPM= "equal_to,0",
                                        alert_limit="equal_to,90",
                                        emergency_credit="equal_to,0",
                                        topup_limit= "equal_to,35",
                                        mmc="equal_to,100",
                                        fd_price="equal_to,[10000,0,0,0,0,0]",
                                        energy_price= "equal_to,[10000,10000,0,0,0,0]",
                                        energy_slab="equal_to,[1,2,0,0,0]",
                                        tariff_type= "equal_to,0"
                                        )) 
        print 'connect load for increasing energy'.center(self.width,'-')
        list.append(self.eng.verify_energy_data(              
                            current_account_balance="equal_to,70000",
                            energy_diffrence=2000))
        time.sleep(7)
        print "Enter time string in format last day of current month and time 23:59:30 ".center(self.width,'-')
        time_string=str(input( ))
        list.append(self.eng.set_time(str(time_string)))
        time.sleep(7)
        list.append(self.eng.verify_time())
        time.sleep(30)
        self.eng.dlms_tap()
        list.append(self.eng.verify_prepaid_data(
                                    prepaid_status="equal_to,1",        ## prepaid disable
                                    account_balance="equal_to,30000",
                                    next_tariff_to_activate="equal_to,1",
                                    current_active_tariff=1,
                                    net_positive_recharge="equal_to,70000",
                                    net_negative_recharge="equal_to,0",
                                    net_recharge="equal_to,70000",
                                    current_account_balance="equal_to,30000",
                                    current_FD_cost="equal_to,10000",
                                    current_energy_cost="equal_to,30000"        ## Acc Prepaid disable
                            ))
        if False in list:
            test_result=False
            return test_result
        else:
            test_result=True
            return test_result
        self.eng.endcase()



    







        


















   


















    # eng.verify_set_power_limit(100)
    # eng.get_time("2017-11-01 12:00:00")
    # eng.verify_billing_count()
    # eng.verify_metering_data(   
    #                             voltage = "in_range, 220.00, 250.00", 
    #                             current = "in_range,0.00,10.00",
    #                             # power_factor = "equal to,1.00",
    #                             # frequency = "in range,49.00,50.00",
    #                             # active_energy = "in range,2250.0,2280.0",
    #                             # reactive_energy = "in range 0.00, 2250.0",
    #                             # apparent_energy = "in range,2250.0,2280.0",
    #                             # factory_init_time = ""
    #                         )
    # eng.verify_num_load_load_survey()
    #     get_factory_reset_time()
        # eng.get_time()
    #     find_num_survey()
    #     get_meter_num_survey()
    #     result_case()

    # eng.verify_load_survey(   
    #                             factory_time
    #                             voltage = "in_range, 220.00, 250.00", 
    #                             current = "in_range,0.00,10.00"
                                
    #                         )
    # eng.verify_time("now")

    #

    # eng.verify_power_limit(power_limit="equal_to,7200")
    # # print"case execute"
    # eng.set_power_limit(100)
    # eng.verify_power_limit("equal,100")
    # print "case execute 1"
    # eng.verify_power_limit(90,120, "in_range")
    
    # print "case execute 2"
    # time.sleep(3)
    # eng.verify_relay_state(OFF)
    # print "case execute 3"
    # time.sleep(10)
    # eng.verify_relay_state(ON)
    # print "case execute 4"

    
    # eng.verify_slab_status(ENABLE,DISABLE)
    # print "case 5 execute"
    # eng.verify_fd_status(ENABLE,DISABLE)
    # print "case"
    # eng.get_time("now")
    # eng.set_time("2018-11-30 12:00:00")
    # eng.verify_active_MD_time("MD month":-1
    # eng.verify_billing_count("2018-11-30 12:00:00")                                           
    # print "case MD execute"
    # eng.set_power_limit(100)
    #do power cycle 2 3 times
    # eng.verify_power_failure_duration(30)

    # eng.set_power_limit(100)# verify power limit in manual control
    #eng.relay_manual_control(OFF)
    # eng.turn_relay(ON)
    # eng.verify_relay_state(ON)
    # #connect load of 150 watt and wait for 3 sec
    # time.sleep(23)
    # eng.recharge(50)
    # eng.verify_credits("greater than",0)
    # #remove  connected load and wait for 5 sec
    # time.sleep(6)


    # eng.verify_tamper(true)
    # eng.set_account_bal(0)
    # eng.verify_credits()
    # eng.recharge(50)
    # eng.verify_credits(0,60)
    # eng.relay_auto_control()
    # eng.set_power_limit(100)
    # #connect load of 150 watt and wait for 3 sec
    # time.sleep(3)
    # time.sleep(10)
    # # remove 150 watt load and connect 50 watt wait for 10 sec
    # time.sleep(10)
    

    # eng.verify_get_live_tamper()#for earth
    # eng.clear_account()
    # eng.verify_credits()
    # eng.recharge(50)
    # eng.verify_credits()
    # eng.relay_auto_control()
    # eng.set_power_limit(100)
    # #connect load of 150 watt and wait for 3 sec
    # time.sleep(3)
    # time.sleep(10)
    # # remove 150 watt load and connect 50 watt wait for 10 sec
    # time.sleep(10)

    # eng.verify_get_live_tamper()#for magnet
    # eng.clear_account()
    # eng.verify_credits()
    # eng.recharge(50)
    # eng.verify_credits()
    # eng.relay_auto_control()
    # eng.set_power_limit(100)
    # #connect load of 150 watt and wait for 3 sec
    # time.sleep(3)
    # time.sleep(10)
    # # remove 150 watt load and connect 50 watt wait for 10 sec
    # time.sleep(10)

    # eng.do_factory_reset()
    # eng.verify_get_billing_info() // tbd before
    # # do power cycle for 2-3 times
    # eng.verify_get_billing_info()
    # eng.set_billing_timestamp(end of month/yy/mm/dd,hh:mm:ss)
    # # set billing time stamp to the end of the month
    # eng.verify_get_billing_info() # check billing count

    # eng.factory_reset()
    # eng.verify_get_billing_info()
    # # do power cycle for 2-3 times
    # eng.verify_get_billing_info()
    # eng.set_billing_timestamp(end of month/yy/mm/dd,hh:mm:ss)
    # # set billing time stamp to the end of the month
    # # power of the meter
    # eng.verify_get_billing_info(check billing count=2)    # check billing count

    # time.sleep(30)
    # eng.set_ip_time(end of month/yy/mm/dd,hh:mm:ss)
    # # set billing time stamp to the end of the month
    # # do power cycle exact time of billing generation
    # eng.verify_get_billing_info(check billing count =3)   # check billing count

    # # connect load to meter
    # eng.factory_reset()#  # clear all billing records
    # eng.verify_get_billing_info(check billing count=0)#verify billing index:0 (command)
    # eng.factory_reset()
    # eng.verify_get_billing_info(check billing count=1)
    # eng.factory_reset()# do hard reset
    # eng.verify_get_billing_info(check billing count=2)

    # # disconnect load from meter
    # eng.factory_reset()#  # clear all billing records
    # eng.verify_get_billing_info(check billing count=0)
    # eng.factory_reset()
    # eng.verify_get_billing_info(check billing count=1)
    # eng.factory_reset()# do hard reset
    # eng.verify_get_billing_info(check billing count=2)

    # eng.set_ip_time(now)
    # eng.verify_meter_time()
    # eng.factory_reset()  # clear all billing records
    # eng.verify_get_billing_info(check power on time )
    # time.sleep(60)
    # eng.factory_reset()
    # eng.verify_get_billing_info(check power on time )
    # #do 4 power cycles one by one at the rate of 2 power cycles per minute
    # #check the time after last power cycle.
    # eng.verify_get_billing_info(check power on time== last power cycle time )

    
    # eng.factory_reset() # clear all billing records and note the time
    # eng.verify_get_billing_info(power on timestamp=noted time)

    
    # eng.factory_reset() # clear all billing records and note the time
    # eng.verify_get_billing_info(power on timestamp=noted time)
    # # do 4 power cycles
    # eng.verify_get_billing_info(power on timestamp=noted time)
    # time.sleep(120)
    # eng.factory_reset() # clear all billing records and note the time
    # eng.verify_get_billing_info(power on timestamp=noted time)

    # eng.factory_reset() # clear all billing records and note the time
    # eng.verify_get_billing_info(power on timestamp=noted time)
    # eng.verify_get_billing_info(first power up timestamp=noted time)
    # eng.set_ip_time(2 months later)
    # eng.verify_get_billing_info(first power up timestamp=noted time)

    # eng.factory_reset() # clear all billing records and note the time
    # eng.verify_get_billing_info(last power failure=0d 0h 0m 0s)

    # # power off meter for 1 min
    # eng.verify_get_billing_info(last power failure=0d 0h 1m 0s)

    # # power off meter for 5 min
    # eng.verify_get_billing_info(last power failure=0d 0h 5m 0s)

    # eng.verify_time(current)
    # eng.set_ip_time(1 month later frm current time)
    # eng.verify_time(current)
    # eng.verify_get_billing_info(last power failure=30/29/28d 0h 0m 0s)# change according to month


    # eng.set_ip_time(current)
    # eng.verify_time(current)
    # eng.set_ip_time(1 year later frm current time)
    # eng.verify_time(current)
    # eng.verify_get_billing_info(last power failure=365/366/d 0h 0m 0s)# change according to month

    # eng.verify_demand_integration_period(30 min /60 min)
    # #wait for 30 min for MD generation
    # eng.verify_get_billing_info(check MD = consumed energy calculation)
    # # check MD timestamp and value 

    # eng.verify_demand_integration_period(30 min /60 min)
    # eng.set_demand_integration_period(5 min)
    # eng.verify_time(current)
    # eng.set_ip_time(yy-mm-dd 23:55:40)
    # time.sleep(20)
    # eng.verify_get_billing_info(check all parameter)

    # eng.factory_reset()#reset meter
    # eng.verify_demand_integration_period(30 min /60 min)
    # eng.set_demand_integration_period(5 min)  # multiple of 5 only
    # # do hard reset and check DIP period
    # eng.verify_demand_integration_period(5 min)
    # eng.verify_get_billing_info(check MD and MD time)

    # eng.verify_get_billing_info(check billing timestamp= 1st day of next month)
    # eng.verify_set_billing_timestamp(2018-mm-11 11:55:00)
    # # hard reset of meter
    # eng.verify_get_billing_info(check billing timestamp= 1st day of next month)

    # eng.set_demand_integration_period(5 min) # check MD for 5 min
    # eng.verify_get_billing_info(check billing timestamp= 1st day of next month)
    # eng.set_ip_time(month end for current month)

    # eng.get_billing_index(0) # billing for 15 min
    # eng.verify_get_billing_index(all parameter)
    # eng.set_demand_integration_period(15 min)
    # eng.set_ip_time(month end for set month)

    # eng.get_billing_index(0)
    # eng.verify_get_billing_index(all parameter)
    # eng.get_billing_index(1)
    # eng.verify_get_billing_index(all parameter)
    # eng.set_demand_integration_period(5 min)
    # time.sleep(300)
    # ng.verify_get_billing_index(0, all parameter)
    # eng.verify_get_billing_info(all parameter)
    # # do power cycle for and check again 2 records
    # eng.verify_get_billing_index(0, all parameter)
    # eng.verify_get_billing_index(1, all parameter)

    # eng.verify_get_billing_print_direct()
    # eng.set_billing_timestamp(5 th day of next month)
    # eng 





































