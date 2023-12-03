# Name: Jessica Ortega
# Course: CS 4250
# Date: December 2, 2023
# Time Spent: 

import requests
from bs4 import BeautifulSoup
from queue import Queue
from pymongo import MongoClient
from urllib.parse import urljoin

client = MongoClient('mongodb://localhost:27017/')
db = client.web_crawler
pages_collection = db.pages

def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1_tag = soup.find('h1', class_='cpp-h1')
    return h1_tag and h1_tag.get_text().strip() == 'Permanent Faculty'

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error retrieving HTML from {url}: {e}")
    return None

def store_page(url, html):
    pages_collection.insert_one({'url': url, 'html': html})

def parse_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    return [urljoin(base_url, link['href']) for link in links]

def crawler_thread(frontier, base_url):
    visited_urls = set()

    while not frontier.empty():
        url = frontier.get()

        if url not in visited_urls:
            visited_urls.add(url)

            html = fetch_html(url)
            if html:
                if target_page(html):
                    store_page(url, html)
                    return

                for link in parse_links(html, base_url):
                    if link not in visited_urls:
                        frontier.put(link)

if __name__ == "__main__":
    frontier = Queue()
    base_url = 'https://www.cpp.edu/sci/computer-science/index.shtml'
    frontier.put(base_url)

    crawler_thread(frontier, base_url)

    client.close()
