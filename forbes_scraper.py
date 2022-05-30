from forbes import Forbes_Scraper

print("Welcome to Forbes Billioners list scraper")
print("You can choose a number and the scraper will scrape the billioners list starting from the richest")
num = int(input('Introduce the number of billioners you want to scrape: '))
forbes = Forbes_Scraper()
forbes.run_scraper(num)
forbes.quit_scraper()