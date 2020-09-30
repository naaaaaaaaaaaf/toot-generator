from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class DomainForm(FlaskForm):
    domain = StringField('ドメイン:', validators=[DataRequired()])

class TokenForm(FlaskForm):
    token = StringField('コード:', validators=[DataRequired()])