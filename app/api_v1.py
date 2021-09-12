import datetime

from flask import render_template, request, jsonify
from sqlalchemy.orm.exc import NoResultFound

from app import app
from app.database import db_session
from app.models.all import Track, Artist, Album, ArtistToTrackAssociation, TrackToAlbumAssociation, \
    AlbumToStoresAssociation, StoreEnum, Store
from flask_restful import fields, marshal_with, abort, Api, Resource


@app.route('/api/v1/resources/tracks', methods=['GET'])
def index():
    # form = ScrapeForm()
    #
    # if request.method == 'POST':
    #     if form.validate() == False:
    #         return render_template("index.html", form=form)
    #     # scrape using posted data as input
    #     result = scrape(request.form["url"], request.form["keyword"])
    #     new_result = Result(**result)
    #     # save to DB
    #     db_session.add(new_result)
    #     db_session.commit()
    #
    # # retrieve all Results
    results = Track.query.order_by(Track.track_id.desc()).all()

    return jsonify(results)


@app.route('/')
@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")


api = Api(app)

artist_fields = {
    'artist_id': fields.Integer,
    'uri': fields.Url('artist_ep'),
    'name': fields.String,
    # 'role': fields.String,
    'status': fields.String,
    'error': fields.String
}

track_fields = {
    'track_id': fields.Integer,
    'uri': fields.Url('track_ep'),
    'title': fields.String,
    'version': fields.String,
    'explicit': fields.Boolean,
    'isrc': fields.String,
    'audio_file': fields.String,
    'artists': fields.Nested(artist_fields),
    'status': fields.String,
    'error': fields.String
}

album_fields = {
    'album_id': fields.Integer,
    'uri': fields.Url('album_ep'),
    'title': fields.String,
    'upc': fields.String,
    'artwork_file': fields.String,
    'release_date': fields.String,
    'stores': fields.List(fields.String),
    'tracks': fields.Nested(track_fields),
    'status': fields.String,
    'error': fields.String
}


class Artists(Resource):
    @marshal_with(artist_fields)
    def get(self, artist_id=0):
        if artist_id == "all":
            results = Artist.query.order_by(Artist.artist_id.desc()).all()
        else:
            try:
                results = Artist.query.filter_by(artist_id=artist_id).one()
            except NoResultFound as e:
                results = {"error": "{}, Artist with ID '{}' not found".format(str(e), artist_id)}
        return results

    def delete(self, artist_id=0):
        to_delete = Artist.query.filter_by(artist_id=artist_id).delete()
        if to_delete:
            # TODO: do it the ORM way
            ArtistToTrackAssociation.query.filter_by(artist_id=artist_id).delete()
            db_session.commit()
        return "", 204

    def put(self, artist_id=0):
        to_update = Artist.query.filter_by(artist_id=artist_id)
        if to_update:
            json = request.get_json()
            to_update.update(json)
            db_session.commit()
        return "", 201

    @marshal_with(artist_fields)
    def post(self, artist_id=0):
        json = request.get_json()
        artist = Artist(**json)
        db_session.add(artist)
        db_session.commit()

        return artist, 201


# Artists resource routing
api.add_resource(Artists, '/api/v1/resources/artists/<artist_id>', endpoint='artist_ep')


class Tracks(Resource):
    @marshal_with(track_fields)
    def get(self, track_id):
        if track_id == "all":
            results = Track.query.order_by(Track.track_id.desc()).all()
        else:
            try:
                results = Track.query.filter_by(track_id=track_id).one()
            except NoResultFound as e:
                results = {"error": "{}, Track with ID '{}' not found".format(str(e), track_id)}
        return results

    def delete(self, track_id):
        to_delete = Track.query.filter_by(track_id=track_id).delete()
        if to_delete:
            # TODO: do it the ORM way
            ArtistToTrackAssociation.query.filter_by(track_id=track_id).delete()
            db_session.commit()
        return "", 204

    def put(self, track_id):
        to_update = Track.query.filter_by(track_id=track_id)
        if to_update:
            json = request.get_json()
            to_update.update(json)
            db_session.commit()
        return "", 201

    @marshal_with(track_fields)
    def post(self, track_id):
        json = request.get_json()
        track = Track(**json)
        db_session.add(track)
        db_session.commit()

        return track, 201


# Tracks resource routing
api.add_resource(Tracks, '/api/v1/resources/tracks/<track_id>', endpoint='track_ep')


class Albums(Resource):
    @marshal_with(album_fields)
    def get(self, album_id):
        if album_id == "all":
            results = Album.query.order_by(Album.album_id.desc()).all()
        else:
            try:
                results = Album.query.filter_by(album_id=album_id).one()
            except NoResultFound as e:
                results = {"error": "{}, Album with ID '{}' not found".format(str(e), album_id)}
        return results

    def delete(self, album_id):
        to_delete = Album.query.filter_by(album_id=album_id).delete()
        if to_delete:
            # TODO: do it the ORM way
            TrackToAlbumAssociation.query.filter_by(album_id=album_id).delete()
            AlbumToStoresAssociation.query.filter_by(album_id=album_id).delete()
            db_session.commit()
        return "", 204

    def put(self, album_id):
        album_to_update = Album.query.filter_by(album_id=album_id)
        if album_to_update:
            json = request.get_json()
            if "release_date" in json:
                json["release_date"] = datetime.date.fromisoformat(json["release_date"])
            album_to_update.update(json)
            db_session.commit()
        return "", 201

    @marshal_with(album_fields)
    def post(self, album_id):
        json = request.get_json()
        album = Album(**json)
        db_session.add(album)
        db_session.commit()
        if "stores" in json:
            for s in json["stores"]:
                store = Store.query.filter_by(name=s).first()
                if not store:
                    store = Store(name=s)
                    db_session.add(store)
                    db_session.commit()
                album.stores.append(store)
            db_session.add(album)
            db_session.commit()
        if "tracks" in json:
            for t in json["tracks"]:
                track = Track(**t)
                album.tracks.append(track)
            db_session.add(album)
            db_session.commit()

        return album, 201


# Albums resource routing
api.add_resource(Albums, '/api/v1/resources/albums/<album_id>', endpoint='album_ep')
