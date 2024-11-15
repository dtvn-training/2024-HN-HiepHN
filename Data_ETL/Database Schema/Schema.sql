create table seller (id bigint,seller_url varchar(255) unique, seller_name varchar(255), primary key (id));

create table brand (id bigint, brand_url varchar(255) unique, brand_name varchar(255), primary key (id)) ;

create table category (id bigint, category varchar(255), primary key (id));

create table product (id bigint, product_name varchar(255), seller_id bigint, brand_id  bigint, product_url varchar(500) unique, number_sold bigint,
avg_rating float, number_reviews bigint, descript text, source varchar(255), primary key(id), foreign key(seller_id) references seller(id),
foreign key(brand_id) references brand(id));

create table img (id bigint, product_id bigint, img_link varchar(255), foreign key(product_id) references product(id));

create table price (id bigint, product_id bigint, original_price bigint, current_price bigint, discounted_rate bigint, primary key(id),
foreign key(product_id) references product(id));

create table product_category (product_id bigint, category_id bigint, foreign key(product_id) references product(id), foreign key(category_id) references category(id));

create table review (id bigint, product_id bigint, rating float, content text, primary key(id), foreign key (product_id) references product(id));

create table review_img(id bigint, review_id bigint, img_link varchar(255), primary key(id), foreign key(review_id) references review(id));