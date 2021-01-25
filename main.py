# coding: utf8
import logging
import requests
import re
import csv
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
csv_path = "extract/"
url_base = 'http://books.toscrape.com/'


def retrieve_data_books(url_produit):
    info = []
    response = requests.get(url_produit)
    # Si Page Ok => On continue
    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')
        contenus = soup.find_all("table")[0].find_all("td")

        for contenu in contenus:  # Parcours du tableau Information et ajout des infos dans la list info.
            info.append(contenu.text)

        if soup.select("#product_description ~ p"):
            description = soup.select("#product_description ~ p")[0].text
        else:
            description = ""

        return {
            "productpage_url": url_produit,
            "upc": info[0],
            # Information Title
            "title": soup.find_all("div", class_="product_main")[0].h1.text,
            "price_including_tax": info[3],
            "price_excluding_tax": info[2],
            "number_available": re.search("\d.", info[5]).group(),
            "product_description": description,
            "category": soup.find("ul", class_='breadcrumb').find_all("a")[2].text,
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


def listing_category(url):
    cat = {}
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')
        categories = soup.find('ul', class_='nav').find('ul').find_all('li')

        for categorie in categories:
            cat[categorie.a.text.split()[0]] = (categorie.a['href'])

    return cat


def csv_writer(data, categorie):
    with open(csv_path + categorie + '.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['productpage_url', 'upc', 'title', 'price_including_tax',  'price_excluding_tax',
                      'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        try:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='', extrasaction='raise')
            writer.writeheader()
            writer.writerows(data)
        except ValueError as err:
            logging.info("Echec extraction CSV : Un champ inconnu est présent => " + str(err))
            raise Warning


def define_url_to_scrap(url_base):

    collections = {}
    categorys = listing_category(url_base)  # On récolte la liste des categories
    logging.info('Categorie : Pass')
    for category in categorys.items():
        collections[category[0]] = books_url(url_base + category[1])  # On récolte les liens de tous les livres
        logging.info(f'Récupération de la categorie {category[0]} situé à {url_base + category[1]!r} : Fait')

    return collections


if __name__ == '__main__':

    logging.info('Lancement Scrap')
    dict = define_url_to_scrap(url_base)

    for categorie in dict.keys():
        data = []
        for book in dict[categorie]:
            #  logging.info(f'Récupération informations du livre {book!r} de la categorie {categorie!r}: En cours')
            data.append(retrieve_data_books(book))
        try:
            csv_writer(data, categorie)
            logging.info(f'Tous les livres de la categorie {categorie!r} sont récupérés')
        except Warning:
            logging.info("Une erreur c'est produite lors de l'écriture du fichier CSV")
