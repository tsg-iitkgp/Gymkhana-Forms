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
from dotenv import load_dotenv
from mail import async_send_mail

load_dotenv()

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


def checkDateInput(from_date, to_date):
    from_date_object = datetime.datetime.strptime(from_date,'%Y-%m-%d')
    to_date_object = datetime.datetime.strptime(to_date, '%Y-%m-%d')

    today = datetime.datetime.now()

    startDiff = from_date_object - today
    startDiff = startDiff.days

    if startDiff < 2:
        return 1

    dayDiff = to_date_object - from_date_object
    dayDiff = dayDiff.days

    if dayDiff < 3:
        return -1

    return 0



@app.route("/", methods=['GET'])
def go_to_adminpage():
    return redirect(url_for('admin_login'))

@app.route("/check", methods = ['POST'])
def erp_cred_check():
    print('in check ')
    roll_no = request.json['roll_number']
    with open(roll_no, 'rb') as f:
        s = pickle.load(f)
    login_details = {
        'user_id': request.json['roll_number'],
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
    except IndexError:
        print('Wrong Credentials')
        return jsonify(message="wrong creds")
    
    
    
    # print(' req.get_json is ', request.json)
    '''
    request.json =  {'roll_no': '18MA20034', 'password': 'password', 'answer': 'answer', 'days': ['1', '3']}
    '''
#    days = request.json['days']
   # days_int = [int(day) for day in days]
    try:
        roll_number = request.json['roll_number']
        from_date = request.json['from']
        to_date = request.json['to']
        if checkDateInput(from_date, to_date) == 1:
            return jsonify(message="Choose a from date atleast 2 days away")

        if checkDateInput(from_date, to_date) == -1:
            return jsonify(message="The rebate period must be atleast 5 days long")

        cursor.execute("SELECT name, hall FROM students WHERE roll_number = '{}'".format(roll_number))
        x = cursor.fetchall()[0]
        name = x[0]
        hall = x[1]
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO `requests` (`timestamp`,`roll_number`, `from_date`, `to_date`) VALUES (%s, %s, %s, %s)"
        values = [timestamp, roll_number, from_date, to_date]
        val = tuple(values)
        cursor.execute(sql, val)
        db.commit()
        print("Added to DB successfully")
        return jsonify(message="success")
    
    except Exception as e:
        print("Exception: {}".format(e))
        return jsonify(message="DB Error")

    # TODO if correct Write to Database and send success message else send failuue

    # 1. verify if the user erp credentials are correct or not
    # if correct - Add details in database
    # else - Give warning
    return jsonify(message="success")


@app.route("/que", methods=['POST'])
def send_ques():
    # improve by adding a message
    if datetime.datetime.today().weekday() == 6:
        return jsonify(que="wrong day")
    s = requests.Session()
    r = s.get(ERP_HOMEPAGE_URL)

    roll_no = request.json['roll_number']
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
        # TODO 
        '''
        based on username and password, read from database
        - hall name
        - list of students
        '''
    
        hall = request.form['username']
        hall = "BRH"

        session['hall'] = hall

        sqlQuery = "SELECT * FROM requests INNER JOIN students ON requests.roll_number = students.roll_number WHERE hall = '{}' ORDER BY requests.timestamp DESC".format(hall)
        cursor.execute(sqlQuery)
        approvalList = cursor.fetchall()
        
        approvals = []

        for row in approvalList:
            studRow =  {}
            approvalID = row[0]
            timestamp = row[1]
            roll_number = row[2]
            from_date = row[3]
            to_date = row[4]
            approval_status = row[5]
            name = row[7]

            studRow["id"] = approvalID
            studRow["timestamp"] = timestamp
            studRow["roll_number"] = roll_number
            studRow["name"] = name
            studRow["from_date"] = from_date
            studRow["to_date"] = to_date
            studRow["approval_status"] = approval_status
            approvals.append(studRow)

        print(approvals) 
        if request.form['username'] == 'admin' and request.form['password'] == "password":
            return render_template('applications.html', table = approvals, hall=hall)
        else:
            flash('Credentials are wrong')
    return render_template('admin-login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin'))


@app.route('/get_csv', methods = ['POST'])
def get_csv():
    month = monthList[datetime.datetime.now().month]
    hall = session['hall']
    if hall is None:
        return redirect(url_for('admin_login')) 
    #month = "march"
    
    sqlQuery = "SELECT id, timestamp,students.roll_number, name, email, hall, from_date, to_date, approval_status FROM requests INNER JOIN students ON requests.roll_number = students.roll_number WHERE hall = '{}'".format(hall)
    cursor.execute(sqlQuery)
    results = cursor.fetchall()
    columns = ('id','timestamp','roll_number', 'name', 'email', 'hall', 'from_date', 'to_date', 'approval_status')
    table_data_from_database = []
    for row in results:
        table_data_from_database.append(dict(zip(columns, row)))

    CSVheaders = list(columns)
   
    filename = '{}_students.csv'.format(hall)
    return send_csv(table_data_from_database, filename, CSVheaders)


@app.route('/approve', methods = ['POST'])
def approve():
    print('here in single approve')
    print(request.json)
    cursor.execute("SELECT * FROM requests WHERE requests.roll_number = '{}' ORDER BY requests.timestamp DESC ".format(request.json['roll']))
    stud = cursor.fetchall()[0]

    
    # TODO with the roll number obtained change N -> Y of single row 
    # Send the page again by reading the table from DB again
    hall = session['hall']
    stud = list(stud)
    requestID = stud[0]
    cursor.execute("UPDATE requests SET approval_status = 'Y' WHERE requests.id = '{}'".format(requestID))
    print("UPDATED SUCCESSFULLY") 
    db.commit()
    cursor.execute("SELECT from_date, to_date FROM requests WHERE requests.id = '{}'".format(requestID))
    res = cursor.fetchall()[0]
    from_date = res[0]
    to_date = res[1]

    cursor.execute("SELECT name, email FROM students WHERE roll_number = '{}'".format(request.json['roll']))
    x = cursor.fetchone()
    name = x[0]
    email = x[1]
    body = "Hi {}! <br><br> Your Mess Rebate from {} to {} has been approved. <br><br> Thank You! <br> Technology Coordinator, TSG IITKGP".format(name, from_date, to_date)
    async_send_mail(email, "Mess Rebate Approved", body)
    #table_data_from_database = [{'roll': '18me1234', 'name': 'kau', 'dates' : '1,3','approved_status': 'Yoooo'}, {'roll': '18ce1234', 'name': 'rkau', 'dates' : '2,3', 'approved_status': 'Yes'}]
    return render_template('applications.html', table = approvals, hall=hall)

#@app.route('/approve_all', methods = ['POST'])
#def approve_all():
    # TODO change in database the status of all N -> Y using session['hall']
    #hall = session['hall']
    #table_data_from_database = [{'roll': '18me1234', 'name': 'kau', 'dates' : '1,3','approved_status': 'Yes'}, {'roll': '18ce1234', 'name': 'rkau', 'dates' : '2,3', 'approved_status': 'Yes'}]
    #return render_template('applications.html', table = table_data_from_database, hall=hall)


if __name__ == '__main__':
    app.run(debug=True)
