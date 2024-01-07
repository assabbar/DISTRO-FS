

import ctypes
import os
import json
import hashlib
import secrets
import shutil
import datetime

BASE_PATH = "/home/malak016/Documents/TDIA1"
current_user_path = None


def create_user_directory(username):
    user_path = os.path.join(BASE_PATH, username)
    os.makedirs(user_path, exist_ok=True)
    return user_path


import os
import stat
def log_event(event, log_path):
    # Ajouter un enregistrement de journal avec la date et l'heure actuelles
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = "{}: {}\n".format(timestamp, event)

    # Vérifier si le répertoire 'log' existe, sinon le créer
    log_directory = os.path.dirname(log_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Ajouter l'entrée du journal au fichier
    with open(log_path, "a") as log_file:
        log_file.write(log_entry)

def create_user_subdirectories(username):
    global current_user_path
    current_user_path = create_user_directory(username)

    # Ajouter rep1, REP2, log/timing_fich, log/timing_user et ERROR
    subdirectories = ["rep1", "REP2", os.path.join("log", "timing_user.txt"),
                      os.path.join("ERROR", "fichier_erreur.txt")]

    # Définir le chemin du fichier journal en dehors de la boucle
    log_path = os.path.join(current_user_path, "log", "timing_user.txt")

    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(current_user_path, subdirectory)

        # Si le nom se termine par une extension, créez un fichier vide
        if subdirectory.endswith((".txt", ".log")):
            # Créez le répertoire parent s'il n'existe pas
            os.makedirs(os.path.dirname(subdirectory_path), exist_ok=True)

            # Créez le fichier vide
            with open(subdirectory_path, "w") as file:
                # Ajoutez une entrée dans le fichier journal avec le nom d'utilisateur
                log_entry = "{} a créé le fichier : {}\n".format(username, subdirectory)
                log_event(log_entry, log_path)
        else:
            os.makedirs(subdirectory_path, exist_ok=True)

            # Exclure ERROR et fichier_erreur de l'enregistrement dans le fichier journal
            if subdirectory != os.path.join("ERROR", "fichier_erreur"):
                # Ajout d'une entrée dans le fichier journal avec le nom d'utilisateur
                log_entry = "{} a créé son compte\n".format(username)
                log_event(log_entry, log_path)

def load_user_data():
    user_data_file = os.path.join(BASE_PATH, "mdp.txt")
    if os.path.exists(user_data_file):
        with open(user_data_file, "r") as file:
            lines = file.readlines()
            user_data = {}
            for line in lines:
                if ":" in line:
                    username, salt, hashed_password = line.strip().split(":")
                    user_data[username] = {"password": (salt, hashed_password)}
                    log_path = os.path.join(BASE_PATH, username, "log", "timing_user.txt")
                    log_event("{} s'est connecté à son compte".format(username), log_path)
            return user_data
    else:
        return {}


def save_user_data(user_data):
    user_data_file = os.path.join(BASE_PATH, "mdp.txt")
    with open(user_data_file, "w") as file:
        for username, data in user_data.items():
            salt, hashed_password = data["password"]
            file.write("{}:{}:{}\n".format(username, salt, hashed_password))



def hasher_mot_de_passe(mot_de_passe):
    # Génération d'un sel aléatoire
    sel = secrets.token_hex(16)  # 16 octets pour le sel

    # Concaténation du mot de passe avec le sel
    mot_de_passe_avec_sel = mot_de_passe + sel

    # Hachage du mot de passe avec le sel
    hachage = hashlib.sha256(mot_de_passe_avec_sel.encode()).hexdigest()

    # Retourner le sel et le hachage pour stockage
    return sel, hachage


def log_error(error_message, username):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = "{}: {}\n".format(timestamp, error_message)

    error_log_path = os.path.join(BASE_PATH, username, "ERROR", "fichier_erreur.txt")

    # Assurez-vous que le répertoire 'ERROR' existe
    if not os.path.exists(os.path.dirname(error_log_path)):
        os.makedirs(os.path.dirname(error_log_path))

    # Ajoutez l'entrée du journal des erreurs au fichier
    with open(error_log_path, "a") as error_log_file:
        error_log_file.write(log_entry)
def login(user_data):
    global current_user_path
    username = input("Entrez votre nom d'utilisateur : ")
    password = input("Entrez votre mot de passe : ")

    if username in user_data:
        stored_salt, stored_hash = user_data[username]["password"]
        # Utiliser le sel stocké pour hacher le mot de passe fourni
        entered_hash = hashlib.sha256((password + stored_salt).encode()).hexdigest()

        if stored_hash == entered_hash:
            current_user_path = os.path.join(BASE_PATH, username)
            print("Connexion réussie ! Vous êtes maintenant dans votre répertoire : {}.".format(current_user_path))

            return True
        else:
            # Enregistrer l'erreur dans le fichier d'erreur de l'utilisateur
            error_message = "Tentative de connexion avec un mot de passe incorrect pour le compte '{}'.".format(username)

            log_error(error_message, username)
            print("Mot de passe incorrect.")
            return False
    else:
        # Enregistrer l'erreur dans le fichier d'erreur de l'utilisateur
        error_message = "Tentative de connexion avec un nom d'utilisateur inexistant : '{}'.".format(username)

        log_error(error_message, username)
        print("Le compte '{}' n'existe pas.".format(username))
        return False


def create_account(user_data):
    global current_user_path
    username = input("Entrez votre nom d'utilisateur : ")
    password = input("Entrez votre mot de passe : ")

    if username in user_data:
        print("Le compte '{}'existe deja.".format(username))

    else:
        # Utiliser la fonction de hachage pour sécuriser le mot de passe
        salt, hashed_password = hasher_mot_de_passe(password)
        user_data[username] = {"password": (salt, hashed_password)}
        save_user_data(user_data)
        create_user_subdirectories(username)
        current_user_path = os.path.join(BASE_PATH, username)
        print("Le compte '{}' a été créé avec succès. Vous êtes maintenant dans votre répertoire : {}".format(username, current_user_path))


def create_directory(dir_name):
    global current_user_path

    if current_user_path:
        new_dir_path = os.path.join(current_user_path, "rep1", dir_name)

        try:
            os.makedirs(new_dir_path)
            print("Répertoire '{}' créé avec succès dans {}/rep1.".format(dir_name, current_user_path))


            # Enregistrez l'événement dans le fichier journal de l'utilisateur
            log_path = os.path.join(current_user_path, "log", "timing_user.txt")
            log_entry = "Répertoire '{}' créé à {}.\n".format(dir_name, datetime.datetime.now())

            log_event(log_entry, log_path)

        except FileExistsError:
            print("Le répertoire '{}' existe déjà dans {}/rep1.".format(dir_name, current_user_path))

    else:
        print("Vous devez d'abord vous connecter.")

def create_file(file_name):
    global current_user_path

    if current_user_path:
        file_path = os.path.join(current_user_path, "rep1", file_name)

        try:
            with open(file_path, "w") as file:
                # Vous pouvez ajouter du contenu au fichier si nécessaire
                file.write("Contenu initial du fichier")

            print("Fichier '{}' créé avec succès dans {}/rep1.".format(file_name, current_user_path))

            # Enregistrez l'événement dans le fichier journal de l'utilisateur
            log_path = os.path.join(current_user_path, "log", "timing_user.txt")
            log_entry = "Le fichier '{}' créé à {}.\n".format(file_name, datetime.datetime.now())

            log_event(log_entry, log_path)

        except Exception as e:
            print("Erreur lors de la création du fichier '{}': {}".format(file_name, e))

    else:
        print("Vous devez d'abord vous connecter.")


def check_directory_existence(directory_name):
    global current_user_path
    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path)
        target_directory_path = os.path.join(user_root_path, directory_name)

        # Utiliser os.walk pour parcourir tous les sous-répertoires
        for root, dirs, files in os.walk(user_root_path):
            if directory_name in dirs:
                print("Le répertoire '{}' existe dans {}.".format(directory_name, root))

                # Enregistrez l'événement dans le fichier journal de l'utilisateur
                log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                log_entry = "{} a cherché l'existence du répertoire '{}' à {}.\n".format(
                    os.path.basename(current_user_path), directory_name, datetime.datetime.now()
                )
                log_event(log_entry, log_path)

                return

        print("Le répertoire '{}' n'existe pas dans {}.".format(directory_name, user_root_path))
    else:
        print("Vous devez d'abord vous connecter.")

