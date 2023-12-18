import base64
from flask import Flask, render_template, url_for, flash, redirect, send_file, request, g, jsonify, make_response, abort
from flask_migrate import Migrate
from forms import RegistrationForm, LoginForm, UpdateUserForm, CheckoutForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Category, Product, CartProduct, Cart, ShippingAddress, OrderProduct, Order
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import io
import requests
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost/FlaskProject'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Вы должны войти в систему'
login_manager.login_message_category = 'warning'
#Функция представления, которая обрабатывает вход в систему

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Тестирование подключения БД
@app.route('/')
def hello_world():
    with app.app_context():
        db.create_all()
        table_names = db.metadata.tables.keys()
        test_name = db.metadata.info.items()
    return str(table_names)

#with app.app_context():
    # Удаление пользователя из базы данных (например, по его идентификатору)
    User.query.filter_by(id=1).delete()
    db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.context_processor
def inject_user():
    user = current_user
    return dict(user=user)


@app.before_request
def before_request():
    g.user = current_user


@app.route('/index')
def index():
    products_with_categories = []
    products = Product.query.all()
    for product in products:
        product_with_category = {
            'name': product.name,
            'price': product.price,
            'category': product.Category.name,  # Обновленное обращение к отношению
            'image_url': product.image_url,
            'description': product.description,
            'id': product.id
        }
        products_with_categories.append(product_with_category)
    return render_template('index.html', products=products_with_categories, user=current_user)  # Передача текущего пользователя в шаблон


#Страница с контактами
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Регистрация
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт создан! Теперь вы можете авторизоваться', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.cookies.get('message')
    if message:
        message = base64.b64decode(message).decode('utf-8')
        flash(message, 'warning')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            response = make_response(redirect(url_for('index')))
            response.set_cookie('message', '', expires=0)
            return response
        else:
            flash('Авторизация невозможна! Пожалуйста, проверьте имя пользователя и\или пароль!', 'danger')
    return render_template('login.html', title='Login', form=form, user=current_user)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    form = UpdateUserForm(obj=user)

    orders = Order.query.filter_by(user_id=current_user.id).all()
    for order in orders:
        order.items = OrderProduct.query.filter_by(order_id=order.id).all()
        for item in order.items:
            item.product = Product.query.get(item.product_id)

    if request.method == 'POST':
        if form.validate():
            if form.password.data:
                if form.password.data == form.confirm_password.data:
                    user.username = form.username.data
                    user.password = generate_password_hash(form.password.data)
                    db.session.commit()
                    flash('Информация об аккаунте обновлена', 'success')
                else:
                    flash('Пароли не совпадают', 'danger')
            else:
                user.username = form.username.data
                db.session.commit()
                flash('Имя пользователя обновлено', 'success')
        else:
            flash('Пароли не совпадают', 'danger')

    orders = user.orders
    return render_template('account.html', title='Account', user=user, form=form, orders=orders)


def get_product_by_id(id):
    if id:
        return Product.query.get(id)
    else:
        return None


@app.route('/get-product-image')
def get_product_image():
    product_id = request.args.get('productId')
    product = get_product_by_id(product_id)  # ваша функция для получения продукта
    if product and product.image_url:
        image_data = base64.b64decode(product.image_url)
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
    else:
        return 'Изображение не найдено'
    

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not current_user.is_authenticated:
        response = jsonify({'message': 'Вы должны войти в систему, чтобы добавить товар в корзину.'})
        response.status_code = 401
        return response
    product = Product.query.get_or_404(product_id)
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
    cart_item = CartProduct.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartProduct(cart_id=cart.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('cart'))


#Страница корзины
@app.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        cart_items = CartProduct.query.filter_by(cart_id=cart.id).all()
    else:
        cart_items = []
    return render_template('cart.html', cart_items=cart_items)


@app.route('/clear_cart', methods=['GET','POST'])
def clear_cart():
    if request.method == 'GET':
        return redirect(url_for('cart'))
    if not current_user.is_authenticated:
        response = jsonify({'message': 'Вы должны войти в систему, чтобы добавить товар в корзину.'})
        response.status_code = 401
        return response
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        CartProduct.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    formdata = request.form if request.method == 'POST' else None
    form = CheckoutForm(formdata)
    if form.validate_on_submit():
        delivery_address = form.new_address.data  # всегда берем адрес из формы
        order = Order(user_id=current_user.id, delivery_address=delivery_address, delivery_time=form.delivery_time.data)
        db.session.add(order)
        db.session.commit()
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            cart_products = CartProduct.query.filter_by(cart_id=cart.id).all()
            for item in cart_products:
                order_product = OrderProduct(product_id=item.product_id, quantity=item.quantity, order_id=order.id)  # используем id заказа
                db.session.add(order_product)
                db.session.delete(item)
            db.session.commit()
        #flash('Ваш заказ успешно оформлен!', 'success',)

        # очистка корзины
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            CartProduct.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()

        # Проверка, что заказ был создан
        order = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).first()
        if order:
            print(f'Заказ {order.id} был успешно создан для пользователя {current_user.id}')
        else:
            print('Заказ не был создан')
            # Возможно, вам стоит добавить здесь обработку ошибки

        return redirect(url_for('account'), code=302)
    else:
        flash("Ошибка в поле Новый адрес: Введите корректный адрес", 'danger')
        flash("Ошибка в поле Желаемое время доставки: Укажите корректную дату, как в шаблоне", 'danger')
    return render_template('checkout.html', title='Оформление заказа', form=form)


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index', next=request.url))
    
