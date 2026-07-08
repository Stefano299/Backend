from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='test@example.com',
            first_name='Mario',
            last_name='Rossi'
        )

    def test_anonymous_redirect(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("profile")}')

    def test_profile_page_accessible(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Il Mio Profilo')
        self.assertContains(response, 'Mario')
        self.assertContains(response, 'Rossi')

    def test_profile_update_post(self):
        self.client.login(username='testuser', password='Password123!')
        
        post_data = {
            'first_name': 'Luigi',
            'last_name': 'Verdi',
            'email': 'luigi@example.com',
            'indirizzo': 'Via Roma 10',
            'citta': 'Milano',
            'codice_postale': '20100',
            'numero_di_telefono': '1234567890'
        }
        
        response = self.client.post(reverse('profile'), data=post_data)
        self.assertRedirects(response, reverse('profile'))
        
        # Refresh from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Luigi')
        self.assertEqual(self.user.last_name, 'Verdi')
        self.assertEqual(self.user.email, 'luigi@example.com')
        self.assertEqual(self.user.indirizzo, 'Via Roma 10')
        self.assertEqual(self.user.citta, 'Milano')
        self.assertEqual(self.user.codice_postale, '20100')
        self.assertEqual(self.user.numero_di_telefono, '1234567890')



class SignupTests(TestCase):
    def test_signup_page_accessible(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crea Account')

    def test_signup_success_redirect_and_message(self):
        post_data = {
            'username': 'newuser',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        response = self.client.post(reverse('signup'), data=post_data)
        self.assertRedirects(response, reverse('login'))
        
        # Verify success message is present in the messages storage
        from django.contrib.messages import get_messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Registrazione completata con successo! Ora puoi effettuare l'accesso.")
        
        # Verify creation of user and Customer group assignment
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.groups.filter(name='Customer').exists())
