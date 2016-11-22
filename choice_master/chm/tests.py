from unittest import TestCase
from os import path

from .admin import XMLFileAdmin
from .messages import LoadQuestionsMessageManager
from .similarity import is_similar
from .xml import XMLParser
from . import factories
from . import models
from choice_master.settings import BASE_DIR

from django.contrib.auth.models import User
from django.urls import reverse
from lxml import etree

import random
import string


class Request():
    """
    A Request toy to use in load_questions
    Note that load_question only needs a session duplicates list
    """
    def __init__(self, sess=[]):
        self.session = dict()
        self.session['duplicates'] = sess


# This function is defined here for convinience
def random_string(length):
    list_of_chars = [random.choice(string.ascii_uppercase)
                     for _ in range(length)]
    return "".join(list_of_chars)


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


class TestAdministratorLoadingQuestions(TestCase):
    """
    Testing loading xml files as admin functionality.

    Como administrador quiero cargar preguntas al sistema para un tema dado
    =======================================================================

    Criterios de aceptación:
    ------------------------

    - El superusuario debe poder cargar nuevas preguntas al sistema.

    - Las preguntas deben tener un formato XML.

    - Cuando se carga una pregunta el sistema debe revisar alguna métrica para
      buscar similitud con otra preguntas previamente cargadas.

    - Los archivos de preguntas pueden tener más de una pregunta posible.

    - Las preguntas se cargan con distintas opciones (multiple-choice) y una
      respuesta entre dichas opciones.

    - Se debe definir un esquema XML fijo para las preguntas y un esquema de
      validación xsd.
    """

    def setUp(self):
        """ Set up for load_question testing"""
        cases = 100
        max_length = 30
        answers_length = 10

        self.request = Request()

        self.data_list = []
        for x in range(cases):
            answers = []
            for x in range(answers_length - 1):
                answers.append(
                    {'text': random_string(max_length),
                     'is_correct': random.choice([False, True])})

            # Just in case, add a correct one
            answers.append({'text': 'correct', 'is_correct': True})

            data = {
                'subject': random_string(max_length),
                'topic': random_string(max_length),
                'question': random_string(max_length),
                'answers': answers
            }
            self.data_list.append(data)

            name = random_string(max_length)
            subject = factories.SubjectFactory.create(name=name)
            topic = factories.TopicFactory.create(subject=subject)

            text = random_string(max_length)
            question = factories.QuestionFactory.create(text=text,
                                                        topic=topic)
            factories.AnswerFactory.create_batch(answers_length,
                                                 question=question)

    def test_load_valid_question(self):
        """Test the case where the question is valid"""

        for data in self.data_list:

            subject = factories.SubjectFactory.create(name=data['subject'])
            topic = factories.TopicFactory.create(name=data['topic'],
                                                  subject=subject)

            # Create an empty question manager
            mm = LoadQuestionsMessageManager()

            # Run the code to be tested
            XMLFileAdmin.load_question(data, mm, self.request)

            self.assertEquals(mm.no_subject, [])
            self.assertEquals(mm.no_topic, [])
            self.assertEquals(mm.validation_error, [])
            self.assertEquals(len(mm.added), 1)
            self.assertEquals(mm.added[0].text, data['question'])
            queryset = models.Question.objects.filter(text=data['question'],
                                                      topic=topic)
            self.assertEquals(len(queryset), 1)
            for ans in data['answers']:
                text = ans['text']
                is_correct = ans['is_correct']
                queryset = models.Answer.objects.filter(text=text,
                                                        is_correct=is_correct)

                exists = queryset.exists()
                self.assertTrue(exists)

    def test_load_no_subject_question(self):
        """Test the case where the Subject does not exists"""
        for data in self.data_list:

            # Create an empty question manager
            mm = LoadQuestionsMessageManager()

            # Run the code to be tested
            XMLFileAdmin.load_question(data, mm, self.request)

            self.assertEquals(len(mm.no_subject), 1)
            self.assertEquals(len(mm.no_subject[0]), 2)
            self.assertEquals(mm.no_subject[0][1], (data['question']))
            self.assertEquals(mm.no_topic, [])
            self.assertEquals(mm.validation_error, [])
            self.assertEquals(mm.added, [])
            queryset = models.Question.objects.filter(text=data['question'])
            self.assertEquals(len(queryset), 0)

            for ans in data['answers']:
                text = ans['text']
                is_correct = ans['is_correct']
                queryset = models.Answer.objects.filter(text=text,
                                                        is_correct=is_correct)
                exists = queryset.exists()
                self.assertFalse(exists)

    def test_load_no_topic_question(self):
        """Test the case where the Topic does not exists"""
        for data in self.data_list:

            factories.SubjectFactory.create(name=data['subject'])

            # Create an empty question manager
            mm = LoadQuestionsMessageManager()

            # Run the code to be tested
            XMLFileAdmin.load_question(data, mm, self.request)

            self.assertEquals(len(mm.no_topic), 1)
            self.assertEquals(len(mm.no_topic[0]), 2)
            self.assertEquals(mm.no_topic[0][1], (data['question']))
            self.assertEquals(mm.no_subject, [])
            self.assertEquals(mm.validation_error, [])
            self.assertEquals(mm.added, [])
            queryset = models.Question.objects.filter(text=data['question'])
            self.assertEquals(len(queryset), 0)

            for ans in data['answers']:
                text = ans['text']
                is_correct = ans['is_correct']
                queryset = models.Answer.objects.filter(text=text,
                                                        is_correct=is_correct)
                exists = queryset.exists()
                self.assertFalse(exists)

    def test_load_exists_question(self):
        """Test the case where the question already exists"""
        for data in self.data_list:

            subject = factories.SubjectFactory.create(name=data['subject'])
            topic = factories.TopicFactory.create(name=data['topic'],
                                                  subject=subject)

            factories.QuestionFactory.create(text=data['question'],
                                             topic=topic)
            # Create an empty question manager
            mm = LoadQuestionsMessageManager()

            # Run the code to be tested
            XMLFileAdmin.load_question(data, mm, self.request)
            self.assertEquals(len(mm.validation_error), 1)
            self.assertEquals(len(mm.validation_error[0]), 2)
            self.assertEquals(len(mm.validation_error[0][0].messages), 1)
            self.assertEquals(mm.validation_error[0][0].messages[0],
                              'The question already exists')
            self.assertEquals(mm.validation_error[0][1], data['question'])
            self.assertEquals(mm.no_topic, [])
            self.assertEquals(mm.no_subject, [])
            self.assertEquals(mm.added, [])
            queryset = models.Question.objects.filter(text=data['question'],
                                                      topic=topic)

            self.assertEquals(len(queryset), 1)

            for ans in data['answers']:
                # It might seem confusing given that the answers might be the
                # same to test weather or not
                text = ans['text']
                is_correct = ans['is_correct']
                queryset = models.Answer.objects.filter(text=text,
                                                        is_correct=is_correct)
                exists = queryset.exists()
                self.assertFalse(exists)

    def test_load_similar_question(self):
        """Test the case where the similar question already exists"""
        i = 1
        for data in self.data_list:
            subject = factories.SubjectFactory.create(name=data['subject'])
            topic = factories.TopicFactory.create(name=data['topic'],
                                                  subject=subject)
            text = data['question']
            text = text[:-1] + "a"
            factories.QuestionFactory.create(text=text, topic=topic)
            # Create an empty question manager
            mm = LoadQuestionsMessageManager()

            # Run the code to be tested
            XMLFileAdmin.load_question(data, mm, self.request)
            self.assertEquals(len(self.request.session['duplicates']), i)
            i = i + 1
            self.assertEquals(mm.no_topic, [])
            self.assertEquals(mm.no_subject, [])
            self.assertEquals(mm.added, [])
            queryset = models.Question.objects.filter(text=data['question'],
                                                      topic=topic)

            self.assertEquals(len(queryset), 0)

            for ans in data['answers']:
                # It might seem confusing given that the answers might be the
                # same to test weather or not
                text = ans['text']
                is_correct = ans['is_correct']
                queryset = models.Answer.objects.filter(text=text,
                                                        is_correct=is_correct)
                exists = queryset.exists()
                self.assertFalse(exists)


