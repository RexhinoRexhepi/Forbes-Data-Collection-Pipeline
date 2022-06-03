import unittest
import forbes
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class TestScraper(unittest.TestCase):
    def setUp(self):
        self.bot = forbes.Forbes_Scraper()

    def test_accept_cookies(self):
        WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="trustarc-agree-btn"]')))
        self.bot.driver.find_element(By.XPATH, '//button[@class="trustarc-agree-btn"]').click()

        WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="elon-musk"]')))

    def test_close_first_option(self):
        time.sleep(5)
        WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, '(//div[@class="table-row-group__container"]/div)[1]')))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()