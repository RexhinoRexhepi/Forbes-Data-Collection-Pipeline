from forbes import Forbes_Scraper

print("Welcome to Forbes Billionaires list scraper")
print("You can choose a number, and the scraper will scrape the billionaires list starting from the richest.")

max_billionaires = 2640

while True:
    try:
        num = int(input(f"Enter the number of billionaires you want to scrape (maximum {max_billionaires}): "))
        if num <= 0 or num > max_billionaires:
            raise ValueError
        break
    except ValueError:
        print(f"Invalid input. Please enter a positive integer up to {max_billionaires}.")

forbes = Forbes_Scraper()
forbes.run_scraper(num)
forbes.quit_scraper()