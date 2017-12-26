from app import app

# GET /
@app.route('/')
@app.route('/about')
def home_page():
  return "TODO home page displaying the API"
