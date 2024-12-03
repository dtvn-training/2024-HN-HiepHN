import scrapy
import pandas as pd
import os 
import logging
import time

from dotenv import load_dotenv

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy_selenium import SeleniumRequest

load_dotenv()

MAX_URL_CRAWL = int(os.getenv("MAX_URL_CRAWL"))
WAIT_TIME = int(os.getenv("WAIT_TIME"))
   
class ScrapingClubSpider(scrapy.Spider):
    name = "tiki_product"
    
    # Read url of product need to be crawled from csv
    def __init__(self, name: str | None = None, **kwargs: EC.Any):
        super().__init__(name, **kwargs)
        
        current_dir = os.path.dirname(__file__)
        target_dir = os.path.normpath(os.path.join(current_dir,"../../output/tiki_url_filtered.csv"))
        df = pd.read_csv(target_dir)
        
        self.urls = df["url"].tolist()
        
        self.current_index = 0 
        
        self.max_size = min(MAX_URL_CRAWL,len(self.urls))
        
        if MAX_URL_CRAWL == -1:
            self.max_size = len(self.urls)
            
    # Crawl 1 element from css     
    def crawl_from_css(self, type, attribute, parameters, dict, key, driver, css):
        
        if type == "property":
            try:
                attr = getattr(driver.find_element(By.CSS_SELECTOR, css), attribute) 
                dict[key] = attr
            except Exception as e:
                logging.error(e)
        else:
            try:
                attr = getattr(driver.find_element(By.CSS_SELECTOR, css), attribute)
                args = [x for x in parameters.split(',')]
                dict[key] = attr(*args)
            except Exception as e:
                logging.error(e)
                
    # Crawl list elements having the same css
    def crawl_list_css(self, type, attribute, parameters, dict, key, driver, css):
        if type == "property":
            try:
                dict[key] = []
                element_list = driver.find_elements(By.CSS_SELECTOR, css)
                for element in element_list:
                    attr = getattr(element, attribute)
                    dict[key].append(attr)
            except Exception as e:
                logging.error(e)
        else:
            try:
                dict[key] = []
                element_list = driver.find_elements(By.CSS_SELECTOR, css)
                args = [x for x in parameters.split(',')]
                for element in element_list:
                    attr = getattr(element, attribute)
                    dict[key].append(attr(*args))
            except Exception as e:
                logging.error(e)
        
    # Tell driver to wait till an element is found
    def wait_till_found(self, time, driver, css):
        try:
            WebDriverWait(driver,time).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        except Exception as e:
            logging.error(e)          
        
    def start_requests(self):
        # 1 request per time since the middleware only use 1 web driver
        if self.current_index < self.max_size:
            yield SeleniumRequest(url=self.urls[self.current_index], callback=self.parseProduct, errback=self.errback, dont_filter=True)
            
        
    def parseProduct(self,response):
        
        driver = response.request.meta["driver"]
        product = {}
        
        # Simulate user behavior
        driver.set_window_position(0, 0)
        driver.set_window_size(1920, 1080)
        ActionChains(driver).scroll_by_amount(0, 1000).perform()
        
        product["product_url"] = driver.current_url

        # Wait till the seller element is found 
        self.wait_till_found(WAIT_TIME, driver, "div.SellerHeader__SellerHeaderStyled-sc-la7c6v-0")
        WebDriverWait(driver, 2)

        key_css_attr_params = [("product_name", ".Title__TitledStyled-sc-c64ni5-0", "text", ""),
                        ("current_price", ".product-price__current-price", "text", ""),
                        ("discount_rate", ".product-price__discount-rate", "text", ""),
                        ("original_price", ".product-price__original-price", "text", ""),
                        ("number_solds", ".styles__RatingStyled-sc-1onuk2l-0 .styles__StyledQuantitySold-sc-1onuk2l-3", "text", ""),
                        ("number_reviews", ".styles__RatingStyled-sc-1onuk2l-0 .number", "text", ""),
                        ("brand_name", "h6 a", "text", ""),
                        ("brand_url", "h6 a", "get_attribute", "href"),
                        ("seller_name", "div.SellerName__SellerNameStyled-sc-5d1cxl-0", "text", ""),
                        ("seller_url", "div.SellerName__SellerNameStyled-sc-5d1cxl-0 a", "get_attribute", "href")]
        
        # Crawl data from css class 
        for key,css,attr,params in key_css_attr_params:
            if attr == "text":
                self.crawl_from_css("property", attr, params, product, key, driver, css)
            else:
                self.crawl_from_css("method", attr, params, product, key, driver, css)
         
        # Sometime the seller element display and then disappear in short time, need to reload
        if product.get("seller_name","") == "":
            yield SeleniumRequest(url=self.urls[self.current_index], callback=self.parseProduct, errback=self.errback, dont_filter=True)
        
        else:   
            # Scroll to let the element appear         
            ActionChains(driver).scroll_by_amount(0,1000).perform()
            self.wait_till_found(WAIT_TIME, driver, ".HighlightInfo__HighlightInfoContentStyled-sc-1pr13u3-0")

            ActionChains(driver).scroll_by_amount(0,1000).perform()
            self.wait_till_found(WAIT_TIME, driver, ".ToggleContent__Wrapper-sc-fbuwol-1")
                
            ActionChains(driver).scroll_by_amount(0,1000).perform()
            
            self.crawl_list_css("method", "get_attribute", "src", product, "product_imgs", driver, ".thumbnail-list div.content span.slider picture.webpimg-container img")            
            
            self.crawl_list_css("property", "text", "", product, "feature", driver, ".HighlightInfo__HighlightInfoContentStyled-sc-1pr13u3-0")            
            
            self.crawl_list_css("property", "text", "", product, "category", driver, ".breadcrumb-item")           
            product["category"] = ";;".join([txt for txt in product["category"]])
            
            # Click button to display all hidden content 
            try:
                button_more = driver.find_element(By.CSS_SELECTOR, ".btn-more")
                button_more.click()
            except Exception as e:
                logging.error(e)
                
            self.crawl_from_css("property", "text", "", product, "description", driver, ".ToggleContent__View-sc-fbuwol-0")
        
            self.crawl_list_css("property", "text", "", product, "detail", driver, "div[style=\"display: grid; grid-template-columns: 55% 45%; gap: 4px;\"].WidgetTitle__WidgetContentRowStyled-sc-12sadap-3")            
                    
            # Scroll down and wait till review comment is displayed
            ActionChains(driver).scroll_by_amount(0,1000).perform()
            self.wait_till_found(WAIT_TIME, driver, ".customer-reviews__pagination li a.next")

            WebDriverWait(driver, 1)
            
            self.crawl_from_css("property", "text", "", product, "avg_rating", driver, ".review-rating__point")
             
            # Crawl reviews
            review_list_table = []
                    
            try:
                review_list = driver.find_elements(By.CSS_SELECTOR, ".review-comment")
                    
                for review in review_list:
                    review_table = []
                    # Find and click button to display all review content
                    try:
                        show_more_button = review.find_element(By.CSS_SELECTOR, ".show-more-content")
                        show_more_button.click()
                    except Exception as e:
                        logging.error(e)
                        
                    try:
                        review_table.append(review.find_element(By.CSS_SELECTOR, ".review-comment__rating").get_attribute("innerHTML"))
                    except Exception as e :
                        logging.error(e)
                        review_table.append("")
                        
                    try:
                        review_table.append(review.find_element(By.CSS_SELECTOR, ".review-comment__content").text)
                    except Exception as e :
                        logging.error(e)
                        review_table.append("")
                        
                    try:
                        review_img = []
                        imgs = review.find_elements(By.CSS_SELECTOR, ".review-comment__image")
                        for img in imgs:
                            review_img.append(img.get_attribute("style"))
                        review_table.append(review_img)
                    except Exception as e:
                        review_table.append([])
                        
                    review_list_table.append(review_table)
                            
            except Exception as e:
                logging.error(e)
                
            yield {
                    "product_name":product.get("product_name",""),
                    "product_url":product.get("product_url",""),
                    
                    "avg_rating":product.get("avg_rating"),
                    "number_sold":product.get("number_solds"),
                    "number_reviews":product.get("number_reviews"),
                    
                    "product_imgs":product.get("product_imgs"),
                    
                    "current_price":product.get("current_price",""),
                    "discount_rate":product.get("discount_rate",""),
                    "original_price":product.get("original_price",""),
                    
                    "brand_name":product.get("brand_name",""),
                    "brand_url":product.get("brand_url",""),
                    
                    "seller_name":product.get("seller_name",""),
                    "seller_url":product.get("seller_url",""),
                    
                    "review":review_list_table,
                    
                    "feature":product.get("feature",""),
                    "category":product.get("category",""),
                    "detail":product.get("detail",""),
                    "description":product.get("description","")
                        
            }
            
            self.current_index += 1
            if self.current_index < self.max_size:
                yield SeleniumRequest(url=self.urls[self.current_index], callback=self.parseProduct, errback=self.errback, dont_filter=True)
    
    def errback(self, failure):
        self.current_index += 1
        if self.current_index < self.max_size:
            yield SeleniumRequest(url=self.urls[self.current_index], callback=self.parseProduct, errback=self.errback, dont_filter=True)
