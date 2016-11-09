from flask import Flask, render_template, flash, request, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, PasswordField
from flask_debugtoolbar import DebugToolbarExtension
import logging
from logging.handlers import RotatingFileHandler
from htpasswd import HtpasswdFile
import os

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.environ['APP_SECRET_KEY']
app.config['allowed_users'] = 'allowed_users'
app.config['allowed_users.htpasswd'] = 'allowed_users.htpasswd'
toolbar = DebugToolbarExtension(app)

def lookupEmail(email):
    with open(app.config['allowed_users']) as f:
        for line in f:
            if email in line:
                return True
    return False
    
def EmailInList(form, field):
    if not lookupEmail(field.data):
        raise validators.ValidationError('Email not in allowed list')

def updatePassword(form):
    passwordfile = HtpasswdFile(app.config['allowed_users.htpasswd'], create=True)
    passwordfile.load()
    passwordfile.update(form['email'].data, form['password'].data)
    passwordfile.save()

class ReusableForm(Form):
    email = TextField('Email:', validators=[validators.required(), EmailInList])
    password = PasswordField('Password:',
                             validators=[validators.required(),
                             validators.Length(min=6, max=128),
                             validators.EqualTo('confirm', message='Passwords must match'),
                             ])
    confirm  = PasswordField('Repeat Password')

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print form.errors
    if request.method == 'POST':
        app.logger.info('Info')
        email=request.form['email']
        print email

        if form.validate():
            # Save the comment here.
            flash('Hello ' + email)
            updatePassword(form)
            flash('Password updated!')
        else:
            for key in form.errors:
                flash('{field} Error: {msg}'.format(field=key, msg=form.errors[key][0]))

    return render_template('hello.html', form=form)

if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
