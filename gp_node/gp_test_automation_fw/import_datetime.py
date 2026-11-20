from datetime import datetime
from dateutil import relativedelta
settime1="2012-05-15 12:00:00"
settime2="2012-09-15 17:00:00"
date1 = datetime.strptime(str(settime1), '%Y-%m-%d %H:%M:%S')
date2 = datetime.strptime(str(settime2), '%Y-%m-%d %H:%M:%S')
r = relativedelta.relativedelta(date2, date1)
r.months
print r.months

def onep_bundle(*argv):
    for arg in argv: 
        print("voltage :", arg)
        print("current :", arg)
        print("power factor :", arg)
        print("tampers :", arg) 
onep_bundle=("voltage:240"
            "current:10" 
            "power factor:1.0"
            "tampers:" "cover open")
# if __name__ == '__main__':
#             onep_bundle(*argv)      