admin = Admin(app, name='ElectroShop', template_mode='bootstrap3', index_view=MyAdminIndexView())

class OrderModelView(ModelView):
    column_labels = {
        'Is_confirmed': 'Подтверждение'
    }
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin.add_view(OrderModelView(Order, db.session))

class ProductModelView(ModelView):
    form_overrides = {
        'image_url': FileUploadField
    }

    def on_model_change(self, form, model, is_created):
        if form.image_url.data:
            image_data = form.image_url.data.read()
            model.image_url = base64.b64encode(image_data).decode('utf-8')
        return super().on_model_change(form, model, is_created)
    
admin.add_view(ProductModelView(Product, db.session))


"""

descriptions = [
    "Умные часы XYZ предлагают стильный дизайн и широкий спектр функций, включая отслеживание активности, уведомления о звонках и сообщениях, и возможность управления музыкой.",
    "Беспроводные наушники ABC обеспечивают кристально чистый звук и комфортное ношение. Совместимы с различными устройствами и обладают длительным временем работы от батареи.",
    "Электронная книга E-Read предлагает удобное чтение в любом месте. Легкая, с длительным временем работы от батареи и возможностью хранения тысяч книг.",
    "Фитнес-браслет FitBand поможет отслеживать вашу физическую активность, сердечный ритм и качество сна. Стильный и удобный для повседневного использования.",
    "Портативная колонка SoundBox обеспечивает мощный звук и беспроводное подключение. Компактный дизайн и длительное время работы от аккумулятора делают ее идеальным выбором для музыки в движении.",
    "Внешний жесткий диск 1ТБ предлагает большое пространство для хранения данных, быструю передачу файлов и надежное резервное копирование. Идеальное решение для хранения и защиты ваших ценных файлов."
]



with app.app_context():

    with app.app_context():
    
    # Получаем список всех продуктов
    products = Product.query.all()
    # Обновляем каждый продукт с соответствующим описанием
    for i, product in enumerate(products):
        product.description = descriptions[i]

    # Сохраняем изменения в базе данных
    db.session.commit()


    categories =[
        Category(name='Умные часы и браслеты'),
        Category(name='Аудио оборудование'),
        Category(name='Электронные книги'),
        Category(name='Портативная акустика'),
        Category(name='Аксессуары для ПК')
    ]


    for category in categories:
        if not Category.query.filter_by(name=category.name).first():
            db.session.add(category)

    db.session.commit()


    def save_product_to_db(name, price, image_path, category_id):
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            new_product = Product(name=name, price=price, image_url=image_data, category_id=category_id)
            db.session.add(new_product)
            db.session.commit()

    # Список продуктов с их изображениями
    products = [
        {'name': 'Умные часы XYZ', 'category_id': 1, 'price': 9999.99, 'image_path': 'img/SmartWatch.jpg'},
        {'name': 'Беспроводные наушники ABC', 'category_id': 2, 'price': 4999.50, 'image_path': 'img/TWS.jpg'},
        {'name': 'Электронная книга E-Read', 'category_id': 3, 'price': 7999.00, 'image_path': 'img/E-Read.jpg'},
        {'name': 'Фитнес-браслет FitBand', 'category_id': 1, 'price': 2999.99, 'image_path': 'img/FitBand.jpg'},
        {'name': 'Портативная колонка SoundBox', 'category_id': 4, 'price': 2599.99, 'image_path': 'img/SoundBox.jpg'},
        {'name': 'Внешний жесткий диск 1ТБ', 'category_id': 5, 'price': 4599.99, 'image_path': 'img/HardDiskDrive.jpg'}
    ]

    # Заполнение таблицы products в базе данных
    for product in products:
        save_product_to_db(product['name'], product['price'], product['image_path'], product['category_id'])

"""
        
if __name__ == '__main__':
    app.run(debug=True)
        