from __init__ import Session
from __init__ import Seller, Brand, Product, Img, Price, Review, ReviewImg, Category
import os
import pandas as pd

session=Session()

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"../Data"))

df = pd.read_csv(os.path.join(target_dir,"./transformed_data.csv"),keep_default_na=False)

for idx, row in df.iterrows():
    seller_dict=dict(seller_url=row["seller_url"],seller_name=row["seller_name"])
    seller=Seller.get_or_create(session,seller_dict)
    
    brand_dict=dict(brand_url=row["brand_url"],brand_name=row["brand_name"])
    brand=Brand.get_or_create(session,brand_dict)
    
    product_dict=dict(product_name=row["product_name"],product_url=row["product_url"],seller=seller,brand=brand,number_sold=row["number_sold"]
                      ,avg_rating=row["avg_rating"],number_reviews=row["number_reviews"],descript=row["descript"],source=row["source"])
    product=Product.get_or_create(session,product_dict)
    
    for product_img in row["product_imgs"].split(","):
        img_dict=dict(product=product,img_url=product_img)
        img = Img.get_or_create(session,img_dict)
    
    price_dict=dict(product=product,original_price=row["original_price"],current_price=row["current_price"],discounted_rate=row["discount_rate"])
    price=Price.create(session,price_dict)
    
    for review in row["review"].split("|"):
        if not review:
            continue
        [rating,content,review_imgs]=review.split("++")
        review_dict = dict(product=product,rating=rating,content=content)
        review = Review.create(session,review_dict)
        
        for review_img in review_imgs.split(";"):
            if review_img.strip():
                review_img_dict=dict(review=review,review_img_url=review_img)
                review_img = ReviewImg.get_or_create(session,review_img_dict)
    
    for category in row["category"].split(";;"):
        if not category:
            continue
        
        category_dict = dict(category=category)  
        category= Category.get_or_create(session,category_dict)
        
        product.categories.append(category)
        # category.products.append(product)
    session.commit()
