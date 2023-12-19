# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, DateTimeField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired, Regexp
from datetime import datetime

"""
Этот код определяет формы, используемые в приложении Flask с использованием Flask-WTF и WTForms.
"""

class RegistrationForm(FlaskForm):
    """

    - RegistrationForm - форма регистрации, которая содержит поля для имени пользователя, пароля, подтверждения пароля и кнопки отправки.

    """
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')



class LoginForm(FlaskForm):
    """

    - LoginForm - форма входа, которая содержит поля для имени пользователя, пароля, флажка "запомнить меня" и кнопки отправки.

    """
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')  # Добавляем поле remember
    submit = SubmitField('Авторизация')



class UpdateUserForm(FlaskForm):
    """

    - UpdateUserForm - форма обновления информации пользователя, которая содержит поля для имени пользователя, пароля, подтверждения пароля и кнопки отправки.

    """
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Update')



class FutureDateTime(InputRequired):
    """

    - FutureDateTime - пользовательский валидатор, который проверяет, что введенная дата и время находятся в будущем.

    """
    def __init__(self, message=None):
        if not message:
            message = 'Дата и время должны быть в будущем'
        super().__init__(message=message)

    def __call__(self, form, field):
        if field.data and field.data < datetime.now():
            raise ValidationError(self.message)



class CheckoutForm(FlaskForm):
    """

    - CheckoutForm - форма оформления заказа, которая содержит поля для нового адреса, желаемого времени доставки и кнопки отправки. Эта форма также отключает защиту от межсайтовой подделки запроса (CSRF).

    """
    class Meta:
        csrf = False
    new_address = StringField('Новый адрес', validators=[DataRequired()])
    delivery_time = DateTimeField('Желаемое время доставки', validators=[DataRequired(), FutureDateTime()], format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Оформить заказ')

