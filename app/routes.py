from app import app
from flask import render_template

# GET /
@app.route('/')
@app.route('/about')
def home_page():
  return render_template('index.html')
