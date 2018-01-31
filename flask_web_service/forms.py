from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, length, EqualTo

# some class
class StripFlaskForm(FlaskForm):
    """ Auto-remove trailing space on a FlaskForm """
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            filters.append(my_strip_filter)
            return unbound_field.bind(form=form, filters=filters, **options)

# some functions
def my_strip_filter(value):
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value

# FlaskForm define
class LoginForm(StripFlaskForm):
    username = StringField('Utilisateur', validators=[DataRequired(), length(max=16, min=3)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), length(max=64, min=3)])
    submit = SubmitField('Valider')

class UpdatePwdForm(StripFlaskForm):
    password_1 = PasswordField('Nouveau mot de passe', 
                               validators=[DataRequired(), length(max=64, min=3), 
                               EqualTo('password_2', message='Les mots de passe ne correspondent pas')])
    password_2 = PasswordField('Confirmation du mot de passe', validators=[DataRequired(), length(max=32)])
    submit = SubmitField('Valider')

class CnfDeviceForm(StripFlaskForm):
    name = StringField('Nom', validators=[DataRequired(), length(max=16)])
    tx_pulse_n1 = StringField('Nom de la voie 1', default='vm', validators=[])
    tx_pulse_w1 = IntegerField('Poids de la voie 1', default=1, validators=[])
    tx_pulse_n2 = StringField('Nom de la voie 2', default='vc', validators=[])
    tx_pulse_w2 = IntegerField('Poids  de la voie 2', default=10, validators=[])
    submit = SubmitField('Valider')
