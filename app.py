from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')  # Use environment variable for security
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

# Shared password for site access
SITE_PASSWORD = os.getenv('SITE_PASSWORD', 'musicpass')  # Load from environment variable

# Database model for events
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == SITE_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('events'))
    return render_template('login.html')

@app.route('/events')
def events():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('events.html', events=events)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        description = request.form.get('description')
        new_event = Event(title=title, date=datetime.strptime(date, "%Y-%m-%d"), description=description)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('events'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
