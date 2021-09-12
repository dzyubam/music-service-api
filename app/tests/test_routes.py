import json
from unittest import TestCase

from app import app
from app.database import db_session
from app.models.all import Store, StoreEnum


class TestRoutes(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.url_prefix = "/api/v1/resources"

    def tearDown(self):
        pass

    ###########
    # Artists #
    ###########
    def test_create_artist(self):
        response = self.create_artist("Pink")
        response_json = response.get_json()

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        self.assertIn("name", response_json)
        self.assertIn("artist_id", response_json)
        self.assertIn("uri", response_json)
        self.assertIn("status", response_json)
        self.assertIn("error", response_json)
        self.assertIsNone(response_json["status"])
        self.assertIsNone(response_json["error"])

    def test_get_one_artist(self):
        artist_name = "Test Get 1 Artist"
        response = self.create_artist(artist_name)
        response_json = response.get_json()
        new_artist_uri = response_json['uri']

        # Retrieve the newly created artist
        response = self.app.get(new_artist_uri)
        response_json = response.get_json()

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.is_json)
        self.assertTrue(response_json['uri'] == new_artist_uri)
        self.assertTrue(response_json['name'] == artist_name)

    def test_get_all_artists(self):
        response = self.app.get('{}/artists/all'.format(self.url_prefix))
        response_json = response.get_json()

        print(json.dumps(response_json, indent=4))

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.is_json)
        self.assertTrue(type(response_json) == list)

    def test_update_artists(self):
        response = self.app.get('{}/artists/all'.format(self.url_prefix))
        response_json = response.get_json()

        # First check there were artists to be deleted
        self.assertTrue(len(response_json))

        # Update artists one by one
        for a in response_json:
            self.pp(a)
            new_name = "{} UPDATED".format(a["name"])
            payload = json.dumps(dict(name=new_name))
            self.app.put(a['uri'], headers={"Content-Type": "application/json"}, data=payload)

        # Get all artists again and see if all artist names got updated
        response = self.app.get('{}/artists/all'.format(self.url_prefix))
        response_json = response.get_json()

        for a in response_json:
            self.pp(a)
            updated_name = a["name"]
            self.assertTrue("UPDATED" in updated_name)

    def test_delete_artists(self):
        # Create at least one new artist first
        response = self.create_artist("Test Artist 1")

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        response = self.app.get('{}/artists/all'.format(self.url_prefix))
        response_json = response.get_json()

        # Delete artists one by one
        for a in response_json:
            self.pp(a)
            response = self.app.delete(a['uri'])
            self.assertTrue(response.status_code == 204)

        # Check that no artists are left
        response = self.app.get('{}/artists/all'.format(self.url_prefix))
        response_json = response.get_json()
        self.assertFalse(len(response_json))

    ##########
    # Tracks #
    ##########
    def test_create_track(self):
        response = self.create_track("Cover Me In Sunshine", "Studio Edit", False, "TEST000000001",
                                     "https://cdn.coolcompany.io/test.wav", [dict(name="Pink")])
        response_json = response.get_json()

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        self.assertIn("title", response_json)
        self.assertIn("version", response_json)
        self.assertIn("explicit", response_json)
        self.assertIn("isrc", response_json)
        self.assertIn("audio_file", response_json)
        self.assertIn("artists", response_json)
        self.assertIn("status", response_json)
        self.assertIn("error", response_json)
        self.assertIsNone(response_json["status"])
        self.assertIsNone(response_json["error"])

    def test_get_one_track(self):
        new_track = dict(title="Cover Me In Sunshine", version="Studio Edit", explicit=False, isrc="TEST000000001",
                         audio_file="https://cdn.coolcompany.io/test.wav", artists=[dict(name="Pink")])
        response = self.create_track(**new_track)
        response_json = response.get_json()
        new_track_uri = response_json['uri']
        new_track_id = response_json['track_id']
        new_track['uri'] = new_track_uri
        new_track['track_id'] = new_track_id
        # TODO: test equality of nested artists properly
        del new_track['artists']
        self.pp(new_track)

        # Retrieve the newly created track
        response = self.app.get(new_track_uri)
        response_json = response.get_json()
        # TODO: test equality of nested artists properly
        del response_json['artists']
        del response_json['status']
        del response_json['error']
        self.pp(response_json)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.is_json)
        self.assertTrue(response_json == new_track)

    def test_get_all_tracks(self):
        response = self.app.get('{}/tracks/all'.format(self.url_prefix))
        response_json = response.get_json()

        print(json.dumps(response_json, indent=4))

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.is_json)
        self.assertTrue(type(response_json) == list)

    def test_update_tracks(self):
        # Create at least one new track first
        response = self.create_track("Cover Me In Sunshine TEST", "Studio Edit", False, "TEST000000001",
                                     "https://cdn.coolcompany.io/test.wav", [dict(name="Pink")])

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        response = self.app.get('{}/tracks/all'.format(self.url_prefix))
        response_json = response.get_json()

        # Update tracks one by one
        for a in response_json:
            self.pp(a)
            new_title = "{} UPDATED TITLE".format(a["title"])
            payload = json.dumps(dict(title=new_title, version="Radio Edit"))
            self.app.put(a['uri'], headers={"Content-Type": "application/json"}, data=payload)

        # Get all tracks again and see if all track names got updated
        response = self.app.get('{}/tracks/all'.format(self.url_prefix))
        response_json = response.get_json()

        for a in response_json:
            self.pp(a)
            updated_title = a["title"]
            self.assertTrue("UPDATED TITLE" in updated_title)

    def test_delete_tracks(self):
        # Create at least one new track first
        response = self.create_track("Cover Me In Sunshine TEST", "Studio Edit", False, "TEST000000001",
                                     "https://cdn.coolcompany.io/test.wav", [dict(name="Pink")])

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        response = self.app.get('{}/tracks/all'.format(self.url_prefix))
        response_json = response.get_json()

        # Delete tracks one by one
        for a in response_json:
            self.pp(a)
            response = self.app.delete(a['uri'])
            self.assertTrue(response.status_code == 204)

        # Check that no tracks are left
        response = self.app.get('{}/tracks/all'.format(self.url_prefix))
        response_json = response.get_json()
        self.assertFalse(len(response_json))

    ##########
    # Albums #
    ##########
    def test_create_album(self):
        self.create_stores()
        response = self.create_album("Sample Album",
                                     "00000000000111",
                                     "https://cdn.coolcompany.io/test.jpg",
                                     "2021-01-01",
                                     ["apple", "spotify"],
                                     [
                                         dict(title="Cover Me In Sunshine",
                                              version="Studio Edit",
                                              explicit=False,
                                              isrc="TEST000000001",
                                              audio_file="https://cdn.coolcompany.io/test.wav",
                                              artists=[dict(name="Pink")]),
                                         dict(title="Cover Me In Dirt",
                                              version="Studio Edit",
                                              explicit=True,
                                              isrc="TEST000000002",
                                              audio_file="https://cdn.coolcompany.io/test.wav",
                                              artists=[dict(name="Pink")]),
                                         dict(title="Cover Me In Paint",
                                              version="Studio Edit",
                                              explicit=False,
                                              isrc="TEST000000003",
                                              audio_file="https://cdn.coolcompany.io/test.wav",
                                              artists=[dict(name="Pink")]),
                                     ])
        response_json = response.get_json()

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        self.assertIn("title", response_json)
        self.assertIn("upc", response_json)
        self.assertIn("artwork_file", response_json)
        self.assertIn("release_date", response_json)
        self.assertIn("stores", response_json)
        self.assertIn("tracks", response_json)
        self.assertIn("status", response_json)
        self.assertIn("error", response_json)
        self.assertIsNone(response_json["status"])
        self.assertIsNone(response_json["error"])

    def test_get_one_album(self):
        new_album = dict(title="Cover Me In Sunshine",
                         upc="00000000000111",
                         artwork_file="https://cdn.coolcompany.io/test.jpg",
                         release_date="2021-01-01",
                         stores=["spotify", "apple", "youtube"],
                         tracks=[
                             dict(title="Cover Me In Sunshine",
                                  version="Studio Edit",
                                  explicit=False,
                                  isrc="TEST000000001",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                             dict(title="Cover Me In Dirt",
                                  version="Studio Edit",
                                  explicit=True,
                                  isrc="TEST000000002",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                             dict(title="Cover Me In Paint",
                                  version="Studio Edit",
                                  explicit=False,
                                  isrc="TEST000000003",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                         ])
        response = self.create_album(**new_album)
        response_json = response.get_json()
        new_album_uri = response_json['uri']
        new_album_id = response_json['album_id']
        new_album['uri'] = new_album_uri
        new_album['album_id'] = new_album_id
        # TODO: test equality of nested artists properly
        del new_album['tracks']
        self.pp(new_album)

        # Retrieve the newly created track
        response = self.app.get(new_album_uri)
        response_json = response.get_json()
        # TODO: test equality of nested artists properly
        del response_json['tracks']
        del response_json['status']
        del response_json['error']
        self.pp(response_json)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.is_json)
        self.assertTrue(response_json == new_album)

    def test_get_all_albums(self):
        response = self.app.get('{}/albums/all'.format(self.url_prefix))
        response_json = response.get_json()

        print(json.dumps(response_json, indent=4))

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.is_json)
        self.assertTrue(type(response_json) == list)

    def test_update_albums(self):
        # Create at least one new album first
        new_album = dict(title="Cover Me In Sunshine",
                         upc="00000000000111",
                         artwork_file="https://cdn.coolcompany.io/test.jpg",
                         release_date="2021-01-01",
                         stores=["spotify", "apple", "youtube"],
                         tracks=[
                             dict(title="Cover Me In Sunshine",
                                  version="Studio Edit",
                                  explicit=False,
                                  isrc="TEST000000001",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                             dict(title="Cover Me In Dirt",
                                  version="Studio Edit",
                                  explicit=True,
                                  isrc="TEST000000002",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                             dict(title="Cover Me In Paint",
                                  version="Studio Edit",
                                  explicit=False,
                                  isrc="TEST000000003",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                         ])
        response = self.create_album(**new_album)

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        response = self.app.get('{}/albums/all'.format(self.url_prefix))
        response_json = response.get_json()

        # Update tracks one by one
        for a in response_json:
            self.pp(a)
            new_title = "{} UPDATED TITLE".format(a["title"])
            payload = json.dumps(dict(title=new_title, release_date="2021-11-11"))
            self.app.put(a['uri'], headers={"Content-Type": "application/json"}, data=payload)

        # Get all albums again and see if all album names got updated
        response = self.app.get('{}/albums/all'.format(self.url_prefix))
        response_json = response.get_json()

        for a in response_json:
            self.pp(a)
            updated_title = a["title"]
            updated_release_date = a["release_date"]
            self.assertTrue("UPDATED TITLE" in updated_title)
            self.assertTrue(updated_release_date == "2021-11-11")

    def test_delete_albums(self):
        # Create at least one new album first
        new_album = dict(title="Cover Me In Sunshine",
                         upc="00000000000111",
                         artwork_file="https://cdn.coolcompany.io/test.jpg",
                         release_date="2021-01-01",
                         stores=["spotify", "apple", "youtube"],
                         tracks=[
                             dict(title="Cover Me In Sunshine",
                                  version="Studio Edit",
                                  explicit=False,
                                  isrc="TEST000000001",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                             dict(title="Cover Me In Dirt",
                                  version="Studio Edit",
                                  explicit=True,
                                  isrc="TEST000000002",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                             dict(title="Cover Me In Paint",
                                  version="Studio Edit",
                                  explicit=False,
                                  isrc="TEST000000003",
                                  audio_file="https://cdn.coolcompany.io/test.wav",
                                  artists=[dict(name="Pink")]),
                         ])
        response = self.create_album(**new_album)

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.is_json)

        response = self.app.get('{}/albums/all'.format(self.url_prefix))
        response_json = response.get_json()

        # Delete albums one by one
        for a in response_json:
            self.pp(a)
            response = self.app.delete(a['uri'])
            self.assertTrue(response.status_code == 204)

        # Check that no albums are left
        response = self.app.get('{}/albums/all'.format(self.url_prefix))
        response_json = response.get_json()
        self.assertFalse(len(response_json))

    @staticmethod
    def pp(json_to_print):
        print(json.dumps(json_to_print, indent=4))

    def create_artist(self, artist_name):
        payload = json.dumps(dict(name=artist_name))
        return self.app.post("{}/artists/new".format(self.url_prefix),
                             headers={"Content-Type": "application/json"},
                             data=payload)

    def create_track(self, title, version, explicit, isrc, audio_file, artists):
        payload = json.dumps(dict(
            title=title,
            version=version,
            explicit=explicit,
            isrc=isrc,
            audio_file=audio_file,
            artists=artists,
        ))
        return self.app.post("{}/tracks/new".format(self.url_prefix),
                             headers={"Content-Type": "application/json"},
                             data=payload)

    def create_album(self, title, upc, artwork_file, release_date, stores, tracks):
        payload = json.dumps(dict(
            title=title,
            upc=upc,
            artwork_file=artwork_file,
            release_date=release_date,
            stores=stores,
            tracks=tracks,
        ))
        return self.app.post("{}/albums/new".format(self.url_prefix),
                             headers={"Content-Type": "application/json"},
                             data=payload)

    @staticmethod
    def create_stores():
        for store in StoreEnum:
            db_session.add(Store(store))
        db_session.commit()
