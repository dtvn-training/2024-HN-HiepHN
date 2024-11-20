from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
import os


engine = create_engine("mysql://root:1234@localhost/test", echo = True)
Base = declarative_base()
Session = sessionmaker(bind = engine)

class Review(Base):
    __tablename__= "review"
    id = Column(Integer, primary_key = True, autoincrement=True)
    product_id = Column(Integer)
    rating = Column(Float)
    content = Column(String)
    
class ReviewImg(Base):
    __tablename__= "review_img"
    id= Column(Integer, primary_key = True, autoincrement=True)
    review_id = Column(Integer)
    img_link = Column(String)

session = Session()

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"../Data"))

df = pd.read_csv(os.path.join(target_dir,"./review.csv"),encoding='utf8',na_filter=False)


df['review_id'] = None
print(df)
for idx,row in df.iterrows():
    # print(df)
    review = Review(product_id = row["product_id"], rating = row["rating"], content=row["content"])

    try:
        session.add(review)
        session.commit()

        df.at[idx,'review_id'] = review.id
        if df.at[idx,'img'] != '':
            review_imgs = df.at[idx,'img'].split(';')
            for img in review_imgs:
                review_img = ReviewImg(review_id=df.at[idx,'review_id'],img_link=img)
                try:
                    session.add(review_img)
                    session.commit()
                except SQLAlchemyError as e: 
                    session.rollback()

                
        
    except SQLAlchemyError as e: 
        session.rollback() 
   













