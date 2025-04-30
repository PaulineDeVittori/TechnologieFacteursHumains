import time
import platform
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, sosfilt, sosfiltfilt
from collections import deque
import threading
import pygame
import random
import plux

# ----- Configuration pour Bitalino -----
osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

# ----- Classe de capture des signaux -----
class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__(address)
        self.duration = 0
        self.frequency = 0
        self.x_data = []
        self.y_data = []
        self.latest_emg = 0

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Affichage en temps réel des données")
        self.ax.set_xlabel("Echantillons")
        self.ax.set_ylabel("Amplitude")
        plt.ion()
        plt.show(block=False)

    def onRawFrame(self, nSeq, data):
        self.x_data.append(nSeq)
        self.y_data.append((data[0], data[1], data[2]))
        self.latest_emg = data[0]

        y_emg = [d[0] for d in self.y_data]
        y_ppg = [d[1] for d in self.y_data]
        y_resp = [d[2] for d in self.y_data]

        self.ax.clear()
        self.ax.plot(self.x_data, y_emg, label="EMG", color="blue")
        self.ax.plot(self.x_data, y_ppg, label="PPG", color="red")
        self.ax.plot(self.x_data, y_resp, label="RESP", color="green")
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

        print(f"EMG: {data[0]}")
        return nSeq > self.duration * self.frequency

# ----- Acquisition en thread séparé -----
class AcquisitionThread(threading.Thread):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.daemon = True

    def run(self):
        self.device.start(self.device.frequency, [1, 2, 3], 16)
        self.device.loop()
        self.device.stop()
        self.device.close()

# ----- Lancement du jeu -----
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

    running = True
    while running:
        screen.fill(GREEN)
        pygame.draw.rect(screen, BLUE, (goal_x, goal_y, goal_width, goal_height))
        pygame.draw.rect(screen, RED, (goalkeeper_x, goalkeeper_y, goalkeeper_width, goalkeeper_height))
        pygame.draw.circle(screen, BLACK, (ball_x, ball_y), ball_radius)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Lire la valeur EMG
        emg_value = device.latest_emg
        print(f"EMG reçu dans jeu: {emg_value}")

        if emg_value > 100 and not ball_launched:
            ball_speed_y = -5
            ball_launched = True

        ball_x += ball_speed_x
        ball_y += ball_speed_y

        if ball_y <= 0 or ball_y > HEIGHT:
            ball_launched = False
            ball_x = WIDTH // 2
            ball_y = HEIGHT - 100
            ball_speed_y = 0

        # Mouvement gardien
        current_time = pygame.time.get_ticks()
        if current_time - last_change_time > random.randint(3000, 5000):
            randomized_speed = goalkeeper_speed + random.uniform(-2, 2)
            last_change_time = current_time

        goalkeeper_x += randomized_speed * goalkeeper_direction
        if goalkeeper_x <= 200:
            goalkeeper_direction = 1
        elif goalkeeper_x >= WIDTH - goalkeeper_width - 200:
            goalkeeper_direction = -1

        # Rebond
        if goalkeeper_y <= ball_y + ball_radius <= goalkeeper_y + goalkeeper_height and \
           goalkeeper_x <= ball_x <= goalkeeper_x + goalkeeper_width:
            ball_speed_y = -ball_speed_y
            ball_speed_x = random.choice([-5, 5])

        # Goal
        if goal_x <= ball_x <= goal_x + goal_width and goal_y <= ball_y <= goal_y + goal_height:
            score += 1
            print("But ! Score:", score)
            ball_launched = False
            ball_x = WIDTH // 2
            ball_y = HEIGHT - 100
            ball_speed_y = 0

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# ----- Main -----
if __name__ == "__main__":
    device = NewDevice("BTH98:D3:C1:FE:03:04")  # Remplace par ton adresse si différente
    device.duration = 40
    device.frequency = 10

    thread = AcquisitionThread(device)
    thread.start()

    game_loop(device)

    thread.join()
