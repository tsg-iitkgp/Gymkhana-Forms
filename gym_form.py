from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class GymForm(FlaskForm):
    name = StringField('Name of the Candidate', validators = [DataRequired(), Length(min = 2)])
    age_years = IntegerField('Years', validators = [DataRequired()])
    age_months = IntegerField('Months', validators = [DataRequired()])
    gender = RadioField('Gender', choices = [('Male', 'Male'), ('Female', 'Female')], validators = [DataRequired()])
    supporting_name = StringField('Parent/Guardian/Spouse Name', validators=[DataRequired(), Length(min = 2)])
    contact = IntegerField('Contact Number', validators = [DataRequired()])

    # radio for choosing employee or student
    emp_or_student = RadioField(' IIT Employee/IIT Student', choices = [('IIT Employee', 'IIT Employee'), ('IIT Student', 'IIT Student')])

    # if an employee
    emp_dept = StringField('Department')
    ec_no = StringField('EC NO')

    # if a student
    hall = StringField('Hall')
    room = StringField('Room Number')
    roll_num = StringField('Roll Number')
    student_dept = StringField('Department')

    purpose = RadioField('Purpose of Joining', choices = [('Fitness', 'Fitness'), ('Weight Lifting', 'Weight Lifting'), ('others', 'Others(Please specify)')])
    other_reason = StringField('Other Reason')

    submit = SubmitField('Submit')


