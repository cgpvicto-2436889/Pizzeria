/*
	Création de la base de donnée de la pizzeria.
    Va ètre utiliser dans un interface web.
*/
DROP DATABASE IF EXISTS database_pizza;
CREATE DATABASE database_pizza;
USE database_pizza;

CREATE TABLE croutes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255),
    prix INT
);

CREATE TABLE sauces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255),
    prix INT
);

CREATE TABLE garnitures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255),
    prix INT
);

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255),
    adresse VARCHAR(255),
    numero_telephone VARCHAR(255)
);

CREATE TABLE etat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255)
);

CREATE TABLE commandes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    date_commande DATETIME,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE pizzas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commande_id INT,
    croute_id INT,
    sauce_id INT,
    FOREIGN KEY (commande_id) REFERENCES commandes(id),
    FOREIGN KEY (croute_id) REFERENCES croutes(id),
    FOREIGN KEY (sauce_id) REFERENCES sauces(id)
);

CREATE TABLE garniture_pizza (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pizza_id INT,
    garniture_id INT,
    FOREIGN KEY (pizza_id) REFERENCES pizzas(id),
    FOREIGN KEY (garniture_id) REFERENCES garnitures(id)
);

CREATE TABLE status_commandes (
	id INT AUTO_INCREMENT PRIMARY KEY,
    etat_id INT,
    commande_id INT,
    FOREIGN KEY (etat_id) REFERENCES etat(id),
    FOREIGN KEY (commande_id) REFERENCES commandes(id)
);
#Insertion des données dans la base de données

-- ---------------------------------------------------------
-- INSERTION DES DONNÉES DE BASE
-- ---------------------------------------------------------

-- CROUTES
INSERT INTO croutes (nom, prix) VALUES
('Classique', 10),
('Mince', 12),
('Épaisse', 13);

-- SAUCES
INSERT INTO sauces (nom, prix) VALUES
('Tomate', 0),
('Spaghetti', 1),
('Alfredo', 2);

-- GARNITURES
INSERT INTO garnitures (nom, prix) VALUES
('Pepperoni', 2),
('Champignons', 1),
('Oignons', 1),
('Poivrons', 1),
('Olives', 1),
('Anchois', 2),
('Bacon', 2),
('Poulet', 3),
('Maïs', 1),
('Fromage', 2),
('Piments forts', 1);

-- ÉTATS POSSIBLES
INSERT INTO etat (nom) VALUES
('Commander'),
('Livré');


-- ---------------------------------------------------------
-- CRÉATION DE TRIGGERS
-- ---------------------------------------------------------
DELIMITER $$

CREATE TRIGGER apres_insertion_commande 
AFTER INSERT ON commandes 
FOR EACH ROW
BEGIN
	INSERT INTO status_commandes (etat_id, commande_id)
	VALUES (1, NEW.id);
END$$

DELIMITER ;