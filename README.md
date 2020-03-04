# Gymkhana-Forms
Repository for Gym and Swimming pool form under Gymkhana

Setup instructions:
- Create a virtual environment using venv
`python3 -m venv env`

- Activate it
`source env/bin/activate`

- Install dependencies
`pip3 install -r requirements.txt`

- Start the server
`python3 app.py`


## Deployment

The forms are hosted on our DO server in a screen session with gunicorn.

## Endpoints
- Getting Security question from ERP 
```
endpoint: '/que' 
method: POST
data format to be sent from frontend: { 'roll_number' : 18ME30006 }
returns: 
  - If the roll number is a valid one:
    { que: 'ONE SECURITY QUESTION' }
  - If INVALID roll number:
    { que: 'Invalid Roll Number' } 
  
```
- Verifies ERP Credentials and adds requested dates on success
```
endpoint: '/check'
method: POST
sample data format to be sent from frontend: 
    { "roll_number": 18ME30006, "password": SOME_PASSWORD,  "answer":RELAVANT_ANSWER, "from": YYYY-MM-DD, "to": YYYY-MM-DD}
returns:
-  If failed to login in ERP:
    { message: 'error in login' }
 - If credentials are wrong:
    { message: 'wrong creds' }
 - If the request is successfully added to Database
     { message : 'success' }
 - If failed to update to the Database:
     { message: 'DB Error' }   
  
```
