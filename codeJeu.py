import pygame
import random

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu de Foot")

clock = pygame.time.Clock()
FPS = 60

goal_width = 200
goal_height = 20
goal_x = (WIDTH - goal_width) // 2
goal_y = 30

goalkeeper_width = 80
goalkeeper_height = 20
goalkeeper_x = (WIDTH - goalkeeper_width) // 2
goalkeeper_y = goal_y + goal_height

ball_radius = 15
ball_x = WIDTH // 2
ball_y = HEIGHT - 100
ball_speed_x = 0
ball_speed_y = 0

goalkeeper_speed = 5  # Vitesse de base du gardien
goalkeeper_direction = 1

ball_launched = False

# Variables pour l'aléatoire de la vitesse
min_time = 3000  # Temps minimum avant de changer la vitesse (en millisecondes)
max_time = 5000  # Temps maximum avant de changer la vitesse (en millisecondes)
last_change_time = pygame.time.get_ticks()  # Temps du dernier changement
randomized_speed = goalkeeper_speed  # Vitesse initiale du gardien

def draw_goal():
    pygame.draw.rect(screen, BLUE, (goal_x, goal_y, goal_width, goal_height))

def draw_goalkeeper(x):
    pygame.draw.rect(screen, RED, (x, goalkeeper_y, goalkeeper_width, goalkeeper_height))

def draw_ball(x, y):
    pygame.draw.circle(screen, BLACK, (x, y), ball_radius)

def check_goal(ball_x, ball_y):
    if goal_x <= ball_x <= goal_x + goal_width and goal_y <= ball_y <= goal_y + goal_height:
        return True
    return False

def reset_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, ball_launched
    ball_x = WIDTH // 2
    ball_y = HEIGHT - 100
    ball_speed_x = 0
    ball_speed_y = 0
    ball_launched = False



def game_loop():
    global goalkeeper_x, ball_x, ball_y, ball_speed_x, ball_speed_y, goalkeeper_direction, ball_launched, randomized_speed, last_change_time

    game_over = False
    score = 0

    while not game_over:
        screen.fill(GREEN)
        draw_goal()
        draw_goalkeeper(goalkeeper_x)
        draw_ball(ball_x, ball_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not ball_launched:  # Lancer le ballon avec la barre d'espace
                    ball_speed_x = 0
                    ball_speed_y = -5  # Le ballon va vers le haut
                    ball_launched = True

        ball_x += ball_speed_x
        ball_y += ball_speed_y

        if ball_y <= 0:  # Si le ballon touche le haut de l'écran
            ball_speed_y = 0  # Le ballon arrête de se déplacer vers le haut
            ball_launched = False  # Le ballon ne peut plus être relancé tant qu'il n'est pas réinitialisé

        if ball_y > HEIGHT:  # Si le ballon sort par le bas de l'écran
            reset_ball()  # Réinitialiser le ballon

        # Vérifier si le temps écoulé depuis le dernier changement est supérieur à un intervalle aléatoire (3 à 5 secondes)
        current_time = pygame.time.get_ticks()
        if current_time - last_change_time >= random.randint(min_time, max_time):
            # Modifier la vitesse du gardien de manière aléatoire
            randomized_speed = goalkeeper_speed + random.uniform(-2, 2)  # Variation plus douce de la vitesse
            last_change_time = current_time  # Réinitialiser le temps du dernier changement

        # Déplacer le gardien avec la vitesse aléatoire
        goalkeeper_x += randomized_speed * goalkeeper_direction

        if goalkeeper_x <= 200:  # Définir la limite gauche
            goalkeeper_direction = 1
        elif goalkeeper_x >= WIDTH - goalkeeper_width - 200:  # Définir la limite droite
            goalkeeper_direction = -1

        if goalkeeper_y <= ball_y + ball_radius <= goalkeeper_y + goalkeeper_height and \
           goalkeeper_x <= ball_x <= goalkeeper_x + goalkeeper_width:
            ball_speed_y = -ball_speed_y
            ball_speed_x = random.choice([-5, 5])

        if check_goal(ball_x, ball_y):
            score += 1
            print("But ! Score:", score)
            reset_ball()  # Réinitialiser le ballon après un but

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

game_loop()
