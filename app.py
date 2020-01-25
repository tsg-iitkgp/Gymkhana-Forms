from flask import Flask, render_template, flash, url_for
from gym_form import GymForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp_secret_key'



@app.route("/")
@app.route("/", methods=['GET', 'POST'])
def gym_form():
    form = GymForm()
    if form.validate_on_submit():
        flash('Request sent successfully, will be processed soon')
    return render_template('gym-form.html', form = form)




if __name__ == '__main__':
    app.run(debug=True)
