"""
Tests for app chm
"""
from .admin import XMLFileAdmin
from .messages import LoadQuestionsMessageManager
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class TestLogin(TestCase):
    """
    Testing login functinality

    Como usuario quiero poder ingresar al sistema con mis credenciales de
    usuario.
    =====================================================================

    Criterios de aceptación:
    ------------------------
        - Los usuarios registrados deben poder acceder al sistema mediante un
          formulario de login donde ingresen su nombre de usuario y contraseña.
        - En caso de que el usuario exista y los datos sean correctos el
          usuario accederá a la aplicación.
        - Si hubo algún error en el proceso de login se le indicará al usuario.
    """

    def setUp(self):
        """
        Set up environment for TestLogin
            - create a user
        """
        # save this password, as it will be salted and hashed
        self.valid_user_password = 'test_passwd'
        self.valid_user = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password=self.valid_user_password,
        )
        self.account_login_url = reverse('account_login')
        self.index_url = reverse('index')

    def test_anonymous_user_is_redirected_to_login(self):
        """Test that anonymous can not see index.html"""

        # given I am not authenthicated
        user = AnonymousUser()

        # when I go to the index url
        response = self.client.get(self.index_url, follow=True)

        # then I get redirected to the login page
        self.assertRedirects(response, self.account_login_url)

    def test_login_redirects_to_index(self):
        """
        Test successful login scenario.
        When user provides a valid username and password combination, then she
        should be redirected to the home page.
        """

        # given I am a registered user
        user = self.valid_user

        # when I provide my credentials
        data = {'login': user.username, 'password': self.valid_user_password}
        response = self.client.post(self.account_login_url, data, follow=True)

        # then I am redirected to the index page
        self.assertRedirects(response, self.index_url)

        # and I am authenticated
        self.assertFalse(response.context['user'].is_anonymous())

    def test_login_wrong_username(self):
        """
        Test unsuccessful login scenario.
        When user provides an invalid username then an error is shown.
        """
        # given I am a registered user
        user = self.valid_user

        # when I provide a wrong username
        data = {'login': 'NyP', 'password': self.valid_user_password}
        response = self.client.post(self.account_login_url, data, follow=True)

        # then I am not redirected to the index page
        self.assertEquals(response.redirect_chain, [])

        # and an error is shown
        form = response.context['form']
        expected_error = {
            '__all__': [
                'The username and/or password you specified are not correct.'
            ]
        }
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors, expected_error)

    def test_login_wrong_password(self):
        """
        Test unsuccessful login scenario
        When user provides an invalid password then an error is shown.
        """
        # given I am a registered user
        user = self.valid_user

        # when I provide a wrong passowrd
        data = {'login': user.username, 'password': 'NyP'}
        response = self.client.post(self.account_login_url, data, follow=True)

        # then I am not redirected to the index page
        self.assertEquals(response.redirect_chain, [])

        # and an error is shown
        form = response.context['form']
        expected_error = {
            '__all__': [
                'The username and/or password you specified are not correct.'
            ]
        }
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors, expected_error)


class TestRegisterNewUser(TestCase):
    """
    Testing register functinality

    Como usuario quiero poder registrarme en el sistema
    ===================================================

    Criterios de aceptación:
    ------------------------
        - Un nuevo usuario debe poder registrarse en el sistema.
        - Los campos que el usuario debe completar son:
            - Nombre de usuario,
            - contraseña y confirmación,
            - email.
        - El usuario debe ser notificado al registrarse correctamente.
    """

    def setUp(self):
        """ Set up for registration steps"""
        self.signup_url = reverse('account_signup')

    def test_register_successful(self):
        """ Test user is able to register"""

        # given my username is available
        self.assertFalse(User.objects.filter(username='NyP').exists())
        data = {
            'username': 'NyP',
            'email': 'NyP@NyP.com',
            'password1': 'p2-mm3.aFl$',
            'password2': 'p2-mm3.aFl$',
        }

        # when I fill the required data on the form
        response = self.client.post(self.signup_url, data, follow=True)

        # then I am registered to use the application
        self.assertTrue(User.objects.filter(username='NyP').exists())
        self.assertFalse(response.context['user'].is_anonymous())

        # and I see a message
        html = response.content.decode('utf-8')
        self.assertTrue('You signed up succesfully' in html)
