import DataGraph as data
#import codeJeu
#import pygame
import time

# Callback à chaque donnée reçue
def traiter_donnee(nSeq, valeur):
    print(f"[EN DIRECT] Frame {nSeq} => Valeur : {valeur}")

if __name__ == "__main__":
    print("Début de l'acquisition en temps réel...")

    donnees_finales = data.exampleAcquisition(data_callback=traiter_donnee)

    print("Acquisition terminée.")
    print(f"{len(donnees_finales)} échantillons collectés.")

