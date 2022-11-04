#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# METTRE UN TRUC CONTRE LES ENTREES TROP LONGUES
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, exception
from flask_wtf import Form
from forms import *
# My imports
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
from time import strftime
from datetime import date
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app) # db from models.py
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

### My models are located in models.py ### 

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#my filters
# verify form input lenght
class ValueTooLargeError(Exception):
    """Raised when the input value is too large"""
    pass
def veriflenght(inputValue, maxLenght):
  if len(str(inputValue)) <= int(maxLenght):
    return str(inputValue)
  else:
    raise ValueTooLargeError
# verify type integer 
class notAnIntError(Exception):
    """Raised when the input is not an integer"""
    pass
def verifInt(inputValue):
  try:
    inputValue = (int(inputValue))
    if isinstance(inputValue, int):
      return str(inputValue)
  except:
    raise notAnIntError
# verify date format 
class notInDateFormatError(Exception):
    """Raised when the input is not an integer"""
    pass
def verifDate(inputValue):
  try: 
    dateutil.parser.parse(inputValue, fuzzy=False)
    return inputValue
  except ValueError:
    raise notInDateFormatError

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cities = db.session.query(Venue.city).distinct().all()
  listOfCities = []
  for city in cities:
    listOfCities.append(city.city)
  
  listOfCities.reverse() # last to first

  data = []
  for city in listOfCities:
    cityData = {}
    cityData['city'] = city
    state = Venue.query.filter_by(city=city).first().state
    cityData['state'] = state
    cityData['venues'] = Venue.query.filter_by(state=state).all()
    data.append(cityData)
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  query = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  response = {}
  response['count'] = query.count()
  response['data'] = query.all()
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venueData = Venue.query.filter_by(id=venue_id).first()
  venueData.genres = venueData.genres.split(',') # transform commas separate string into a list

  # upcoming shows data
  upcomingShowsCount = Show.query.join(Venue).filter(Show.start_time > date.today(), Show.venue_id == venue_id).count()
  upcomingShows = Show.query.join(Venue).filter(Show.start_time > date.today(), Venue.id == venue_id).all()
  # upcoming shows data
  pastShowsCount = Show.query.join(Venue).filter(Show.start_time < date.today(), Show.venue_id == venue_id).count()
  pastShows = Show.query.join(Venue).filter(Show.start_time < date.today(), Venue.id == venue_id).all()

  # data modeling for upcoming shows
  venueData.upcoming_shows_count = upcomingShowsCount
  venueData.upcoming_shows = []
  for show in upcomingShows:
    UpcomingShow = {}
    artist = Artist.query.filter_by(id=show.artist_id).first()
    UpcomingShow['artist_id'] = show.artist_id
    UpcomingShow['artist_name'] = artist.name
    UpcomingShow['artist_image_link'] = artist.image_link
    UpcomingShow['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    venueData.upcoming_shows.append(UpcomingShow)
  # data modeling for past shows
  venueData.past_shows_count = pastShowsCount
  venueData.past_shows = []
  for show in pastShows:
    pastShow = {}
    artist = Artist.query.filter_by(id=show.artist_id).first()
    pastShow['artist_id'] = show.artist_id
    pastShow['artist_name'] = artist.name
    pastShow['artist_image_link'] = artist.image_link
    pastShow['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    venueData.past_shows.append(pastShow)

  return render_template('pages/show_venue.html', venue=venueData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # veriflenght is a filter to check string length* (not lenght btw)
  try:
    venue = Venue(
      name=veriflenght(request.form.get('name'), 120),
      city=veriflenght(request.form.get('city'),120),
      state=veriflenght(request.form.get('state'),120),
      address=veriflenght(request.form.get('address'),120),
      phone=veriflenght(request.form.get('phone'),120),
      genres=','.join(request.form.getlist('genres')),
      image_link=veriflenght(request.form.get('image_link'),500),
      facebook_link=veriflenght(request.form.get('facebook_link'),120),
      website_link=veriflenght(request.form.get('website_link'),120),
      seeking_talent=True if request.form.get('seeking_talent') else False,
      seeking_description=veriflenght(request.form.get('seeking_description'),120)
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueTooLargeError:
    flash('ERROR : Form fields must not be greater than 120 characters, 500 for image_link')
    db.session.rollback()
  except:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  try:
    # delete only if there is no upcoming shows related to the venue
    upShowCount = Show.query.join(Venue).filter(Show.start_time > date.today(), Show.venue_id == venue_id).count()
    if upShowCount < 1:
      # deleting the venue's past shows
      Show.query.filter_by(venue_id=venue_id).delete()
      # deleting the venue
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      flash('The venue and the past shows related it have been deleted')
    else:
      raise exception
  except:
    db.session.rollback()
    flash('This venue couldn\'t be deleted. It wont work if there is an upcoming show related to it')
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  # the search query
  query = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  response = {}
  response['count'] = query.count()
  # retrieving all data corresponding to the search
  response['data'] = query.all()

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id).first()
  data.genres = data.genres.split(",")

  # upcoming shows data
  upcomingShowsCount = Show.query.join(Artist).filter(Show.start_time > date.today(), Show.artist_id == artist_id).count()
  upcomingShows = Show.query.join(Artist).filter(Show.start_time > date.today(), Artist.id == artist_id).all()
  # past shows data
  pastShowsCount = Show.query.join(Artist).filter(Show.start_time < date.today(), Show.artist_id == artist_id).count()
  pastShows = Show.query.join(Artist).filter(Show.start_time < date.today(), Artist.id == artist_id).all()

  data.upcoming_shows_count = upcomingShowsCount
  data.upcoming_shows = []
  for show in upcomingShows:
    showdata = {}
    venue = Venue.query.filter_by(id=show.venue_id).first()
    showdata['venue_id'] = venue.id
    showdata['venue_name'] = venue.name
    showdata['venue_image_link'] = venue.image_link
    showdata['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    data.upcoming_shows.append(showdata)

  data.past_shows_count = pastShowsCount
  data.past_shows = []
  for show in pastShows:
    showdata = {}
    venue = Venue.query.filter_by(id=show.venue_id).first()
    showdata['venue_id'] = venue.id
    showdata['venue_name'] = venue.name
    showdata['venue_image_link'] = venue.image_link
    showdata['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    data.past_shows.append(showdata)

  # shows the artist page with the given artist_id
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # filling the form field with the artist's existing data
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  genreslist = artist.genres.split(',')
  form.genres.data = genreslist
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data  = True if artist.seeking_venue else False
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name=veriflenght(request.form.get('name'), 120)
    artist.city=veriflenght(request.form.get('city'), 120)
    artist.state=veriflenght(request.form.get('state'), 120)
    artist.phone=veriflenght(request.form.get('phone'), 120)
    artist.genres= ','.join(request.form.getlist('genres'))
    artist.image_link=veriflenght(request.form.get('image_link'), 500)
    artist.facebook_link=veriflenght(request.form.get('facebook_link'), 120)
    artist.website_link=veriflenght(request.form.get('website_link'), 120)
    artist.seeking_venue=True if request.form.get('seeking_venue') else False
    artist.seeking_description=veriflenght(request.form.get('seeking_description'), 120)
    flash('Artist ' + request.form.get('name') + ' was successfully modified!')
    db.session.commit()
  except ValueTooLargeError:
    flash('ERROR : Form fields must not be greater than 120 characters, 500 for image link')
    db.session.rollback()
  except:
    flash('An error occurred. ' + artist.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # filling the form field with the venue's existing data
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.image_link.data = venue.image_link
  genreslist = venue.genres.split(',')
  form.genres.data = genreslist
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data  = True if venue.seeking_talent else False
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name=veriflenght(request.form.get('name'), 120)
    venue.city=veriflenght(request.form.get('city'),120)
    venue.state=veriflenght(request.form.get('state'),120)
    venue.phone=veriflenght(request.form.get('phone'),120)
    venue.genres=','.join(request.form.getlist('genres'))
    venue.image_link=request.form.get('image_link')
    venue.facebook_link=veriflenght(request.form.get('facebook_link'),120)
    venue.website_link=veriflenght(request.form.get('website_link'),500)
    venue.seeking_talent=True if request.form.get('seeking_talent') else False
    venue.seeking_description=veriflenght(request.form.get('seeking_description'),120)
    flash('Venue ' + venue.name + ' was successfully modified!')
    db.session.commit()
  except ValueTooLargeError:
    flash('ERROR : Form fields must not be greater than 120 characters, 500 for image link')
    db.session.rollback()
  except:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    db.session.rollback()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist = Artist(
      name=veriflenght(request.form.get('name'),120),
      city=veriflenght(request.form.get('city'),120),
      state=request.form.get('state'),
      phone=veriflenght(request.form.get('phone'),120),
      genres=','.join(request.form.getlist('genres')),
      image_link=veriflenght(request.form.get('image_link'),500),
      facebook_link=veriflenght(request.form.get('facebook_link'),120),
      website_link=veriflenght(request.form.get('website_link'),120),
      seeking_venue=True if request.form.get('seeking_venue') else False,
      seeking_description=veriflenght(request.form.get('seeking_description'),120)
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueTooLargeError:
    flash('ERROR : Form fields must not be greater than 120 characters, 500 for image link')
    db.session.rollback()
  except:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + artist.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # hope you will understand
  data = [] # list of shows
  shows = Show.query.all() # the shows
  shows.reverse() # the shows form the last to the first
  # i needed to deal with some issues
  for item in shows: # building data for every single show
    showData = {}
    artist = Artist.query.filter_by(id=item.artist_id).first()
    venue = Venue.query.filter_by(id=item.venue_id).first()
    showData['artist_id'] = item.artist_id
    showData['artist_name'] = artist.name
    showData['venue_id'] = item.venue_id
    showData['venue_name'] = venue.name
    showData['start_time'] = item.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    showData['artist_image_link'] = artist.image_link
    data.append(showData) # and sending it to the list

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(
      artist_id=verifInt(request.form.get('artist_id')),
      venue_id=verifInt(request.form.get('venue_id')),
      start_time=verifDate(request.form.get('start_time')),
    )
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # on unsuccessful db insert :
  except notAnIntError:
    flash('Error! Your show has not been created!. IDs must be integers!')
    db.session.rollback()
  except notInDateFormatError:
    flash('Error! Your show has not been created!. Check your date format!')
    db.session.rollback()
  except:
    flash('An error occurred. Show could not be listed. Be sure to put valid IDs')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
#### THE END, thanks !