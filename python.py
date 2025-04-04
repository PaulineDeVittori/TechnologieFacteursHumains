import pygame
import random
from emg_acquisition_script import emg_signal, start_emg_acquisition  # 

SEUILemg=2000 

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

# Variables aléatoire de la vitesse
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
    global ball_speed_y, ball_launched

    start_emg_acquisition()  # Démarrer l'acquisition EMG

    while not game_over:
        screen.fill(GREEN)
        draw_goal()
        draw_goalkeeper(goalkeeper_x)
        draw_ball(ball_x, ball_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        #  Lancer la balle si l'EMG dépasse un seuil
        # au lieu de  if event.type == pygame.KEYDOWN:
        if emg_signal > SEUILemg and not ball_launched:
            ball_speed_y = -5
            ball_launched = True
            print("Tir déclenché par EMG")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
