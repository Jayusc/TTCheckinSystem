from flask import Flask, request, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.append("../module")
from checkpoint import Checkpoints
from datetime import time, timedelta
from config import CheckInSystemConfig, Database
from db_table import Employee, ClockRecord, Device
import socket
from flask_session import Session

# Database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Database.connect
db = SQLAlchemy(app)

#config session
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'HawaiiDream'
Session(app)

# host ip
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

# checkpoint
checkpoints = Checkpoints(db)

# run
app.debug = True
app.run(host="0.0.0.0", port=9122, debug=False)

@app.route("/")
def init():
    if session["name"] == None:
        return redirect("/login")
    return render_template("configPage.html", config = checkpoints.config)

@app.route("/login",methods = ["GET","POST"])
def login():
    input_name = ""
    input_pwd = ""
    if request.method == "POST":
        input_name = request.form.get("username")
        input_pwd = request.form.get("pwd")
        # check username and password
        if authentication(input_name,input_pwd):
            identity = db.session.query(Employee).filter_by(username = input_name).first()
            # TODO:Add response
            session["name"] = identity.ename
            return redirect("/")
    # Failed authentication
    return render_template("login.html")

def authentication(name=None,pwd=None):
    dbUser = db.session.query(Employee).filter_by(username = name).first()
    if dbUser == None:
        return False
    elif dbUser.password == pwd:
        return True
    return False

    
@app.route('/setTime', methods=['POST'])
def result():
    """
    Set checkin time and checkout time

    """
    print(request.form)
    checkpoints.config = CheckInSystemConfig(request.form["clockin"], request.form["clockout"])
    checkpoints.addTrigger()
    checkpoints.scheduler.print_jobs()
    return render_template("configPage.html", config = checkpoints.config)

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/login")
