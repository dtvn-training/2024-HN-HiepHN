import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import time
from selenium.webdriver.common.by import By
from datetime import datetime

import pandas as pd

class ScrapingClubSpider(scrapy.Spider):
    name = "lazada_product"
    
    review_per_page=5
     
    def start_requests(self):
        df=pd.read_csv("./output/lazada_url_filtered.csv")
        urls=df["url"].tolist()
        for i in range(1,100):
            time.sleep(2)
            try:
                yield SeleniumRequest(url=urls[i], callback=self.parseProduct)
            except Exception as e:
                print(e)
        
    def parseProduct(self,response):
        driver = response.request.meta["driver"]
        product={}


        driver.set_window_position(0,0)
        driver.set_window_size(1920,1080)
            # driver.save_screenshot("tiki1.png")
        time.sleep(2)
        ActionChains(driver).scroll_by_amount(0,1000).perform()

        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.seller-container")))
            product["seller_name"] = driver.find_element(By.CSS_SELECTOR,"div.seller-name__detail").text
            product["seller_url"] = driver.find_element(By.CSS_SELECTOR,"div.seller-name__detail a").get_attribute("href")

        except Exception as e:
            print(e)
            
            # driver.save_screenshot("tiki2.png")
        ActionChains(driver).scroll_by_amount(0,1000).perform()
        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,".pdp-product-highlights")))
        except Exception as e: 
            print(e)
    
            # driver.save_screenshot("tiki3.png")
        ActionChains(driver).scroll_by_amount(0,1000).perform()

        try: 
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,".pdp-view-more-btn")))
        except Exception as e:
            print(e)
            
            # driver.save_screenshot("tiki4.png")
        ActionChains(driver).scroll_by_amount(0,1000).perform()
            
          
        code_lines=[
            "product[\"product_name\"] = driver.find_element(By.CSS_SELECTOR,\"h1\").text",
            "product[\"product_url\"] = driver.current_url",

            "product[\"current_price\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-price_type_normal\").text",
            "product[\"discount_rate\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-product-price__discount\").text",
            "product[\"original_price\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-price_type_deleted\").text",
                
            "product[\"avg_rating\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-review-summary__stars\").get_attribute(\"innerHTML\")",
            "product[\"number_reviews\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-review-summary__link\").text",
            
            "product[\"brand_name\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-product-brand__brand-link\").text",
            "product[\"brand_url\"] = driver.find_element(By.CSS_SELECTOR,\".pdp-product-brand__brand-link\").get_attribute(\"href\")",
                
        ]
            
        for line in code_lines:
            try:
                exec(line)
            except Exception as e:
                print("error"+line)
                print(e)
                    
        product["product_imgs"]=[]
        try:
            product_imgs=driver.find_elements(By.CSS_SELECTOR,".item-gallery__thumbnail-image")
                
            for img in product_imgs:
                product["product_imgs"].append(img.get_attribute("src"))
            
        except Exception as e:
            print(e)
                 
           
        product["feature"] = []
        try: 
            hightlights=driver.find_elements(By.CSS_SELECTOR,".pdp-product-highlights ul li")
            
            for hightlight in hightlights:
                product["feature"].append(hightlight.text)
        except Exception as e:
                print(e)
            
        product["category"]= []
        try:    
            categories=driver.find_elements(By.CSS_SELECTOR,".breadcrumb_item")
        
            for category in categories:
                product["category"].append(category.text)
        except Exception as e:
                print(e)
            
        try:
            button_more = driver.find_element(By.CSS_SELECTOR,".pdp-view-more-btn")
            button_more.click()
        except Exception as e:
            print(e)
            
        try:
            descripts = driver.find_element(By.CSS_SELECTOR,".detail-content")
            product["description"]=descripts.text
            print(descripts.text)
        except Exception as e:
            print(e)
            
        product["detail"]=[]
        try:
            details=driver.find_elements(By.CSS_SELECTOR,".pdp-general-features ul li")
            for detail in details:
                product["detail"].append(detail.text)
        except Exception as e:
            print(e)
                
            # driver.save_screenshot("tiki5.png")
        ActionChains(driver).scroll_by_amount(0,1000).perform()
        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"button.next-pagination-item")))
        except Exception as e:
            print(e)
            # driver.save_screenshot("tiki6.png")



        review_list_table=[]
        time_start = datetime.now()
        # while True:
        #     if (datetime.now()-time_start).total_seconds() > 10:
        #         print("time out")
        #         break
        #     try:
        #         WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"button.next-pagination-item")))
        #     except Exception as e:
        #         print(e)
                
        try:
            review_list = driver.find_elements(By.CSS_SELECTOR,".mod-reviews .item")
                
            for review in review_list:
                review_table=[]
                # try:
                #     show_more_button = review.find_element(By.CSS_SELECTOR,".show-more-content")
                #     show_more_button.click()
                # except Exception as e:
                #     print(e)
                    
                try:
                    review_table.append(review.find_element(By.CSS_SELECTOR,".top .container-star").get_attribute("innerHTML"))
                except Exception as e :
                    print(e)
                    review_table.append("")
                    
                try:
                    review_table.append(review.find_element(By.CSS_SELECTOR,".item-content .content").text)
                except Exception as e :
                    print(e)
                    review_table.append("")
                    
                    review_img=[]
                    
                try:
                    imgs = review.find_elements(By.CSS_SELECTOR,".review-image__item .image")
                    for img in imgs:
                        review_img.append(img.get_attribute("style"))
                    review_table.append(review_img)
                except :
                    review_table.append([])
                
                # if len(review_list_table)>(self.review_per_page-1) and review_table[1] == review_list_table[len(review_list_table)-(self.review_per_page-1)][1]:
                #     print(review_table[1])
                #     print(review_list_table[len(review_list_table)-(self.review_per_page-1)][1])
                #     break    
                review_list_table.append(review_table)
                    
        except Exception as e:
            print(e) 
            
            
            # try:
            #     next_comment_button = driver.find_element(By.CSS_SELECTOR,"button.next-pagination-item")
            #     next_comment_button.click()
            # except Exception as e:
            #     print("button err")
            #     print(e)
            #     break 
            
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