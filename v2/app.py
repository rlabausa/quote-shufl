#!/path/to/python/virtual/env

import os
import getpass

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, flash, redirect

from db import PostgresDB
from forms import QuoteForm, QuoteTagForm, TagForm

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
       
def flash_validation_errors(form):
    if form.errors:
        keys = form.errors.keys()
        
        for key in keys:
            # TODO clean up message flashing 
            flash(f'{key}: {form.errors[key]}', 'error')
        
# view functions
#================
@app.route('/')
def index():
    username = getpass.getuser()
    quote = db.quote_select_random()

    return render_template('index.html',
                            quote=quote, 
                            username=username)   

@app.route('/quotes') # route reflects REST naming conventions for collections/resources
def quote(): # view function name reflects actual relation name in DB
    cols = db.table_get_all_colnames('quote')
    rows = db.quote_select_all()

    return render_template('table_auto.html', 
                            cols=cols, 
                            rows=rows, 
                            h_value='[quote]', 
                            function_new='quote_new', 
                            function_update= 'quote_update')

@app.route('/quotes/<int:id>', methods=['GET', 'POST'])
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
            
            redirect(url_for('quote_update', id=id))
        
        elif form.quote_delete.data:
            response = db.quote_delete_one(id)

            if response:
                flash(response, 'error')
            else:
                flash('Successful DELETE', 'message')
            
            return redirect(url_for('quote'))

    return render_template('form_quote_update.html', form=form, quote=quote)

@app.route('/quotes/new', methods=['GET', 'POST'])
def quote_new():
    form = QuoteForm()

    if form.validate_on_submit():
        db.quote_insert_one(form.quote_body.data, form.quote_source.data)
        flash('Successful INSERT', 'message')

        return redirect(url_for('quote_new'))

    flash_validation_errors(form)        

    return render_template('form_quote_new.html', form=form)

@app.route('/quote_tags')
def quote_tag():
    cols = db.table_get_all_colnames('quote_tag')
    rows = db.quotetag_select_all()

    return render_template('table_auto.html',
                            cols=cols, 
                            rows=rows, 
                            h_value='[quote_tag]', 
                            function_new='quote_tag_new',
                            function_update='quote_tag_update')

@app.route('/quote_tags/<int:q_id>/<int:t_id>', methods=['GET', 'POST'])
def quote_tag_update(q_id, t_id):
    form = QuoteTagForm(quote_id=q_id, tag_id=t_id, quotetag_submit='Delete')

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

@app.route('/quote_tags/new', methods=['GET', 'POST'])
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

@app.route('/tags')
def tag():
    cols = db.table_get_all_colnames('tag')
    rows = db.tag_select_all()

    return render_template('table_auto.html',
                            cols=cols, 
                            rows=rows, 
                            h_value='[tag]', 
                            function_new='tag_new',
                            function_update='tag_update')

@app.route('/tags/new', methods=['GET', 'POST'])
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

@app.route('/tags/<int:id>', methods=['GET', 'POST'])
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
