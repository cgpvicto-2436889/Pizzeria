from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

"""
Connexion à la base de donné 
"""
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

@app.route("/")
def accueil():
    """
    Créer la route pour ammener à la page d'accueil
    """
    return render_template("accueil.html")

@app.route("/commande")
def commande():
    """
    Créer la route pour ammener à la page de commande

    Créer les SELECT pour que la page affiche les infos pour la pizza
    dans le questionnaire

    Returns:
        Les chaines de caractères qui contient les infos de la pizza qui sont afficher dans la page de la commande,
        La page html de la commande (commande.html)
    """
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM croutes")
    croutes = cursor.fetchall()

    cursor.execute("SELECT * FROM sauces")
    sauces = cursor.fetchall()

    cursor.execute("SELECT * FROM garnitures")
    garnitures = cursor.fetchall()

    cursor.close()

    return render_template("commande.html",croutes=croutes,sauces=sauces,garnitures=garnitures)

@app.route("/confirmer", methods=["POST"])
def confirmer():
    """
    1 - Récupère les infos qui sont entrées dans la commande
    2 - Insère le client dans la base de donnée si l'utilisateur n'est pas trouver dans la base de donnée
    3 - Insère la commande et les infos qui viennent avec (croute, sauce, garnitures)
    4 - Récupère les infos de la pizza pour faire le résumer de la commande

    Returns:
        Les chaines de caractères qui contient les infos de la commande,
        La page html de la confirmation de la commande (commande_envoyer.html)
    """
    cursor = db.cursor()

    # RÉCUPÉRER LES INFOS
    client_nom = request.form["nom"]
    adresse = request.form["adresse"]
    telephone = request.form["telephone"]
    
    croute = request.form["croute"]
    sauce = request.form["sauce"]
    garnitures = request.form.getlist("garnitures")

    select_num_telephone = """
        SELECT clients.telephone
    """

    # INSERTION CLIENT. Si le numéro de téléphone existe déja dans la base de donnée ca ne va rien faire sinon ajouter les infos de l'utilisateur
    si_client_bd = "SELECT id FROM clients WHERE numero_telephone = %s"
    cursor.execute(si_client_bd, (telephone,))
    result = cursor.fetchone()

    if result:
        # Le client existe, on prend son ID
        client_id = result[0]
    else:
        # Le client n’existe pas --> on l’insère
        sql_insert = "INSERT INTO clients (nom, adresse, numero_telephone) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert, (client_nom, adresse, telephone))
        client_id = cursor.lastrowid

    # INSERTION COMMANDES
    inserer_commande = "INSERT INTO commandes (client_id, date_commande) VALUES (%s, NOW())"
    cursor.execute(inserer_commande, (client_id,))
    commande_id = cursor.lastrowid

    # INSERTION PIZZA (Liée à la commande)
    inserer_pizza = "INSERT INTO pizzas (commande_id, croute_id, sauce_id) VALUES (%s, %s, %s)"
    cursor.execute(inserer_pizza, (commande_id, croute, sauce))
    pizza_id = cursor.lastrowid

    # INSERTION GARNITURES
    if garnitures:
        inserer_garniture = "INSERT INTO garniture_pizza (pizza_id, garniture_id) VALUES (%s, %s)"
        for g in garnitures:
            cursor.execute(inserer_garniture, (pizza_id, g))
    db.commit()

    # Récupération des infos pour afficher le resumer
    
    # Croute
    cursor.execute("SELECT nom FROM croutes WHERE id = %s", (croute,))
    croute_nom = cursor.fetchone()[0]

    # Sauce
    cursor.execute("SELECT nom FROM sauces WHERE id = %s", (sauce,))
    sauce_nom = cursor.fetchone()[0]

    # Garnitures
    requete_garnitures = """
        SELECT 
            nom 
        FROM garnitures
        INNER JOIN garniture_pizza ON garniture_pizza.garniture_id = garnitures.id
        INNER JOIN pizzas ON pizzas.id = garniture_pizza.pizza_id
        INNER JOIN commandes ON commandes.id = pizzas.commande_id
        WHERE commandes.id = %s
    """
    cursor.execute(requete_garnitures, (commande_id,))
    garnitures_noms = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return render_template("commande_envoyer.html", croute=croute_nom, sauce=sauce_nom, garnitures=garnitures_noms)

@app.route("/commandes_attente")
def commandes_attente():
    """
    Selectionne les commandes dans la base de donnée pour les afficher dans les commandes en attente

    Returns:
        La chaine de caractère de chaque commande prit dans le select,
        La page html des commandes en attentes (commandes_attente.html)
    """
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            commandes.id AS id,
            commandes.date_commande,
            clients.numero_telephone AS telephone,
            clients.adresse AS adresse
        FROM commandes
        INNER JOIN clients ON commandes.client_id = clients.id
        INNER JOIN status_commandes ON commandes.id = status_commandes.commande_id
        WHERE status_commandes.etat_id = 1
        ORDER BY commandes.date_commande ASC
    """)
    commandes = cursor.fetchall()
    cursor.close()

    return render_template("commandes_attente.html", commandes=commandes)

@app.route("/commandes_attente/<int:id>", methods=["POST"])
def livrer_commande(id):
    """
    Quand le bouton sera pressé, ça va initialiser le status de la commande a livrer

    Returns:
        Ça va retourner la page des commandes en attentes comme un "refresh" de page
    """
    cursor = db.cursor()

    # Met à jour l'état de la commande "Livrée"
    sql_update_status = "UPDATE status_commandes SET etat_id = 2 WHERE commande_id = %s"
    cursor.execute(sql_update_status, (id,))

    db.commit()
    cursor.close()

    return redirect(url_for("commandes_attente"))

if __name__ == '__main__':
    app.run(debug=True)