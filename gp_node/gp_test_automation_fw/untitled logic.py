        # meter_date1 = (meter_time).split(':')[0].split(' ')[0]
        # print "meter_date"


      # meter_time1=self.outdata
        # meter_time1=datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=meter_time)
        # print "factory_init_time",meter_time1
        # meter_date1 =(meter_time).split(':')[0].split(' ')[0]
        # print "factory_init_time",meter_date1
        







       # self.result_case(start_value, end_value)
        


    #     def verify_meter_time(self):
    #     self.send_cmd(GET_TIME_TX)
    #     self.response_read(GET_TIME)
    #     meter_time = self.verify_result_without_arg(GET_TIME_TX)
    #     meter_time=str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=meter_time))
    #     print "meter time is:",(meter_time)
    #     meter_date1 = str(meter_time).split(':')[0].split(' ')[0]
    #     print "meter time is:",meter_date1
    #     return meter_time

    # def factory_reset_time(self, meter_time,num_block):
    #     # print "Meter time in reset time", meter_time
        
    #     date = self.verify_result_without_arg(FACTORY_INIT_2_TX)
    #     date_time=str(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=date))
    #     # print "date time are :",date_time
    #     meter_date = str(date_time).split(':')[0].split(' ')[0]
    #     print "meter_ date time are:", (meter_date)

    #     dummy_time = str(meter_date)+" 00:00:00"
    #     # print "dummy_time is:",(dummy_time)
    #     dummy_time = datetime.datetime.strptime(dummy_time,'%Y-%m-%d %H:%M:%S')
    #     meter_time = datetime.datetime.strptime(meter_time,'%Y-%m-%d %H:%M:%S')
    #     # print "another print time is:",type(dummy_time), type(meter_time)
    #     block_num_load = int(abs((dummy_time - meter_time).total_seconds())/1800)
    #     # print "block load profile:",block_num_load
    #     if (num_block == block_num_load):
    #         return "pass"
    #     else:
    #         return "fail"