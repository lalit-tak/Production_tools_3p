import csv

# with open('csv1.csv') as fd: 
#   reader=csv.reader(fd) 
#   # interestingrows=[row for idx, row in enumerate(reader) if idx in (26)]
#   for row in fd.readlines():
#       print row

    # print interestingrows,type(interestingrows)










# with open('csv.csv', mode='r') as csv_file:
csv_reader = [1,2,3,[4,5,[6,7]]]
    # line_count = 0

print (csv_reader[3][5]).replace('[','').replace(']','')
print (csv_reader[5][5]).replace('[','').replace(']','')


    # for row in csv_file.readlines():
    #   print row

# with open('csv.csv', mode='r') as csv_file:
#     csv_reader = csv.reader(csv_file)
#     line_count = 0

#     fd_type=[row for idx, row in enumerate(csv_reader) if idx == 1]
#     print fd_type
#     fd_telescopic=[row for idx, row in enumerate(csv_reader) if idx == 2]
#     print fd_telescopic
#     mmc_application=[row for idx, row in enumerate(csv_reader) if idx == 3]
#     print mmc_application
#     friendly_hours1=[row for idx, row in enumerate(csv_reader) if idx == 4]
#     print friendly_hours1
#     friendly_hours2=[row for idx, row in enumerate(csv_reader) if idx == 5]
#     print friendly_hours2
#     alert_limit=[row for idx, row in enumerate(csv_reader) if idx == 6]
#     print alert_limit
#     emergency_credit=[row for idx, row in enumerate(csv_reader) if idx == 7]
#     print emergency_credit
#     top_up_limit=[row for idx, row in enumerate(csv_reader) if idx == 8]
#     print top_up_limit
#     mmc=[row for idx, row in enumerate(csv_reader) if idx == 9]
#     print mmc
#     fdPrice=[row for idx, row in enumerate(csv_reader) if idx in (10,15)]
#     print fdPrice
#     energy_Price=[row for idx, row in enumerate(csv_reader) if idx in (16,21)]
#     print energy_Price
#     energySlab=[row for idx, row in enumerate(csv_reader) if idx in (22,26)]
#     print energySlab
   
    
    



    # for index in range(len(self.fdPrice)):
    #         payload.extend(serialize.serialize_uint32(self.fdPrice[index],"reverse"))

    #     for index in range(len(self.energyPrice)):
    #         payload.extend(serialize.serialize_uint16(self.energyPrice[index],"reverse"))
    #     for index in range(len(self.energySlab)):
    #         payload.extend(serialize.serialize_uint16(self.energySlab[index],"reverse"))
    #     payload.extend(serialize.serialize_uint8(self.tariffType,"reverse"))

    # (interestingrows[0][0]).replace('[','').replace(']','')
     