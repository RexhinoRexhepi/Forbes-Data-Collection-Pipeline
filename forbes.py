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
import os
import urllib.request
import time
import datetime
import smtplib
import boto3
import uuid

class Forbes_Scraper:

    def __init__(self, url: str = 'https://www.forbes.com/billionaires/'):
        '''
        Initializing the web browser and getting the url indicated
        '''
    
        self.driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.driver.maximize_window()
        self.driver.get(url)

        """
        Sets chrome options for Selenium.
        Chrome options for headless browser is enabled.
        """
        chrome_options = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.headless = True

    def accept_cookies(self, xpath: str = '//button[@class="trustarc-agree-btn"]'):
        '''
        Acepting cookies if there is any
        '''
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        except TimeoutException:
            print('No cookies found')
        return None
    
    def close_first_option(self, xpath: str = '(//div[@class="table-row-group__container"]/div)[1]'):
        '''
        We have to go through every billioner, so we have to close the first option and start iterating through all of them
        '''
        time.sleep(2)
        open_element = self.driver.find_element(By.XPATH, xpath)
        open_element.location_once_scrolled_into_view
        open_element.click()
        return None

    def get_links(self, num, xpath: str = '//div[@class="table-row-group__container"]/div'):
        '''
        Declare and empty list and then for each of billioners we click we get the link and store it
        '''
        self.billioners_link = []
        self.billioners_img = {
            'name': [],
            'img_link': []
        }
        self.num = num
        
        list_billioners = self.driver.find_elements(By.XPATH, xpath)
        for billioners in list_billioners[0:num]:
            time.sleep(1)
            billioners.click()
            time.sleep(1)
            
            try:
                self.billioners_link.append(self.driver.find_element(By.XPATH, '//div[@class="table-row-group"]/div[@class!="left-rail"]//a [@class="bio-button"]').get_attribute('href'))
            except TimeoutException:
                print("No link found!")
            try:
                self.billioners_img['img_link'].append(self.driver.find_element(By.XPATH, '//div[@class="avatar"]/img').get_attribute('src'))
            except TimeoutException:
                print("No image link found!")
            try:
                self.billioners_img['name'].append(self.driver.find_element(By.XPATH, '//div[@class="avatar"]/img').get_attribute('alt'))
            except TimeoutException:
                print("No image name found!")

    def get_billioners_data(self):
        '''Get the billioners data throgh the dictionary with empty lists'''
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
                rank = self.driver.find_element(By.XPATH, '//span[@class="list-name--rank"]')
                self.billioners_data['rank'].append(rank.text)
            except TimeoutException:
                print("no rank found!")
            try:
                full_name = self.driver.find_element(By.XPATH, '//div[@class="listuser-header__name"]').text
                self.billioners_data['full_name'].append(full_name)
            except TimeoutException:
                print("No name found!")
            try:
                age = self.driver.find_element(By.XPATH, '(//span[@class="profile-stats__text"])[1]')
                self.billioners_data['age'].append(age.text)
            except TimeoutException:
                print("No age found!")
            try:
                net_worth = self.driver.find_element(By.XPATH, '//div[@class="profile-info__item-value"]')
                self.billioners_data['net_worth'].append(net_worth.text)
            except TimeoutException:
                print("No net worth found!")
            try:
                source = self.driver.find_element(By.XPATH, '(//span[@class="profile-stats__text"])[3]')
                self.billioners_data['source'].append(source.text)
            except TimeoutException:
                print("No source found!")

    def save_billioners_data(self):
        '''
        create a folder and store all the data we scrape
        '''
        df = pd.DataFrame(self.billioners_data)
        os.makedirs('data', exist_ok=True) 
        df.to_csv('data/billioners_data.csv', index=False, encoding='utf-8')  

    def save_img_data(self):
        
        df =pd.DataFrame(self.billioners_img)
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/img_links.csv', index=False, encoding='utf-8')

    def pull_img(self):
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
        path = "/home/rexhino/Web_Scraping_Project/Forbes-Data-Collection-Pipeline/data"
        os.chdir(path)

        s3 = boto3.client('s3')
        for my_file in os.listdir():
            if '.csv' in my_file:
                bucket = 'billioners-bucket'
                file_key = 'Billioners_data/' + str(my_file) 
                s3.upload_file(my_file, bucket, file_key)
            
    def dumb_images_to_aws(self):
        img_path = "/home/rexhino/Web_Scraping_Project/Forbes-Data-Collection-Pipeline/data/images"
        os.chdir(img_path)

        s3 = boto3.client('s3')
        for my_file in os.listdir():
            bucket = 'billioners-bucket'
            file_key = 'Billioners_Images/' + str(my_file) 
            s3.upload_file(my_file, bucket, file_key)

    def run_scraper(self,num):
        self.accept_cookies()
        print("accepting cookies")
        self.close_first_option()
        self.get_links(num)
        print("getting the profile links...")
        self.get_billioners_data()
        print("getting the data")
        self.save_billioners_data()
        print("saving the data")
        self.save_img_data()
        self.pull_img()
        print("saving images")
        self.dump_data_to_aws()
        self.dumb_images_to_aws()
        print("dumping data & images on a S3 bucket")

    def quit_scraper(self):
        self.driver.quit()
                
if __name__ == '__main__':
    forbes = Forbes_Scraper()
    forbes.run_scraper()
    forbes.quit_scraper()