def check_file_existence(file_name):
    global current_user_path
    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path)
        target_file_path = os.path.join(user_root_path, file_name)

        # Utiliser os.walk pour parcourir tous les sous-répertoires
        for root, dirs, files in os.walk(user_root_path):
            if file_name in files:
                print("Le fichier '{}' existe dans {}.".format(file_name, root))

                # Enregistrez l'événement dans le fichier journal de l'utilisateur
                log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                log_entry = "{} a cherché l'existence du fichier '{}' à {}.\n".format(
                    os.path.basename(current_user_path), file_name, datetime.datetime.now()
                )
                log_event(log_entry, log_path)

                return

        print("Le fichier '{}' n'existe pas dans {}.".format(file_name, user_root_path))
    else:
        print("Vous devez d'abord vous connecter.")



def list_directories_and_files(directory="", indent=0):
    global current_user_path
    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path)
        target_directory_path = os.path.join(user_root_path, directory)

        if not os.path.exists(target_directory_path):
            print("Le répertoire '{}' n'existe pas dans {}.".format(directory, user_root_path))
            return

        # Utiliser os.listdir pour obtenir la liste des fichiers et répertoires
        contents = os.listdir(target_directory_path)

        if not contents:
            return

        # Enregistrez l'événement dans le fichier journal de l'utilisateur
        log_path = os.path.join(current_user_path, "log", "timing_user.txt")
        log_entry = "{} a listé le contenu du répertoire '{}' à {}.\n".format(
            os.path.basename(current_user_path), directory, datetime.datetime.now()
        )
        log_event(log_entry, log_path)

        for item in contents:
            item_path = os.path.join(target_directory_path, item)

            # Vérifier si c'est un répertoire
            if os.path.isdir(item_path):
                print("\t" * indent + "Répertoire : {}".format(item))
                # Appeler récursivement pour afficher les sous-répertoires
                list_directories_and_files(os.path.join(directory, item), indent + 1)
            else:
                print("\t" * indent + "Fichier : {}".format(item))

    else:
        print("Vous devez d'abord vous connecter.")


