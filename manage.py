# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import sys

from flask import Flask
from flask_script import Manager
from models import db
from models.artist import Artist
from models.genre import Genre, VenueGenre, ArtistGenre
from models.show import Show
from models.venue import Venue

# ----------------------------------------------------------------------------#
# App Config.

# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
manager = Manager(app)

genres = [
    'Alternative',
    'Blues',
    'Classical',
    'Country',
    'Electronic',
    'Folk',
    'Funk',
    'Hip-Hop',
    'Heavy Metal',
    'Instrumental',
    'Jazz',
    'Musical Theatre',
    'Pop',
    'Punk',
    'R&B',
    'Reggae',
    'Rock n Roll',
    'Soul',
    'Swing',
    'Other'
]
artists = [
    {
        "name": "Guns N Petals",
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    },
    {
        "name": "Matt Quevedo",
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    },
    {
        "name": "The Wild Sax Band",
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    }
]
venues = [
    {
        "name": "The Musical Hop",
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    },
    {
        "name": "The Dueling Pianos Bar",
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    },
    {
        "name": "Park Square Live Music & Coffee",
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    }
]


@manager.command
def seed_db():
    genre_objs = [Genre(name=genre) for genre in genres]
    artist_objs = [Artist(**artist) for artist in artists]
    venue_objs = [Venue(**venue) for venue in venues]

    try:
        db.session.add_all(genre_objs)
        db.session.add_all(artist_objs)
        db.session.add_all(venue_objs)
        db.session.commit()

        # genre ids
        genre_ids = {}
        for genre in genre_objs:
            genre_ids.update({genre.name: genre.id})

        # artist ids
        artist1_id = artist_objs[0].id
        artist2_id = artist_objs[1].id
        artist3_id = artist_objs[2].id

        # venue ids
        venue1_id = venue_objs[0].id
        venue2_id = venue_objs[1].id
        venue3_id = venue_objs[2].id

        # add artist genres
        artists_genres = [
            ArtistGenre(artist_id=artist1_id, genre_id=genre_ids["Rock n Roll"]),
            ArtistGenre(artist_id=artist2_id, genre_id=genre_ids["Jazz"]),
            ArtistGenre(artist_id=artist3_id, genre_id=genre_ids["Jazz"]),
            ArtistGenre(artist_id=artist3_id, genre_id=genre_ids["Classical"])
        ]
        db.session.add_all(artists_genres)

        # add venue genres
        venues_genres = [
            VenueGenre(venue_id=venue1_id, genre_id=genre_ids["Jazz"]),
            VenueGenre(venue_id=venue1_id, genre_id=genre_ids["Reggae"]),
            VenueGenre(venue_id=venue1_id, genre_id=genre_ids["Swing"]),
            VenueGenre(venue_id=venue1_id, genre_id=genre_ids["Classical"]),
            VenueGenre(venue_id=venue1_id, genre_id=genre_ids["Folk"]),

            VenueGenre(venue_id=venue2_id, genre_id=genre_ids["Classical"]),
            VenueGenre(venue_id=venue2_id, genre_id=genre_ids["R&B"]),
            VenueGenre(venue_id=venue2_id, genre_id=genre_ids["Hip-Hop"]),

            VenueGenre(venue_id=venue3_id, genre_id=genre_ids["Rock n Roll"]),
            VenueGenre(venue_id=venue3_id, genre_id=genre_ids["Jazz"]),
            VenueGenre(venue_id=venue3_id, genre_id=genre_ids["Classical"]),
            VenueGenre(venue_id=venue3_id, genre_id=genre_ids["Folk"]),
        ]
        db.session.add_all(venues_genres)

        # add shows

        shows = [
            {'artist_id': artist1_id, 'venue_id': venue3_id,
             'start_time': '2019-06-15T23:00:00.000Z'},
            {'artist_id': artist3_id, 'venue_id': venue3_id,
             'start_time': '2035-04-01T20:00:00.000Z'},
            {'artist_id': artist3_id, 'venue_id': venue3_id,
             'start_time': '2035-04-08T20:00:00.000Z'},
            {'artist_id': artist3_id, 'venue_id': venue3_id,
             'start_time': '2035-04-15T20:00:00.000Z'},
            {'venue_id': venue1_id, 'artist_id': artist1_id,
             'start_time': '2019-05-21T21:30:00.000Z'},
            {'venue_id': venue3_id, 'artist_id': artist2_id,
             'start_time': '2019-06-15T23:00:00.000Z'},
            {'venue_id': venue3_id, 'artist_id': artist3_id,
             'start_time': '2035-04-01T20:00:00.000Z'},
            {'venue_id': venue3_id, 'artist_id': artist3_id,
             'start_time': '2035-04-08T20:00:00.000Z'},
            {'venue_id': venue3_id, 'artist_id': artist3_id,
             'start_time': '2035-04-15T20:00:00.000Z'},
        ]
        show_objs = [Show(**show) for show in shows]
        db.session.add_all(show_objs)
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

# Default port:
if __name__ == '__main__':
    manager.run()