class TestSimilarity(TestCase):
    """
    Testing similarity function.

    Como administrador quiero cargar preguntas al sistema para un tema dado
    =======================================================================

    Criterios de aceptación:
    ------------------------

    - Cuando se carga una pregunta el sistema debe revisar alguna métrica para
      buscar similitud con otras preguntas previamente cargadas. (only the
      metric will be tested here)
    """

    def setUp(self):
        """Set up for similarity testing"""

        # It has two list of dicts, one for similar strings
        # and another that are not
        self.similar = []
        self.not_similar = []
        for i in range(1, 50):
            # Create two strings that we are sure that are similar
            str1_similar = random_string(10)
            str2_similar = "p" + str1_similar + "d"
            self.similar.append({'fst': str1_similar, 'snd': str2_similar})
            # Create two strings that we are sure that are not similar
            str1_not_similar = random_string(50)
            str2_not_similar = "bla" + str1_not_similar[5:10] + "maaaal"
            self.not_similar.append({
                                    'fst': str1_not_similar,
                                    'snd': str2_not_similar,
                                    })

    def test_is_similar(self):
        """Test the case where the strings to compare are similar"""
        for i in range(1, 30):
            fst_similar = self.similar[i]['fst']
            snd_similar = self.similar[i]['snd']
            self.assertIs(is_similar(fst_similar, snd_similar), True)

    def test_is_not_similar(self):
        """Test the case where the strings to compare are not similar"""
        for i in range(1, 30):
            fst_not_similar = self.not_similar[i]['fst']
            snd_not_similar = self.not_similar[i]['snd']
            self.assertIs(is_similar(fst_not_similar, snd_not_similar), False)


