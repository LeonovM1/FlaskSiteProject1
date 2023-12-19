# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, DateTimeField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired, Regexp
from datetime import datetime


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')  # Добавляем поле remember
    submit = SubmitField('Авторизация')

class UpdateUserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Update')


class FutureDateTime(InputRequired):
    def __init__(self, message=None):
        if not message:
            message = 'Дата и время должны быть в будущем'
        super().__init__(message=message)

    def __call__(self, form, field):
        if field.data and field.data < datetime.now():
            raise ValidationError(self.message)

class CheckoutForm(FlaskForm):
    class Meta:
        csrf = False
    new_address = StringField('Новый адрес', validators=[DataRequired()])
    delivery_time = DateTimeField('Желаемое время доставки', validators=[DataRequired(), FutureDateTime()], format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Оформить заказ')
