from calendar import monthrange
from datetime import datetime
import datetime

# d1 = datetime.strptime(str('2011-08-15 12:00:00'), '%Y-%m-%d %H:%M:%S')
# d2 = datetime.strptime(str('2012-02-15'), '%Y-%m-%d')

# def monthdelta(d1, d2):
#     delta = 0
#     while True:
#         mdays = monthrange(d1.year, d1.month)[1]
#         d1 += timedelta(days=mdays)
#         if d1 <= d2:
#             delta += 1
#             print delta
#         else:
#             break
#     return delta

# class datetime(object):

#     def __init__(self):
    
#         self.outdata=1543484603
#         self.date1=datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.outdata)
#         self.start_value="2018-11-29 10:00:00"

#     def monthdelta(self, date1,start_value):
#         delta = 0
#         while True:
#             mdays = monthrange(date1.year, date1.month)[1]
#             d1 += timedelta(days=mdays)
#             if date1 <= date1:
#                 delta += 1
#                 print delta
#             else:
#                 break
#         return delta

#     def maxwell_cal_time(self,start_value):
#         print start_value
#        # if start_value == " ":
#        #     start_value = 0
#         if start_value == "now":
#            start_value = datetime.datetime.now()
#            self.argument=start_value
#         else:
#            try:
#                time_str = start_value.split(' ')[1]
#                if len(time_str) == 6:
#                    time_str = time_str[0] + time_str[1] + ":" + time_str[2] + time_str[3] + ":" +\
#                               time_str[4] + time_str[5]
#                    start_time = start_time.split(' ')[0] + " " + time_str
#                start_value = datetime.datetime.strftime(start_value, "%Y-%m-%d %H:%M:%S")
#            except:
#                return "Incorrect data and/or data format, should be YYYY-MM-DD HH:MM:SS"
#         unix_time_zero = datetime.datetime(1970, 1, 1)
#         seconds_since_epoch = int((start_value - unix_time_zero).total_seconds())
#         self.argument=seconds_since_epoch

# if __name__ == '__main__':
#     a=datetime()
#     a.maxwell_cal_time(start_value)
#     a.monthdelta(date1,start_value)


