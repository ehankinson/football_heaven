import csv
import json

YEAR = 2024
FILE_NAME = "PFF_{stat}_{year}.csv"

files = [
    "Passing",
    "Passing_Depth",
    "Passing_Pressure",
    "Receiving",
    "Receiving_Depth",
    "Receiving_Scheme",
    "Rushing",
    "Blocking",
    "Blocking_Pass",
    "Blocking_Rush",
    "Defense",
    "Defense_Pass_Rush",
    "Defense_Run_Defense",
    "Defense_Coverage",
    "Defense_Coverage_Scheme"
]


for f in files:
    file_name = FILE_NAME.format(stat=f, year=YEAR)

    with open(f"csv/{file_name}", "r") as c:
        reader = csv.reader(c)

        for row in reader:
            a = 5
        

        
        


