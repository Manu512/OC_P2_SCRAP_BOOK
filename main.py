# coding: utf8
import requests
import re
from bs4 import BeautifulSoup

url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'


def books(url_produit):
    info = []
    response = requests.get(url_produit)
    if response.ok:  #Si Page bien charge => On passe a la suite
        soup = BeautifulSoup(response.content, 'lxml')
        contenu = soup.find_all("table")[0].find_all("td")
        for cont in contenu:  # Parcours du tableau Information et ajout des infos dans la list info.
            info.append(cont.text)

        return {
            "productpage_url": url_produit,
            "upc": info[0],
            "title": soup.find_all("div", class_="product_main")[0].h1.text,  #Information Title
            "price_including_tax": info[3],
            "price_excluding_tax": info[2],
            "number_available":    re.search("\d.", info[5]).group(),
            "product_description": soup.select('#product_description ~ p')[0].text,
            "category": info[1],
            "review_rating": soup.find_all("p", class_="star-rating")[0].attrs['class'][1],  #Information N° etoile
            "image_url": soup.find_all("div", class_="item active")[0].img.attrs['src'] #Information URL Image
        }



if __name__ == '__main__':
    print(books(url))

