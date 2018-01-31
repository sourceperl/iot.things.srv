from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, length


class LoginForm(FlaskForm):
    username = StringField('Utilisateur', validators=[DataRequired(), length(max=16)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), length(max=32)])
    submit = SubmitField('Valider')

class UpdatePwdForm(FlaskForm):
    password_1 = PasswordField('Nouveau mot de passe', validators=[DataRequired(), length(max=32)])
    password_2 = PasswordField('Confirmation du mot de passe', validators=[DataRequired(), length(max=32)])
    submit = SubmitField('Valider')

class CnfDeviceForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), length(max=16)])
    submit = SubmitField('Valider')
