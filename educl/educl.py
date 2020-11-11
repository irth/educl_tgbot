import requests
from bs4 import BeautifulSoup

URL = "https://edukacja.pwr.wroc.pl"
INDEX_URL = URL + "/EdukacjaWeb/studia.do"
LOGIN_PATH = "/EdukacjaWeb/logInUser.do"
LOGIN_URL = URL + LOGIN_PATH


def bs(response):
    return BeautifulSoup(response.content, 'html.parser')


class EduCL:
    def __init__(self):
        self._session = None
        self._logged_in = False
        self._last_messages_url = ""

    def _get_messages_url(self, soup):
        return URL + soup.find('a', title="Wiadomości")['href']

    def login(self, user, password):
        self._session = requests.session()

        # get the tokens and cookies
        r = self._session.get(INDEX_URL)
        form = bs(r).find('form', action=LOGIN_PATH)
        hidden = {}
        for hidden_field in form.find_all('input', type='hidden'):
            hidden[hidden_field["name"]] = hidden_field["value"]
        # log in
        r = self._session.post(LOGIN_URL, data={
            "login": user,
            "password": password,
            **hidden,
        })

        soup = bs(r)
        success = soup.find('td', class_='ZALOGOWANY_GRAF') is not None
        if success:
            self._last_messages_url = self._get_messages_url(bs(r))
            self._logged_in = True
        return success

    def fetch_messages(self):
        if not self._logged_in:
            raise Exception("Not logged in")
        r = self._session.get(self._last_messages_url)
        s = bs(r)
        self._last_messages_url = self._get_messages_url(s)

        messages_table = s.find('table', class_='KOLOROWA').find_all('tr')
        messages_info = []
        for tr in messages_table[1:]:
            i = [td.text.strip() for td in tr.find_all('td')]
            if len(i) != 5:
                continue
            link = "https://edukacja.pwr.wroc.pl" + tr.find('a')['href']
            messages_info.append(Message(
                self,
                author=i[1],
                topic=i[2],
                priority=i[3],
                timestamp=i[4],
                link=link))
        return messages_info


class Message():
    def __init__(self, educl, author, topic, priority, timestamp, link):
        self._educl = educl
        self.author = author
        self.topic = topic
        self.priority = priority
        self.timestamp = timestamp
        self.link = link

    def __repr__(self):
        return "<[%s, %s] %s - %s>" % (self.timestamp, self.priority, self.author, self.topic)

    def fetch_contents(self):
        r = self._educl._session.get(self.link)
        soup = bs(r)
        self._educl._last_messages_url = self._educl._get_messages_url(soup)
        for tr in soup.find('table', class_='KOLOROWA').find_all('tr'):
            tds = tr.find_all('td')
            if "Treść:" in tds[0].text:
                return tds[1].text.strip()
