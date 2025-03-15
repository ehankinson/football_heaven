import os
import csv
import glob
import time

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PFFScraper:
    def __init__(self):
        self.chrome_path = '/usr/bin/google-chrome'
        self.links = [
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/passing?week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/passing-depth?split=deep&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/passing-pressure?week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/passing-concept?position=QB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/receiving?position=QB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/receiving-depth?position=WR,TE,RB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/receiving-scheme?position=WR,TE,RB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/rushing?position=WR,TE,RB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/offense-blocking?position=HB,FB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/offense-pass-blocking?position=T,G,C,TE,RB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/offense-run-blocking?position=T,G,C,TE,RB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/defense?position=T,G,C,TE,RB&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/defense-pass-rush?position=DI,ED,LB,CB,S&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/defense-run?position=DI,ED,LB,CB,S&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/defense-coverage?position=DI,ED,LB,CB,S&week={week}",
            "https://premium.pff.com/nfl/positions/{year}/SINGLE/defense-coverage-scheme?position=LB,CB,S&week={week}"
        ]
        self.file_names = [
            "PFF_Passing_{year}.csv",
            "PFF_Passing_Depth_{year}.csv",
            "PFF_Passing_Pressure_{year}.csv",
            "PFF_Passing_Concept_{year}.csv",
            "PFF_Receiving_{year}.csv",
            "PFF_Receiving_Depth_{year}.csv",
            "PFF_Receiving_Scheme_{year}.csv",
            "PFF_Rushing_{year}.csv",
            "PFF_Offense_Blocking_{year}.csv",
            "PFF_Offense_Pass_Blocking_{year}.csv",
            "PFF_Offense_Run_Blocking_{year}.csv",
            "PFF_Defense_{year}.csv",
            "PFF_Defense_Pass_Rush_{year}.csv",
            "PFF_Defense_Run_{year}.csv",
            "PFF_Defense_Coverage_{year}.csv",
            "PFF_Defense_Coverage_Scheme_{year}.csv"
        ]
        self.weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 28, 29, 30, 32]
        self.playoffs = {
            28: 29,
            29: 30,
            30: 31,
            32: 32  
        }
        
        # Setup Chrome options with your profile
        self.chrome_options = webdriver.ChromeOptions()
        
        # Add your Chrome profile
        self.download_dir = str(Path.home()) + "/Downloads"
        self.chrome_options.add_argument(f'--user-data-dir={str(Path.home())}/.config/google-chrome')
        self.chrome_options.add_argument('--profile-directory=Default')
        # self.chrome_options.add_argument('--headless=new')
        
        # Create a new Chrome driver instance
        self.driver = webdriver.Chrome(options=self.chrome_options)



    def process_csv(self, week, year, latest_file, file_name):
        relative_path = f"csv/{file_name}"
        with open(relative_path, 'a+') as output_file:
            with open(latest_file, 'r') as input_file:
                reader = csv.reader(input_file)
                for count, row in enumerate(reader):
                    if count > 0 and row[1] == "player":
                        continue
                    row.insert(0, "Week") if count == 0 else row.insert(0, week) if week not in self.playoffs else row.insert(0, self.playoffs[week])
                    writer = csv.writer(output_file)
                    writer.writerow(row)
        print(f"Finished processing of week {week} for year {year}")



    def scrape_data(self, start_year, end_year):
        try:
            for year in range(start_year, end_year + 1):
                for file_name, link in zip(self.file_names, self.links):
                    updated_file_name = file_name.format(year=year)
                    print(f"Writing to file {updated_file_name}\nUsing the link {link}")
                    for week in self.weeks:
                        self.driver.get(link.format(week=week, year=year))
                        time.sleep(3)
                        
                        csv_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'kyber-button') and contains(., 'CSV')]"))
                        )
                        csv_button.click()
                        
                        print("Waiting for CSV download...")
                        time.sleep(4)

                        # Look for CSV files in downloads directory
                        files = glob.glob(os.path.join(self.download_dir, "*.csv"))
                        latest_file = max(files, key=os.path.getctime)
                        print("File was successfully downloaded, Beginning to process...")
                        
                        self.process_csv(week, year, latest_file, updated_file_name)
                        print(f"Finished week {week} for year {year}")
                        
                        time.sleep(2.5)

            print("All weeks & years processed successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.driver.quit()



def main():
    try:
        start_year = int(input("Enter start year (2006-2024): "))
        end_year = int(input("Enter end year (2006-2024): "))
        
        if not (2006 <= start_year <= 2024 and 2006 <= end_year <= 2024):
            print("Years must be between 2006 and 2024")
            return
        if start_year > end_year:
            print("Start year must be less than or equal to end year")
            return

        scraper = PFFScraper()
        scraper.scrape_data(start_year, end_year)

    except ValueError:
        print("Please enter valid year numbers")
    except KeyboardInterrupt:
        print("\nScript terminated by user")

if __name__ == "__main__":
    main()