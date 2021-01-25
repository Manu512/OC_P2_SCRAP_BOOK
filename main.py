# coding: utf8
import requests
import re
import csv
from bs4 import BeautifulSoup

csv_path = "extract/"
url_base = 'http://books.toscrape.com/'
# url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
# url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'
url = 'http://books.toscrape.com/catalogue/category/books/travel_2/index.html'


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
            "number_available": re.search("\d.", info[5]).group(),
            "product_description": soup.select("#product_description ~ p")[0].text,
            "category": info[1],
            # Information N° etoile
            "review_rating": soup.find_all("p", class_="star-rating")[0].attrs['class'][1],
            "image_url": url_base + soup.select("div.item.active")[0].img.attrs["src"].replace("../../", "")
        }


def books_url(url_category):
    category = []
    links = []
    response = requests.get(url_category)
# Si Page Ok => On continue
    if response.ok:
        category.append(url_category)
        category_base = url_category.replace("index.html", "")
        soup = BeautifulSoup(response.content, 'lxml')

# On cherche la class Next pour définir s'il y a plusieurs pages dans la catégorie, on sort de la boucle
        while True:
            if not soup.find('li', class_='next'):
                break
            response = requests.get(category_base + soup.find('li', class_='next').a['href'])
            if response.ok:
                category.append(response.url)
                soup = BeautifulSoup(response.content, 'lxml')

# Une fois toutes les pages récupérées on passe à la recuperation des livres
    for chemin in category:
        response = requests.get(chemin)
        if response.ok:
            soup = BeautifulSoup(response.content, 'lxml')
            contenu = soup.find_all("article", class_="product_pod")
            for cont in contenu:
                link = cont.a['href']
                links.append(url_base + "catalogue/" + link.replace("../../../", ""))

    return links


def csv_writer(data):
    with open(csv_path + data[0]['category'] + '.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['productpage_url', 'upc', 'title', 'price_including_tax',  'price_excluding_tax',
                      'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        try:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='', extrasaction='raise')
            writer.writeheader()
            writer.writerows(data)
        except ValueError as err:
            print("Echec extraction CSV : Un champ inconnu est présent => " + str(err))
            raise Warning


def scrap():
    infos = []
    livres = books_url(url)

    for livre in livres:
        infos.append(books(livre))

    try:
        csv_writer(infos)
        print("Toutes les données sont récupérées")
    except Warning:
        print("Une erreur c'est produite lors de l'écriture du fichier CSV")



if __name__ == '__main__':
    scrap()