def rename_directory_or_file(old_name, new_name):
    global current_user_path
    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path)

        # Parcourir tous les sous-répertoires de C:\TDIA1\malak\rep1
        for root, dirs, files in os.walk(user_root_path):
            # Chercher et renommer les répertoires
            if old_name in dirs:
                target_path = os.path.join(root, old_name)
                new_path = os.path.join(root, new_name)

                if os.path.exists(target_path):
                    # Renommer le répertoire
                    os.rename(target_path, new_path)
                    print("Le nom de '{}' a été changé avec succès en '{}'.".format(old_name, new_name))

                    # Enregistrez l'événement dans le fichier journal de l'utilisateur
                    log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                    log_entry = "{} a renommé le répertoire '{}' en '{}' à {}.\n".format(
                        os.path.basename(current_user_path), old_name, new_name, datetime.datetime.now()
                    )
                    log_event(log_entry, log_path)

                    return

            # Chercher et renommer les fichiers
            for file_name in files:
                if file_name == old_name:
                    target_path = os.path.join(root, old_name)
                    new_path = os.path.join(root, new_name)

                    if os.path.exists(target_path):
                        # Renommer le fichier
                        os.rename(target_path, new_path)
                        print("Le nom de '{}' a été changé avec succès en '{}'.".format(old_name, new_name))

                        # Enregistrez l'événement dans le fichier journal de l'utilisateur
                        log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                        log_entry = "{} a renommé le fichier '{}' en '{}' à {}.\n".format(
                            os.path.basename(current_user_path), old_name, new_name, datetime.datetime.now()
                        )
                        log_event(log_entry, log_path)

                        return

        print("Le répertoire ou le fichier '{}' n'existe pas dans {}.".format(old_name, user_root_path))

    else:
        print("Vous devez d'abord vous connecter.")


