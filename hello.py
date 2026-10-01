from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

# form class definition
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your UofT Email address?', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    submit = SubmitField('Submit')

# create the application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():

        old_name = session.get('name')
        old_email = session.get('email')

        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')

        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')

        session['name'] = form.name.data
        session['email'] = form.email.data

        return redirect(url_for('chat_page'))

    return render_template('index.html',
        form = form, name = session.get('name'), email = session.get('email'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

# clear session data when the user goes to the /clear route
@app.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('index'))

# chat bot
@app.route('/chat', methods=['GET'])
def chat_page():
    if 'name' not in session:
        return redirect(url_for('index'))

    return render_template('chat.html', name=session.get('name'))

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']

    if "my name is" in message.lower():
        # get the name from the message
        name = message[message.lower().index("my name is") + len("my name is"):].strip()

        session['chat_name'] = name

        response = "Hello! Nice to meet you, " + name + "!"
    
    elif "what is my name" in message.lower():
        if 'chat_name' in session:
            response = "Your name is " + session.get('chat_name') + "."
        else:
            response = "I don't know your name yet."
            
    elif "my email is" in message.lower():
        # get the email from the message
        email = message[message.lower().index("my email is") + len("my email is"):].strip()

        session['chat_email'] = email

        if 'chat_name' not in session:
            response = "Thanks for sharing your email! I will remember it as " + email + "."
        else:
            response = "Thanks for sharing your email, " + session.get('chat_name') + "! I will remember it as " + email + "."
    else:
        response = "I'm sorry, I didn't understand that."

    return ({"response": response})

    
# error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
