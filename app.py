from flask import Flask, render_template, flash, url_for, request, redirect, jsonify, session
import requests
from flask_cors import CORS
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup as bs
import getpass
import re
from flask_csv import send_csv
from admin_login import AdminLogin
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
import dill as pickle
import datetime
import mysql.connector
import os

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'

CORS(app)

ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ac.in/IIT_ERP3/'
ERP_LOGIN_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/auth.htm'
ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/getSecurityQues.htm'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DB")

db = mysql.connector.connect(host=host, user=user, passwd=password, database=database)

monthList = {1:"january", 2:"february", 3:"march", 4:"april", 5:"may", 6:"june", 7:"july", 8:"august", 9:"september", 10:"october", 11:"november", 12:"december"}
dayList = {0:"monday", 1:"tuesday", 2:"wednesday", 3:"thursday", 4:"friday", 5:"saturday", 6:"sunday"}

cursor = db.cursor()

headers = {
    'timeout': '20',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}

@app.route("/", methods=['GET'])
def go_to_adminpage():
    return redirect(url_for('admin_login'))

@app.route("/check", methods = ['POST'])
def erp_cred_check():
    print('in check ')
    roll_no = request.json['roll_no']
    with open(roll_no, 'rb') as f:
        s = pickle.load(f)
    login_details = {
        'user_id': request.json['roll_no'],
        'password': request.json['password'],
        'answer': request.json['answer'],
        'requestedUrl': 'https://erp.iitkgp.ac.in/IIT_ERP3',
    }
    try:
        r = s.post(ERP_LOGIN_URL, data=login_details,
                headers = headers)
        if r.status_code == 200:
            print('r statscode is 200')
        #     return jsonify(message="success")
    except Exception as e:
        print('Error in login to ERP ',e)
        return jsonify(message="error in login")
    
    try:
        ssoToken = re.search(r'\?ssoToken=(.+)$', r.history[1].headers['Location']).group(1)
        return jsonify(message='success')
    except IndexError:
        print('Wrong Credentials')
        return jsonify(message="wrong creds")
    
    
    
    # print(' req.get_json is ', request.json)
    '''
    request.json =  {'roll_no': '18MA20034', 'password': 'password', 'answer': 'answer', 'days': ['1', '3']}
    '''
    days = request.json['days']
    days_int = [int(day) for day in days]

    baseQuery = "INSERT INTO {} ({}, ".format(requests, request.json['roll_no'])
    nDays = len(days)

    # check if atleast one is not in range of 0 to 6
    for day in days_int:
        if day < 0 or day > 6:
            return jsonify(message="Please send properly")
    
    chosenDays = ""
    for day in days:
        x = dayList[day]
        chosenDays = chosenDays + x +","
      
    chosenDays += ") VALUES ("
    for i in range(0, nDays + 1):
        chosenDays += "%s,"
       
    chosenDays += ")"
    sql = baseQuery + chosenDays
    val = [request.json['roll_no']]
    for day in days:
        val.append("Y")
        
    val = tuple(val)
    cursor.execute(sql, val)
    db.commit()
    print("Added to DB successfully")
    return jsonify(message="success")

    # TODO if correct Write to Database and send success message else send failuue

    # 1. verify if the user erp credentials are correct or not
    # if correct - Add details in database
    # else - Give warning




@app.route("/que", methods=['POST'])
def send_ques():
    # improve by adding a message
    if datetime.datetime.today().weekday() == 6:
        return jsonify(que="wrong day")
    s = requests.Session()
    r = s.get(ERP_HOMEPAGE_URL)

    roll_no = request.json['roll_no']
    r = s.post(ERP_SECRET_QUESTION_URL, data={'user_id': roll_no},
            headers = headers)
    secret_question = r.text

    with open(roll_no, 'wb+') as f:
        pickle.dump(s, f)

    if (secret_question == "FALSE"):
        return jsonify(que="Invalid Roll Number")
    else:
        return jsonify(que = secret_question)

@app.route("/admin", methods=['GET', 'POST'])
def admin_login():
    # UNCCOMMENT THIS SO AS TO DO MAKE MESS PERSON LOGIN ON SUNDAY ONLY
    # if datetime.datetime.today().weekday() != 6:
    #     flash('You can only login on sunday')
    #     return

    if current_user.is_authenticated:
        return redirect(url_for('applications'))
    form = AdminLogin()

    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash('password')
        # TODO 
        '''
        based on username and password, read from database
        - hall name
        - list of students
        '''
        
        hall = "MTH"
        table_data_from_database = [{'roll': '18me1234', 'name': 'kau', 'dates' : '1,3','approved_status': 'Y'}, {'roll': '18ce1234', 'name': 'rkau', 'dates' : '2,3', 'approved_status': 'N'}]
        #Storing hall name in session for future usage
        session['hall'] = hall
        
        if request.form['username'] == 'admin' and bcrypt.check_password_hash(password_hash, request.form['password']):
            return render_template('applications.html', table = table_data_from_database, hall=hall)
        else:
            flash('Credentials are wrong')
    return render_template('admin-login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin'))


@app.route('/get_csv', methods = ['POST'])
#@login_required
def get_csv():
    month = monthList[datetime.datetime.now().month]
    hall = session['hall']
    month = "march"
    print("Getting Data for Hall {}".format(hall+"_"+month))
    sqlQuery = "SELECT * FROM {}".format(hall+"_"+month)
    cursor.execute(sqlQuery)
    columns = tuple([d[0] for d in cursor.description])
    table_data_from_database = []
    for row in cursor:
        table_data_from_database.append(dict(zip(columns, row)))

    CSVheaders = ['roll_number', 'name', 'email', 'hall']
    for i in range(1, 31):
        date = str(i) + "-" + month
        CSVheaders.append(date)

    filename = '{}_students.csv'.format(hall+"_"+month)
    return send_csv(table_data_from_database, filename, CSVheaders)


@app.route('/approve', methods = ['POST'])
def approve():
    print('here in single approve')
    print(request.json)
    # TODO with the roll number obtained change N -> Y of single row 
    # Send the page again by reading the table from DB again
        
    hall = session['hall']

    #table_data_from_database = [{'roll': '18me1234', 'name': 'kau', 'dates' : '1,3','approved_status': 'Yoooo'}, {'roll': '18ce1234', 'name': 'rkau', 'dates' : '2,3', 'approved_status': 'Yes'}]
    return render_template('applications.html', table = table_data_from_database, hall=hall)

@app.route('/approve_all', methods = ['POST'])
def approve_all():
    # TODO change in database the status of all N -> Y using session['hall']
    hall = session['hall']
    table_data_from_database = [{'roll': '18me1234', 'name': 'kau', 'dates' : '1,3','approved_status': 'Yes'}, {'roll': '18ce1234', 'name': 'rkau', 'dates' : '2,3', 'approved_status': 'Yes'}]
    return render_template('applications.html', table = table_data_from_database, hall=hall)


if __name__ == '__main__':
    app.run(debug=True)
