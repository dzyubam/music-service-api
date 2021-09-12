import datetime
import enum

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship

from app.database import Base


class ArtistRole(enum.Enum):
    primary_artist = 1
    secondary_artist = 2


class ArtistToTrackAssociation(Base):
    __tablename__ = "assoc_artist_to_track"

    artist_id = Column(Integer, ForeignKey("artists.artist_id"), primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.track_id"), primary_key=True)

    role = Column(Enum(ArtistRole), default=ArtistRole.primary_artist.name)

    artist = relationship("Artist")
    track = relationship("Track")


class TrackToAlbumAssociation(Base):
    __tablename__ = "assoc_track_to_album"

    track_id = Column(Integer, ForeignKey("tracks.track_id"), primary_key=True)
    album_id = Column(Integer, ForeignKey("albums.album_id"), primary_key=True)

    track = relationship("Track")
    album = relationship("Album")


class StoreEnum(enum.Enum):
    spotify = 1
    apple = 2
    youtube = 3


class Store(Base):
    __tablename__ = 'stores'

    store_id = Column(Integer, primary_key=True)
    name = Column(Enum(StoreEnum), default=StoreEnum.spotify.name)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return StoreEnum[self.name.name].name


class AlbumToStoresAssociation(Base):
    __tablename__ = "assoc_album_to_stores"

    album_id = Column(Integer, ForeignKey("albums.album_id"), primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), primary_key=True)

    album = relationship("Album")
    store = relationship("Store")


class Artist(Base):
    __tablename__ = 'artists'

    artist_id = Column(Integer, primary_key=True)
    name = Column(String(1024))

    tracks = relationship("Track", secondary=ArtistToTrackAssociation.__tablename__, back_populates="artists",
                          uselist=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Artist {}>'.format(self.__dict__)


class Track(Base):
    __tablename__ = 'tracks'

    track_id = Column(Integer, primary_key=True)
    title = Column(String(128))
    version = Column(String(128))
    explicit = Column(Boolean)
    isrc = Column(String(128))
    audio_file = Column(String(1024))

    artists = relationship(Artist, secondary=ArtistToTrackAssociation.__tablename__, cascade="all",
                           back_populates="tracks", uselist=True)

    def __init__(self, title=None, version=None, explicit=None, isrc=None, audio_file=None, artists=[]):
        self.title = title
        self.version = version
        self.explicit = True if str(explicit).lower() == 'true' else False
        self.isrc = isrc
        self.audio_file = audio_file
        self.artists = [Artist(**a) for a in artists]

    def __repr__(self):
        return '<Track {}>'.format(self.__dict__)


class Album(Base):
    __tablename__ = 'albums'

    album_id = Column(Integer, primary_key=True)
    title = Column(String(128))
    upc = Column(String(128))
    artwork_file = Column(String(1024))
    release_date = Column(Date)

    stores = relationship(Store, secondary=AlbumToStoresAssociation.__tablename__, backref="albums", uselist=True)
    tracks = relationship(Track, secondary=TrackToAlbumAssociation.__tablename__, backref="albums", uselist=True)

    def __init__(self, title=None, upc=None, artwork_file=None, release_date=None, stores=[], tracks=[]):
        self.title = title
        self.upc = upc
        self.artwork_file = artwork_file
        self.release_date = datetime.date.fromisoformat(release_date)

    def __repr__(self):
        return "<Album {}>".format(self.__dict__)
