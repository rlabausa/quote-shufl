from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired

class QuoteForm(FlaskForm):
    quote_id = IntegerField() # populated by DB in *_update form
    quote_body = TextAreaField(validators=[DataRequired()])
    quote_source = StringField(validators=[DataRequired()])
    quote_submit = SubmitField('Submit')
    quote_delete = SubmitField('Delete')

class QuoteTagForm(FlaskForm):
    quote_id = IntegerField(validators=[DataRequired()])
    tag_id = IntegerField(validators=[DataRequired()])
    quotetag_submit = SubmitField('Submit')

class TagForm(FlaskForm):
    tag_id = IntegerField() # populated by DB in *_update form
    tag_name = StringField(validators=[DataRequired()])
    tag_submit = SubmitField('Submit')
    tag_delete = SubmitField('Delete')
