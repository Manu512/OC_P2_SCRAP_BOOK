# coding: utf8
import logging
import requests
import re
import csv
import os
#  import shutil
from bs4 import BeautifulSoup
from multiprocessing import Pool

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
csv_path = "extract/"
image_path = "extract/images/"
url_base = 'http://books.toscrape.com/'


def init():
    p = os.path.dirname(os.path.realpath(__file__))
    # shutil.rmtree(p + '\\' + csv_path.replace('/',''),  ignore_errors=True)
    try:
        os.makedirs(p + "\\" + image_path, exist_ok=True)
    except OSError as error:
        logging.info("Erreur : Le chemin " + p + "\\" + image_path + "ne peut pas etre crée :" + str(error))


def retrieve_data_books(url: str):
    info = []
    response = requests.get(url)
# Si la page est chargé, on récupère les informations.
    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')
        img = url_base + soup.select("div.item.active")[0].img.attrs["src"].replace("../../", "")
        contenus = soup.find_all("table")[0].find_all("td")
        # Parcours du tableau Information et ajout des infos dans la list info.
        for contenu in contenus:
            info.append(contenu.text)

        if soup.select("#product_description ~ p"):
            description = soup.select("#product_description ~ p")[0].text
        else:
            description = ""
        return {
            "productpage_url": url,
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
            "image_url": img
        }
    else:
        logging.info("Erreur de récupération sur l'url :" + url)
        return {
            "productpage_url": url,
            "upc": "",
            "title": "",
            "price_including_tax": "",
            "price_excluding_tax": "",
            "number_available": "",
            "product_description": "",
            "category": "",
            # Information N° etoile
            "review_rating": "",
            "image_url": ""
        }


def define_books_url(url_category: str) -> list:
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


def listing_category(url: str) -> dict:
    cat = {}
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')
        categories = soup.find('ul', class_='nav-list').find('ul').find_all('a')
        for categorie in categories:
            cat[categorie.text.strip().replace(" ", "_")] = categorie['href']
    return cat


def csv_writer(data: list, categorie: str):
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


def define_url_to_scrap(url: str) -> dict:
    collections = {}
    categorys = listing_category(url)  # On récupère la liste des categories
    logging.info('Categorie : Pass')
    for category in categorys.items():
        # On récolte les liens de tous les livres en parsant toutes les categories et en creant une list collections.
        collections[category[0]] = define_books_url(url + category[1])
        logging.info(f'Récupération des liens de la categorie {category[0]} situé à {url_base + category[1]!r} : Fait')
    return collections


def extract_book_picture(jpg_url: str):
    response = requests.get(jpg_url)
    if response.ok:
        with open(image_path + jpg_url.split('/')[-1], 'wb') as handle:
            handle.write(response.content)
    else:
        logging.info("Erreur de récupération de l'image :" + jpg_url)


def main():
    init()
    logging.info('Lancement Scrap')
    urls = define_url_to_scrap(url_base)
    img_all = []
    for categorie in urls.keys():
        data = []
        for book in urls[categorie]:
            # logging.info(f'Récupération informations du livre {book!r} de la categorie {categorie!r}: En cours')
            data.append(retrieve_data_books(book))
            img_all.append(data[-1]['image_url'])
    # On envoie les données de la categorie dans la fonction de stockage des données en CSV.
        try:
            csv_writer(data, categorie)
            logging.info(f'Tous les livres de la categorie {categorie!r} sont récupérés')
        except Warning:
            logging.info("Une erreur c'est produite lors de l'écriture du fichier CSV")

    logging.info("Récupération des images")
    p = Pool(20)
    p.map(extract_book_picture, img_all)


if __name__ == '__main__':
    main()
