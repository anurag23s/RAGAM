from sqlalchemy.orm import relationship
from app import app, db
from sqlalchemy import ForeignKey

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    is_creator = db.Column(db.Boolean, default=False)
    playlists = relationship('Playlist', backref='user', lazy=True)
    blacklist = db.Column(db.Boolean, default=False)
    
    
    #ratings = relationship('Rating', backref='user', lazy=True)
    
    
    

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    artist = db.Column(db.String(100))
    file_path = db.Column(db.String(255), nullable=False)
    playlists = relationship('Playlist', secondary='playlist_song', back_populates='songs')
    genre = db.Column(db.String(20))
    flag = db.Column(db.Boolean, default=False)  # Add this line for genre
    album_id = db.Column(db.Integer, ForeignKey('album.id'), nullable=True)  # Add this line for album

    album = relationship('Album', back_populates='songs', lazy=True)

    @property
    def average_rating(self):
        # Calculate the average rating of the song
        if self.ratings:
            ratings = [rating.rating for rating in self.ratings]
            if ratings:
                return sum(ratings) / len(ratings)

        return 0.0
        #average_rating = db.Column(db.Float, default=0.0)
    #ratings = relationship('Rating', backref='song', lazy=True)

    #def __init__(self, title, lyrics, duration, artist, file_path):
        #self.title = title
        #self.lyrics = lyrics
        #self.duration = duration
        #self.artist = artist
        #self.file_path = file_path
        #self.ratings = []
        
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.Boolean, default=False)
    songs = relationship('Song', back_populates='album', lazy=True)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = relationship('Song', secondary='playlist_song', back_populates='playlists')

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)

#class Rating(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    #rating = db.Column(db.Integer, nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    user = relationship('User', backref='ratings', lazy=True)
    song = relationship('Song', backref='ratings', lazy=True)