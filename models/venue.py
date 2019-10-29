from models import db
from models.genre import VenueGenre
from models.show import Show


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String())
    deleted = db.Column(db.Boolean, default=False)

    shows = db.relationship('Show', backref='venues', lazy=True)
    genres = db.relationship('Genre', secondary='venue_genre', viewonly=True)

    def add_genres(self, items):
        return [
            VenueGenre(venue_id=self.id, genre_id=genre)
            for genre in items
        ]

    def get_genres(self):
        return [genre.name for genre in self.genres]

    def update_genres(self, genres):
        #  genres in db
        venue_genres_in_db = VenueGenre.get_genres_ids(venue_id=self.id)

        # generate a list of new genres not in db
        genres_to_insert = list(set(genres) - set(venue_genres_in_db))
        if genres_to_insert:
            genres_objs = self.add_genres(genres_to_insert)
            db.session.add_all(genres_objs)

    @classmethod
    def get_enum(cls):
        return [
            (venue.id, venue.name)
            for venue in cls.query.with_entities(cls.id, cls.name).all()
        ]

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first_or_404()

    @classmethod
    def get_by_id_full(cls, id):
        details = {}
        venue = cls.get_by_id(id)
        past_shows = Show.get_past_by_venue(id)
        upcoming_shows = Show.get_upcoming_by_venue(id)
        details.update(venue)
        details.update({'upcoming_shows': upcoming_shows})
        details.update({'upcoming_shows_count': len(upcoming_shows)})
        details.update({'past_shows': past_shows})
        details.update({'past_shows_count': len(past_shows)})

        return details

    @classmethod
    def search_by_name(cls, venue_name):
        venues = cls.query.filter(
            cls.name.ilike(f'%{venue_name}%')
        ).all()
        return [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.count_upcoming_by_venue_id(venue.id)
            }
            for venue in venues
        ]

    @classmethod
    def exists(cls, name):
        return cls.query.filter(db.func.lower(cls.name) == db.func.lower(name)).count()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id).serialize

    @classmethod
    def get_by_city_state(cls, state, city):
        state_venues = cls.query.filter_by(city=city, state=state).all()

        venues = [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.count_upcoming_by_venue_id(venue.id)
            }
            for venue in state_venues
        ]
        return venues

    @classmethod
    def get_all(cls):
        venues = cls.query.with_entities(cls.city, cls.state).group_by(cls.state, cls.city).all()
        results = [
            {
                'city': venue.city,
                'state': venue.state,
                'venues': cls.get_by_city_state(state=venue.state, city=venue.city)
            }
            for venue in venues
        ]

        return results

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.get_genres(),
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        }

    def __repr__(self):
        return f'<Venue name={self.name} >'
