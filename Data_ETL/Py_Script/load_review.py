from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import pandas as pd
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

session = Session()

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"../Data"))

df = pd.read_csv(os.path.join(target_dir,"./review.csv"),encoding='latin-1')

df['review_id'] = None
for idx,row in df.iterrows():
    # print(df)
    review = Review(product_id = row["product_id"], rating = row["rating"], content=row["content"])

    try:
        # session.add()
        # session.commit()

        # df.at[idx,'review_id'] = review.id
        review_imgs = df.at[idx,'img'].split(',')
        print(review_imgs)
        
    except IntegrityError as e: 
        session.rollback() 














