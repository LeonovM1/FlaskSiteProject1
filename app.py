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
from datetime import datetime
import re


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

"""

Создание экземпляра класса Flask

Секретный ключ необходим для обеспечения безопасности сессий на стороне клиента. Он используется Flask и его расширениями для криптографической подписи cookies и другой информации.

Установка URI для базы данных SQLAlchemy. Он включает в себя тип базы данных (PostgreSQL), имя пользователя (postgres), пароль (1111), хост (localhost) и имя базы данных (FlaskProject).

Инициализация базы данных с экземпляром приложения

Инициализация движка миграции. Миграции - это способ внесения изменений в схему вашей базы данных без потери данных.

Создание экземпляра класса LoginManager, который используется для управления сессиями пользователей.

Инициализация менеджера входа с экземпляром приложения



"""
#Функция представления, которая обрабатывает вход в систему
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Тестирование подключения БД
@app.route('/testDB')
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


@app.route('/')
def index():
    """

    Эта функция обрабатывает главную страницу ("/") приложения. 
    Она получает все продукты из базы данных, создает список словарей products_with_categories, 
    где каждый словарь содержит информацию о продукте (имя, цена, категория, URL изображения, описание, идентификатор). 
    Затем эта функция возвращает HTML-шаблон 'index.html', передавая в него список продуктов и текущего пользователя.

    """
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
    """

    Эта функция используется Flask-Login для загрузки пользователя из базы данных. 
    Она принимает user_id в качестве аргумента, 
    преобразует его в целое число и выполняет запрос к базе данных для получения пользователя с этим идентификатором. 
    Если пользователь с таким идентификатором существует, он возвращается функцией. 
    Если такого пользователя нет, функция возвращает None.

    """
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт создан! Теперь вы можете авторизоваться', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
"""

Эта функция обрабатывает регистрацию нового пользователя. 
Она создает форму регистрации и, если форма успешно прошла валидацию при отправке, 
генерирует хэшированный пароль, создает нового пользователя с введенным именем пользователя и хэшированным паролем, 
добавляет пользователя в базу данных и делает коммит. 
Затем функция выводит сообщение об успешной регистрации и перенаправляет пользователя на страницу входа. 
Если форма не была отправлена или не прошла валидацию, функция возвращает шаблон 'register.html' с формой регистрации.

"""


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    """

    Эта функция обрабатывает вход пользователя в систему. 
    Она сначала проверяет, есть ли сообщение в cookies. 
    Если есть, она декодирует сообщение и выводит его. 
    Затем функция создает форму входа. 
    Если форма успешно прошла валидацию при отправке, функция ищет пользователя с введенным именем пользователя. 
    Если пользователь существует и введенный пароль совпадает с хэшированным паролем пользователя, 
    функция входит в систему как этот пользователь и перенаправляет на главную страницу, удаляя сообщение из cookies. 
    Если пользователь не найден или пароль не совпадает, функция выводит сообщение об ошибке. 
    Если форма не была отправлена или не прошла валидацию, функция возвращает шаблон 'login.html' с формой входа.

    """
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
    """

    Эта функция обрабатывает страницу аккаунта пользователя.
    Она требует авторизации пользователя.
    Функция получает текущего пользователя и форму обновления информации пользователя.
    Затем она получает все заказы текущего пользователя и для каждого заказа получает все связанные с ним продукты.

    Если метод запроса - POST и форма прошла валидацию, функция проверяет, был ли введен новый пароль.
    Если пароль был введен и он совпадает с подтверждением пароля,
    функция обновляет имя пользователя и пароль в базе данных,
    а затем выводит сообщение об успешном обновлении информации об аккаунте.
    Если пароли не совпадают, функция выводит сообщение об ошибке.

    Если пароль не был введен, функция просто обновляет имя пользователя и выводит сообщение об успешном обновлении имени пользователя.

    Наконец, функция возвращает шаблон 'account.html', передавая в него текущего пользователя, форму и заказы.

    """
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
    """

    Эта функция обрабатывает запрос на получение изображения продукта.
    Она принимает идентификатор продукта из параметров запроса,
    затем использует этот идентификатор для получения продукта из базы данных.
    Если продукт существует и у него есть URL изображения,
    функция декодирует данные изображения из base64 и возвращает их как файл.
    Если продукт не существует или у него нет URL изображения,
    функция возвращает сообщение об ошибке "Изображение не найдено"

    """
    product_id = request.args.get('productId')
    product = get_product_by_id(product_id)  # ваша функция для получения продукта
    if product and product.image_url:
        image_data = base64.b64decode(product.image_url)
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
    else:
        return 'Изображение не найдено'
    


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """

    Эта функция обрабатывает добавление продукта в корзину.
    Она принимает идентификатор продукта в качестве параметра маршрута.
    Если пользователь не авторизован, функция возвращает JSON-ответ с сообщением об ошибке и статусом 401.
    Если пользователь авторизован, функция ищет продукт по идентификатору и корзину текущего пользователя.
    Если корзины не существует, она создает новую. Затем функция ищет продукт в корзине.
    Если продукт уже есть в корзине, она увеличивает его количество на 1.
    Если продукта нет в корзине, она добавляет новый элемент в корзину с количеством 1.
    После этого функция сохраняет изменения в базе данных и перенаправляет пользователя на страницу корзины.

    """
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
    """

    Эта функция обрабатывает страницу корзины пользователя.
    Она требует авторизации пользователя. Функция получает корзину текущего пользователя.
    Если корзина существует, она получает все товары в корзине.
    Если корзины не существует, она создает пустой список товаров.
    Наконец, функция возвращает шаблон 'cart.html', передавая в него список товаров в корзине.

    """
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        cart_items = CartProduct.query.filter_by(cart_id=cart.id).all()
    else:
        cart_items = []
    return render_template('cart.html', cart_items=cart_items)



