from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os


engine = create_engine("mysql://root:1234@localhost/test", echo = True)
Base = declarative_base()
Session = sessionmaker(bind = engine)

class Product(Base):
    __tablename__= "product"
    id = Column(Integer, primary_key = True, autoincrement=True)
    product_name = Column(String)
    seller_id = Column(Integer)
    brand_id = Column(Integer)
    product_url = Column(String)
    number_sold = Column(Integer)
    avg_rating = Column(Float)
    number_reviews = Column(Integer)
    descript = Column(String)
    source = Column(String)

session = Session()

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"../Data"))

df = pd.read_csv(os.path.join(target_dir,"./product.csv"),encoding="utf-8")

df['id'] = None
for idx,row in df.iterrows():
    # print(df)
    product = Product(product_name=row["product_name"],seller_id=row["seller_id"],brand_id=row["brand_id"],product_url=row["product_url"],number_sold=row["number_sold"],
                      avg_rating=row["avg_rating"],number_reviews=row["avg_rating"],descript=row["descript"],source=row["source"])

    try:
        session.add(product)
        session.commit()

        df.at[idx,'id'] = product.id
        
    except IntegrityError as e: 
        session.rollback() 
        
        existing_product = session.query(Product).filter_by(product_url=row['product_url']).first() 
        if existing_product: 
            df.at[idx,'id'] = existing_product.id
    except SQLAlchemyError as e: 
        session.rollback() 
                        
df[['id','product_url',]].to_csv(os.path.join(target_dir,"./loaded_product.csv"),index=False)

















