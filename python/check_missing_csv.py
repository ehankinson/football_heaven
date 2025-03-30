import csv

FILE = "csv/PFF_Passing_{year}.csv"

list1 = []
list2 = []
skip = False
header_count = 0

for year in range(2006, 2025):
    with open(FILE.format(year=year), "r") as f:
        reader = csv.reader(f)

        for row in reader:

            if row[1] == "player":
                header_count += 1
                if header_count > 2:
                    if list1 == list2:
                        skip = True
                        break
                    else:
                        list1 = list2
                        list2 = []

            elif header_count < 2:
                list1.append(row)

            else:
                list2.append(row)
        
        if skip:
            print(f"{FILE.format(year=year)} is missing info, please re-run")
