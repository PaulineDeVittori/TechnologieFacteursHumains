import pygame
import sys
import os
import importlib

def menu_main():
    pygame.init()
    pygame.mixer.init()
    
    # Dimensions de l'écran
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Menu - Jeu de Foot")
    clock = pygame.time.Clock()
    FPS = 60

    # Couleurs
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 100, 0)
    LIGHT_GREEN = (50, 150, 50)
    RED = (200, 0, 0)
    BLUE = (0, 0, 200)
    YELLOW = (255, 255, 0)
    GRAY = (150, 150, 150)
    SKY_BLUE = (135, 206, 235)

    # Polices
    font_title = pygame.font.SysFont("Arial", 72, bold=True)
    font_button = pygame.font.SysFont("Arial", 48, bold=True)
    font_input = pygame.font.SysFont("Arial", 36)
    font_info = pygame.font.SysFont("Arial", 24)

    # Variables du menu
    win_score = 5  # Valeur par défaut
    input_active = False
    input_text = str(win_score)
    
    # Créer un dossier pour les assets s'il n'existe pas
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Charger ou créer les images
    try:
        background_img = pygame.image.load("assets/field.png")
        background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    except:
        # Créer un terrain de foot stylisé comme fond
        background_img = pygame.Surface((WIDTH, HEIGHT))
        # Arrière-plan vert clair
        background_img.fill(LIGHT_GREEN)
        # Lignes du terrain
        pygame.draw.rect(background_img, WHITE, (50, 50, WIDTH-100, HEIGHT-100), 2)
        # Cercle central
        pygame.draw.circle(background_img, WHITE, (WIDTH//2, HEIGHT//2), 70, 2)
        # Point central
        pygame.draw.circle(background_img, WHITE, (WIDTH//2, HEIGHT//2), 5)
        # Surface de réparation (en bas)
        pygame.draw.rect(background_img, WHITE, (WIDTH//2-150, HEIGHT-100, 300, 100), 2)

    try:
        ball_img = pygame.image.load("assets/ball.png")
        ball_img = pygame.transform.scale(ball_img, (80, 80))
    except:
        # Créer une image de ballon simple
        ball_size = 80
        ball_img = pygame.Surface((ball_size, ball_size), pygame.SRCALPHA)
        # Ballon noir avec motif
        pygame.draw.circle(ball_img, BLACK, (ball_size//2, ball_size//2), ball_size//2)
        pygame.draw.circle(ball_img, WHITE, (ball_size//2, ball_size//2), ball_size//2-5)
        # Motifs du ballon
        pygame.draw.polygon(ball_img, BLACK, [(ball_size//2, 10), (ball_size//2-15, ball_size//2), 
                                             (ball_size//2+15, ball_size//2)])
        pygame.draw.polygon(ball_img, BLACK, [(ball_size//2, ball_size-10), (ball_size//2-15, ball_size//2), 
                                             (ball_size//2+15, ball_size//2)])

    # Chargement des sons
    try:
        menu_sound = pygame.mixer.Sound("assets/menu.wav")
        click_sound = pygame.mixer.Sound("assets/click.wav")
    except:
        # Si les sons ne sont pas disponibles, on crée des dummy sounds
        menu_sound = pygame.mixer.Sound(buffer=bytearray(100))
        click_sound = pygame.mixer.Sound(buffer=bytearray(100))
        print("Sons non disponibles. Créez un dossier 'assets' avec les fichiers son.")

    # Jouer la musique du menu en boucle
    menu_sound.set_volume(0.3)
    menu_sound.play(-1)  # -1 signifie boucle infinie

    # Variables d'animation
    ball_positions = [(WIDTH // 2 - 200, HEIGHT // 4), (WIDTH // 2 + 200, HEIGHT // 4)]
    ball_directions = [1, -1]
    ball_speeds = [2, 3]

    # Fonction pour créer un bouton
    def draw_button(text, rect, active=True):
        color = BLUE if active else GRAY
        
        # Dessiner le fond du bouton avec une bordure
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 3)
        
        # Effet 3D
        pygame.draw.line(screen, (color[0]//2, color[1]//2, color[2]//2), 
                        (rect.left, rect.bottom), (rect.right, rect.bottom), 5)
        pygame.draw.line(screen, (color[0]//2, color[1]//2, color[2]//2), 
                        (rect.right, rect.top), (rect.right, rect.bottom), 5)
        
        # Texte du bouton
        button_text = font_button.render(text, True, WHITE)
        text_rect = button_text.get_rect(center=rect.center)
        screen.blit(button_text, text_rect)
        
        return rect

    # Boucle principale
    running = True
    while running:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si le clic est sur le bouton Play
                if play_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    try:
                        win_score = max(1, int(input_text))
                        menu_sound.stop()
                        pygame.quit()
                        # Lancer le jeu avec la valeur sélectionnée
                        launch_game(win_score)
                        return  # Quitter le menu
                    except ValueError:
                        # Réinitialiser la valeur en cas d'erreur
                        input_text = "5"
                        
                # Vérifier si le clic est sur l'input
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                    
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            win_score = max(1, int(input_text))
                            input_active = False
                        except ValueError:
                            input_text = "5"
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit() and len(input_text) < 2:
                        input_text += event.unicode
                        
        # Mettre à jour les positions des ballons animés
        for i in range(len(ball_positions)):
            ball_positions[i] = (
                ball_positions[i][0] + ball_speeds[i] * ball_directions[i],
                ball_positions[i][1] + 0.5 * ball_directions[i]
            )
            
            # Inverser la direction si le ballon atteint les bords
            if ball_positions[i][0] < 50 or ball_positions[i][0] > WIDTH - 50:
                ball_directions[i] *= -1

        # Dessiner le fond
        screen.blit(background_img, (0, 0))
        
        # Ajouter un ciel
        pygame.draw.rect(screen, SKY_BLUE, (0, 0, WIDTH, 50))
        
        # Dessiner les ballons animés
        for pos in ball_positions:
            screen.blit(ball_img, (pos[0] - 40, pos[1] - 40))
        
        # Dessiner le titre
        title_shadow = font_title.render("JEU DE FOOT", True, BLACK)
        title_text = font_title.render("JEU DE FOOT", True, YELLOW)
        screen.blit(title_shadow, (WIDTH // 2 - title_text.get_width() // 2 + 3, 80 + 3))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Dessiner le bouton Play
        play_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 80)
        draw_button("JOUER", play_button_rect)
        
        # Dessiner la zone d'input
        input_label = font_input.render("Nombre de buts pour gagner:", True, WHITE)
        screen.blit(input_label, (WIDTH // 2 - input_label.get_width() // 2, HEIGHT // 2 - 50))
        
        input_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 50)
        input_color = YELLOW if input_active else WHITE
        pygame.draw.rect(screen, BLACK, input_rect.inflate(6, 6))
        pygame.draw.rect(screen, input_color, input_rect)
        
        text_surface = font_input.render(input_text, True, BLACK)
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # Informations sur le jeu
        info_text1 = font_info.render("Utilisez la force musculaire (EMG) pour shooter !", True, WHITE)
        info_text2 = font_info.render("Appuyez sur ESPACE pour tester sans capteur", True, WHITE)
        screen.blit(info_text1, (WIDTH // 2 - info_text1.get_width() // 2, HEIGHT - 80))
        screen.blit(info_text2, (WIDTH // 2 - info_text2.get_width() // 2, HEIGHT - 50))
        
        # Mettre à jour l'écran
        pygame.display.flip()
        clock.tick(FPS)

def launch_game(win_score):
    """
    Importe le module de jeu principal et modifie la variable win_score
    avant d'exécuter le jeu
    """
    try:
        # On importe le fichier du jeu principal
        import capteurjeu  # Assurez-vous que votre fichier s'appelle foot_game.py
        
        # Sauvegarde de la variable win_score originale
        original_win_score = None
        
        # Modifier la variable win_score dans le jeu
        # Parcourir les fonctions du module pour trouver game_loop
        for attr_name in dir(capteurjeu):
            if attr_name == 'game_loop':
                game_loop_func = getattr(capteurjeu, attr_name)
                
                # Créer une fonction wrapper qui va modifier win_score
                def patched_game_loop(device):
                    # Trouvons la variable win_score dans le corps de la fonction
                    import inspect
                    source = inspect.getsource(game_loop_func)
                    
                    # Exécuter la fonction originale avec les modifications nécessaires
                    # On doit modifier le code source pour changer win_score
                    original_game_code = capteurjeu.game_loop.__code__
                    
                    # Notre approche alternative : utiliser un monkey patch simple
                    def run_game():
                        # Accès à la variable locale win_score du module foot_game
                        # La variable win_score doit être définie dans le contexte global de game_loop
                        for line in source.split('\n'):
                            if 'win_score =' in line:
                                # On a trouvé la définition
                                globals_copy = capteurjeu.__dict__.copy()
                                globals_copy['win_score'] = win_score
                                capteurjeu.__dict__.update(globals_copy)
                                break
                        
                        # Maintenant on exécute la fonction originale
                        capteurjeu.game_loop(device)
                    
                    run_game()
                
                # Remplacer temporairement la fonction
                original_game_loop = capteurjeu.game_loop
                capteurjeu.game_loop = patched_game_loop
                
                # C'est plus simple d'injecter directement la variable
                capteurjeu.win_score = win_score
                
                break
        
        # Exécuter le jeu comme dans le fichier original
        print(f"Lancement du jeu avec {win_score} buts pour gagner...")
        
        # Cette partie doit correspondre au code dans __main__ de votre jeu
        import time
        
        # Paramètres de l'acquisition
        address = "BTH98:D3:C1:FE:03:04"  # Adresse Bluetooth du Bitalino
        duration = 120
        frequency = 10
        
        # Créer le dispositif
        device = capteurjeu.SignalDevice(address)
        device.start_acquisition()
        device.duration = duration
        device.frequency = frequency
        
        # Attendre que la connexion soit établie
        time.sleep(2)
        
        # Lancer le jeu
        try:
            capteurjeu.game_loop(device)
        except Exception as e:
            print(f"Erreur dans le jeu: {e}")
        finally:
            print("Fermeture de l'application...")
            
        # Restaurer la fonction originale si nécessaire
        if original_game_loop:
            capteurjeu.game_loop = original_game_loop
            
    except ImportError:
        print("Erreur: Le fichier du jeu (capteurjeu.py) n'a pas été trouvé.")
        print("Assurez-vous que le code du jeu est sauvegardé dans un fichier nommé 'capteurjeu.py'")
    except Exception as e:
        print(f"Erreur lors du lancement du jeu: {e}")

if __name__ == "__main__":
    menu_main()