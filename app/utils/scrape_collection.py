import requests
from bs4 import BeautifulSoup

from flask import current_app as capp

def get_all_ids(url):
    page = requests.get(url, headers={'User-Agent': 'discogs_pyvy/1.0'}).text
    soup = BeautifulSoup(page, 'lxml')

    inputs = soup.find('input', {'id': 'jump_to_page_bottom'})
    if inputs:
        max_pages = int(inputs.attrs['max'])
        current_page = int(inputs.attrs['value'])
    else:
        max_pages = 1
        current_page = 1

    if max_pages > current_page:
        all_pages = [url + '?page=%d' % i for i in range(1, max_pages + 1)]
        ids = []
        for page in all_pages:
            print('Parsing', page)
            new_ids = get_ids_on_page(page)
            ids.append(new_ids)
        ids = [item for sublist in ids for item in sublist]
    else:
        ids = get_ids_on_page(url)
    return ids


def get_ids_on_page(page_url):
    page_data = requests.get(page_url, headers={'User-Agent': 'discogs_pyvy/1.0'}).text
    soup = BeautifulSoup(page_data, 'lxml')
    spans = soup.find_all('span', {'class': 'rating'})
    ids = [i.attrs['data-post-url'] for i in spans]
    ids = [int(i.split('=')[1]) for i in ids]
    return ids

if __name__ == '__main__':
    url = 'https://www.discogs.com/user/milksteaks4me/collection'

    all = get_all_ids(url)
    print(all)