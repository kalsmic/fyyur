from models import db


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    artists = db.relationship('Artist', secondary='artist_genre', viewonly=True)
    venues = db.relationship('Venue', secondary='venue_genre', viewonly=True)

    @classmethod
    def get_enum(cls):
        return [(genre.id, genre.name) for genre in cls.query.all()]

    def details(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __repr__(self):
        return f'<Genre name = {self.name}/>'


class ArtistGenre(db.Model):
    __tablename__ = 'artist_genre'

    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)

    genre = db.relationship('Genre', backref=db.backref('artist_genre', cascade='all, delete-orphan'))
    artist = db.relationship('Artist', backref=db.backref('artist_genre', cascade='all, delete-orphan'))

    __table_args__ = (db.UniqueConstraint(genre_id, artist_id),)

    @classmethod
    def delete_old(cls, artist_id, genres):
        venues_to_delete = db.session.query(cls).filter_by(artist_id=artist_id).filter(cls.genre_id.notin_(genres))
        venues_to_delete.delete(synchronize_session=False)

    @classmethod
    def get_genres_ids(cls, artist_id):
        results = cls.query.filter_by(artist_id=artist_id).all()
        return [str(result.genre_id) for result in results]

    def __repr__(self):
        return f'<ArtistGenre artist {self.artist_id} genre {self.artist_id}>'


class VenueGenre(db.Model):
    __tablename__ = 'venue_genre'

    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)

    genre = db.relationship('Genre', backref=db.backref('venue_genre', cascade='all, delete-orphan'))
    venue = db.relationship('Venue', backref=db.backref('venue_genre', cascade='all, delete-orphan'))

    __table_args__ = (db.UniqueConstraint(genre_id, venue_id),)

    @classmethod
    def delete_old(cls, venue_id, genres):
        venues_to_delete = db.session.query(cls).filter_by(venue_id=venue_id).filter(cls.genre_id.notin_(genres))
        venues_to_delete.delete(synchronize_session=False)

    @classmethod
    def get_genres_ids(cls, venue_id):
        results = cls.query.filter_by(venue_id=venue_id).all()
        return [str(result.genre_id) for result in results]

    def __repr__(self):
        return f'<VenreGenre venue {self.venue_id} genre {self.genre_id}>'