class TestXSD(TestCase):
    """
    Testing XSD schema.

    Como administrador quiero cargar preguntas al sistema a travéz de un
    documento XML, debe adaptarse al schema xsd implementado. Lo último es
    lo que se testea aquí.
    =======================================================================

    Criterios de aceptación:
    ------------------------

    - El archivo XML puede tener varias preguntas, cada una de ellas tiene una
    Materia (subject)
    y un tema (topic) también tiene el texto que la describe y respuestas. Debe
    haber, al menos,
    una respuesta correcta.
    """
    # XSD schema path to validate the xml
    SCHEMA_PATH = path.join(BASE_DIR, 'static', 'xml_files', 'question.xml')
    # XML file path with a valid question correspondingly with xsd schema
    # defined
    VALID_XML_PATH = path.join(
                                BASE_DIR,
                                'static',
                                'xml_files',
                                'test',
                                'valid_question.xml')
    # XML file path with a question does not have a topic attribute
    XML_WITHOUT_TOPIC_PATH = path.join(
                                        BASE_DIR,
                                        'static',
                                        'xml_files',
                                        'test',
                                        'without_topic.xml')
    # XML file path with a question does not have a subject attribute
    XML_WITHOUT_SUBJECT_PATH = path.join(
                                        BASE_DIR,
                                        'static',
                                        'xml_files',
                                        'test',
                                        'without_subject.xml')
    # XML file path with a question does not have a any correct answer
    XML_WITHOUT_CORRECT_PATH = path.join(
                                        BASE_DIR,
                                        'static',
                                        'xml_files',
                                        'test',
                                        'without_correct.xml')

    def setUp(self):
        """Set up for XSD schema validation testing"""
        with open(self.SCHEMA_PATH, "r") as f:
            xmlschema_doc = etree.parse(f)
        self.schema = etree.XMLSchema(xmlschema_doc)

        with open(self.VALID_XML_PATH, "r") as v:
            self.valid_xml_file = etree.parse(v)

        with open(self.XML_WITHOUT_TOPIC_PATH, "r") as t:
            self.without_topic_xml_file = etree.parse(t)

        with open(self.XML_WITHOUT_SUBJECT_PATH, "r") as s:
            self.without_subject_xml_file = etree.parse(s)

        with open(self.XML_WITHOUT_CORRECT_PATH, "r") as c:
            self.without_correct_xml_file = etree.parse(c)

    def test_valid_schema_from_xsd(self):
        """Test the case where the xml file is valid"""

        self.assertIs(self.schema.validate(self.valid_xml_file), True)

    def test_without_topic_from_xsd(self):
        """
        Test the case where the xml file is invalid.
        The questions does not have topic.
        """
        self.assertIs(self.schema.validate(self.without_topic_xml_file), False)

    def test_without_subject_from_xsd(self):
        """
        Test the case where the xml file is invalid.
        The questions does not have subject.
        """
        self.assertIs(
                    self.schema.validate(self.without_subject_xml_file),
                    False)

    def test_without_correct_from_xsd(self):
        """
        Test the case where the xml file is invalid.
        The questions does not have any correct answer.
        """
        self.assertIs(
                    self.schema.validate(self.without_correct_xml_file),
                    False)


