# coding: utf8
import requests
import re
import csv
from bs4 import BeautifulSoup

url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'


def books(url_produit):
    info = []
    response = requests.get(url_produit)
    # Si Page Ok => On continue
    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')
        contenus = soup.find_all("table")[0].find_all("td")
        for contenu in contenus:  # Parcours du tableau Information et ajout des infos dans la list info.
            info.append(contenu.text)

        return {
            "productpage_url": url_produit,
            "upc": info[0],
            # Information Title
            "title": soup.find_all("div", class_="product_main")[0].h1.text,
            "price_including_tax": info[3],
            "price_excluding_tax": info[2],
            "number_available":    re.search("\d.", info[5]).group(),
            "product_description": soup.select("#product_description ~ p")[0].text,
            "category": soup.find("ul",class_='breadcrumb').find_all("a")[2].text,
            # Information N° etoile
            "review_rating": soup.find_all("p", class_="star-rating")[0].attrs['class'][1],
            #TODO : Modifier le ../.. par la racine reel lors de l'itération
            "image_url": soup.select("div.item.active")[0].img.attrs["src"]
        }


if __name__ == '__main__':
    with open('extract/book.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['productpage_url', 'upc', 'title', 'price_including_tax',  'price_excluding_tax',
                      'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(books(url))


