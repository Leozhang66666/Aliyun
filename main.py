from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
import openai
import bcrypt
from markupsafe import Markup

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
users = {}

users = {
    'exampleUser': {
        'password': b'somehashedpassword',
        'night_mode': False 
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if 'username' in session:
        message_content = Markup(f"Welcome back, {session['username']}! <a href='/logout'>Logout</a>")
    else:
        message_content = "Please enter your destination."

    if 'input' in request.args:
        user_input = request.args['input']
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_BASE_URL")

        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            max_tokens=150,
            messages=[
                {"role": "system", "content": "You are an expert in trip planning, you need to cover the information about all the flights, food, culture, hotel, scenic spot of every country."}, 
                {"role": "user", "content": user_input}
            ]
        )
        message_content = response.choices[0].message.content

    return render_template('index.html', message=message_content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        user = users.get(username)
        if user and bcrypt.checkpw(password, user['password']):
            session['username'] = username
            session['night_mode'] = user.get('night_mode', False) 
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        if username in users:
            flash('Username already exists.')
        else:
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            users[username] = {'password': hashed_password, 'night_mode': False}
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    if 'username' not in session:
        flash("You need to log in to access settings.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password'].encode('utf-8')
        new_password = request.form['new_password'].encode('utf-8')
        user = users.get(session['username'])

        if user and bcrypt.checkpw(current_password, user['password']):
            new_hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
            users[session['username']]['password'] = new_hashed_password
            flash('Your password has been updated.')

        night_mode = request.form.get('night_mode') == 'on'
        users[session['username']]['night_mode'] = night_mode
        session['night_mode'] = night_mode
        print("Night mode updated in session:", session['night_mode'])  
        flash('Settings updated.')

    return render_template('settings.html', user_night_mode=users[session['username']]['night_mode'])
@app.route('/plan_trip', methods=['GET', 'POST'])
def plan_trip():
    trip_suggestion = None 
    if request.method == 'POST':
        destination = request.form['destination']
        budget = request.form['budget']
        hotel = request.form['hotel']
        time = request.form['time']

        user_input = f"Plan a trip to {destination} with a budget of ${budget}, staying for {time} days at a hotel named {hotel}."

        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_BASE_URL")
        
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            #set this up for presentation...
            max_tokens=500,
            messages=[
                {"role": "system", "content": "You are an expert in trip planning, you require the information about food, culture, scenic spots, hotels(about stars), flights for every country. In your response, you need to tell the users a very detailed plan, for example, whether the requirements are acievable, the name of the hotel,  and the transportation used when gooing to scenic spots. For example Day1:,Day2:.... You have to switch lines per day 50 words limited."},
                {"role": "user", "content": user_input}
            ]
        )

        
        trip_suggestion = response['choices'][0].message.content if response.get('choices') else "Could not generate a plan."

    return render_template('plan_trip.html', trip_suggestion=trip_suggestion)




if __name__ == '__main__':
    app.run(debug=True)