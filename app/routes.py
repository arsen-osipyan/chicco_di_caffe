from flask import render_template, flash, redirect, url_for, request, g
from app import app, db
from app.forms import LoginForm, RegistrationForm, \
    RecipeForm, SortForm, EditSort, EditRecipe, EditProfile
from flask_login import current_user, login_user, \
    logout_user, login_required
from app.models import User, Sort, Recipe
from werkzeug.urls import url_parse
from config import Config
from werkzeug.security import generate_password_hash


@app.route('/')
@app.route('/index')
def index():
    sorts = Sort.query.order_by(Sort.timestamp).all()[::-1]
    recipes = Recipe.query.order_by(Recipe.timestamp).all()[::-1]
    return render_template('index.html', title='Главная', sorts=sorts, recipes=recipes, ADMIN_EMAILS=Config.ADMINS)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Имя пользователя или пароль некорректны.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Войти', form=form, ADMIN_EMAILS=Config.ADMINS)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=False)
        return redirect(url_for('index'))
    return render_template('register.html', title='Регистрация', form=form, ADMIN_EMAILS=Config.ADMINS)


@app.route('/new_sort', methods=['GET', 'POST'])
@login_required
def new_sort():
    if current_user.email not in app.config["ADMINS"]:
        flash('[ACCESS DENIED]')
        return redirect(url_for('index'))
    form = SortForm()
    if form.validate_on_submit():
        sort = Sort(title=form.title.data,
                    user_id=current_user.id,
                    bouquet=form.bouquet.data,
                    description=form.description.data)
        db.session.add(sort)
        db.session.commit()
        flash('Новый сорт добавлен!')
        return redirect(url_for('index'))
    return render_template('sort_form.html', title='Новый сорт', form=form, ADMIN_EMAILS=Config.ADMINS)


@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data,
                        user_id=current_user.id,
                        sort_id=Sort.query.filter_by(title=str(form.sort_id.data)).first().id,
                        coffee_mass=form.coffee_mass.data,
                        water_mass=form.water_mass.data,
                        water_temp=form.water_temp.data,
                        grinding=form.grinding.data,
                        acidity=form.acidity.data,
                        tds=form.tds.data,
                        body=form.body.data)
        db.session.add(recipe)
        db.session.commit()
        flash('Новый рецепт добавлен!')
        return redirect(url_for('index'))
    return render_template('recipe_form.html', title='Новый рецепт', form=form, ADMIN_EMAILS=Config.ADMINS)


@app.route('/user/<user_id>')
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    recipes = Recipe.query.filter_by(user_id=user_id)
    return render_template('user.html', user=user, recipes=recipes, ADMIN_EMAILS=Config.ADMINS)


@app.route('/sort/<sort_id>')
def sort(sort_id):
    s = Sort.query.filter_by(id=sort_id).first_or_404()
    u = User.query.filter_by(id=s.user_id).first()
    r = Recipe.query.filter_by(sort_id=sort_id).all()
    return render_template('sort.html', sort=s, user=u, recipes=r, ADMIN_EMAILS=Config.ADMINS)


@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    r = Recipe.query.filter_by(id=recipe_id).first_or_404()
    u = User.query.filter_by(id=r.user_id).first()
    s = Sort.query.filter_by(id=r.sort_id).first()
    other = Recipe.query.filter_by(sort_id=s.id).all()
    return render_template('recipe.html', recipe=r, sort=s, user=u, other=other, ADMIN_EMAILS=Config.ADMINS)


@app.route('/database')
@login_required
def database():
    if current_user.email not in app.config["ADMINS"]:
        flash('[ACCESS DENIED]')
        return redirect(url_for('index'))
    else:
        users = User.query.all()
        recipes = Recipe.query.all()
        sorts = Sort.query.all()
        return render_template('database.html', users=users, recipes=recipes, sorts=sorts, ADMIN_EMAILS=Config.ADMINS)


