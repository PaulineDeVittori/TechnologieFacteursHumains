import time
import threading
import pygame
import sys
import platform
import random
import numpy as np
from collections import deque

# Configuration pour Bitalino selon le système d'exploitation
osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

import plux

# ----- Classe de capture des signaux (sans graphique) -----
class SignalDevice(plux.SignalsDev):
    def __init__(self, address, callback=None):
        plux.SignalsDev.__init__(self)  # Seulement self comme argument
        self.address = address  # Stocker l'adresse comme attribut séparé
        self.duration = 0
        self.frequency = 0
        self.latest_emg = 0
        self.latest_ppg = 0
        self.latest_resp = 0
        self.callback = callback
        self.max_samples = 0
        self.current_samples = 0

    def onRawFrame(self, nSeq, data):
        # Stocker les dernières valeurs pour accès externe
        self.latest_emg = data[0]
        self.latest_ppg = data[1]
        self.latest_resp = data[2]
        self.current_samples = nSeq

        # Imprimer les valeurs (pour debug, peut être supprimé/commenté)
        print(f"EMG: {data[0]:.1f}, PPG: {data[1]:.1f}, RESP: {data[2]:.1f}")

        # Appeler le callback si fourni
        if self.callback:
            self.callback(nSeq, data)

        # Condition d'arrêt basée sur le nombre d'échantillons
        
        return False
    
    def start_acquisition(self, frequency=100, active_ports=[1, 2, 3]):
        self.start(frequency, active_ports, 16)
        acquisition_thread = threading.Thread(target=self.loop, daemon=True)
        acquisition_thread.start()
    
    

