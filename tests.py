import unittest

from party import app
from model import db, example_data, connect_to_db


class PartyTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        """Test homepage shows party description."""

        result = self.client.get("/")
        self.assertIn("board games, rainbows, and ice cream sundaes", result.data)

    def test_no_rsvp_yet(self):
        """Test party address doesn't show before someone RSVPS."""

        result = self.client.get('/')
        self.assertEquals(200, result.status_code)
        self.assertIn("Please RSVP", result.data)
        self.assertNotIn("123 Magic Unicorn Way", result.data)

    def test_rsvp(self):
        """Test that RSVP details show after RSVP."""

        result = self.client.post("/rsvp",
                                  data={"name": "Jane",
                                        "email": "jane@jane.com"},
                                  follow_redirects=True)
        self.assertEquals(200, result.status_code)
        self.assertNotIn("Please RSVP", result.data)
        self.assertIn("123 Magic Unicorn Way", result.data)


class PartyTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['RSVP'] = False

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_games_before_rsvp(self):
        """Test that non-RSVP'd user cannot see games list."""

        result = self.client.get('/games', follow_redirects=True)
        self.assertEquals(200, result.status_code)
        self.assertIn("Please RSVP", result.data)
        self.assertNotIn('Apples to Apples', result.data)

    def test_games_after_rsvp(self):
        """Test that game info appears on the site."""

        self.client.post("/rsvp",
                         data={"name": "Jane",
                         "email": "jane@jane.com"},
                         follow_redirects=True)
        result = self.client.get('/games')
        self.assertEquals(200, result.status_code)
        self.assertIn('Apples to Apples', result.data)
        self.assertIn('hilarious comparisons', result.data)


if __name__ == "__main__":
    unittest.main()
