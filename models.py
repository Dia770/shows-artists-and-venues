from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

### ressource_utile : IMPORTATION DE MODELS.PY DANS APP 
# https://stackoverflow.com/questions/9692962/flask-sqlalchemy-import-context-issue/9695045#9695045

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String()) #
    genres = db.Column(db.String()) #
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False) #
    seeking_description = db.Column(db.String()) #
    
    shows = db.relationship('Show', backref='venue', lazy=True) #

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False) 
    city = db.Column(db.String(120), nullable=False) 
    state = db.Column(db.String(120), nullable=False) 
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String()) #
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False) #
    seeking_description = db.Column(db.String()) #

    shows = db.relationship('Show', backref='artist', lazy=True) #

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id  = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False) 
    start_time = db.Column(db.DateTime, nullable=False) 

    # artist_name = db.Column(db.String())
    # venue_name = db.Column(db.String())
    # venue_image_link = db.Column(db.String())