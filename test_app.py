import unittest
from flask_login import login_user
from app import app, db, User, Product, Cart, CartProduct
from werkzeug.security import generate_password_hash, check_password_hash
import random, time

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            user = User.query.filter_by(username="test").first()
            if user:
                cart = Cart.query.filter_by(user_id=user.id).first()
                if cart:
                    CartProduct.query.filter_by(cart_id=cart.id).delete()
                Cart.query.filter_by(user_id=user.id).delete()
                User.query.filter_by(username="test").delete()
                db.session.commit()
            db.session.remove()
        super().tearDown()

    def test_user_registration(self):
        username = "test" + str(int(time.time() * 1000))
        response = self.app.post('/register', data=dict(username=username, password="test", confirm_password="test"))
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            user = User.query.filter_by(username=username).first()
        self.assertIsNotNone(user)

    def test_user_login(self):
        with app.app_context():
            user = User.query.filter_by(username="test").first()
            if user:
                db.session.delete(user)
                db.session.commit()
            hashed_password = generate_password_hash("test")
            user = User(username="test", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            with app.test_request_context():
                login_user(user)
            response = self.app.post('/login', data=dict(username="test", password="test"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        with app.app_context():
            user = User.query.filter_by(username="test").first()
            if user:
                db.session.delete(user)
                db.session.commit()
            hashed_password = generate_password_hash("test")
            user = User(username="test", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            product = Product(name="test_product", price=100.0, image_url="test_url", category_id=1)
            db.session.add(product)
            db.session.commit()
            with app.test_request_context():
                login_user(user)
            response = self.app.post('/add_to_cart/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_clear_cart(self):
        with app.app_context():
            user = User.query.filter_by(username="test").first()
            if user:
                db.session.delete(user)
                db.session.commit()
            hashed_password = generate_password_hash("test")
            user = User(username="test", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            with app.test_request_context():
                login_user(user)
            response = self.app.post('/clear_cart', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        with app.app_context():
            user = User.query.filter_by(username="test").first()
            if user:
                db.session.delete(user)
                db.session.commit()
            hashed_password = generate_password_hash("test")
            user = User(username="test", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            with app.test_request_context():
                login_user(user)
            response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()