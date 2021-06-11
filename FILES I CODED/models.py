from database import db
import datetime

class User(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    rsvp = db.relationship("Attendance", backref="user", lazy = True)
    event = db.relationship("Event", backref="user", lazy = True)
    ratings = db.relationship("Rating", backref="user", lazy = True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()

class Event(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(200))
    info = db.Column("info", db.String(500))
    date = db.Column("date", db.String(100))
    location = db.Column("location", db.String(100))
    tags = db.Column("tags", db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    rsvp = db.relationship("Attendance", backref="event", lazy = True)
    ratings = db.relationship("Rating", backref="event", cascade="all, delete-orphan", lazy = True)

    def __init__(self, name, info, date, location, tags, user_id):
        self.name = name
        self.info = info
        self.date = date
        self.location = location
        self.tags = tags
        self.user_id = user_id



class Rating(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    nums = db.Column("nums", db.String(500))
    average = db.Column("average", db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable = False)

    def __init__(self, nums, average, user_id, event_id):
        self.nums = nums
        self.average = average
        self.user_id = user_id
        self.event_id = event_id



class Attendance(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    #rsvp = db.Column("rsvp", db.Boolean)
    user_name = db.Column(db.VARCHAR, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, user_name, event_id, user_id):
        #self.rsvp = rsvp
        self.user_name = user_name
        self.event_id = event_id
        self.user_id = user_id
