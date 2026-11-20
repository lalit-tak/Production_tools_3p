import csv 
with open('people.csv', '+') as csvFile:
    reader = csv.read(csvFile)
    for row in reader:
        print(row)

# csvFile.close()  