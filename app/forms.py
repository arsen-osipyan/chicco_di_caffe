from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, \
    EqualTo
from app.models import User, Sort
from flask_login import current_user
from werkzeug.security import check_password_hash


EMPTY_FIELD = "Поле должно быть заполненным"


class LoginForm(FlaskForm):
    username = StringField('Имя:', validators=[DataRequired(EMPTY_FIELD)])
    password = PasswordField('Пароль:', validators=[DataRequired(EMPTY_FIELD)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя:', validators=[DataRequired(EMPTY_FIELD)])
    email = StringField('Почта:', validators=[DataRequired(EMPTY_FIELD), Email("Введите корректный email")])
    password = PasswordField('Пароль:', validators=[DataRequired(EMPTY_FIELD)])
    password2 = PasswordField(
        'Пароль еще раз:', validators=[DataRequired(EMPTY_FIELD), EqualTo('password', "Пароли не совпадают")])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Найден пользователь с таким же именем.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Найден пользователь с такой же почтой.')


class SortForm(FlaskForm):
    title = StringField('Название сорта:', validators=[DataRequired(EMPTY_FIELD)])
    bouquet = StringField('Букет:', validators=[DataRequired(EMPTY_FIELD)])
    description = TextAreaField('Описание:', validators=[DataRequired(EMPTY_FIELD)])
    submit = SubmitField('Добавить')


class RecipeForm(FlaskForm):
    title = StringField('Название рецепта:', validators=[DataRequired(EMPTY_FIELD)])
    sort_id = SelectField("Выберите название кофе:", validators=[DataRequired(EMPTY_FIELD)],
                          choices=Sort.query.all())
    coffee_mass = DecimalField("Масса кофе, г:", validators=[DataRequired(EMPTY_FIELD)])
    water_mass = IntegerField("Масса воды, мл:", validators=[DataRequired(EMPTY_FIELD)])
    water_temp = IntegerField("Температура воды, C:", validators=[DataRequired(EMPTY_FIELD)])
    acidity = IntegerField("Кислотность (оцените сами от 0 до 10):")
    tds = IntegerField("Насыщенность (оцените сами от 0 до 10):")
    grinding = DecimalField("Помол:", validators=[DataRequired(EMPTY_FIELD)])
    body = TextAreaField("Шаги", validators=[DataRequired(EMPTY_FIELD)])
    submit = SubmitField("Добавить")


class EditSort(FlaskForm):
    bouquet = StringField('Букет:', validators=[DataRequired(EMPTY_FIELD)])
    description = TextAreaField('Описание:', validators=[DataRequired(EMPTY_FIELD)])
    submit = SubmitField('Подтвердить')

    def validate_title(self, title):
        if len(Sort.query.filter_by(title = title.data).all()) > 1:
            raise ValidationError("Такой сорт уже зарегистрирован")



class EditRecipe(FlaskForm):
    sort_id = SelectField("Выберите название кофе:", validators=[DataRequired(EMPTY_FIELD)],
                          choices=Sort.query.all())
    coffee_mass = DecimalField("Масса кофе, г:", validators=[DataRequired(EMPTY_FIELD)])
    water_mass = IntegerField("Масса воды, мл:", validators=[DataRequired(EMPTY_FIELD)])
    water_temp = IntegerField("Температура воды, C:", validators=[DataRequired(EMPTY_FIELD)])
    acidity = IntegerField("Кислотность (оцените сами от 0 до 10):")
    tds = IntegerField("Насыщенность (оцените сами от 0 до 10):")
    grinding = DecimalField("Помол:", validators=[DataRequired(EMPTY_FIELD)])
    body = TextAreaField("Шаги", validators=[DataRequired(EMPTY_FIELD)])
    submit = SubmitField("Подтвердить")

class EditProfile(FlaskForm):
    new_pass = PasswordField('Новый пароль:', validators=[DataRequired(EMPTY_FIELD)])
    old_pass = PasswordField('Старый пароль:', validators=[DataRequired(EMPTY_FIELD)])
    submit = SubmitField("Подтвердить")

    def validate_old_pass(self, old_pass):
        hash = User.query.filter_by(id=current_user.id).first().password_hash
        if not check_password_hash(hash, old_pass.data):
            raise ValidationError('Пароль неверен!')


