from flask import Flask, render_template, flash, url_for, request, redirect, jsonify
import requests
from flask_cors import CORS
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup as bs
import getpass
import re
from flask_csv import send_csv
from admin_login import AdminLogin
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required, LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'

CORS(app)

ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ac.in/IIT_ERP3/'
ERP_LOGIN_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/auth.htm'
ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/getSecurityQues.htm'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'


headers = {
    'timeout': '20',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}

@app.route("/")
@app.route("/check", methods = ['POST'])
def erp_cred_check():
    print('in check ')
    s = requests.Session()
    r = s.get(ERP_HOMEPAGE_URL)
    soup = bs(r.text, 'html.parser')
    sessionToken = soup.find_all(id='sessionToken')[0].attrs['value']
    login_details = {
        'user_id': request.json['roll_no'],
        'password': request.json['password'],
        'answer': request.json['answer'],
        'sessionToken': sessionToken,
        'requestedUrl': 'https://erp.iitkgp.ac.in/IIT_ERP3',
    }
    r = s.post(ERP_LOGIN_URL, data=login_details,
            headers = headers)
    # Based on response see whether credentials are correct or wrong
    print(' req.get_json is ', request.json)
    '''
    This needs to be added in the database
    request.json =  {'roll_no': '18MA20034', 'password': 'password', 'answer': 'answer', 'days': ['1', '3']}
    '''
   
    # TODO 
    # 1. verify if the user erp credentials are correct or not
    # if correct - Add details in database
    # else - Give warning

    try:
        ssoToken = re.search(r'\?ssoToken=(.+)$',
                     r.history[1].headers['Location']).group(1)
        print('in try')
    except IndexError:
        print("Error: Please make sure the entered credentials are correct!")

@app.route("/que", methods=['POST'])
def send_ques():
    s = requests.Session()
    r = s.get(ERP_HOMEPAGE_URL)
    r = s.post(ERP_SECRET_QUESTION_URL, data={'user_id': request.json['roll_no']},
            headers = headers)
    if (r.text == 'FALSE'): 
        return jsonify(que='Invalid Roll Number')
    secret_question = r.text
    return jsonify(que = secret_question)

@app.route("/admin", methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('applications'))
    form = AdminLogin()

    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash('password')
        if request.form['username'] == 'admin' and bcrypt.check_password_hash(password_hash, request.form['password']):
            return render_template('applications.html')

    return render_template('admin-login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin'))

@app.route("/applications", methods=['GET', 'POST'])
@login_required
def applicatons():
    # TODO read from database
    table_data_from_databade = [{'roll': '18me1234', 'name': 'kau', 'dates' : '1,3'}, {'roll': '18ce1234', 'name': 'rkau', 'dates' : '2,3'}]
    if method.request == "GET":
        print(' in get')
        return render_template('applications.html', table = table_data_from_databade)
    if method.request == 'POST':
        print(' in posr')
        return send_csv(table_data_from_databade)


if __name__ == '__main__':
    app.run(debug=True)
