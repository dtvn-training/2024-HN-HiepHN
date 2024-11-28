from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql://root:1234@localhost/test", echo = True)
Base = declarative_base()
Session = sessionmaker(bind = engine)

product_category_association = Table(
    'product_category',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


class Seller(Base):
    __tablename__ = "seller"
    id = Column(Integer, primary_key = True, autoincrement=True)
    seller_url = Column(String, unique=True)
    seller_name = Column(String)
    
    products = relationship("Product", back_populates = "seller")
    
    @classmethod
    def get_or_create(cls, session, dict):
        seller = session.query(cls).filter_by(seller_url = dict["seller_url"]).first()
        if not seller:
            seller = cls(seller_url = dict["seller_url"], seller_name = dict["seller_name"])
            session.add(seller)
        
        return seller
        
    
class Brand(Base):
    __tablename__ = "brand"
    id = Column(Integer, primary_key = True, autoincrement=True)
    brand_url = Column(String, unique=True)
    brand_name = Column(String)
    
    products = relationship("Product", back_populates="brand")
    
    @classmethod
    def get_or_create(cls, session, dict):
        brand = session.query(cls).filter_by(brand_url = dict["brand_url"]).first()
        if not brand:
            brand = cls(brand_url = dict["brand_url"], brand_name = dict["brand_name"])
            session.add(brand)
        
        return brand
    

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key = True, autoincrement = True)
    product_name = Column(String)
    product_url = Column(String, unique=True)
    seller_id = Column(Integer, ForeignKey('seller.id'))
    brand_id = Column(Integer, ForeignKey("brand.id"))
    number_sold = Column(Integer)
    avg_rating = Column(Float)
    number_reviews = Column(Integer)
    descript = Column(String)
    source = Column(String)
    
    seller = relationship("Seller", back_populates = "products")
    brand  = relationship("Brand", back_populates = "products")
    
    imgs = relationship("Img", back_populates = "product")
    price = relationship("Price", back_populates = "product")
    reviews = relationship("Review", back_populates = "product")
    
    categories = relationship("Category", secondary = product_category_association, back_populates = "products")
    
    @classmethod
    def get_or_create(cls, session, dict):
        product = session.query(cls).filter_by(product_url = dict["product_url"]).first()
        if not product:
            product = cls(product_name = dict["product_name"], product_url = dict["product_url"], seller = dict["seller"],brand = dict["brand"], number_sold = dict["number_sold"],
                        avg_rating = dict["avg_rating"], number_reviews = dict["number_reviews"], descript = dict["descript"], source = dict["source"])
            session.add(product)
        
        return product
    
    
class Img(Base):
    __tablename__  = "img"
    id = Column(Integer, primary_key= True, autoincrement=True)
    img_url = Column(String, unique=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    
    product = relationship("Product", back_populates="imgs")
    
    @classmethod
    def get_or_create(cls, session, dict):
        img = session.query(cls).filter_by(img_url = dict["img_url"]).first()
        if not img:
            img = cls(img_url = dict["img_url"], product = dict["product"])
            session.add(img)
        
        return img
    
    
class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key = True, autoincrement = True)
    product_id = Column(Integer, ForeignKey("product.id"))
    original_price = Column(Integer)
    current_price = Column(Integer)
    discounted_rate = Column(Integer)
    
    product = relationship("Product", back_populates = "price")
    
    @classmethod
    def create(cls, session, dict):
        
        price = cls(product = dict["product"], original_price = dict["original_price"],current_price = dict["current_price"],discounted_rate = dict["discounted_rate"])
        session.add(price)
        
        return price
    
    
class Review(Base):
    __tablename__ = "review"
    id = Column(Integer, primary_key = True, autoincrement = True)
    product_id = Column(Integer, ForeignKey("product.id"))
    rating = Column(Float)
    content = Column(String)
    
    product = relationship("Product", back_populates = "reviews")
    review_imgs = relationship("Review_Img", back_populates = "review")
    
    @classmethod
    def create(cls, session, dict):
        
        review = cls(product = dict["product"], rating = dict["rating"], content = dict["content"])
        session.add(review)
        
        return review
    
    
class Review_Img(Base): 
    __tablename__ = "review_img"
    id = Column(Integer, primary_key = True, autoincrement = True)
    review_id = Column(Integer, ForeignKey("review.id"))
    img_url = Column(String, unique = True)
    
    review = relationship("Review", back_populates = "review_imgs")
    
    @classmethod
    def get_or_create(cls, session, dict):
        review_img = session.query(cls).filter_by(img_url = dict["review_img_url"]).first()
        if not review_img:
            review_img = cls(img_url = dict["review_img_url"], review = dict["review"])
            session.add(review_img)
        
        return review_img
    

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key = True, autoincrement = True)
    category = Column(String, unique = True)
    
    products = relationship("Product", secondary = product_category_association, back_populates = "categories")

    
    @classmethod
    def get_or_create(cls, session, dict):
        category = session.query(cls).filter_by(category = dict["category"]).first()
        if not category:
            category = cls(category = dict["category"])
            session.add(category)
        
        return category

