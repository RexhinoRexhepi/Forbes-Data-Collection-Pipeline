# **Forbes Billionaires Scraper**

This scraper is designed to extract the data of the first 'n' billionaires in Forbes' Billionaire list, including their name, age, net worth, source, and profile link. It also downloads the image of each billionaire.
Requirements

This scraper requires the following Python libraries to be installed:

   * selenium
   * webdriver_manager
   * pandas
   * numpy
   * requests
   * boto3
   * smptlib
    
    The scraper also requires the Chrome browser to be installed and compatible with the installed webdriver_manager library.
    
  ## **Usage**
    
    1.To initiate the Forbes Scraper program, open your terminal and enter the command python3 forbes_scraper.py. 
    Once executed, the program will prompt you to specify the number of billionaires you would like to scrape from the Forbes list.
    Enter the desired number when prompted and press the Enter key to start the scraping process.
    
    2.The data will be stored in a dictionary named billioners_data, with the following keys:

   * uuid: A unique ID for each billionaire.
   * rank: The rank of each billionaire.
   * full_name: The full name of each billionaire.
   * age: The age of each billionaire.
   * net_worth: The net worth of each billionaire.
   * source: The source of each billionaire's wealth.
   * link: The profile link of each billionaire.

    3.The images will be downloaded and stored in a folder named images in the current directory.
   
 ## **Notes**

    If the Forbes website has updated its design or structure, this scraper may not work properly.
    This scraper is intended for educational and personal use only. It is not intended for commercial use.
