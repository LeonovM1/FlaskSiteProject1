from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    cart = db.relationship('Cart', backref='User', uselist=False)
    orders = db.relationship('Order', backref='User', lazy=True)

    def is_active(self):
        return True

class ShippingAddress(db.Model):
    __tablename__ = 'Shipping_address'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.User.id'), nullable=False)
    address = db.Column(db.String(200), nullable=False)

class Category(db.Model):
    __tablename__ = 'Category'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    products = db.relationship('Product', backref='Category', lazy=True)

class Product(db.Model):
    __tablename__ = 'Product'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.Category.id'), nullable=False) 
    image_url = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
class Cart(db.Model):
    __tablename__ = 'Cart'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.User.id'))
    items = db.relationship('CartProduct', backref='Cart', lazy=True)

class CartProduct(db.Model):
    __tablename__ = 'Cart_product'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.Cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.Product.id'))
    quantity = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'Order'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.User.id'), nullable=False)
    items = db.relationship('OrderProduct', backref='Order', lazy=True)
    delivery_address = db.Column(db.String(200), nullable=False)
    delivery_time = db.Column(db.DateTime, nullable=False)

class OrderProduct(db.Model):
    __tablename__ = 'Order_product'
    __table_args__ = {'schema': 'FlaskSite'}
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.Order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('FlaskSite.Product.id'))
    quantity = db.Column(db.Integer, nullable=False)

