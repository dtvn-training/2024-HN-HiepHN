from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

engine = create_engine("mysql://root:1234@localhost/test", echo = True)
Base = declarative_base()
Session = sessionmaker(bind = engine)

class Brand(Base):
    __tablename__= "brand"
    id = Column(Integer, primary_key = True, autoincrement=True)
    brand_url = Column(String)
    brand_name = Column(String)

class Seller(Base):
    __tablename__= "seller"
    id = Column(Integer, primary_key = True, autoincrement=True)
    seller_url = Column(String)
    seller_name = Column(String)
    

session = Session()

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"../Data"))

df_seller = pd.read_csv(os.path.join(target_dir,"./seller.csv"),keep_default_na=False)
df_brand  = pd.read_csv(os.path.join(target_dir,"./brand.csv"),keep_default_na=False)


df_seller['id'] = None
df_brand['id'] = None


for idx,row in df_seller.iterrows():
    # print(df)
    seller = Seller(seller_url=row['seller_url'], seller_name = row['seller_name'])
    try:
        session.add(seller)
        session.commit()

        df_seller.at[idx,'id'] = seller.id
        
    except IntegrityError as e: 
        session.rollback() 
        
        existing_seller = session.query(Seller).filter_by(seller_url=row['seller_url']).first() 
        if existing_seller: 
            df_seller.at[idx,'id'] = existing_seller.id
    except SQLAlchemyError as e: 
        session.rollback() 

for idx,row in df_brand.iterrows():
    # print(df)
    brand = Brand(brand_url=row['brand_url'], brand_name = row['brand_name'])
    try:
        session.add(brand)
        session.commit()

        df_brand.at[idx,'id'] = brand.id
        
    except IntegrityError as e: 
        print(e)
        session.rollback() 
        
        existing_brand = session.query(Brand).filter_by(brand_url=row['brand_url']).first() 
        if existing_brand: 
            df_brand.at[idx,'id'] = existing_brand.id
    except SQLAlchemyError as e:
        print(e) 
        session.rollback() 
                
df_seller[['seller_url','id',]].to_csv(os.path.join(target_dir,"./loaded_seller.csv"),index=False)
df_brand[['brand_url','id']].to_csv(os.path.join(target_dir,"./loaded_brand.csv"),index=False)

















