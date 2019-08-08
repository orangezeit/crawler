import requests
import json
from pyquery import PyQuery
import re
import os
import time


class InstagramCrawler:

    def __init__(self, username):

        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

        self.username = username
        self.person_id = None
        self.files = set()
        self.count = 0

    def get(self, url, params=None):

        try:
            response = requests.get(url, params, headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                print('status code:', response.status_code)
        except Exception as error:
            print(error)

    def parse_post(self, post):

        data = json.loads(PyQuery(self.get(post))('script[type="text/javascript"]').eq(3).text()[21:-1],
                          encoding='utf-8')['entry_data']['PostPage'][0]['graphql']['shortcode_media'][
            'edge_sidecar_to_children']

        for edge in data['edges']:

            if edge['node']['is_video']:
                self.files.add(edge['node']['video_url'])
            else:
                self.files.add(edge['node']['display_url'])

            self.count += 1

    def parse_main(self):

        profile = f'https://www.instagram.com/{self.username}'
        data = json.loads(PyQuery(self.get(profile))('script[type="text/javascript"]').eq(3).text()[21:-1],
                          encoding='utf-8')['entry_data']['ProfilePage'][0]

        self.person_id = data['logging_page_id'][12:]
        data = data['graphql']['user']['edge_owner_to_timeline_media']

        for edge in data['edges']:

            if edge['node']['__typename'] == 'GraphSidecar':

                self.parse_post(f"http://www.instagram.com/p/{edge['node']['shortcode']}")

            elif edge['node']['is_video']:

                post = f"http://www.instagram.com/p/{edge['node']['shortcode']}"
                self.files.add(
                    json.loads(PyQuery(self.get(post))('script[type="text/javascript"]').eq(3).text()[21:-1],
                               encoding='utf-8')['entry_data']['PostPage'][0]['graphql']['shortcode_media'][
                        'video_url'])
                self.count += 1

            else:

                self.files.add(edge['node']['display_url'])
                self.count += 1

        return data['page_info']['end_cursor'], data['page_info']['has_next_page']

    def parse_next(self, end_cursor):

        params = {'query_hash': 'f2405b236d85e8296cf30347c9f08c2a',
                  'variables': f'{{"id":"{self.person_id}","first":{12},"after":"{end_cursor}"}}'}
        html = self.get('https://www.instagram.com/graphql/query/', params)

        if html is None:
            print(self.person_id, end_cursor)
            return end_cursor, False

        data = json.loads(html, encoding='utf-8')['data']['user']['edge_owner_to_timeline_media']

        for edge in data['edges']:

            if edge['node']['__typename'] == 'GraphSidecar':
                self.parse_post(f"http://www.instagram.com/p/{edge['node']['shortcode']}")
            elif edge['node']['is_video']:
                self.files.add(edge['node']['video_url'])
                self.count += 1
            else:
                self.files.add(edge['node']['display_url'])
                self.count += 1

        return data['page_info']['end_cursor'], data['page_info']['has_next_page']

    def download(self):

        path = r'C:\Users\Jack\Pictures\Saved Pictures\Instagram\{:s}'.format(self.username)

        if not os.path.exists(path):
            os.makedirs(path)

        for file in self.files:

            try:
                response = requests.get(file, headers=self.headers)
                if response.status_code == 200:
                    file_name = re.search(r'\d+_\d+_\d+_n\.\w+', file).group()
                    with open('\\'.join([path, file_name]), 'wb') as f:
                        f.write(response.content)
                else:
                    print('status code:', response.status_code)
            except Exception as error:
                print(error)

    def crawl(self):

        end_cursor, has_next = self.parse_main()
        print('parsing...', self.count, 'links')

        while has_next:
            end_cursor, has_next = self.parse_next(end_cursor)
            print('parsing...', self.count, 'links')
            time.sleep(1)
            break

        print('parsed', self.count, 'links')
        self.download()


if __name__ == '__main__':

    """
    BASE_URL = 'https://www.instagram.com/accounts/login/'
    LOGIN_URL = BASE_URL + 'ajax/'

    USERNAME = '123'
    PASSWD = '456'

    session = requests.Session()
    session.headers = headers
    session.headers.update({'Referer': BASE_URL})

    req = session.get(BASE_URL)
    soup = BeautifulSoup(req.content, 'html.parser')
    body = soup.find('body')

    pattern = re.compile('window._sharedData')
    script = body.find("script", text=pattern)
    data = json.loads(script.get_text()[21:-1])

    csrf = data['config'].get('csrf_token')
    login_data = {'username': USERNAME, 'password': PASSWD}
    session.headers.update({'X-CSRFToken': csrf})
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    print(login.content)
    """

    ic = InstagramCrawler('diegoarnary')
    ic.crawl()





