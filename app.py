from flask import Flask, render_template, url_for, request, session, redirect,flash
from flask_pymongo import PyMongo
import bcrypt
from uuid import uuid4

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'main'
app.config['MONGO_URI'] = '****MONGO DB URL****'
app.secret_key = '****SECRET KEY****'
mongo = PyMongo(app)



@app.route('/')
def index():
    if 'username' in session:
        users = mongo.db.users
        current_user = users.find_one({ 'name' : session['username']})
        
        data={'tasks':[{'task':'You have No Tasks!'}]}
        
                
        data['user']=current_user['nick']
        
        if 'tasks' in current_user:
            tasks=[ x for x in current_user['tasks'] if x['status']==0]
            if len(tasks) > 0:
                data['tasks']=tasks
            
        
        return render_template('home.html',data=data) 

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    flash('Invalid username/password combination')
    # Redirect user to login
    return redirect("/")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        
        existing_user = users.find_one({'name' : request.form['username']})
        print(existing_user)
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass , 'nick':request.form['nick'] })
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        flash('That username already exists!')
        return redirect("/register")
    return render_template('register.html')


@app.route("/add",methods=["POST"])
def add():
    users = mongo.db.users
    task=request.form['tasks']
    users.update({'name' : session['username']}, {'$push': {'tasks': {"u_id": uuid4().hex,'task' : task , "status" : 0  }}})
    return redirect("/")

@app.route("/remove/<string:u_id>",methods=["POST"])
def remove(u_id):
    users = mongo.db.users
    users.update({'name' : session['username'] , 'tasks.u_id' : u_id }, { '$set': {"tasks.$.status": 1}})
    return redirect("/")

@app.route("/logout",methods=["POST"])
def logout():
    """Log user out"""

    # Forget any username
    session.clear()

    # Redirect user to login
    return redirect("/")



if __name__ == '__main__':
    
    app.run()