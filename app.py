from flask import Flask, render_template, request, url_for, redirect, session
from bson.objectid import ObjectId  # convert string IDs to ObjectId objects
from pymongo import MongoClient
import bcrypt
#from venv.config import DB_PASSWORD
import os

 # the name of the app
app = Flask(__name__)


#connect to database

#client = MongoClient(f"mongodb+srv://my_userName:my_pwd@cluster0.qhpicyw.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(f"mongodb+srv://Gracie:{os.getenv('DB_PASSWORD')}@cluster0.qhpicyw.mongodb.net/?retryWrites=true&w=majority")
db=client.mydb

todos = db.todos


# @app.route('/')
# def index():
#     if 'username' in session:
#         return 'Welcome ' + session['username']

#   return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():

    users = db.db.users
    login_user = users.find_one({'name' : request.form['username']})
# first, find the user in the database through the username, using bcrypt.checkpw() to compare both pwd (using encoded UTF-8),
 # if match redirects user to index page , if not return invalid  username pwd.
    if login_user:
        if bcrypt.checkpw(request.form['pass'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Invalid username or password'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method== 'POST':
        users= db.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name':request.form['username'], 'password':hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return 'Username already in database'
    return render_template('register.html')



@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('index'))

    all_todos = todos.find()
    return render_template('index.html', todos=all_todos)

# for deleting a todo, first we add a new route that accepts POST requests,
#  the new delete() view function will receive the ID of the todo to be deleted from the URL,
#   then use that ID (as a string) to delete it.
@app.post('/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


#adding a new route that accepts GET and Post requests to update the todos
@app.route('/<id>/update/', methods=('GET', 'POST'))
def update(id):
    todo = todos.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.update_one({"_id": ObjectId(id)}, {"$set": {'content': content, 'degree': degree}})
        return redirect(url_for('index'))
    return render_template('update.html', todo=todo)






# #  PLAYING WITH THE APP:
# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'

# @app.route('/gracie')
# def hello_gracie():  # put application's code here
#     return 'Hello miss Ludwig!'
#
# # prevent people changing things to our website
# @app.route('/capitalize/<word>/')
# def capitalize(word):
#     return '<h1>{}<h1>'.format(escape(word.capitalize()))
#
# @app.route('/upper/<word>/')
# def upper(word):
#     return '<h1>{}<h1>'.format(escape(word.upper()))
#
# @app.route('/add/<int:n1>,<int:n2>/')
# def add(n1, n2):
#     return '<h1>{}<h1>'.format(n1 + n2)
# # divide first number
# @app.route('/divide/<int:n1>,<int:n2>/')
# def divide(n1, n2):
#     return '<h1>{}<h1>'.format(n1 / n2)


if __name__ == '__main__':
    app.secret_key = 'secretivekeyagain'
    app.run(debug=True)

