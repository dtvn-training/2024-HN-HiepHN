import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import time
from selenium.webdriver.common.by import By


class ScrapingClubSpider(scrapy.Spider):
        name = "tiki_url"
        
        def start_requests(self):
            url = "https://tiki.vn/"
            yield SeleniumRequest(url=url, callback=self.parse)
            
        def parse(self, response):
            driver = response.request.meta["driver"]

            category_list = driver.find_elements(
                By.CSS_SELECTOR, ".styles__StyledItemV2-sc-oho8ay-1")

            url_categories = []
            for category in category_list:
                url_categories.append(category.find_element(
                    By.CSS_SELECTOR, "a").get_attribute("href"))

            for url_category in url_categories:
                time.sleep(2)
                yield SeleniumRequest(url=url_category, callback=self.parseCategory)

        def parseCategory(self, response):
            driver = response.request.meta["driver"]

            while True:
                time.sleep(1)

                try:
                    show_button = driver.find_element(By.CSS_SELECTOR,".styles__Button-sc-143954l-1")
                except NoSuchElementException:
                    break
                    
                show_button.click()
            
            url_products = []
            
            product_list = driver.find_elements(By.CSS_SELECTOR,".styles__ProductItemContainerStyled-sc-bszvl7-0 ")
            
            for product in product_list:
                url_products.append(product.find_element(By.CSS_SELECTOR,"a").get_attribute("href"))
                
            for url_product in url_products:
                yield {
                    "url":url_product
                }
                # time.sleep(2)
                # yield SeleniumRequest(url=url_product, callback=self.parseProduct)            
                
            
