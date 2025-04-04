import DataGraph as data
import codeJeu
import pygame
import time

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
        # Appeler une fonction dans codeJeu pour simuler une action, par exemple:
        # codeJeu.lancer_ball()

    if ppg > 1000:
        print("PPG élevé, action dans le jeu.")
        # codeJeu.action_jeu_avec_ppg()

    if resp < 600:
        print("Respiration faible, autre action dans le jeu.")
        # codeJeu.autre_action()

if __name__ == "__main__":
    print("Début de l'acquisition en temps réel...")

    # Lancement de l'acquisition des données avec le callback qui va traiter chaque valeur
    donnees_finales = data.exampleAcquisition(data_callback=traiter_donnee)

    print("Acquisition terminée.")
    print(f"{len(donnees_finales)} échantillons collectés.")
