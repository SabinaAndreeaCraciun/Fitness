-- Crear base de datos
CREATE DATABASE IF NOT EXISTS mariadb;
USE mariadb;  -- Asegúrate de usar la base de datos después de crearla

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuaris (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    contrasenya TEXT NOT NULL,  -- Contraseña hasheada con bcrypt
    nivell VARCHAR(20) DEFAULT 'Principiante'  -- Nivel de usuario, predeterminado 'Principiante'
);

-- Crear tabla de ejercicios
CREATE TABLE IF NOT EXISTS exercicis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL  -- Nombre del ejercicio
);

-- Crear tabla de rutinas
CREATE TABLE IF NOT EXISTS rutines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuari_id INT,  -- Referencia a la tabla de usuarios
    exercici_id INT,  -- Referencia a la tabla de ejercicios
    series INT,  -- Número de series
    repeticions INT,  -- Número de repeticiones
    FOREIGN KEY (usuari_id) REFERENCES usuaris(id),  -- Clave foránea a usuaris
    FOREIGN KEY (exercici_id) REFERENCES exercicis(id)  -- Clave foránea a exercicis
);
