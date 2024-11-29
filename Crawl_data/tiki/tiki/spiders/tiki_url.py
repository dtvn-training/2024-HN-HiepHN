import scrapy
import time
import os 

from dotenv import load_dotenv

from scrapy_selenium import SeleniumRequest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

MAX_URL_PER_CATEGORY = int(os.getenv("MAX_URL_PER_CATEGORY"))   
SORT_TYPE = os.getenv("SORT_TYPE")
SLEEP_TIME = int(os.getenv("SLEEP_TIME"))
START_URL = os.getenv("START_URL")
FILTER_ADS = os.getenv("FILTER_ADS")
ADS_LINK = os.getenv("ADS_LINK")

class ScrapingClubSpider(scrapy.Spider):
        name = "tiki_url"
        
        def __init__(self, name: str | None = None, **kwargs: EC.Any):
            super().__init__(name, **kwargs)
            self.current_index = 0
            self.url_categories = []
        
        def start_requests(self):
            url = START_URL
            yield SeleniumRequest(url = url, callback = self.parse)
            
        def parse(self, response):
            driver = response.request.meta["driver"]

            category_list = driver.find_elements(
                By.CSS_SELECTOR, ".styles__StyledItemV2-sc-oho8ay-1")
  
            for category in category_list:
                self.url_categories.append(category.find_element(
                    By.CSS_SELECTOR, "a").get_attribute("href"))
                
            if self.current_index < len(self.url_categories):
                yield SeleniumRequest(url = self.url_categories[self.current_index] + "?sort=" + SORT_TYPE, callback = self.parseCategory, errback = self.errback)

        def parseCategory(self, response):
            driver = response.request.meta["driver"]
            prev_list_size = 0
            url_products = []
            

            while True:
                if MAX_URL_PER_CATEGORY != -1 and len(url_products) >= MAX_URL_PER_CATEGORY:
                    break
                
                product_list = driver.find_elements(By.CSS_SELECTOR, ".styles__ProductItemContainerStyled-sc-bszvl7-0")
                
                for i in range (prev_list_size, len(product_list)):
                    if MAX_URL_PER_CATEGORY !=-1 and len(url_products) >= MAX_URL_PER_CATEGORY: 
                        break
                    
                    if FILTER_ADS == "TRUE":
                        if not product_list[i].find_element(By.CSS_SELECTOR, "a").get_attribute("href").startswith(ADS_LINK):
                            url_products.append(product_list[i].find_element(By.CSS_SELECTOR, "a").get_attribute("href"))
                    else:
                        url_products.append(product_list[i].find_element(By.CSS_SELECTOR, "a").get_attribute("href"))       
                
                prev_list_size = len(product_list)
                
                try:
                    show_button = driver.find_element(By.CSS_SELECTOR, ".styles__Button-sc-143954l-1")
                except NoSuchElementException as e:
                    break
                    
                time.sleep(SLEEP_TIME)
                show_button.click()
            
            for url_product in url_products:
                yield {
                    "url":url_product
                }
                            
            self.current_index += 1
                
            if self.current_index < len(self.url_categories):
                yield SeleniumRequest(url = self.url_categories[self.current_index] + "?sort=" + SORT_TYPE, callback=self.parseCategory, errback = self.errback)
                
        def errback(self,failure):
            self.current_index += 1
                
            if self.current_index < len(self.url_categories):
                yield SeleniumRequest(url = self.url_categories[self.current_index] + "?sort=" + SORT_TYPE, callback=self.parseCategory, errback = self.errback)
                
