from app import app

@app.route('/')
@app.route('/index')
def index():
    return make_response(open('templates/index.html').read())