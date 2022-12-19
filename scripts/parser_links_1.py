import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama

# запускаем модуль colorama
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW


class ParsingLinks:
    def __init__(self):
        # инициализировать set's для внутренних и внешних ссылок (уникальные ссылки)
        self.internal_urls = set()
        self.external_urls = set()
        self.total_urls_visited = 0
        # запрос для перелистывания страницы
        self.new_urls = "https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json?pages.age.month=12&pages.age.year=2022&pages.direction=page&pages.number=5&pages.target.class=100&pages.target.id=5"
        self.headers = requests.utils.default_headers()
        self.headers.update(
            {
                'User-Agent': 'My User Agent 1.0',
            }
        )
        
    def is_valid(self, url):
        """
        Проверка url
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    def get_all_website_links(self, url):
        """
        Возвращает все найденные URL-адреса на `url, того же веб-сайта.
        """
        # все URL-адреса `url`
        urls = set()
        # доменное имя URL без протокола
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(url, headers=self.headers).content, "html.parser")
        
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # пустой тег href
                continue
            # присоединяемся к URL, если он относительный (не абсолютная ссылка)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # удалить параметры URL GET, фрагменты URL и т. д.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self.is_valid(href):
                # неверный URL
                continue
            if href in self.internal_urls:
                # уже в наборе
                continue
            if domain_name not in href:
                # внешняя ссылка
                if href not in self.external_urls:
                    print(f"{GRAY}[!] Внешняя ссылка: {href}{RESET}")
                    self.external_urls.add(href)
                continue
            print(f"{GREEN}[*] Внутреннея ссылка: {href}{RESET}")
            urls.add(href)
            self.internal_urls.add(href)
            
        requests.get(self.new_urls, headers=self.headers)
        return urls
    
    def crawl(self, url, max_urls):
        """
        Сканирует веб-страницу и извлекает все ссылки.
        Вы найдете все ссылки в глобальных переменных набора external_urls и internal_urls.
        параметры:
            max_urls (int): максимальное количество URL-адресов для сканирования, по умолчанию 30.
        """
        # global total_urls_visited
        self.total_urls_visited += 1
        print(f"{YELLOW}[*] Проверено: {url}{RESET}")
        links = self.get_all_website_links(url)
        for link in links:
            if self.total_urls_visited > max_urls:
                break
            self.crawl(link, max_urls=max_urls)
    
    # def clear_global_variables(self):
    #     clear.

obj = ParsingLinks()

def links_parser(max_urls: int = 0, input_url = 'https://www.volgograd.kp.ru/online/'):
# if __name__ == "__main__":
    # import argparse
    # """
    # parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    # parser.add_argument("url", help="The URL to extract links from.")
    # parser.add_argument("-m", "--max-urls", help="Number of max URLs to crawl, default is 30.", default=30, type=int)
        
    # args = parser.parse_args()
    # url = args.url
    # max_urls = args.max_urls
    # """
    # url = 'https://www.volgograd.kp.ru/online/'
    # max_urls = 30
    url = input_url
    max_urls = max_urls
    internal_urls = obj.internal_urls
    external_urls = obj.external_urls
    
    obj.crawl(url, max_urls=max_urls)
    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total External links:", len(external_urls))
    print("[+] Total URLs:", len(external_urls) + len(internal_urls))
    print("[+] Total crawled URLs:", max_urls)
    
    # domain_name = urlparse(url).netloc
    # # сохранить внутренние ссылки в файле
    # with open(f"{domain_name}_internal_links.txt", "w") as f:
    #     for internal_link in internal_urls:
    #         print(internal_link.strip(), file=f)
    # # сохранить внешние ссылки в файле
    # with open(f"{domain_name}_external_links.txt", "w") as f:
    #     for external_link in external_urls:
    #         print(external_link.strip(), file=f)
    
    return {"internal_urls": internal_urls, "external_urls": external_urls}