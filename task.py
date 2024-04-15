import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random
import time
import mimetypes


visited_urls = set()
to_visit_urls = []
domain = ""
external_domains = set()
unique_documents = set()

stats = {
    "total_pages": 0,
    "all_links": 0,
    "internal_links": 0,
    "external_links": 0,
    "broken_links": 0,
    "internal_subdomains": 0,
    "external_resources_links": 0,
    "unique_external_resources": 0,
    "unique_documents_links": 0,
    "subdomains": set(),
    "external_domains": set(),
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


internal_subdomains = set()

#is internal (url): Определить, относится ли URL к тому же домену или поддомену, что и первоначальный целевой сайт.
def is_internal(url):
    return urlparse(url).netloc == domain or urlparse(url).netloc in internal_subdomains

#add subdomain (url): Если это не основной домен, добавьте поддомен во внутреннюю коллекцию поддоменов.
def add_subdomain(url):
    subdomain = urlparse(url).netloc
    if subdomain != domain:
        internal_subdomains.add(subdomain)
        


def is_document(link):
    link_type, _ = mimetypes.guess_type(link)
    return link_type is not None

            
def crawl(url, depth):
    global domain
    if url in visited_urls or not url.startswith("http") or depth > 1:
        return
    try:
        response = requests.get(url, headers=headers, timeout=5)  # 直接使用requests.get
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            visited_urls.add(url)
            stats["total_pages"] += 1
            
            links = soup.find_all('a', href=True)
            stats["all_links"] += len(links)
            for link in links:
                absolute_link = urljoin(url, link['href'])
                if is_internal(absolute_link):
                    stats["internal_links"] += 1
                    add_subdomain(absolute_link)
                    if absolute_link not in visited_urls:
                        to_visit_urls.append((absolute_link, depth + 1))
                else:
                    stats["external_links"] += 1
                    external_domains.add(urlparse(absolute_link).netloc)
                    if is_document(absolute_link) and absolute_link not in unique_documents:
                        unique_documents.add(absolute_link)
                        stats["unique_documents_links"] += 1
        else:
            stats["broken_links"] += 1
    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")
        stats["broken_links"] += 1
    time.sleep(random.randint(1, 3))  # 适当调整等待时间

    
def start_crawl(start_url):
    global domain
    domain = urlparse(start_url).netloc
    to_visit_urls.append((start_url, 1))  # 开始URL和初始深度
    while to_visit_urls:
        current_url, depth = to_visit_urls.pop(0)  # FIFO队列
        crawl(current_url, depth)
    
    # 更新统计数据
    stats["internal_subdomains"] = len(internal_subdomains)
    stats["external_resources_links"] = stats["external_links"]
    stats["unique_external_resources"] = len(external_domains)

# start_url = input("Enter Link: ")  # 目标网站。
start_url = "https://spbu.ru/"  
start_crawl(start_url)


print(f"Total pages crawled: {stats['total_pages']}")
print(f"All links found: {stats['all_links']}")
print(f"Internal links found: {stats['internal_links']}")
print(f"External links found: {stats['external_links']}")
print(f"Broken links found: {stats['broken_links']}")
print(f"Internal subdomains found: {stats['internal_subdomains']}")
print(f"External resources links: {stats['external_resources_links']}")
print(f"Unique external resources: {stats['unique_external_resources']}")
print(f"Unique documents (doc, docx, pdf) links: {stats['unique_documents_links']}")