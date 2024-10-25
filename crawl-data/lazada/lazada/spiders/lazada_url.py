import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import time
from selenium.webdriver.common.by import By


class ScrapingClubSpider(scrapy.Spider):
        name = "lazada_url"
        
        def start_requests(self):
            url = "https://pages.lazada.vn/wow/gcp/route/lazada/vn/upr_1000345_lazada/channel/vn/upr-router/vn?wh_pid=%2Flazada%2Fchannel%2Fvn%2Fshopping-guide%2Flazflash&hybrid=1&data_prefetch=true&hide_h5_title=true&at_iframe=1&lzd_navbar_hidden=true&disable_pull_refresh=true&prefetch_replace=1&skuIds=2756708%2C254092590%2C260193101%2C270626366%2C2756756%2C275706698%2C286314009&spm=a2o4n.homepage.FlashSale.d_shopMore"
            yield SeleniumRequest(url=url, callback=self.parse)
            
        def parse(self, response):
            driver = response.request.meta["driver"]

            category_list = driver.find_elements(
                By.CSS_SELECTOR, "div.lzd-site-nav-menu-dropdown a")

            url_categories = []
            for category in category_list:
                url_categories.append(category.get_attribute("href"))

            for url_category in url_categories:
                for i in range (1,100):
                    time.sleep(2)
                    new_url=url_category+"/?page="+str(i)
                    yield SeleniumRequest(url=new_url, callback=self.parseCategory)

        def parseCategory(self, response):
            driver = response.request.meta["driver"]
            
            url_products = []
            try:
                product_list = driver.find_elements(By.CSS_SELECTOR,"._95X4G")
                for product in product_list:
                    url_products.append(product.find_element(By.CSS_SELECTOR,"a").get_attribute("href"))
                    print(product.find_element(By.CSS_SELECTOR,"a").get_attribute("href"))
            except Exception as e:
                print(e)
                
            for url_product in url_products:
                yield {
                    "url":url_product
                }
                # time.sleep(2)
                # yield SeleniumRequest(url=url_product, callback=self.parseProduct)            
                
            
