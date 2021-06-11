import os  # os is used to get environment variables IP & PORT
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template
from flask import request
from flask import redirect, url_for
from database import db
from models import User as User
from models import Attendance as Attendance
from models import Event as Event
from models import Rating as Rating
from flask import session
import bcrypt
from forms import RegisterForm, LoginForm, RSVPForm, RateForm

app = Flask(__name__)  # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_event_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = 'SE3155'
#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Setup models
with app.app_context():
    db.create_all()   # run under the app context


# Home
@app.route('/')
@app.route('/index')
def index():
    if session.get('user'):
        return render_template('index.html', user=session['user'])
    return render_template("index.html")


# Events
@app.route('/events')
def get_events():
    if session.get('user'):
        eventsList = db.session.query(Event).all()

        return render_template("Events.html", events=eventsList, user=session["user"])
    else:
        return redirect(url_for('register'))


# Specific Event
@app.route('/events/<event_id>')
def get_event(event_id):
    if session.get('user'):

        my_event = db.session.query(Event).filter_by(id=event_id).one()

        form = RateForm()

        return render_template("Event.html", event=my_event, user=session['user'], form=form)
    else:
        return redirect(url_for('register'))


# rate
@app.route('/events/<event_id>/rate', methods=['POST'])
def rate(event_id):
    if session.get('user'):
        rate_form = RateForm()
        # validate_on_submit only validates using POST
        if rate_form.validate_on_submit():
            rating = request.form['rating']
            if db.session.query(Rating.nums):
                nums = str(db.session.query(Rating.nums).filter_by(event_id=event_id)) + str(rating)
            else:
                nums = str(rating)
            arr = str(nums).split(",")
            summ = 0
            for i in range(len(arr)):
                summ += int(str(arr[i]))
            average = str(float(summ/len(arr)))
            nums += ","
            new_record = Rating(nums, average, int(event_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_event', event_id=event_id))

    else:
        return redirect(url_for('register'))


# Your Events list (login req)
@app.route('/yourEvents')
def get_users_events():
    if session.get('user'):

        my_events = db.session.query(Event).filter_by(user_id=session['user_id']).all()

        return render_template("YourEvents.html", events=my_events, user=session["user"])
    else:
        return redirect(url_for('register'))


# Your Events -> New (login req)
@app.route('/yourEvents/new', methods=['GET', 'POST'])
def new_event():

        if session.get('user'):
            if request.method == 'POST':
                name = request.form['title']
                info = request.form['eventInfo']
                location = request.form['location']
                date = request.form['date']
                tags = request.form['tags']
                new_record = Event(name, info, date, location, tags, session.get('user_id'))
                db.session.add(new_record)
                db.session.commit()
                return redirect(url_for('get_users_events'))
            else:
                return render_template('new.html', user=session['user'])
        else:
            return redirect(url_for('register'))


# Your Events -> edit (login req)
@app.route('/events/edit/<event_id>', methods=['GET', 'POST'])
def update_event(event_id):

        if session.get('user'):
            if request.method == "POST":
                name = request.form['title']
                info = request.form['eventInfo']
                location = request.form['location']
                date = request.form['date']
                tags = request.form['tags']

                event = db.session.query(Event).filter_by(id=event_id).one()
                event.name = name
                event.info = info
                event.location = location
                event.date = date
                event.tags = tags
                db.session.add(event)
                db.session.commit()

                return redirect(url_for('get_users_events'))
            else:
                my_event = db.session.query(Event).filter_by(id=event_id).one()

                return render_template('new.html', event=my_event, user=session['user'])
        else:
            return redirect(url_for('register'))


# Your Events -> delete (login req)
@app.route('/events/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    # check if a user is saved in session
    if session.get('user'):
        # retrieve events from database
        my_event = db.session.query(Event).filter_by(id=event_id).one()
        db.session.delete(my_event)
        db.session.commit()

        return redirect(url_for('get_users_events'))
    else:
        # user is not in session redirect to login
        return redirect(url_for('register'))


# Contact Us
@app.route('/contactUs')
def contact_us():
    if session.get('user'):
        return render_template('ContactUs.html', user=session['user'])
    return render_template('ContactUs.html')


# About Us
@app.route('/aboutUs')
def about_us():
    if session.get('user'):
        return render_template('AboutUs.html', user=session['user'])
    return render_template('AboutUs.html')


# RSVP (login req)
@app.route('/events/<event_id>/rsvp', methods=['POST', 'GET'])
def rsvp(event_id):
    if session.get('user'):
        rsvp_form = RSVPForm()
        event_id=event_id
        # validate_on_submit only validates using POST
        if request.method == 'POST' and rsvp_form.validate_on_submit():
            user_name = request.form['user_name']
            new_record = Attendance(user_name, int(event_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('rsvp_page'))

        return render_template('rsvp.html', event_id=event_id, form=rsvp_form)

    else:
        return redirect(url_for('register'))


# RSVP page
@app.route('/your_rsvps')
def rsvp_page():
    if session.get('user'):
        return render_template('rsvp_page.html', user=session['user'])
    else:
        return redirect(url_for('register'))


# Sign Up / Log In
@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()

    if request.method == 'POST' and register_form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_events'))
    # something went wrong - display register view
    return render_template('register.html', form=register_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_events'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


# Logout (login req)
@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)