import datetime

def remove_directory_recursive(dir_name, current_path=""):
    global current_user_path
    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path, "rep1")
        target_path = os.path.join(user_root_path, current_path, dir_name)

        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            print("Le répertoire '{}' et son contenu ont été supprimés avec succès.".format(dir_name))

            # Enregistrez l'événement dans le fichier journal de l'utilisateur
            log_path = os.path.join(current_user_path, "log", "timing_user.txt")
            log_entry = "{} a supprimé le répertoire '{}' et son contenu à {}.\n".format(
                os.path.basename(current_user_path), dir_name, datetime.datetime.now()
            )
            log_event(log_entry, log_path)

        else:
            print("Le répertoire '{}' n'existe pas dans {}/{}.".format(dir_name, user_root_path, current_path))

        # Suppression récursive dans les sous-répertoires
        if os.path.isdir(target_path):
            sub_directories = [d for d in os.listdir(target_path) if os.path.isdir(os.path.join(target_path, d))]
            for sub_dir in sub_directories:
                new_current_path = os.path.join(current_path, dir_name)
                remove_directory_recursive(sub_dir, new_current_path)
    else:
        print("Vous devez d'abord vous connecter.")

def remove_file(file_name):
    global current_user_path
    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path, "rep1")
        target_path = os.path.join(user_root_path, file_name)

        if os.path.exists(target_path) and os.path.isfile(target_path):
            os.remove(target_path)
            print("Le fichier '{}' a été supprimé avec succès.".format(file_name))

            # Enregistrez l'événement dans le fichier journal de l'utilisateur
            log_path = os.path.join(current_user_path, "log", "timing_user.txt")
            log_entry = "{} a supprimé le fichier '{}' à {}.\n".format(
                os.path.basename(current_user_path), file_name, datetime.datetime.now()
            )
            log_event(log_entry, log_path)

        else:
            print("Le fichier '{}' n'existe pas dans {}.".format(file_name, user_root_path))

    else:
        print("Vous devez d'abord vous connecter.")

import shutil


import shutil
import os
import datetime