@app.route('/delete_user/<user_id>')
@login_required
def delete_user(user_id):
    if current_user.email not in app.config["ADMINS"]:
        flash('[ACCESS DENIED]')
        return redirect(url_for('index'))
    user = User.query.filter_by(id=user_id).first()
    for sort in Sort.query.filter_by(user_id=user.id).all():
        db.session.delete(sort)
        db.session.commit()
    for recipe in Recipe.query.filter_by(user_id=user.id).all():
        db.session.delete(recipe)
        db.session.commit()
    flash('Пользователь \"{}\" (id: {}) удален.'.format(user.username, user.id))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('database'))


@app.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if current_user.email not in app.config["ADMINS"] and current_user.id != recipe.user_id:
        flash('[ACCESS DENIED]')
        return redirect(url_for('index'))
    flash('Рецепт \"{}\" (id: {}) удален'.format(recipe.title, recipe.id))
    db.session.delete(recipe)
    db.session.commit()
    if current_user.id == recipe.user_id:
        return redirect(url_for('user', user_id = current_user.id))
    return redirect(url_for('database'))


@app.route('/delete_sort/<sort_id>')
@login_required
def delete_sort(sort_id):
    if current_user.email not in app.config["ADMINS"]:
        flash('[ACCESS DENIED]')
        return redirect(url_for('index'))
    sort = Sort.query.filter_by(id=sort_id).first()
    for recipe in Recipe.query.filter_by(sort_id=sort.id).all():
        db.session.delete(recipe)
        db.session.commit()
    flash('Сорт \"{}\" (id: {}) удален'.format(sort.title, sort.id))
    db.session.delete(sort)
    db.session.commit()
    return redirect(url_for('database'))


@app.route('/editor/<type>/<id>', methods=['GET', 'POST'])
@login_required
def editor(type, id):
    if type == 'sort':
        if not current_user.email in Config.ADMINS:
            flash('[ACCESS DENIED]')
            return redirect(url_for('index'))
        form = EditSort()
        s = Sort.query.filter_by(id=id).first()
        if form.validate_on_submit():
            s.bouquet = form.bouquet.data
            s.description = form.description.data
            db.session.commit()
            return redirect(url_for('sort', sort_id=id))
        else:
            form.bouquet.data = s.bouquet
            form.description.data = s.description
            return render_template('edit_sort.html', form=form, sort=s, ADMIN_EMAILS=Config.ADMINS)
    elif type == 'recipe':
        form = EditRecipe()
        r = Recipe.query.filter_by(id=id).first()
        if current_user.id != r.user_id:
            flash('[ACCESS DENIED]')
            return redirect(url_for('recipe', recipe_id = r.id))
        if form.validate_on_submit():
            r.sort_id = Sort.query.filter_by(title=form.sort_id.data).first().id
            r.coffee_mass = form.coffee_mass.data
            r.water_mass = form.water_mass.data
            r.water_temp = form.water_temp.data
            r.acidity = form.acidity.data
            r.tds = form.tds.data
            r.grinding = form.grinding.data
            r.body = form.body.data
            db.session.commit()
            return redirect(url_for('recipe', recipe_id=id))
        else:
            form.tds.data = r.tds
            form.coffee_mass.data = r.coffee_mass
            form.water_mass.data = r.water_mass
            form.water_temp.data = r.water_temp
            form.acidity.data = r.acidity
            form.grinding.data = r.grinding
            form.body.data = r.body
            return render_template('edit_recipe.html', form=form, recipe=r, ADMIN_EMAILS=Config.ADMINS)
    else:
        form = EditProfile()
        user = User.query.filter_by(id=current_user.id).first()
        if form.validate_on_submit():
            user.password_hash = generate_password_hash(form.new_pass.data)
            db.session.commit()
            return redirect(url_for('user', user_id = current_user.id))
        else:
            return render_template('edit_profile.html', form=form, user=user, ADMIN_EMAILS=Config.ADMINS)
