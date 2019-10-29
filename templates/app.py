# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import logging
import sys
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment

from forms import *
from models import db
from models.artist import Artist
from models.genre import Genre, VenueGenre, ArtistGenre
from models.show import Show
from models.venue import Venue

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = Venue.get_all()
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    results = Venue.search_by_name(search_term)
    response = {
        'count': len(results),
        'data': results
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data = Venue.get_by_id_full(venue_id)
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    form.genres.choices = Genre.get_enum()

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        data = VenueForm(request.form).data
        new_venue = Venue(
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('state'),
            phone=data.get('phone'),
            image_link=data.get('image_link'),
            facebook_link=data.get('facebook_link'),
            website=data.get('website'),
            seeking_talent=data.get('seeking_talent'),
            seeking_description=data.get('seeking_description')
        )

        venue_exists = Venue.exists(name=data.get('name'))
        if venue_exists:
            flash('Venue with specified name already exists')
        else:

            db.session.add(new_venue)
            db.session.commit()

            # extract genres from form
            genres = data.get('genres')

            db.session.add_all(new_venue.add_genres(genres))
            db.session.commit()

            # on successful db insert, flash success
            flash('Venue ' + data.get('name') + ' was successfully listed!')

    except:

        # TODO: on unsuccessful db insert, flash an error instead.
        print(sys.exc_info())
        flash('An error occurred. Venue ' + data.get('name') + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    print('reached here')
    # return redirect(url_for('index'))
    # return render_template('pages/home.html')

    try:
        venue = Venue.query.get(venue_id)
        print(dir(venue.shows))
        if venue.shows:
       #       soft delete
            venue.deleted = True
            print('soft delete')
            flash('Venue with id ' + venue_id + ' was successfully soft deleted!')
            pass
        else:
            db.session.delete(venue)
            print('permannet deletion')
            flash('Venue with id ' + venue_id + ' was successfully permanently deleted!')
        db.session.commit()
    except:
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
        flash('Error deleting Venue with id ' + venue_id + '!')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # return render_template('pages/home.html')
    return 'True'


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = Artist.query.with_entities(Artist.id, Artist.name).all()

    data = [{'id': artist.id, 'name': artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    artists = Artist.get_artists_by_name(search_term)

    response = {
        "count": len(artists),
        "data": artists
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Artist.get_by_id_full(artist_id)
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.get_by_id(artist_id).serialize

    # set current genres
    artist['genres'] = ArtistGenre.get_genres_ids(artist_id)

    form = ArtistForm(**artist)
    form.genres.choices = Genre.get_enum()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    data = VenueForm(request.form).data

    try:
        artist = Artist.query.get(artist_id)
        artist.name = data.get('name')
        artist.city = data.get('city')
        artist.state = data.get('state')
        artist.phone = data.get('phone')
        artist.image_link = data.get('image_link')
        artist.facebook_link = data.get('facebook_link')
        artist.website = data.get('website')
        artist.seeking_venue=data.get('seeking_venue')
        artist.seeking_description=data.get('seeking_description')
        updated_genres = data.get('genres')

        # Delete genres that are not in updated_genres
        ArtistGenre.delete_old(artist_id=artist_id, genres=updated_genres)

        # update venue genres
        artist.update_genres(updated_genres)
        db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.get_by_id(venue_id)
    print(dir(venue))

    # set current genres
    venue['genres'] = VenueGenre.get_genres_ids(venue_id)

    form = VenueForm(**venue)
    #  set genres list
    form.genres.choices = Genre.get_enum()

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    data = VenueForm(request.form).data

    try:
        vn = Venue.query.get(venue_id)
        vn.name = data.get('name')
        vn.city = data.get('city')
        vn.state = data.get('state')
        vn.phone = data.get('phone')
        vn.image_link = data.get('image_link')
        vn.facebook_link = data.get('facebook_link')
        vn.website = data.get('website')
        vn.seeking_talent=data.get('seeking_talent')
        vn.seeking_description=data.get('seeking_description')
        updated_genres = data.get('genres')

        # Delete genres that are not in updated_genres
        VenueGenre.delete_old(venue_id=venue_id, genres=updated_genres)

        # update venue genres
        vn.update_genres(updated_genres)
        db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    form.genres.choices = Genre.get_enum()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        data = ArtistForm(request.form).data
        new_artist = Artist(
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('phone'),
            phone=data.get('name'),
            image_link=data.get('image_link'),
            facebook_link=data.get('facebook_link'),
            seeking_venue=data.get('seeking_venue'),
            seeking_description=data.get('seeking_description')
        )
        artist_exists = Artist.exists(name=data.get('name'))
        if artist_exists:
            flash('Artist with specified name already exists')
        else:

            db.session.add(new_artist)
            db.session.commit()

            # extract genres from form
            genres = data.get('genres')

            db.session.add_all(new_artist.add_genres(genres))
            db.session.commit()

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:

        # TODO: on unsuccessful db insert, flash an error instead.
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = Show.get_all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    form.artist_id.choices = Artist.get_enum()
    form.venue_id.choices = Venue.get_enum()

    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    try:
        data = ShowForm(request.form).data
        new_show = Show(
            artist_id=data.get('artist_id'),
            venue_id=data.get('venue_id'),
            start_time=data.get('start_time')
        )

        db.session.add(new_show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show created successfully !')

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
