import unittest
from unittest.mock import patch
from portfolio_website import app, db, Photo, About, Contact

class TestPortfolioWebsite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to my Portfolio', response.data)

    def test_gallery_page(self):
        # Create some test photos
        photo1 = Photo(title='Photo 1', image_path='photo1.jpg')
        photo2 = Photo(title='Photo 2', image_path='photo2.jpg')
        db.session.add_all([photo1, photo2])
        db.session.commit()

        response = self.app.get('/gallery')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Photo 1', response.data)
        self.assertIn(b'Photo 2', response.data)

    def test_about_page(self):
        about = About(bio='I am a freelance photographer.')
        db.session.add(about)
        db.session.commit()

        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'I am a freelance photographer.', response.data)

    def test_contact_form(self):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, I would like to hire you.'
        }

        with patch('portfolio_website.send_email') as mock_send_email:
            response = self.app.post('/contact', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Thank you for your message!', response.data)
            mock_send_email.assert_called_with(data['name'], data['email'], data['message'])

    def test_theme_toggle(self):
        response = self.app.get('/')
        self.assertIn(b'<body class="light-theme">', response.data)

        response = self.app.get('/toggle_theme')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')

        response = self.app.get('/')
        self.assertIn(b'<body class="dark-theme">', response.data)

if __name__ == '__main__':
    unittest.main()