@app.route('/clear_cart', methods=['GET','POST'])
def clear_cart():
    """

    Эта функция обрабатывает очистку корзины пользователя.
    Если метод запроса - GET, функция просто перенаправляет пользователя обратно на страницу корзины.
    Если пользователь не авторизован, функция возвращает JSON-ответ с сообщением об ошибке и статусом 401.
    Если пользователь авторизован, функция ищет корзину текущего пользователя.
    Если корзина существует, функция удаляет все товары из корзины,
    сохраняет изменения в базе данных и перенаправляет пользователя обратно на страницу корзины.

    """
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



def validate_date(date_text):
    """

    Эта функция проверяет, соответствует ли введенная дата формату 'YYYY-MM-DD HH:MM:SS'.
    Она принимает строку с датой и временем, проверяет ее с помощью регулярного выражения,
    а затем пытается преобразовать ее в объект datetime.
    Если строка не соответствует формату или не может быть преобразована в datetime,
    функция вызывает исключение ValueError с сообщением 'Неверный формат даты'.
    Если все проверки прошли успешно, функция возвращает True.

    """
    if not re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_text):
        raise ValueError('Неверный формат даты')
    try:
        datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        raise ValueError('Неверный формат даты')


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """

    Эта функция обрабатывает процесс оформления заказа.
    Она требует авторизации пользователя и использует форму CheckoutForm.
    Если форма успешно прошла валидацию при отправке, функция получает время доставки и адрес доставки из формы.

    Если время доставки или адрес доставки не указаны, функция выводит сообщение об ошибке.
    В противном случае, функция проверяет, соответствует ли время доставки формату 'YYYY-MM-DD HH:MM:SS'с помощью функции validate_date.
    Если время доставки не соответствует этому формату,
    функция выводит сообщение об ошибке и возвращает шаблон 'checkout.html'.

    Если все проверки прошли успешно,
    функция создает новый заказ с указанным временем доставки и адресом доставки,
    и сохраняет его в базе данных. Затем функция получает корзину текущего пользователя и переносит все товары из корзины в заказ.
    После этого функция удаляет все товары из корзины и сохраняет изменения в базе данных.

    Наконец, функция выводит сообщение об успешном оформлении заказа и перенаправляет пользователя на страницу аккаунта.
    Если форма не была отправлена или не прошла валидацию, функция возвращает шаблон 'checkout.html'.

    """
    form = CheckoutForm()

    if form.validate_on_submit():
        delivery_time_str = form.delivery_time.data.strftime('%Y-%m-%d %H:%M:%S')
        delivery_address = form.new_address.data

        if not delivery_time_str or not delivery_address:
            flash('Все поля обязательны для заполнения', 'danger')
        else:
            try:
                validate_date(delivery_time_str)
                delivery_time_str = datetime.strptime(delivery_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                flash('Форма даты заполнена не правильно: дата и время не могут быть меньше или равны текущим', 'danger')
                return render_template('checkout.html', title='Оформление заказа', form=form)

        order = Order(user_id=current_user.id, delivery_address=delivery_address, delivery_time=delivery_time_str)
        db.session.add(order)
        db.session.commit()
        
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            cart_products = CartProduct.query.filter_by(cart_id=cart.id).all()
            for item in cart_products:
                order_product = OrderProduct(product_id=item.product_id, quantity=item.quantity, order_id=order.id)
                db.session.add(order_product)
                db.session.delete(item)
            db.session.commit()

        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            CartProduct.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()

        order = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).first()
        if order:
            print(f'Заказ {order.id} был успешно создан для пользователя {current_user.id}')
        else:
            print('Заказ не был создан')
            # Возможно, вам стоит добавить здесь обработку ошибки

        flash('Ваш заказ успешно оформлен!', 'success')
        return redirect(url_for('account'))
    return render_template('checkout.html', title='Оформление заказа', form=form)




class MyAdminIndexView(AdminIndexView):
    """

    Этот код настраивает административный интерфейс Flask-Admin для приложения.

    MyAdminIndexView - это пользовательский класс, который наследуется от 
    AdminIndexView и переопределяет метод is_accessible для ограничения доступа к административному интерфейсу 
    только для аутентифицированных пользователей, которые являются администраторами. 
    Если пользователь не имеет доступа, он будет перенаправлен на главную страницу.
    
    """
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index', next=request.url))
    
admin = Admin(app, name='ElectroShop', template_mode='bootstrap3', index_view=MyAdminIndexView())


class UserModelView(ModelView):
    """
    
    UserModelView- это пользовательский класс, 
    который наследуется от ModelView и переопределяет метод is_accessible таким же образом, как и MyAdminIndexView.

    """
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin.add_view(UserModelView(User, db.session))

class OrderModelView(ModelView):
    """
    
    OrderModelView также определяет пользовательские метки для столбцов в представлении модели.
    
    """
    column_labels = {
        'Is_confirmed': 'Подтверждение'
    }
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin.add_view(OrderModelView(Order, db.session))

class ProductModelView(ModelView):
    """
    
    ProductModelView переопределяет форму для поля image_url, используя FileUploadField, 
    и определяет метод on_model_change, который кодирует изображение в base64 при его загрузке.
    
    В конце каждый из этих представлений модели добавляется в административный интерфейс с помощью метода add_view.
    """
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
ВСЁ ЧТО НАХОДИТСЯ НИЖЕ, НЕ УЧАВСТВУЕТ В ПРОГРАММЕ

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
        