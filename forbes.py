from asyncore import read
from csv import reader
from dataclasses import dataclass
from http import client
from tkinter.tix import Tree
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from  webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
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
        self.driver = Chrome(ChromeDriverManager().install())
        self.driver.maximize_window()
        self.driver.get(url)

    def accept_cookies(self, xpath: str = '//button[@class="trustarc-agree-btn"]'):
        '''
        Acepting cookies if there is any
        '''
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        except TimeoutException:
            print('No cookies found')
    
    def close_first_option(self, xpath: str = '(//div[@class="table-row-group__container"]/div)[1]'):
        '''
        We have to go through every billioner, so we have to close the first option and start iterating through all of them
        '''
        time.sleep(2)
        open_element = self.driver.find_element(By.XPATH, xpath)
        open_element.location_once_scrolled_into_view
        open_element.click()

    def get_links(self, xpath: str = '(//div[@class="table-row-group__container"])[1]/div'):
        '''
        Declare and empty list and then for each of billioners we click we get the link and store it
        '''
        self.billioners_link = []
        self.billioners_img = {
            'name': [],
            'img_link': []
        }
    
        list_billioners = self.driver.find_elements(By.XPATH, xpath)
        for billioners in list_billioners[0:10]:
            time.sleep(1)
            billioners.click()
            time.sleep(1)

            self.billioners_link.append(self.driver.find_element(By.XPATH, '//div[@class="table-row-group"][1]/div[@class!="left-rail"]//a').get_attribute('href'))
            self.billioners_img['img_link'].append(self.driver.find_element(By.XPATH, '//div[@class="avatar"]/img').get_attribute('src'))
            self.billioners_img['name'].append(self.driver.find_element(By.XPATH, '//div[@class="avatar"]/img').get_attribute('alt'))

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
        
        for link in self.billioners_link[0:10]:
            self.driver.get(link)
            time.sleep(1)
    
            self.billioners_data['link'].append(link)
            self.billioners_data["uuid"].append(str(uuid.uuid4()))

            
            # WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@id="mnet"]')))

            rank = self.driver.find_element(By.CLASS_NAME, "list-name--rank")
            self.billioners_data['rank'].append(rank.text)

            full_name = self.driver.find_element(By.XPATH, '//div[@class="listuser-header__name"]').text
            self.billioners_data['full_name'].append(full_name)

            age = self.driver.find_element(By.XPATH, '(//span[@class="profile-stats__text"])[1]')
            self.billioners_data['age'].append(age.text)

            net_worth = self.driver.find_element(By.XPATH, '//div[@class="profile-info__item-value"]')
            self.billioners_data['net_worth'].append(net_worth.text)

            source = self.driver.find_element(By.XPATH, '(//span[@class="profile-stats__text"])[2]')
            self.billioners_data['source'].append(source.text)

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
                    my_path = os.makedirs('data', exist_ok=True)
                    urllib.request.urlretrieve( splitted_line[1], f'data/{splitted_line[0] + ".png"}')
                    print("Image saved for {0}".format(splitted_line[0]))
                    i += 1
                else:
                    print("No result for {0}".format(splitted_line[0]))

    def dump_data_to_aws(self):
        path = "/home/rexhino/Web_Scraping_Project/Forbes-DataCollection-Pipeline/data"
        os.chdir(path)

        s3 = boto3.client('s3')
        for my_file in os.listdir():
            bucket = 'billioners-bucket'
            file_key = 'Top10_billioner&images/' + str(my_file) 
            s3.upload_file(my_file, bucket, file_key)

        self.driver.quit()
                
if __name__ == '__main__':
    bot = Forbes_Scraper()
    bot.accept_cookies()
    bot.close_first_option()
    bot.get_links()
    bot.get_billioners_data()
    bot.save_billioners_data()
    bot.save_img_data()
    bot.pull_img()
    bot.dump_data_to_aws()