class TestXMLParser(TestCase):
    """
    Testing XML Parser.

    Como administrador quiero cargar preguntas al sistema a travéz de un
    documento XML, debe adaptarse al schema xsd implementado. Aquí se testea
    que el documente sea parseado correctamente.
    ==========================================================================

    Criterios de aceptación:
    ------------------------

    - El archivo XML puede tener varias preguntas, cada una de ellas tiene una
    Materia (subject) y un tema (topic) también tiene el texto que la describe
    y respuestas. Debe haber, al menos, una respuesta correcta.
    """
    # Empty xml file path
    EMPTY_TO_PARSE_PATH = path.join(
                                    BASE_DIR,
                                    'static',
                                    'xml_files',
                                    'test',
                                    'empty_to_parse.xml')
    # xml file with a normal format: questions, answers, etc. path
    NORMAL_TO_PARSE_PATH = path.join(
                                    BASE_DIR,
                                    'static',
                                    'xml_files',
                                    'test',
                                    'normal_to_parse.xml')

    def test_parse_questions_from_empty(self):
        """Test the case where the xml file has not questions"""
        try:
            with open(self.EMPTY_TO_PARSE_PATH, "rb") as f:
                self.empty_file = XMLParser(f)
                # No questions
                for question in self.empty_file.parse_questions():
                    self.assertTrue(False)
        except etree.XMLSyntaxError as err:
            # The xml file is empty
            self.assertTrue(True)

    def test_parse_questions_from_normal(self):
        """
            Test the normal case. When the xml file has one or more
            questions with one or more answers.
        """
        with open(self.NORMAL_TO_PARSE_PATH, "rb") as v:
            self.normal_file = XMLParser(v)
            # We need a list of Questions for convinience
            questions_parsed = list()
            for question in self.normal_file.parse_questions():
                questions_parsed.append(question)

        # Check how many questions are in the file
        data1 = questions_parsed[0]
        # Check the subject, topic and text question
        self.assertEquals(data1['subject'], "Algebra")
        self.assertEquals(data1['topic'], "subesp")
        self.assertEquals(data1['question'], "Cuanto es 2 mas 2?")

        # Check answers
        # Check the correspondency with answers
        answer1 = data1['answers'][0]
        self.assertEquals(answer1['text'], "3")
        self.assertFalse(answer1['is_correct'])

        answer2 = data1['answers'][1]
        self.assertEquals(answer2['text'], "1")
        self.assertFalse(answer2['is_correct'])

        answer3 = data1['answers'][2]
        self.assertEquals(answer3['text'], "2")
        self.assertFalse(answer3['is_correct'])

        answer4 = data1['answers'][3]
        self.assertEquals(answer4['text'], "42")
        self.assertTrue(answer4['is_correct'])

        answer5 = data1['answers'][4]
        self.assertEquals(answer5['text'], "5")
        self.assertFalse(answer5['is_correct'])

        data2 = questions_parsed[1]
        # Check the subject, topic and text question
        self.assertEquals(data2['subject'], "AM2")
        self.assertEquals(data2['topic'], "Series de Taylor")
        self.assertEquals(
                        data2['question'],
                        "Todos los patos son de color rojo?")

        # Check answers
        # Check the correspondency with answers
        answer1 = data2['answers'][0]
        self.assertEquals(answer1['text'], "No")
        self.assertTrue(answer1['is_correct'])

        answer2 = data2['answers'][1]
        self.assertEquals(answer2['text'], "Si")
        self.assertFalse(answer2['is_correct'])

        data3 = questions_parsed[2]
        # Check the subject, topic and text question
        self.assertEquals(data3['subject'], "Probabilidad")
        self.assertEquals(data3['topic'], "Bayes")
        self.assertEquals(data3['question'], "Son estas respuestas correctas?")

        # Check answers
        # Check the correspondency with answers
        answer1 = data3['answers'][0]
        self.assertEquals(answer1['text'], "Si")
        self.assertTrue(answer1['is_correct'])

        answer2 = data3['answers'][1]
        self.assertEquals(answer2['text'], "Obvio que sí")
        self.assertTrue(answer2['is_correct'])


class TestVotingOneVote(TestCase):
    """Test voting funcionality"""

    def setUp(self):
        subject = models.Subject.objects.create(name='S')
        topic = models.Topic.objects.create(name='T', subject=subject)
        self.question = models.Question.objects.create(text='?', topic=topic)

    def test_vote_one(self):
        self.assertEqual(self.question.difficulty, 1)
        self.question.vote(1)
        self.question.save()
        self.assertEqual(self.question.difficulty, 1)

    def test_vote_two(self):
        self.question.vote(2)
        self.question.save()
        self.assertEqual(self.question.difficulty, 2)

    def test_vote_three(self):
        self.question.vote(3)
        self.question.save()
        self.assertEqual(self.question.difficulty, 3)

    def test_vote_four(self):
        self.question.vote(4)
        self.question.save()
        self.assertEqual(self.question.difficulty, 4)

    def test_vote_five(self):
        self.question.vote(5)
        self.question.save()
        self.assertEqual(self.question.difficulty, 5)
