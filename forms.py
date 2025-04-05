from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, FloatField
from wtforms.validators import DataRequired, URL, NumberRange
from flask_ckeditor import CKEditorField

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    body = CKEditorField("Description", validators=[DataRequired()])
    photo_link = StringField("Image URL", validators=[DataRequired(), URL()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    price = FloatField('Price (DKK)', validators=[DataRequired(), NumberRange(min=0)])
    stripe_price_id = StringField('Stripe Price ID', validators=[DataRequired()])
    submit = SubmitField("Add Item")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")