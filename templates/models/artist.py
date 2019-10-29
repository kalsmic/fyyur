import datetime

from models import db
from models.genre import ArtistGenre
from models.show import Show


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    website = db.Column(db.String(200))

    shows = db.relationship('Show', backref='artists', lazy=True)
    genres = db.relationship('Genre', secondary='artist_genre', viewonly=True)

    def add_genres(self, items):
        return [
            ArtistGenre(artist_id=self.id, genre_id=genre)
            for genre in items
        ]

    def get_genres(self):
        return [genre.name for genre in self.genres]

    def update_genres(self, genres):
        #  genres in db
        venue_genres_in_db = ArtistGenre.get_genres_ids(artist_id=self.id)

        # generate a list of new genres not in db
        genres_to_insert = list(set(genres) - set(venue_genres_in_db))
        if genres_to_insert:
            genres_objs = self.add_genres(genres_to_insert)
            db.session.add_all(genres_objs)

    @classmethod
    def get_enum(cls):
        return [
            (artist.id, artist.name)
            for artist in cls.query.with_entities(cls.id, cls.name).all()
        ]

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_id_full(cls, id):
        details = {}
        artist = cls.get_by_id(id)
        past_shows = Show.get_past_by_venue(id)
        upcoming_shows = Show.get_upcoming_by_artist(id)
        details.update(artist.serialize)
        details.update({'upcoming_shows': upcoming_shows})
        details.update({'upcoming_shows_count': len(upcoming_shows)})
        details.update({'past_shows': past_shows})
        details.update({'past_shows_count': len(past_shows)})

        return details

    @classmethod
    def get_artists_by_name(cls, name):
        artists = cls.query.filter(cls.name.ilike(f'%{name}%')).outerjoin(Show, cls.id == Show.artist_id).all()
        return [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.num_upcoming_shows
        } for artist in artists]

    @classmethod
    def exists(cls, name):
        return cls.query.filter(db.func.lower(cls.name) == db.func.lower(name)).count()

    @property
    def num_upcoming_shows(self):
        return self.query.join(Show).filter_by(artist_id=self.id).filter(
            Show.start_time > datetime.datetime.now()).count()

    @property
    def num_past_shows(self):
        return self.query.join(Show).filter_by(artist_id=self.id).filter(
            Show.start_time < datetime.datetime.now()).count()

    @property
    def past_shows(self):
        return Show.get_past_by_artist(self.id)

    @property
    def upcoming_shows(self):
        return Show.get_upcoming_by_artist(self.id)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.get_genres(),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        }

    def __repr__(self):
        return f'<Artist name: {self.name}>'