def copy_directory_or_file(source_name, destination_name):
    global current_user_path

    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path, "rep1")
        source_path = os.path.join(user_root_path, source_name)

        # Vérifier si le répertoire ou le fichier source existe
        if os.path.exists(source_path):
            destination_path = os.path.join(BASE_PATH, current_user_path, "REP2", destination_name)

            # Vérifier si le répertoire de destination existe
            if not os.path.exists(destination_path):
                # Copier le répertoire source dans le répertoire de destination
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination_path)
                    print(
                        "Le répertoire '{}' a été copié avec succès dans REP2 avec le nom '{}'.".format(
                            source_name, destination_name
                        )
                    )
                else:
                    shutil.copy2(source_path, destination_path)
                    print(
                        "Le fichier '{}' a été copié avec succès dans REP2 avec le nom '{}'.".format(
                            source_name, destination_name
                        )
                    )

                    # Enregistrez l'événement dans le fichier journal de l'utilisateur
                    log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                    log_entry = "{} a copié le répertoire ou le fichier '{}' vers '{}' à {}.\n".format(
                        os.path.basename(current_user_path), source_name, destination_name, datetime.datetime.now()
                    )
                    log_event(log_entry, log_path)

            else:
                print("Le répertoire de destination '{}' existe déjà dans REP2.".format(destination_name))
        else:
            # Recherche récursive du répertoire ou du fichier dans les sous-répertoires de rep1
            for root, dirs, files in os.walk(user_root_path):
                if source_name in dirs or source_name in files:
                    source_path = os.path.join(root, source_name)
                    destination_path = os.path.join(BASE_PATH, current_user_path, "REP2", destination_name)

                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, destination_path)
                        print(
                            "Le répertoire '{}' a été copié avec succès dans REP2 avec le nom '{}'.".format(
                                source_name, destination_name
                            )
                        )
                    else:
                        shutil.copy2(source_path, destination_path)
                        print(
                            "Le fichier '{}' a été copié avec succès dans REP2 avec le nom '{}'.".format(
                                source_name, destination_name
                            )
                        )

                        # Enregistrez l'événement dans le fichier journal de l'utilisateur
                        log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                        log_entry = "{} a copié le répertoire ou le fichier '{}' vers '{}' à {}.\n".format(
                            os.path.basename(current_user_path), source_name, destination_name, datetime.datetime.now()
                        )
                        log_event(log_entry, log_path)

                        return

            print("Le répertoire ou le fichier source '{}' n'existe pas dans {}.".format(source_name, user_root_path))

    else:
        print("Vous devez d'abord vous connecter.")

import os
import datetime

def list_file_content(file_name):
    global current_user_path

    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path)

        # Parcourir tous les répertoires et sous-répertoires de C:\TDIA1\nom_utilisateur
        for root, dirs, files in os.walk(user_root_path):
            if file_name in files:
                file_path = os.path.join(root, file_name)

                # Vérifier si le fichier existe et s'il est vide
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        content = file.read()

                        if content:
                            print("Contenu du fichier '{}' dans {} :\n{}".format(file_name, root, content))
                        else:
                            print("Le fichier '{}' dans {} est vide.".format(file_name, root))

                    # Enregistrez l'événement dans le fichier journal de l'utilisateur
                    log_path = os.path.join(current_user_path, "log", "timing_user.txt")
                    log_entry = "{} a listé le contenu du fichier '{}' dans {} à {}.\n".format(
                        os.path.basename(current_user_path), file_name, root, datetime.datetime.now()
                    )
                    log_event(log_entry, log_path)

                    return  # Retourner après avoir trouvé et affiché le fichier

        print("Le fichier '{}' n'existe pas dans {}.".format(file_name, user_root_path))

    else:
        print("Vous devez d'abord vous connecter.")

import os
import stat

import os
import stat
import datetime

def give_permissions(file_name, permission):
    global current_user_path

    if current_user_path:
        user_root_path = os.path.join(BASE_PATH, current_user_path, "rep1")
        file_path = os.path.join(user_root_path, file_name)

        # Vérifier si le fichier existe et s'il est accessible
        if os.path.exists(file_path) and os.access(file_path, os.W_OK):
            # Appliquer les permissions
            if permission == "+r":
                os.chmod(file_path, stat.S_IRUSR)  # Ajoute la permission de lecture pour l'utilisateur
            elif permission == "+w":
                os.chmod(file_path, stat.S_IWUSR)  # Ajoute la permission d'écriture pour l'utilisateur
            elif permission == "+e":
                os.chmod(file_path, stat.S_IXUSR)  # Ajoute la permission d'exécution pour l'utilisateur
            elif permission == "+x":
                os.chmod(file_path, stat.S_IRWXU)  # Ajoute toutes les permissions pour l'utilisateur

            print("Les permissions du fichier '{}' ont été mises à jour : {}".format(file_name, permission))

            # Enregistrez l'événement dans le fichier journal de l'utilisateur
            log_path = os.path.join(current_user_path, "log", "timing_user.txt")
            log_entry = "{} a mis à jour les permissions du fichier '{}' à {} à {}.\n".format(
                os.path.basename(current_user_path), file_name, permission, datetime.datetime.now()
            )
            log_event(log_entry, log_path)

        else:
            print("Le fichier '{}' n'a pas été trouvé dans {} ou vous n'avez pas les droits d'accès.".format(file_name, user_root_path))
    else:
        print("Vous devez d'abord vous connecter.")

