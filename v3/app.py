import os
import getpass
from datetime import timedelta

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, flash, redirect
import flask_login

from db import PostgresDB
from forms import QuoteForm, QuoteTagForm, TagForm, LoginForm, PublicSelectTagForm
from user import User

# TODO set up logging
# TODO clean up error handling 

# load environment variables
proj_dir = os.path.dirname(__file__)
env_path = os.path.join(proj_dir, '.env')
load_dotenv(env_path)

# create application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# create database instance
db = PostgresDB(os.environ.get('PG_DB'), os.environ.get('PG_USER'), os.environ.get('PG_PW'))

# set up + configure login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
       
def flash_validation_errors(form):
    if form.errors:
        keys = form.errors.keys()
        
        for key in keys:
            # TODO clean up message flashing 
            flash(f'{key}: {form.errors[key]}', 'error')

@login_manager.user_loader
def load_user(username):
    is_in_db = db.users_select_by_username(username)

    if not is_in_db:
        return 
    else:
        user = User(username)      

        return user

@app.route('/admin')
@flask_login.login_required
def admin():
    rows = db.combined_tables_select_all(distinct=False)

    return render_template('admin.html', rows=rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_id_found = db.users_verify_password(username, password) # user id from Postgres; password hashed in backend
        
        if user_id_found:
            user = User(username)
            flask_login.login_user(user, duration=timedelta(minutes=5))
            return redirect(url_for('admin'))
                
        else:
            flash('invalid login', 'error')
            
            return redirect(url_for('login'))

    return render_template('form_login.html', form=form)

@flask_login.login_required
@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('Successfully logged out.', 'message')
    
    return redirect(url_for('login'))

@app.route('/')
def index():
    username = getpass.getuser()
    quote = db.quote_select_random()

    return render_template('index.html',
                            quote=quote, 
                            username=username)   

@app.route('/quotes')
def quotes_public():
    rows = db.combined_tables_select_all()
    
    return render_template('table_auto_public.html', 
                            page='[quotes]', 
                            rows=rows)

@app.route('/tags', methods=['GET', 'POST'])
def tags_public():
    choices = [(row['name'], row['name']) for row in db.tag_select_all()]

    form = PublicSelectTagForm()
    form.tag_select.choices = choices

    if form.validate_on_submit():
        tag = form.tag_select.data
        return redirect(url_for('quotes_tagged_public',  tag=tag))

    return render_template('tags_public.html', form=form)

@app.route('/quotes/<string:tag>')
def quotes_tagged_public(tag):
    rows = db.combined_tables_select_by_tag(tag)
    page = f'.[{tag.lower()}]'
    
    return render_template('table_auto_public.html', 
                            page=page, 
                            rows=rows)

@app.route('/admin/quotes') 
@flask_login.login_required
def quote():
    cols = db.table_get_all_colnames('quote')
    rows = db.quote_select_all()

    return render_template('table_auto.html', 
                            cols=cols, 
                            rows=rows, 
                            h_value='[quote]', 
                            function_new='quote_new', 
                            function_update= 'quote_update')

@app.route('/admin/quotes/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
def quote_update(id):
    quote = db.quote_select_by_id(id)
    
    form = QuoteForm(quote_id=id, quote_body=quote['body'], quote_source=quote['source'])

    if form.validate_on_submit():
        
        if form.quote_submit.data:
            response = db.quote_update_one(form.quote_body.data, form.quote_source.data, id)

            if response:
                flash(response, 'error')
            else:
                flash('Successful UPDATE', 'message')
                        
            return redirect(url_for('quote_update', id=id))
        
        elif form.quote_delete.data:
            response = db.quote_delete_one(id)

            if response:
                flash(response, 'error')
            else:
                flash('Successful DELETE', 'message')
            
            return redirect(url_for('quote'))

    return render_template('form_quote_update.html', form=form, quote=quote)

@app.route('/admin/quotes/new', methods=['GET', 'POST'])
@flask_login.login_required
def quote_new():
    form = QuoteForm()

    if form.validate_on_submit():
        db.quote_insert_one(form.quote_body.data, form.quote_source.data)
        flash('Successful INSERT', 'message')

        return redirect(url_for('quote_new'))

    flash_validation_errors(form)        

    return render_template('form_quote_new.html', form=form)

@app.route('/admin/quote_tags')
@flask_login.login_required
def quote_tag():
    cols = db.table_get_all_colnames('quote_tag')
    rows = db.quotetag_select_all()

    return render_template('table_auto.html',
                            cols=cols, 
                            rows=rows, 
                            h_value='[quote_tag]', 
                            function_new='quote_tag_new',
                            function_update='quote_tag_update')

@app.route('/admin/quote_tags/<int:q_id>/<int:t_id>', methods=['GET', 'POST'])
@flask_login.login_required
def quote_tag_update(q_id, t_id):
    q_body = db.quote_select_by_id(q_id)['body']
    t_name = db.tag_select_by_id(t_id)['name']
    form = QuoteTagForm(quote_id=q_id, tag_id=t_id, quote_body = q_body, tag_name = t_name, quotetag_submit='Delete')

    if form.validate_on_submit():
        response = db.quotetag_delete_one(q_id, t_id)

        if response:
            flash(response, 'error')
        else:
            flash('Successful DELETE', 'message')

        return redirect(url_for('quote_tag'))
    
    return render_template('form_quotetag_update.html',
                            form=form,
                            function_new='quote_tag_new')  

@app.route('/admin/quote_tags/new', methods=['GET', 'POST'])
@flask_login.login_required
def quote_tag_new():
    form = QuoteTagForm()
    
    if form.validate_on_submit():
        response = db.quotetag_insert_one(form.quote_id.data, form.tag_id.data)

        if response:
            flash(response, 'error')
        else:
            flash('Successful INSERT', 'message')

        return redirect(url_for('quote_tag_new'))

    flash_validation_errors(form)

    return render_template('form_quotetag_new.html', form=form)

@app.route('/admin/tags')
@flask_login.login_required
def tag():
    cols = db.table_get_all_colnames('tag')
    rows = db.tag_select_all()

    return render_template('table_auto.html',
                            cols=cols, 
                            rows=rows, 
                            h_value='[tag]', 
                            function_new='tag_new',
                            function_update='tag_update')

@app.route('/admin/tags/new', methods=['GET', 'POST'])
@flask_login.login_required
def tag_new():
    form = TagForm()

    if form.validate_on_submit():
        response = db.tag_insert_one(form.tag_name.data)

        if response:
            flash(response, 'error')
        else:
            flash('Successful INSERT', 'message')
        
        return redirect(url_for('tag_new'))
    
    flash_validation_errors(form)

    return render_template('form_tag_new.html', 
                            form=form)

@app.route('/admin/tags/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
def tag_update(id):
    tag_name = db.tag_select_by_id(id)['name']
    form = TagForm(tag_id=id, tag_name=tag_name)

    if form.validate_on_submit():
        if form.tag_submit.data:
            response = db.tag_update_one(id, form.tag_name.data)
        
            if response:
                flash(response, 'error')
            else:
                flash('Successful UPDATE', 'message')
            
            return redirect(url_for('tag_update', id=id))
        
        elif form.tag_delete.data:
            response = db.tag_delete_one(id)
        
            if response:
                flash(response, 'error')
            else:
                flash('Successful DELETE', 'message')
            
            return redirect(url_for('tag'))

    flash_validation_errors(form)
    
    return render_template('form_tag_update.html',
                            form=form)


