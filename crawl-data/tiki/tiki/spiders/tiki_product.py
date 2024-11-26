import scrapy
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import time
from selenium.webdriver.common.by import By

import pandas as pd

import os 

class ScrapingClubSpider(scrapy.Spider):
    name = "tiki_product"
        
    def start_requests(self):
        current_dir = os.path.dirname(__file__)
            
        target_dir=os.path.normpath(os.path.join(current_dir,"../../output/tiki_url_filtered.csv"))

        df=pd.read_csv(target_dir)
        urls=df["url"].tolist()
        for i in range(2):
                time.sleep(2)
                try:
                    yield scrapy.Request(url=urls[i], callback=self.parseProduct)
                except Exception as e:
                    print(e)
        
    def parseProduct(self,response):
        driver = webdriver.Chrome()
        driver.get(response.url)
        product={}


        driver.set_window_position(0,0)
        driver.set_window_size(1920,1080)
        ActionChains(driver).scroll_by_amount(0,1000).perform()

        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.SellerName__SellerNameStyled-sc-5d1cxl-0")))
            product["seller_name"] = driver.find_element(By.CSS_SELECTOR,"div.SellerName__SellerNameStyled-sc-5d1cxl-0").text
            product["seller_url"] = driver.find_element(By.CSS_SELECTOR,"div.SellerName__SellerNameStyled-sc-5d1cxl-0 a").get_attribute("href")

        except Exception as e:
            print(e)
            
        ActionChains(driver).scroll_by_amount(0,1000).perform()
        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,".HighlightInfo__HighlightInfoContentStyled-sc-1pr13u3-0")))
        except Exception as e: 
            print(e)
    
        ActionChains(driver).scroll_by_amount(0,1000).perform()

        try: 
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,".ToggleContent__Wrapper-sc-fbuwol-1")))
        except Exception as e:
            print(e)
            
        ActionChains(driver).scroll_by_amount(0,1000).perform()
            
          
        code_lines=[
            "product[\"product_name\"] = driver.find_element(By.CSS_SELECTOR,\".Title__TitledStyled-sc-c64ni5-0\").text",
            "product[\"product_url\"] = driver.current_url",

            "product[\"current_price\"] = driver.find_element(By.CSS_SELECTOR,\".product-price__current-price\").text",
            "product[\"discount_rate\"] = driver.find_element(By.CSS_SELECTOR,\".product-price__discount-rate\").text",
            "product[\"original_price\"] = driver.find_element(By.CSS_SELECTOR,\".product-price__original-price\").text",
                
            
            "product[\"number_solds\"] = driver.find_element(By.CSS_SELECTOR,\".styles__RatingStyled-sc-1onuk2l-0 .styles__StyledQuantitySold-sc-1onuk2l-3\").text",
            "product[\"number_reviews\"] = driver.find_element(By.CSS_SELECTOR,\".styles__RatingStyled-sc-1onuk2l-0 .number\").text",
            
            "product[\"brand_name\"] = driver.find_element(By.CSS_SELECTOR,\"h6 a\").text",
            "product[\"brand_url\"] = driver.find_element(By.CSS_SELECTOR,\"h6 a\").get_attribute(\"href\")",
                
        ]
            
        for line in code_lines:
            try:
                exec(line)
            except Exception as e:
                print("error"+line)
                print(e)
                    
        product["product_imgs"]=[]
        try:
            product_imgs=driver.find_elements(By.CSS_SELECTOR,".thumbnail-list div.content span.slider picture.webpimg-container img")
                
            for img in product_imgs:
                product["product_imgs"].append(img.get_attribute("src"))
            
        except Exception as e:
            print(e)
                 
           
        product["feature"] = []
        try: 
            hightlights=driver.find_elements(By.CSS_SELECTOR,".HighlightInfo__HighlightInfoContentStyled-sc-1pr13u3-0")
            
            for hightlight in hightlights:
                product["feature"].append(hightlight.text)
        except Exception as e:
                print(e)
            
        product["category"]= []
        try:    
            categories=driver.find_elements(By.CSS_SELECTOR,".breadcrumb-item")
            product["category"] = ";;".join([category.text for category in categories])
                            
        except Exception as e:
                print(e)
            
        try:
            button_more = driver.find_element(By.CSS_SELECTOR,".btn-more")
            button_more.click()
        except Exception as e:
            print(e)
            
        try:
            descripts = driver.find_element(By.CSS_SELECTOR,".ToggleContent__View-sc-fbuwol-0")
            product["description"]=descripts.text
            print(descripts.text)
        except Exception as e:
            print(e)
            
        product["detail"]=[]
        try:
            details=driver.find_elements(By.CSS_SELECTOR,"div[style=\"display: grid; grid-template-columns: 55% 45%; gap: 4px;\"].WidgetTitle__WidgetContentRowStyled-sc-12sadap-3")
            for detail in details:
                product["detail"].append(detail.text)
        except Exception as e:
            print(e)
                
        ActionChains(driver).scroll_by_amount(0,1000).perform()
        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,".customer-reviews__pagination li a.next")))
        except Exception as e:
            print(e)

        WebDriverWait(driver,1)

        try:
            avg_rating = driver.find_element(By.CSS_SELECTOR,".review-rating__point")
            product["avg_rating"] = avg_rating.text
        except Exception as e:
            print(e)

        review_list_table=[]
        # while True:
                
        #     try:
        #         WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,".customer-reviews__pagination li a.next")))
        #     except Exception as e:
        #         print(e)
                
        try:
            review_list = driver.find_elements(By.CSS_SELECTOR,".review-comment")
                
            for review in review_list:
                review_table=[]
                try:
                    show_more_button = review.find_element(By.CSS_SELECTOR,".show-more-content")
                    show_more_button.click()
                except Exception as e:
                    print(e)
                    
                try:
                    review_table.append(review.find_element(By.CSS_SELECTOR,".review-comment__rating").get_attribute("innerHTML"))
                except Exception as e :
                    print(e)
                    review_table.append("")
                    
                try:
                    review_table.append(review.find_element(By.CSS_SELECTOR,".review-comment__content").text)
                except Exception as e :
                    print(e)
                    review_table.append("")
                    
                try:
                    review_img=[]
                    imgs = review.find_elements(By.CSS_SELECTOR,".review-comment__image")
                    for img in imgs:
                        review_img.append(img.get_attribute("style"))
                    review_table.append(review_img)
                except Exception as e:
                    print(e)
                    print("abc")
                    review_table.append("ff")
                    
                review_list_table.append(review_table)
                        
        except Exception as e:
            print(e) 
        
        
        
                
                
            # try:
            #     next_comment_button = driver.find_element(By.CSS_SELECTOR,".customer-reviews__pagination li a.next")
            #     next_comment_button.click()
            # except Exception as e:
            #     print("button err")
            #     print(e)
            #     break 
        driver.close()    
        yield{
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