from colorama import Fore, Style, init
init()
def print_help():
    print("""
{0}{1}***********************************************************************{2}
{0}{1}* Commandes disponibles dans votre file système: *{2}
{0}{1}***********************************************************************{2}
{3}* - CR <nom_répertoire> :{4} Créer un répertoire                          
{3}*  
{3}* - CF <nom_fichier> :{4} Créer un fichier
{3}*
{3}* - RENAME <ancien_nom> <nouveau_nom> :{4} Renommer
{3}*
{3}* - EXISTE -R <nom_répertoire> :{4} Vérifier l'existence d'un répertoire
{3}*
{3}* - EXISTE -F <nom_fichier> :{4} Vérifier l'existence d'un fichier
{3}*
{3}* - LISTE-MOI :{4} Lister les répertoires et fichiers
{3}*
{3}* - SUP -R <nom_répertoire> :{4} Supprimer un répertoire
{3}*
{3}* - SUP -F <nom_fichier> :{4} Supprimer un fichier
{3}*
{3}* - GIVE +r <nom_fichier> :{4} Donner le droit de lecture à un fichier
{3}*
{3}* - GIVE +w <nom_fichier> :{4} Donner le droit d'écriture à un fichier
{3}*
{3}* - GIVE +e <nom_fichier> :{4} Donner le droit d'exécution à un fichier
{3}*
{3}* - GIVE +x <nom_fichier> :{4} Donner tous les droits à un fichier
{3}*
{3}* - COPIE <source> <destination> :{4} Copier un fichier ou répertoire
{3}*
{3}* - LFC <nom_fichier> :{4} Lister le contenu d'un fichier*
{0}{1}*********************************************************************{2}
""".format(Fore.YELLOW, Fore.CYAN, Style.RESET_ALL, Fore.YELLOW, Style.RESET_ALL))

import os
import subprocess
#def print_stars_line(width):
   # print("*" * width)

#def print_centered_text(text, width):
   # padding = (width - len(text)) // 2
    #print("*" * padding + text + "*" * padding)

# Programme principal
os.makedirs(BASE_PATH, exist_ok=True)
user_data = load_user_data()

# Définissez une largeur de console par défaut
#console_width = 80

#try:
    # Essayez d'obtenir la largeur de la console
   # console_width = os.get_terminal_size().columns
#except OSError as e:
  # print("Erreur lors de la récupération de la taille de la console : {}".format(e))

#print_stars_line(console_width)
#print_centered_text("Bienvenue dans votre programme", console_width)
#print_stars_line(console_width)
import subprocess

import subprocess

message = "WELCOME  IN TDIA-FS"
subprocess.run(["toilet", "--filter", "gay", message])


choice = input("1. Connexion\n2. Créer un compte\n3. Quitter\nEntrez votre choix : ")

while choice not in {"1", "2", "3"}:
    print("Entrer un choix valide.")
    choice = input()

