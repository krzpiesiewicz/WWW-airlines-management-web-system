import datetime
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from linie_lotnicze.models import Plane, Flight, Airport, Crew, PilotInCommand

def create_data():

    a1 = Airport(name="a1")
    a1.save()
    a2 = Airport(name="a2")
    a2.save()

    start_dt = datetime.datetime(2018, 1, 1)

    p = PilotInCommand(first_names="Jan", last_name="Kowalski")
    p.save()
    c = Crew(pilot_in_command=p)
    c.save()
    p = PilotInCommand(first_names="Jan", last_name="Nowak")
    p.save()
    c = Crew(pilot_in_command=p)
    c.save()

    for i in range(2):
        p = Plane(code=i, seat_count=20)
        p.save()
        f = Flight(plane=p, start_airport=a1, dest_airport=a2, start_time=start_dt,
                   dest_time=start_dt + timedelta(hours=10))
        f.save()
        start_dt += timedelta(hours=5)

class RestApiTest(TestCase):

    username = "user"
    password = "123"

    def setUp(self):
        create_data();
        User.objects.create_user(username=self.username, password=self.password)

    # GETTING CREWS' DATA
    def testGettingCrews(self):
        res = self.client.post('/ajax/crews/', data={'username': self.username, 'password': self.password})
        self.assertEqual(res.status_code, 200)

        expected = b'{"crews": ' +\
        b'{"1": {"pilot_firstnames": "Jan", "pilot_lastname": "Kowalski"}, ' +\
        b'"2": {"pilot_firstnames": "Jan", "pilot_lastname": "Nowak"}}}'
        self.assertEqual(res.content, expected)

    # ASSIGNING A FREE CREW TO A FLIGHT
    def CorrectCrewAssigning(self):
        res = self.client.post('/ajax/save-flight/',
                               data={'username': self.username, 'password': self.password,
                                     'crew_id': 1, 'flight_id': 1})
        self.assertEqual(res.status_code, 200)

    # ASSIGNING A FREE CREW TO TWO FLIGHTS BEING HELD AT THE SAME MOMENT
    def WrongCrewAssigning(self):
        f = Flight.objects.get(id=1)
        f.crew_id = 1
        f.save()
        res = self.client.post('/ajax/save-flight/',
                               data={'username': self.username, 'password': self.password,
                                     'crew_id': 1, 'flight_id': 2})
        self.assertEqual(res.status_code, 403)

# ADDING PASSENGERS TO FLIGHT
class SeleniumTickets(StaticLiveServerTestCase):

    username = "USER"
    password = "USER123"

    def setUp(self):
        User.objects.create_superuser(username=self.username, password=self.password, email="user@example.com")
        create_data()

    def test(self):
        h = webdriver.WebDriver()
        def wait():
            return WebDriverWait(h, 10)

        h.get(self.live_server_url + '/admin/login/?next=/flight/1/')

        wait().until(EC.presence_of_element_located((By.ID, 'id_username')))
        wait().until(EC.presence_of_element_located((By.ID, 'id_password')))
        wait().until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="submit"]')))
        h.find_element_by_css_selector('#id_username').send_keys(self.username)
        h.find_element_by_css_selector('#id_password').send_keys(self.password)
        h.find_element_by_css_selector('input[type="submit"]').click()

        wait().until(EC.presence_of_element_located((By.NAME, 'number_of_seats')))
        wait().until(EC.presence_of_element_located((By.NAME, 'passenger')))
        wait().until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="submit"]')))
        h.find_element_by_name('number_of_seats').send_keys("1")
        h.find_element_by_name('passenger').send_keys("User Userski")
        h.find_element_by_css_selector('input[type="submit"]').click()

        wait().until(EC.presence_of_element_located((By.XPATH, "//li[text()='User Userski']")))

        h.close()

# CHECKING THE ERROR IN ASSIGNING ONE CREW TO TWO FLIGHTS BE HELD AT THE SAME TIME (REST)
class SeleniumCrews(StaticLiveServerTestCase):

    username = "User"
    password = "123456"

    def setUp(self):
        User.objects.create_user(username=self.username, password=self.password)
        create_data()

    def test(self):
        h = webdriver.WebDriver()
        def wait():
            return WebDriverWait(h, 10)

        h.get(self.live_server_url + '/static/crews.html')

        wait().until(EC.presence_of_element_located((By.ID, 'login')))
        login_button = h.find_element_by_css_selector('#login')

        wait().until(EC.presence_of_element_located((By.ID, 'logout')))
        logout_button = h.find_element_by_css_selector('#logout')

        def login():
            self.assertTrue(login_button.is_displayed())
            h.find_element_by_css_selector('#input-username').send_keys(self.username)
            h.find_element_by_css_selector('#input-password').send_keys(self.password)
            login_button.click()
            wait().until(EC.presence_of_element_located((By.ID, 'username')))
            name = h.find_element_by_css_selector('#username')
            wait().until(EC.visibility_of(name))
            self.assertEqual(name.text, self.username)

        def logout():
            wait().until(EC.visibility_of(logout_button))
            logout_button.click()
            wait().until(EC.visibility_of(login_button))

        login()

        wait().until(EC.presence_of_element_located((By.ID, 'flight-select')))
        wait().until(EC.presence_of_element_located((By.ID, 'flight-crew-select')))
        wait().until(EC.presence_of_element_located((By.ID, 'flight-save')))
        wait().until(EC.presence_of_element_located((By.ID, 'flight-save-log')))
        wait().until(EC.presence_of_element_located((By.ID, 'login')))

        flight_select = Select(h.find_element_by_css_selector('#flight-select'))
        flight_crew_select = Select(h.find_element_by_css_selector('#flight-crew-select'))
        flight_save = h.find_element_by_css_selector('#flight-save')
        flight_save_log = h.find_element_by_css_selector('#flight-save-log')

        # FIRST FLIGHT:
        wait().until(EC.element_to_be_clickable((By.ID, 'flight-select')))
        flight_select.select_by_value('1')

        wait().until(EC.element_to_be_clickable((By.ID, 'flight-crew-select')))
        flight_crew_select.select_by_value('1')

        wait().until(EC.element_to_be_clickable((By.ID, 'flight-save')))
        flight_save.click()

        wait().until(EC.visibility_of(flight_save_log))
        self.assertEqual(flight_save_log.text, "Saved.")

        # SECOND FLIGHT:
        wait().until(EC.element_to_be_clickable((By.ID, 'flight-select')))
        flight_select.select_by_value('2')

        wait().until(EC.element_to_be_clickable((By.ID, 'flight-crew-select')))
        flight_crew_select.select_by_value('1')

        wait().until(EC.element_to_be_clickable((By.ID, 'flight-save')))
        flight_save.click()

        wait().until(EC.visibility_of(flight_save_log))
        self.assertEqual(flight_save_log.text, "Not saved.")

        logout()
        h.close()