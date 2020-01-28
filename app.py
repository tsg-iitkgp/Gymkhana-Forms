from flask import Flask, render_template, flash, url_for, request
from gym_form import GymForm

import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb://gymk_db_user:gymk_db_user@cluster0-shard-00-00-fgvux.mongodb.net:27017,cluster0-shard-00-01-fgvux.mongodb.net:27017,cluster0-shard-00-02-fgvux.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = cluster['gymk']
collection = db['gym_form']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp_secret_key'



@app.route("/")
@app.route("/", methods=['GET', 'POST'])
def gym_form():
    form = GymForm()
    if form.validate_on_submit():
        gymk_applicant = {}
        gymk_applicant['name'] = request.form['name']
        gymk_applicant['age_years'] = request.form['age_years']
        gymk_applicant['age_months'] = request.form['age_months']
        gymk_applicant['gender'] = request.form['gender']
        gymk_applicant['supporting_name'] = request.form['supporting_name']
        gymk_applicant['contact'] = request.form['contact']
        gymk_applicant['emp_or_student'] = request.form['emp_or_student']
        gymk_applicant['purpose'] = request.form['purpose']
        gymk_applicant['other_reason'] = request.form['other_reason']
       
        iit_details = {}
        if request.form['emp_or_student'] == 'IIT Employee':
            iit_details['emp_dept'] = request.form['emp_dept']
            iit_details['ec_no'] =request.form['ec_no']
        else:
            iit_details['hall'] = request.form['hall']
            iit_details['room'] =request.form['room']
            iit_details['roll_num'] = request.form['roll_num']
            iit_details['student_dept'] =request.form['student_dept']
        
        gymk_applicant['iit_details'] = iit_details   
        
        print('what is this ',gymk_applicant)
        print('form success')
        # flash('Request sent successfully, will be processed soon')
        collection.insert_one(gymk_applicant)
    else:
        print('form failure')
        # flash('Failed to submit a form')
    return render_template('gym-form.html', form = form)




if __name__ == '__main__':
    app.run(debug=True)