# ----- Configuration du jeu -----
def game_loop(device):
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de Foot")
    clock = pygame.time.Clock()
    FPS = 60

    WHITE = (255, 255, 255)
    GREEN = (0, 100, 0)
    RED = (200, 0, 0)
    BLUE = (0, 0, 200)
    BLACK = (0, 0, 0)

    goal_width = 200
    goal_height = 20
    goal_x = (WIDTH - goal_width) // 2
    goal_y = 30

    goalkeeper_width = 80
    goalkeeper_height = 20
    goalkeeper_x = (WIDTH - goalkeeper_width) // 2
    goalkeeper_y = goal_y + goal_height
    goalkeeper_speed = 5
    goalkeeper_direction = 1
    randomized_speed = goalkeeper_speed

    ball_radius = 15
    ball_x = WIDTH // 2
    ball_y = HEIGHT - 100
    ball_speed_x = 0
    ball_speed_y = 0
    ball_launched = False

    last_change_time = pygame.time.get_ticks()
    score = 0
    emg_threshold = 550  # Seuil pour déclencher une action

    running = True
    while running:
        screen.fill(GREEN)
        pygame.draw.rect(screen, BLUE, (goal_x, goal_y, goal_width, goal_height))
        pygame.draw.rect(screen, RED, (goalkeeper_x, goalkeeper_y, goalkeeper_width, goalkeeper_height))
        pygame.draw.circle(screen, BLACK, (ball_x, ball_y), ball_radius)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Ajouter la possibilité de lancer la balle avec la barre d'espace (pour tests)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not ball_launched:
                    ball_speed_y = -5
                    ball_launched = True

        # Lire la valeur EMG et déclencher une action si le seuil est dépassé
        emg_value = device.latest_emg
        ppg_value = device.latest_ppg
        resp_value = device.latest_resp
        
        # Afficher les valeurs des capteurs à l'écran
        font_small = pygame.font.SysFont(None, 24)
        emg_text = font_small.render(f"EMG: {emg_value:.1f}", True, BLACK)
        ppg_text = font_small.render(f"PPG: {ppg_value:.1f}", True, BLACK)
        resp_text = font_small.render(f"RESP: {resp_value:.1f}", True, BLACK)
        screen.blit(emg_text, (10, HEIGHT - 80))
        screen.blit(ppg_text, (10, HEIGHT - 55))
        screen.blit(resp_text, (10, HEIGHT - 30))

        # Déclencher le lancement du ballon si EMG dépasse le seuil
        if emg_value > emg_threshold and not ball_launched:
            print(f"EMG {emg_value} > {emg_threshold} : lancement de la balle!")
            ball_speed_y = -5
            ball_launched = True

        # Mouvement du ballon
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Réinitialiser le ballon s'il sort de l'écran
        if ball_y <= 0 or ball_y > HEIGHT:
            ball_launched = False
            ball_x = WIDTH // 2
            ball_y = HEIGHT - 100
            ball_speed_x = 0
            ball_speed_y = 0

        # Mouvement gardien
        current_time = pygame.time.get_ticks()
        if current_time - last_change_time > 3000:  # Changer direction toutes les 3 secondes
            randomized_speed = goalkeeper_speed + random.uniform(-2, 2)
            last_change_time = current_time

        goalkeeper_x += randomized_speed * goalkeeper_direction
        if goalkeeper_x <= 200:
            goalkeeper_direction = 1
        elif goalkeeper_x >= WIDTH - goalkeeper_width - 200:
            goalkeeper_direction = -1

        # Rebond sur le gardien
        if goalkeeper_y <= ball_y + ball_radius <= goalkeeper_y + goalkeeper_height and \
           goalkeeper_x <= ball_x <= goalkeeper_x + goalkeeper_width:
            ball_speed_y = -ball_speed_y
            ball_speed_x = random.choice([-5, 5])

        # Marquer un but
        if goal_x <= ball_x <= goal_x + goal_width and goal_y <= ball_y <= goal_y + goal_height:
            score += 1
            print("But ! Score:", score)
            ball_launched = False
            ball_x = WIDTH // 2
            ball_y = HEIGHT - 100
            ball_speed_x = 0
            ball_speed_y = 0

        # Afficher le score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        #nb but 
        if score> 5:
            score_text = font.render(f"But atteint !", True, BLACK)
            break
            
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# ----- Acquisition en thread séparé -----
class AcquisitionThread(threading.Thread):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.daemon = True

    def run(self):
        try:
            # Connecter et démarrer l'acquisition
            print(f"Connexion à l'appareil {self.device.address}...")
            self.device.connect()
            print("Démarrage de l'acquisition...")
            self.device.start(self.device.frequency, [1, 2, 3], 16)
            print("Acquisition en cours...")
            self.device.loop()
            print("Acquisition terminée.")
            self.device.stop()
            self.device.close()
        except Exception as e:
            print(f"Erreur dans le thread d'acquisition: {e}")

# ----- Fonction de callback pour traiter les données en temps réel -----
def traiter_donnee(nSeq, data):
    """
    Fonction de callback simple pour le traitement optionnel des données
    """
    # Ce callback est minimal - les valeurs sont déjà stockées dans le device
    # et accessibles directement via device.latest_emg, etc.
    pass

# ----- Main -----
if __name__ == "__main__":    
    print("Démarrage de l'application...")
    
    # Paramètres de l'acquisition
    address = "BTH98:D3:C1:FE:03:04"  # Remplacez par votre adresse Bluetooth
    duration = 120  # Durée en secondes (plus longue pour laisser le temps de jouer)
    frequency = 10  # Fréquence d'échantillonnage
    
    # Créer le dispositif avec callback minimal
    device = SignalDevice(address, callback=traiter_donnee)
    device.start_acquisition()
    device.duration = duration
    device.frequency = frequency
    
    # Attendre que la connexion soit établie (petit délai)
    time.sleep(2)
    
    try:
        # Lancer le jeu dans le thread principal
        game_loop(device)
    except Exception as e:
        print(f"Erreur dans le jeu: {e}")
    finally:
        print("Fermeture de l'application...")