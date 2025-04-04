import DataGraph as data
import codeJeu
import pygame
import time
import threading

# Callback à chaque donnée reçue
def traiter_donnee(nSeq, valeurs):
    """
    Traite les données en temps réel reçues des capteurs (EMG, PPG, Respiration).
    """
    emg, ppg, resp = valeurs  # Décompose les valeurs des 3 capteurs

    print(f"[EN DIRECT] Frame {nSeq} => EMG : {emg}, PPG : {ppg}, Respiration : {resp}")
    
    # Si tu veux déclencher des actions dans le jeu en fonction des valeurs :
    # Par exemple, tu peux utiliser une valeur spécifique des capteurs pour contrôler le jeu
    if emg > 550:
        print("EMG élevé, lancer une action dans le jeu.")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        pygame.event.post(event)

    if ppg > 1000:
        print("PPG élevé, action dans le jeu.")
        # codeJeu.action_jeu_avec_ppg()

    if resp < 600:
        print("Respiration faible, autre action dans le jeu.")
        # codeJeu.autre_action()

def run_acquisition():
    # Lancer l'acquisition avec le callback
    data.exampleAcquisition(data_callback=traiter_donnee)

def run_jeu():
    # Lancer le jeu (codeJeu.py)
    codeJeu.game_loop()
    
if __name__ == "__main__":
    print("Début de l'acquisition en temps réel...")

    # Lancement de l'acquisition des données avec le callback qui va traiter chaque valeur
    donnees_finales = data.exampleAcquisition(data_callback=traiter_donnee)

    print("Acquisition terminée.")
    print(f"{len(donnees_finales)} échantillons collectés.")
    print("Début de l'acquisition et du jeu en temps réel...")

    # Initialisation de Pygame dans le thread principal
    pygame.init()
    
    # Créer deux threads pour exécuter en parallèle l'acquisition et le jeu
    thread_acquisition = threading.Thread(target=run_acquisition, daemon=True)
    thread_jeu = threading.Thread(target=run_jeu, daemon=True)

    # Démarrer les threads
    thread_acquisition.start()
    thread_jeu.start()

    # Boucle principale pour garder le programme en vie
    try:
        while thread_jeu.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Arrêt du programme.")

    print("Programme terminé.")