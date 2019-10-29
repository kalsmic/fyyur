import datetime
from models import db


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime)

    artist = db.relationship('Artist', viewonly=True)
    venue = db.relationship('Venue', viewonly=True)

    @classmethod
    def count_upcoming_by_venue_id(cls, venue_id):
        return cls.query.filter_by(venue_id=venue_id).filter(cls.start_time > datetime.datetime.now()).count()

    @classmethod
    def count_past_by_venue_id(cls, venue_id):
        return cls.query.filter_by(venue_id=venue_id).filter(cls.start_time < datetime.datetime.now()).count()

    @classmethod
    def get_past_by_venue(cls, venue_id):
        shows = cls.query.filter_by(venue_id=venue_id).filter(cls.start_time < datetime.datetime.now()).all()
        return [show.show_details for show in shows]

    @classmethod
    def get_past_by_artist(cls, artist_id):
        shows = cls.query.filter_by(artist_id=artist_id).filter(cls.start_time < datetime.datetime.now()).all()
        return [show.show_details for show in shows]

    @classmethod
    def get_upcoming_by_venue(cls, venue_id):
        shows = cls.query.filter_by(venue_id=venue_id).filter(Show.start_time > datetime.datetime.now()).all()
        return [show.show_details for show in shows]

    @classmethod
    def get_upcoming_by_artist(cls, artist_id):
        shows = cls.query.filter_by(artist_id=artist_id).filter(Show.start_time > datetime.datetime.now()).all()
        return [show.show_details for show in shows]

    @classmethod
    def get_all(cls):
        return [show.show_details for show in cls.query.order_by(cls.venue_id.desc()).all()]

    @property
    def show_details(self):
        return {
            'id': self.id,
            'venue_id': self.venue_id,
            'venue_name': self.venue.name,
            "artist_id": self.artist_id,
            "artist_name": self.artist.name,
            "artist_image_link": self.artist.image_link,
            'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M")
        }

    def __repr__(self):
        return f'<Show id: {self.id} artist_id:{self.artist_id} venue_id: {self.venue_id}'
