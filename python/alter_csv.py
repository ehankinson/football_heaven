import csv

INDEXS = [23, 61, 93, 126]
LENGTH = 142


def delete_array(row: list[str], index: int) -> list[bool]:
    delete_rows = []
    while "grades" in row[index]:
        if row[index].endswith("grades_pass"):
            delete_rows.append(False)
        else:
            delete_rows.append(True)
        index += 1

    return delete_rows



def alter_row(row: list[str], delete_rows: list[bool]) -> list[str]:
    for i in INDEXS:
        for delete in delete_rows:
            if delete:
                del row[i]
            else:
                i += 1
    
    return row



def process_file(_file: str, start_year: int, end_year: int) -> None:
    for year in range(start_year, end_year):
        all_rows = []
        with open(_file.format(year=year), "r") as f:
            reader = csv.reader(f)

            week = 0
            for count, row in enumerate(reader):
                if row[1] == "player":
                    delete_rows = delete_array(row, INDEXS[0])
                    week += 1

                if len(row) == LENGTH:
                    all_rows.append(row)

                elif row[LENGTH:] == [""] * (len(row) - LENGTH):
                    all_rows.append(row[:LENGTH])
                
                else:
                    new_row = alter_row(row, delete_rows)
                    all_rows.append(new_row)
                    try:
                        assert len(new_row) == LENGTH
                    except:
                        print(f"Row {count}: {new_row}")
                        raise Exception("Length is not 142, it is {}".format(len(new_row)))
    
        with open(_file.format(year=year), "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(all_rows) 


start_year = 2006
end_year = 2025
_file = "csv/PFF_Passing_Pressure_{year}.csv"

process_file(_file, start_year, end_year)
                