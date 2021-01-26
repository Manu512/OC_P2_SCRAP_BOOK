# __Books Scrap Projet P2__

## Prérequis
Une installation de Python 3.3 minimum pour pouvoir créer l'environnement virtuel avec cette méthode.

## Installation environnement virtuel
Se diriger sur le repertoire ou l'on souhaite installer l'environnement virtuel.
Executer la commande :
* `python3 -m venv 'env'` ('env' sera le repertoire où seront stocké les données de l'environnement 
python)

## Activation et installations des dépendances nécessaires au script dans l'environnement virtuel
###Sous Windows les commandes à executer :
* `env/Script/activate`
* `pip install -r requirements.txt`

###Sous Linux les commandes à executer : 
* `source env/bin/activate`
* `pip install -r requirements.txt`

###Installation dependances manuellement :
* `pip install beautifulsoup4~=4.9.1 requests~=2.25.1 lxml==4.6.2` 

##Execution du code d'application

* `python3 main.py`

##Résultat

Le résultat du scraping sera stocké dans un sous-repertoire 'extract' et les images des livres seront stocké 
dans 'extract/images/'

Chaque image extraite sera nommée en fonction de son nom de fichier. On le retrouvera dans la derniere colonne 
du fichier catégorie.csv  