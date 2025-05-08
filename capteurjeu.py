import time
import threading
import pygame
import sys
import platform
import random
import numpy as np
from collections import deque
import os

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
    pygame.mixer.init()  # Initialiser le mixeur pour les sons

    # Dimensions de l'écran
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de Foot - Contrôle par Respiration")
    clock = pygame.time.Clock()
    FPS = 60

    # Couleurs
    WHITE = (255, 255, 255)
    GREEN = (0, 100, 0)
    LIGHT_GREEN = (50, 150, 50)
    RED = (200, 0, 0)
    BLUE = (0, 0, 200)
    BLACK = (0, 0, 0)
    SKY_BLUE = (135, 206, 235)

    # Créer un dossier pour les assets s'il n'existe pas
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Charger ou créer les images
    # Note: Dans un vrai projet, vous devriez avoir ces fichiers
    # Si les images n'existent pas, on crée des surfaces temporaires
    try:
        field_img = pygame.image.load("assets/field.png")
        field_img = pygame.transform.scale(field_img, (WIDTH, HEIGHT))
    except:
        # Créer un terrain de foot stylisé
        field_img = pygame.Surface((WIDTH, HEIGHT))
        # Arrière-plan vert clair
        field_img.fill(LIGHT_GREEN)
        # Lignes du terrain
        pygame.draw.rect(field_img, WHITE, (50, 50, WIDTH-100, HEIGHT-100), 2)
        # Cercle central
        pygame.draw.circle(field_img, WHITE, (WIDTH//2, HEIGHT//2), 70, 2)
        # Point central
        pygame.draw.circle(field_img, WHITE, (WIDTH//2, HEIGHT//2), 5)
        # Surface de réparation (en bas)
        pygame.draw.rect(field_img, WHITE, (WIDTH//2-150, HEIGHT-100, 300, 100), 2)

    try:
        goal_img = pygame.image.load("assets/goal.png")
    except:
        # Créer une image de but
        goal_width, goal_height = 200, 80
        goal_img = pygame.Surface((goal_width, goal_height), pygame.SRCALPHA)
        # Barre supérieure
        pygame.draw.rect(goal_img, WHITE, (0, 0, goal_width, 5))
        # Poteaux
        pygame.draw.rect(goal_img, WHITE, (0, 0, 5, goal_height))
        pygame.draw.rect(goal_img, WHITE, (goal_width-5, 0, 5, goal_height))
        # Filet (lignes diagonales)
        for i in range(0, goal_width, 10):
            pygame.draw.line(goal_img, WHITE, (i, 5), (i//2, goal_height), 1)
            pygame.draw.line(goal_img, WHITE, (goal_width-i, 5), (goal_width-i//2, goal_height), 1)

    try:
        goalkeeper_img = pygame.image.load("assets/goalkeeper.png")
        goalkeeper_img = pygame.transform.scale(goalkeeper_img, (80, 80))
    except:
        # Créer une image simplifiée d'un gardien de but
        goalkeeper_img = pygame.Surface((80, 80), pygame.SRCALPHA)
        # Corps
        pygame.draw.rect(goalkeeper_img, RED, (30, 20, 20, 40))
        # Tête
        pygame.draw.circle(goalkeeper_img, (255, 200, 150), (40, 15), 10)
        # Bras
        pygame.draw.rect(goalkeeper_img, RED, (10, 30, 20, 10))
        pygame.draw.rect(goalkeeper_img, RED, (50, 30, 20, 10))
        # Jambes
        pygame.draw.rect(goalkeeper_img, (0, 0, 128), (30, 60, 10, 20))
        pygame.draw.rect(goalkeeper_img, (0, 0, 128), (40, 60, 10, 20))

    try:
        ball_img = pygame.image.load("assets/ball.png")
        ball_img = pygame.transform.scale(ball_img, (30, 30))
    except:
        # Créer une image de ballon noir simple
        ball_size = 30
        ball_img = pygame.Surface((ball_size, ball_size), pygame.SRCALPHA)
        # Ballon entièrement noir
        pygame.draw.circle(ball_img, BLACK, (ball_size//2, ball_size//2), ball_size//2)

    # Chargement des sons
    try:
        crowd_sound = pygame.mixer.Sound("assets/crowd.wav")
        kick_sound = pygame.mixer.Sound("assets/kick.wav")
        goal_sound = pygame.mixer.Sound("assets/goal.wav")
    except:
        # Si les sons ne sont pas disponibles, on crée des dummy sounds
        crowd_sound = pygame.mixer.Sound(buffer=bytearray(100))
        kick_sound = pygame.mixer.Sound(buffer=bytearray(100))
        goal_sound = pygame.mixer.Sound(buffer=bytearray(100))
        print("Sons non disponibles. Créez un dossier 'assets' avec les fichiers son.")

    # Jouer l'ambiance de foule en boucle
    crowd_sound.set_volume(0.3)
    crowd_sound.play(-1)  # -1 signifie boucle infinie

    # Paramètres du but
    goal_width = 200
    goal_height = 80
    goal_x = (WIDTH - goal_width) // 2
    goal_y = 30
    
    # Position du centre du but pour le tir direct
    goal_center_x = goal_x + goal_width // 2
    goal_center_y = goal_y + goal_height // 2

    # Paramètres du gardien
    goalkeeper_width = 80
    goalkeeper_height = 80
    goalkeeper_x = (WIDTH - goalkeeper_width) // 2
    goalkeeper_y = goal_y + 40
    goalkeeper_base_speed = 5  # Vitesse de base du gardien
    goalkeeper_min_speed = 1   # Vitesse minimale quand le joueur est stressé
    goalkeeper_direction = 1
    current_goalkeeper_speed = goalkeeper_base_speed

    # Seuils pour détecter le stress du joueur et ralentir le gardien
    resp_threshold = 650  # Seuil de respiration
    ppg_threshold = 600   # Seuil de PPG
    is_stressed = False   # État de stress du joueur

    # Paramètres du ballon
    ball_radius = 15
    ball_x = WIDTH // 2
    ball_y = HEIGHT - 100
    ball_speed_x = 0
    ball_speed_y = 0
    ball_launched = False

    # Paramètres du jeu
    last_change_time = pygame.time.get_ticks()
    score = 0
    emg_threshold = 550  # Seuil pour déclencher une action
    game_over = False
    win_score = 10

    # Paramètres pour les effets visuels
    particles = []
    
    # Animation de victoire
    confetti = []
    
    # Police pour le texte
    font_small = pygame.font.SysFont("Arial", 24)
    font_medium = pygame.font.SysFont("Arial", 36)
    font_large = pygame.font.SysFont("Arial", 72, bold=True)

    # Fonction pour créer des particules d'effet
    def create_particles(x, y, color, num_particles=20):
        for _ in range(num_particles):
            particles.append({
                'x': x,
                'y': y,
                'dx': random.uniform(-2, 2),
                'dy': random.uniform(-3, 0),
                'radius': random.uniform(2, 5),
                'color': color,
                'life': random.randint(20, 40)
            })
    
    # Fonction pour créer du confetti
    def create_confetti(num_particles=100):
        for _ in range(num_particles):
            confetti.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-HEIGHT, 0),
                'dx': random.uniform(-1, 1),
                'dy': random.uniform(2, 5),
                'size': random.randint(5, 15),
                'color': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                'life': random.randint(100, 200)
            })
    
    # Fonction pour calculer la direction directe vers le but
    def calculate_direct_path_to_goal():
        # Calculer l'angle pour un tir direct vers le centre du but
        dx = goal_center_x - ball_x
        dy = goal_center_y - ball_y
        distance = (dx**2 + dy**2)**0.5
        
        # Normaliser pour obtenir un vecteur unitaire
        norm_dx = dx / distance
        norm_dy = dy / distance
        
        # Vitesse de base pour le tir
        base_speed = 10
        
        return norm_dx * base_speed, norm_dy * base_speed

    running = True
    while running:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Ajouter la possibilité de lancer la balle avec la barre d'espace (pour tests)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not ball_launched and not game_over:
                    # Calculer trajectoire directe vers le but
                    ball_speed_x, ball_speed_y = calculate_direct_path_to_goal()
                    ball_launched = True
                    kick_sound.play()
                    create_particles(ball_x, ball_y, (255, 255, 255))
                # Reprendre le jeu après victoire
                if event.key == pygame.K_r and game_over:
                    game_over = False
                    score = 0
                    confetti.clear()

        # Lire les valeurs des capteurs
        emg_value = device.latest_emg
        ppg_value = device.latest_ppg
        resp_value = device.latest_resp
        
        # Dessiner le fond et le terrain
        screen.blit(field_img, (0, 0))
        
        # Dessiner le ciel
        pygame.draw.rect(screen, SKY_BLUE, (0, 0, WIDTH, 50))
        
        # Dessiner le but
        screen.blit(goal_img, (goal_x, goal_y))
        
        # Si le jeu n'est pas terminé
        if not game_over:
            # Déclencher le lancement du ballon si EMG dépasse le seuil
            if emg_value > emg_threshold and not ball_launched:
                print(f"EMG {emg_value} > {emg_threshold} : lancement de la balle!")
                
                # Calculer trajectoire directe vers le but
                ball_speed_x, ball_speed_y = calculate_direct_path_to_goal()
                
                ball_launched = True
                kick_sound.play()
                create_particles(ball_x, ball_y, WHITE)

            # Mouvement du ballon
            if ball_launched:
                ball_x += ball_speed_x
                ball_y += ball_speed_y
                
                # Rebond sur les bords
                if ball_x <= ball_radius or ball_x >= WIDTH - ball_radius:
                    ball_speed_x = -ball_speed_x

            # Réinitialiser le ballon s'il sort de l'écran
            if ball_y <= 0 or ball_y > HEIGHT:
                ball_launched = False
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 100
                ball_speed_x = 0
                ball_speed_y = 0

            # Déterminer si le joueur est stressé (RESP et PPG au-dessus des seuils)
            is_stressed = resp_value > resp_threshold and ppg_value > ppg_threshold
            
            # Ajuster la vitesse du gardien en fonction de l'état de stress
            if is_stressed:
                # Calculer un facteur de ralentissement basé sur les valeurs des signaux
                # Plus les valeurs sont élevées au-dessus des seuils, plus le gardien ralentit
                resp_factor = min(1.0, resp_threshold / resp_value)
                ppg_factor = min(1.0, ppg_threshold / ppg_value)
                
                # Combiner les deux facteurs (moyenne) pour un effet plus équilibré
                combined_factor = (resp_factor + ppg_factor) / 2
                
                # Appliquer le facteur à la vitesse de base, mais garantir une vitesse minimale
                current_goalkeeper_speed = max(goalkeeper_min_speed, goalkeeper_base_speed * combined_factor)
                print(f"Joueur stressé! RESP: {resp_value} > {resp_threshold}, PPG: {ppg_value} > {ppg_threshold}")
                print(f"Vitesse du gardien réduite à {current_goalkeeper_speed:.2f}")
            else:
                # Vitesse normale si le joueur n'est pas stressé
                current_goalkeeper_speed = goalkeeper_base_speed

            # Mouvement gardien
            current_time = pygame.time.get_ticks()
            if current_time - last_change_time > 3000:  # Changer direction toutes les 3 secondes
                # Garder la même logique de changement de direction, mais avec vitesse variable
                last_change_time = current_time

            goalkeeper_x += current_goalkeeper_speed * goalkeeper_direction
            if goalkeeper_x <= 200:
                goalkeeper_direction = 1
            elif goalkeeper_x >= WIDTH - goalkeeper_width - 200:
                goalkeeper_direction = -1

            # Dessiner le gardien
            screen.blit(goalkeeper_img, (goalkeeper_x, goalkeeper_y))

            # Rebond sur le gardien (détection de collision améliorée)
            goalkeeper_rect = pygame.Rect(goalkeeper_x+20, goalkeeper_y+10, goalkeeper_width-40, goalkeeper_height-20)
            ball_rect = pygame.Rect(ball_x-ball_radius, ball_y-ball_radius, ball_radius*2, ball_radius*2)
            
            if ball_rect.colliderect(goalkeeper_rect) and ball_launched:
                # Direction du rebond plus réaliste
                ball_launched = False
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 100
                ball_speed_x = 0
                ball_speed_y = 0
                create_particles(ball_x, ball_y, (255, 100, 100))

            # Marquer un but
            goal_rect = pygame.Rect(goal_x+10, goal_y+10, goal_width-20, goal_height-10)
            if ball_rect.colliderect(goal_rect) and ball_launched:
                score += 1
                goal_sound.play()
                print("But ! Score:", score)
                create_particles(ball_x, ball_y, (255, 215, 0), 40)  # Particules dorées
                ball_launched = False
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 100
                ball_speed_x = 0
                ball_speed_y = 0
                
                # Vérifier si le joueur a gagné
                if score >= win_score:
                    game_over = True
                    create_confetti(200)

        # Dessiner le ballon (sans rotation)
        ball_rect = ball_img.get_rect(center=(ball_x, ball_y))
        screen.blit(ball_img, ball_rect.topleft)
            
        # Mettre à jour et dessiner les particules
        for particle in particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                particles.remove(particle)
            else:
                alpha = min(255, particle['life'] * 6)
                particle_surface = pygame.Surface((particle['radius']*2, particle['radius']*2), pygame.SRCALPHA)
                particle_color = (*particle['color'], alpha)
                pygame.draw.circle(particle_surface, particle_color, 
                                (particle['radius'], particle['radius']), particle['radius'])
                screen.blit(particle_surface, (particle['x']-particle['radius'], particle['y']-particle['radius']))
        
        # Si le jeu est gagné, afficher l'animation de confetti
        if game_over:
            # Mettre à jour et dessiner le confetti
            for conf in confetti[:]:
                conf['x'] += conf['dx']
                conf['y'] += conf['dy']
                conf['life'] -= 1
                
                if conf['life'] <= 0 or conf['y'] > HEIGHT:
                    confetti.remove(conf)
                else:
                    pygame.draw.rect(screen, conf['color'], 
                                    (conf['x'], conf['y'], conf['size'], conf['size']))
            
            # Texte de victoire
            victory_text = font_large.render("VICTOIRE !", True, (255, 215, 0))  # Or
            victory_rect = victory_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            # Ombre pour le texte
            shadow_text = font_large.render("VICTOIRE !", True, BLACK)
            shadow_rect = shadow_text.get_rect(center=(WIDTH//2+3, HEIGHT//2+3))
            screen.blit(shadow_text, shadow_rect)
            screen.blit(victory_text, victory_rect)
            
            # Instructions pour rejouer
            restart_text = font_medium.render("Appuyez sur 'R' pour rejouer", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
            screen.blit(restart_text, restart_rect)
            
            # Si tous les confettis sont partis, en créer de nouveaux
            if len(confetti) < 50:
                create_confetti(50)
            
        # Afficher le score
        score_text = font_medium.render(f"Score: {score}/{win_score}", True, BLACK)
        score_shadow = font_medium.render(f"Score: {score}/{win_score}", True, (50, 50, 50))
        screen.blit(score_shadow, (12, 12))
        screen.blit(score_text, (10, 10))
        
        # Afficher les valeurs des capteurs avec les seuils
        sensor_bg = pygame.Surface((350, 120), pygame.SRCALPHA)
        sensor_bg.fill((0, 0, 0, 128))
        screen.blit(sensor_bg, (10, HEIGHT - 130))
        
        # Textes des capteurs avec indication des seuils
        emg_color = WHITE if not emg_value > emg_threshold else (255, 100, 100)
        ppg_color = WHITE if not ppg_value > ppg_threshold else (255, 100, 100)
        resp_color = WHITE if not resp_value > resp_threshold else (255, 100, 100)
        
        emg_text = font_small.render(f"EMG: {emg_value:.1f} / {emg_threshold}", True, emg_color)
        ppg_text = font_small.render(f"PPG: {ppg_value:.1f} / {ppg_threshold}", True, ppg_color)
        resp_text = font_small.render(f"RESP: {resp_value:.1f} / {resp_threshold}", True, resp_color)
        
        # Message de stress et instruction
        if is_stressed:
            stress_text = font_small.render("STRESS DÉTECTÉ! Gardien ralenti", True, (255, 100, 100))
        else:
            stress_text = font_small.render(" ", True, WHITE)
        
        screen.blit(emg_text, (20, HEIGHT - 120))
        screen.blit(ppg_text, (20, HEIGHT - 95))
        screen.blit(resp_text, (20, HEIGHT - 70))
        screen.blit(stress_text, (20, HEIGHT - 45))
        
        # Barre de progression EMG (pour tirer)
        emg_bar_width = 150
        emg_fill = min(emg_value / emg_threshold * emg_bar_width, emg_bar_width)
        pygame.draw.rect(screen, (100, 100, 100), (20, HEIGHT - 20, emg_bar_width, 10))
        pygame.draw.rect(screen, (255, 0, 0) if emg_value > emg_threshold else (0, 255, 0), 
                        (20, HEIGHT - 20, emg_fill, 10))
        
        # Barre de progression RESP
        resp_bar_width = 100
        resp_fill = min(resp_value / resp_threshold * resp_bar_width, resp_bar_width)
        pygame.draw.rect(screen, (100, 100, 100), (200, HEIGHT - 20, resp_bar_width, 10))
        pygame.draw.rect(screen, (0, 0, 255) if resp_value > resp_threshold else (100, 100, 255), 
                        (200, HEIGHT - 20, resp_fill, 10))
        
        # Barre de progression PPG
        ppg_bar_width = 100
        ppg_fill = min(ppg_value / ppg_threshold * ppg_bar_width, ppg_bar_width)
        pygame.draw.rect(screen, (100, 100, 100), (320, HEIGHT - 20, ppg_bar_width, 10))
        pygame.draw.rect(screen, (255, 0, 255) if ppg_value > ppg_threshold else (200, 100, 200), 
                        (320, HEIGHT - 20, ppg_fill, 10))
        
        pygame.display.flip()
        clock.tick(FPS)

    # Nettoyage
    crowd_sound.stop()
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