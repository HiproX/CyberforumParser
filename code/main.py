from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import concurrent.futures

class ParserCyberforum:
    '''Parser of topics with zero answers on the Cyberforum site'''
    def __init__(self):
        self.__driver = self.__get_ChromeDriver()
    def __enter__(self):
        return self;
    def __exit__(self, exc_type, exc_value, traceback):
        driver.quit()
    def __get_ChromeDriver(self):
        options = Options()
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        return webdriver.Chrome(options=options)
    def __initSoup(self, url):
        self.__driver.get(url)
        html_content = self.__driver.page_source
        return BeautifulSoup(html_content, 'html.parser')
    def run(self, url):
        soup = self.__initSoup(url)

        result = None
        
        them = soup.find('h1')
        if them:
            them = them.get_text().strip()
            result = {'them': them, 'posts': []}
            
            post_table = soup.find('tbody', {'id': lambda value: value and value.startswith('threadbits_forum_')})
            if post_table:
                post_row = post_table.find_all('tr', {'id':lambda value: value and value.startswith('vbpostrow_')})
                
                if post_row:
                    for post in post_row:
                        title = post.find('a', {'id': lambda value: value and value.startswith('thread_title_')}, href=True)
                        views = post.find('a', {'target': lambda value: value and value in '_blank'})
                        if title and views:
                            try:
                                views = int(views.get_text())
                            except ValueError:
                                continue;
                            if views == 0:
                                result['posts'].append({'title': title.get_text(), 'ref': title['href']})
        return result

def print_tree(d, indent=0):
    if isinstance(d, list):
        for value in d:
            print_tree(value, indent= 0)
    else:
        for key, value in d.items():
            print(' ' * indent + str(key))
            if isinstance(value, dict):
                print_tree(value, indent + 4)
            if isinstance(value, list):
                for item in value:
                    print_tree(item, indent + 4)
            else:
                print(' ' * (indent + 4) + str(value))

def thread_parse(url):
    parser = ParserCyberforum()
    return parser.run(url)
                
urls = ['https://www.cyberforum.ru/cpp/', 'https://www.cyberforum.ru/cpp-beginners/', 'https://www.cyberforum.ru/cpp-networks/',
       'https://www.cyberforum.ru/c/', 'https://www.cyberforum.ru/c-beginners/',
       'https://www.cyberforum.ru/python/', 'https://www.cyberforum.ru/python-tasks/', 'https://www.cyberforum.ru/python-beginners/',
       'https://www.cyberforum.ru/net-framework/', 'https://www.cyberforum.ru/csharp-net/', 'https://www.cyberforum.ru/csharp-beginners/']
res = []

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(thread_parse, url) for url in urls]
    res = [f.result() for f in concurrent.futures.as_completed(results)]

print_tree(res)