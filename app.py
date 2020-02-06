from flask import Flask, render_template, flash, url_for, request, redirect, jsonify
import requests
from flask_cors import CORS
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup as bs
import getpass
import re

app = Flask(__name__)
CORS(app)

ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ac.in/IIT_ERP3/'
ERP_LOGIN_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/auth.htm'
ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/getSecurityQues.htm'

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


if __name__ == '__main__':
    app.run(debug=True)
