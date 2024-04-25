CREATE TABLE IF NOT EXISTS user ( id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(120) NOT NULL UNIQUE, name VARCHAR(80) NOT NULL, password VARCHAR(120) NOT NULL);

CREATE TABLE IF NOT EXISTS place ( id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(80) NOT NULL, description VARCHAR(200) NOT NULL, coordinate VARCHAR(60) NOT NULL, direction VARCHAR(120) NOT NULL, img VARCHAR(120) NOT NULL, type VARCHAR(80) NOT NULL, counter INT DEFAULT 0);

CREATE TABLE IF NOT EXISTS feature_counters ( id INT AUTO_INCREMENT PRIMARY KEY, feature INT NOT NULL, counter INT DEFAULT 0);

CREATE TABLE IF NOT EXISTS review ( id INT AUTO_INCREMENT PRIMARY KEY,Rating INT NOT NULL,comment VARCHAR(700) NOT NULL,user_id INT NOT NULL,place_id INT NOT NULL,FOREIGN KEY (user_id) REFERENCES user(id),FOREIGN KEY (place_id) REFERENCES place(id));

CREATE TABLE IF NOT EXISTS android_distribution ( id INT AUTO_INCREMENT PRIMARY KEY, device VARCHAR(120) NOT NULL, android VARCHAR(120) NOT NULL);


INSERT INTO feature_counters (feature) VALUES (1), (2), (3), (4), (5);
