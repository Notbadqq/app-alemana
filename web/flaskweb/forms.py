from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length

#Clase post, puede servir de guia para mantener registro de cohortes
class PostForm(FlaskForm):
    title = StringField('Titulo', validators=[DataRequired(), Length(max=128)])
    title_slug = StringField('Titulo slug', validators=[Length(max=128)])
    content = TextAreaField('Contenido')
    submit = SubmitField('Enviar')

#Clase que describe el formulario para buscar una descripcion
class DescriptionForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()], id="descriptions")
    submit = SubmitField('Search')