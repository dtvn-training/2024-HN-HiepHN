from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os


engine = create_engine("mysql://root:1234@localhost/test", echo = True)
Base = declarative_base()
Session = sessionmaker(bind = engine)

class Category(Base):
    __tablename__= "category"
    id = Column(Integer, primary_key = True, autoincrement=True)
    category = Column(String)
    
    
class ProductCategory(Base):
    __tablename__ = "product_category"
    product_id = Column(Integer, primary_key = True)
    category_id = Column(Integer)

session = Session()

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"../Data"))

df = pd.read_csv(os.path.join(target_dir,"./category.csv"),encoding="utf-8",sep=";")

df['category_id'] = None
for idx,row in df.iterrows():
    # print(df)r
    category = Category(category = row['category'])

    try:
        session.add(category)
        session.commit()

        df.at[idx,'category_id'] = category.id
        
    except IntegrityError as e: 
        session.rollback() 
        
        existing_category = session.query(Category).filter_by(category=row['category']).first() 
        if existing_category: 
            df.at[idx,'category_id'] = existing_category.id
    except SQLAlchemyError as e: 
        session.rollback() 
    
    product_category = ProductCategory(product_id=row['id'],category_id=df.at[idx,'category_id'])
    
    try:
        session.add(product_category)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
                        

