if choice == "1":
    login(user_data)

    while True:
        # Affiche l'invite de commande personnalisée avec le nom d'utilisateur en couleur
        command_prompt = "{}{}{}>cmd>>{}".format(Fore.CYAN, Style.BRIGHT, os.path.basename(current_user_path), Style.RESET_ALL)
        command = input(command_prompt)

        if command == "EXIT":
            print("Au revoir !")

            # Enregistrez l'événement dans le fichier journal de l'utilisateur
            log_path = os.path.join(current_user_path, "log", "timing_user.txt")
            log_entry = "{} a quitté le programme à {}.\n".format(os.path.basename(current_user_path), datetime.datetime.now())
            log_event(log_entry, log_path)

            break
        elif command.startswith("CR "):
            dir_name = command[3:]
            create_directory(dir_name)
        elif command.startswith("CF "):
            dir_name = command[3:]
            create_file(dir_name)
        elif command.startswith("EXISTE -R "):
            dir_name_to_check = command[10:]
            check_directory_existence(dir_name_to_check)
        elif command.startswith("EXISTE -F "):
            file_name_to_check = command[10:]
            check_file_existence(file_name_to_check)
        elif command == "LISTE-MOI":
            list_directories_and_files()
        elif command.startswith("RENAME "):
            _, old_name, new_name = command.split(" ")
            rename_directory_or_file(old_name, new_name)
        elif command.startswith("SUP -R "):
            dir_to_remove = command[7:]
            remove_directory_recursive(dir_to_remove, "")
        elif command.startswith("SUP -F "):
            file_to_remove = command[7:]
            remove_file(file_to_remove)
        elif command.startswith("COPIE "):
            args = command.split(" ")
            if len(args) == 3:
                _, source_name, destination_name = args
                copy_directory_or_file(source_name, destination_name)
        elif command.startswith("LFC "):
            file_name_to_list = command[4:]
            list_file_content(file_name_to_list)
        elif command.startswith("GIVE "):
            _, permission, file_name_to_give_permissions = command.split(" ")
            give_permissions(file_name_to_give_permissions, permission)
        elif command.startswith("GIVE +w "):
            _, file_name_to_give_write_permission = command.split(" ")
            give_write_permission(file_name_to_give_write_permission)
        elif command == "HELP":
            print_help()
        else:
            print("Commande mal formulée. Veuillez entrer une commande valide.")
elif choice == "2":  # Correction ici
    create_account(user_data)
    while True:
        # Affiche l'invite de commande personnalisée avec le nom d'utilisateur en couleur
        command_prompt = "{}{}{}>cmd>>{}".format(Fore.CYAN, Style.BRIGHT, os.path.basename(current_user_path),Style.RESET_ALL)
        command = input(command_prompt)

        if command == "EXIT":
            print("Au revoir !")
            break
        elif command.startswith("CR "):
            dir_name = command[3:]
            create_directory(dir_name)
        elif command.startswith("CF "):
            dir_name = command[3:]
            create_file(dir_name)
        elif command.startswith("EXISTE -R "):
            dir_name_to_check = command[10:]
            check_directory_existence(dir_name_to_check)
        elif command.startswith("EXISTE -F "):
            file_name_to_check = command[10:]
            check_file_existence(file_name_to_check)
        elif command == "LISTE-MOI":
            list_directories_and_files()
        elif command.startswith("RENAME "):
            _, old_name, new_name = command.split(" ")
            rename_directory_or_file(old_name, new_name)
        elif command.startswith("SUP -R "):
            dir_to_remove = command[7:]
            remove_directory_recursive(dir_to_remove, "")
        elif command.startswith("SUP -F "):
            file_to_remove = command[7:]
            remove_file(file_to_remove)
        elif command.startswith("COPIE "):
            args = command.split(" ")
            if len(args) == 3:
                _, source_name, destination_name = args
                copy_directory_or_file(source_name, destination_name)
        elif command.startswith("LFC "):
            file_name_to_list = command[4:]
            list_file_content(file_name_to_list)
        elif command.startswith("GIVE "):
            _, permission, file_name_to_give_permissions = command.split(" ")
            give_permissions(file_name_to_give_permissions, permission)
        elif command.startswith("GIVE +w "):
            _, file_name_to_give_write_permission = command.split(" ")
            give_write_permission(file_name_to_give_write_permission)
        elif command == "HELP":
            print_help()
        else:
            print("Commande '{}' non reconnue. Veuillez entrer une commande valide.")
elif choice == "3":
    message = "AU REVOIR !"
    subprocess.run(["toilet", "--filter", "gay", message])
  
