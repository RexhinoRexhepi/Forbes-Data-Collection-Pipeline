from genericpath import exists
from itertools import count
from tkinter import N
from numpy import number
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from  webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import math
import os
import urllib.request
import time
import datetime
import smtplib
import boto3
import uuid

class Forbes_Scraper:
    # XPath expressions for various elements on the page
    xpath_cookies = '//button[@class="trustarc-agree-btn"]'
    xpath_first_option = '(//div[@class="table-row-group__container"]/div)[1]'
    xpath_popup_close = '//div[@class="tp-iframe-wrapper"]/button[@class="tp-close tp-active"]'
    xpath_billioners_container = '//div[@class="table-row-group__container"]/div[@class!="below-row-content"]'
    xpath_pagination_buttons = '//div[@class="pagination"]/div/button'
    xpath_billioner_bio_link = '//div[@class="table-row-group"]/div[@class!="left-rail"]//a [@class="bio-button"]'
    xpath_billioner_name = '//div[@class="avatar"]/img'
    xpath_billioner_rank = '//span[@class="list-name--rank"]'
    xpath_billioner_full_name = '//div[@class="listuser-header__name"]'
    xpath_billioner_age = '//span[contains(text(),"age")]/following-sibling::div'
    xpath_billioner_net_worth = '//span[contains(text(),"Net worth")]/following-sibling::div'
    xpath_billioner_source = '//span[contains(text(),"Source")]/following-sibling::div'
    xpath_next_page = '//button[@class="next-page"]'

    def __init__(self, url: str = 'https://www.forbes.com/billionaires/'):

        """
        Initializes the Forbes Scraper class.

        Sets chrome options for Selenium.
        Chrome options for headless browser are enabled.
        Initializes the web browser and opens the specified URL.
        """
        chrome_options = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-popup-blocking")
        # chrome_options.headless = True
    
        self.driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.driver.maximize_window()
        self.driver.get(url)

    def accept_cookies(self):
        """
        Accepts cookies if there is any by locating and clicking the cookies button.
        """
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.xpath_cookies)))
            self.driver.find_element(By.XPATH, self.xpath_cookies).click()
        except TimeoutException:
            print('No cookies found')
        return None
    
    def close_first_option(self):
        """
        Closes the first option to start iterating through all the billionaires.
        """
        time.sleep(2)
        open_element = self.driver.find_element(By.XPATH, self.xpath_first_option)
        open_element.location_once_scrolled_into_view
        open_element.click()
        return None

    def close_pop_up(self):
        """
        Closes any pop-up that may appear.
        """
        try:
            self.driver.find_element(By.XPATH, self.xpath_popup_close).click()
        except:
            pass

    def get_links(self, num):
        """
        Scrapes the billionaire profile links from the page.
        """
        self.num = num

        self.billioners_link = []
        self.billioners_img = {'name': [], 'img_link': []}

        num_billioners = 2640
        num_pages = math.ceil(num_billioners / 200)

        count = 0  # Counter to keep track of the number of people scraped

        while count < num:
            # Wait for the elements to load
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, self.xpath_billioners_container)))

            # Find all the people on the current page
            list_billioners = self.driver.find_elements(By.XPATH, self.xpath_billioners_container)

            # Close the first option before iterating through all the people
            self.close_first_option()

            # Process each person
            for billioner in list_billioners:
                time.sleep(1)
                billioner.click()
                time.sleep(1)

                try:
                    self.billioners_link.append(self.driver.find_element(By.XPATH, self.xpath_billioner_bio_link).get_attribute('href'))
                except TimeoutException:
                    print("No link found!")
                try:
                    self.billioners_img['img_link'].append(self.driver.find_element(By.XPATH, self.xpath_billioner_name).get_attribute('src'))
                except TimeoutException:
                    print("No image link found!")
                try:
                    self.billioners_img['name'].append(self.driver.find_element(By.XPATH, self.xpath_billioner_name).get_attribute('alt'))
                except TimeoutException:
                    print("No image name found!")

                count += 1

                if count >= num:
                    break

            if count >= num:
                break

            if num_pages > 1:
                # Check if there is a next page
                next_button = self.driver.find_element(By.XPATH, self.xpath_next_page)
                if next_button.is_enabled():
                    # Click the next page button
                    next_button.click()
                    time.sleep(2)
                    num_pages -= 1
                else:
                    break
            else:
                break


    def get_billioners_data(self):
        """
        Scrapes the data of each billionaire from their profile pages.
        """
        self.billioners_data = {
            'uuid': [],
            'rank': [],
            'full_name': [],
            'age': [],
            'net_worth': [],
            'source': [],
            'link': []
        }
        
        for link in self.billioners_link:
            self.driver.get(link)
            time.sleep(2)
    
            self.billioners_data['link'].append(link)
            self.billioners_data["uuid"].append(str(uuid.uuid4()))

            
            # WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@id="mnet"]')))
            try:
                rank = self.driver.find_element(By.XPATH, self.xpath_billioner_rank)
                self.billioners_data['rank'].append(rank.text)
            except TimeoutException:
                print("no rank found!")
            try:
                full_name = self.driver.find_element(By.XPATH, self.xpath_billioner_full_name).text
                self.billioners_data['full_name'].append(full_name)
            except TimeoutException:
                print("No name found!")
            try:
                age = self.driver.find_element(By.XPATH, self.xpath_billioner_age)
                self.billioners_data['age'].append(age.text)
            except TimeoutException:
                print("No age found!")
            try:
                net_worth = self.driver.find_element(By.XPATH, self.xpath_billioner_net_worth)
                self.billioners_data['net_worth'].append(net_worth.text)
            except TimeoutException:
                print("No net worth found!")
            try:
                source = self.driver.find_element(By.XPATH, self.xpath_billioner_source)
                self.billioners_data['source'].append(source.text)
            except TimeoutException:
                print("No source found!")

    def save_billioners_data(self):
        '''
        Creates a folder and stores all the data scraped.
        '''
        df = pd.DataFrame(self.billioners_data)
        os.makedirs('data', exist_ok=True) 
        df.to_csv('data/billioners_data.csv', index=False, encoding='utf-8')  

    def save_img_data(self):
        
        df =pd.DataFrame(self.billioners_img)
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/img_links.csv', index=False, encoding='utf-8')

    def pull_img(self):
        """
        Pulls and saves images based on the image links from the CSV file.
        """
        filename = 'data/img_links'

        # open file to read
        with open("{0}.csv".format(filename), 'r') as csvfile:
            # iterate on all lines
            next(csvfile)
            i = 0
            for line in csvfile:
                splitted_line = line.split(',')
                # check if we have an image URL
                if splitted_line[1] != '' and splitted_line[1] != "\n":
                    my_path = os.makedirs('data/images', exist_ok=True)
                    urllib.request.urlretrieve( splitted_line[1], f'data/images/{splitted_line[0] + ".png"}')
                    print("Image saved for {0}".format(splitted_line[0]))
                    i += 1
                else:
                    print("No result for {0}".format(splitted_line[0]))

    def dump_data_to_aws(self):
        """
        Uploads CSV files from the specified directory to an AWS S3 bucket.
        """
        path = "/home/rexhino/Web_Scraping_Project/Forbes-Data-Collection-Pipeline/data"
        os.chdir(path)

        s3 = boto3.client('s3')
        for my_file in os.listdir():
            if '.csv' in my_file:
                bucket = 'billioners-bucket'
                file_key = 'Billioners_data/' + str(my_file) 
                s3.upload_file(my_file, bucket, file_key)
            
    def dumb_images_to_aws(self):
        """
        Uploads images from the specified directory to an AWS S3 bucket.
        """
        img_path = "/home/rexhino/Web_Scraping_Project/Forbes-Data-Collection-Pipeline/data/images"
        os.chdir(img_path)

        s3 = boto3.client('s3')
        for my_file in os.listdir():
            bucket = 'billioners-bucket'
            file_key = 'Billioners_Images/' + str(my_file) 
            s3.upload_file(my_file, bucket, file_key)

    def run_scraper(self,num):
        print("accepting cookies")
        self.accept_cookies()
        print("getting the profile links...")
        self.close_first_option()
        self.get_links(num)
        print("getting the data")
        self.get_billioners_data()
        print("saving the data")
        self.save_billioners_data()
        self.save_img_data()
        print("saving images")
        self.pull_img()
        print("dumping data & images on a S3 bucket")
        self.dump_data_to_aws()
        self.dumb_images_to_aws()
        print("Done!")

    def quit_scraper(self):
        self.driver.quit()
                
if __name__ == '__main__':
    forbes = Forbes_Scraper()
    forbes.run_scraper()
    forbes.quit_scraper()