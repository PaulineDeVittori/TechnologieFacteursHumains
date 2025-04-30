import threading
import time
from queue import Queue
import pygame
import random
import matplotlib.pyplot as plt
from collections import deque
import platform
import sys
import numpy as np

# === Détection et chargement de PLUX (comme dans ton code) ===
osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

import plux

# === Acquisition EMG + Graphe Matplotlib ===
class NewDevice(plux.SignalsDev):
    def __init__(self, address, emg_queue=None):
        super().__init__(address)
        self.duration = 0
        self.frequency = 0
        self.x_data = []
        self.y_data = []
        self.emg_queue = emg_queue

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Affichage en temps réel des données")
        self.ax.set_xlabel("Échantillons")
        self.ax.set_ylabel("Valeur")
        plt.ion()

    def onRawFrame(self, nSeq, data):
        self.x_data.append(nSeq)
        self.y_data.append((data[0], data[1], data[2]))

        y_emg = [d[0] for d in self.y_data]
        y_ppg = [d[1] for d in self.y_data]
        y_resp = [d[2] for d in self.y_data]

        self.ax.clear()
        self.ax.plot(self.x_data, y_emg, label="EMG", color="blue")
        self.ax.plot(self.x_data, y_ppg, label="PPG", color="red")
        self.ax.plot(self.x_data, y_resp, label="Respiration", color="green")
        self.ax.set_xlabel("Échantillons")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)
        self.ax.legend()
        plt.pause(0.01)

        if self.emg_queue:
            self.emg_queue.put(data[0])  # Envoie EMG au jeu

        return nSeq > self.duration * self.frequency

def exampleAcquisition(emg_queue, address="BTH98:D3:C1:FE:03:04", duration=60, frequency=10, active_ports=[1,2,3]):
    device = NewDevice(address, emg_queue=emg_queue)
    device.duration = duration
    device.frequency = frequency
    device.start(frequency, active_ports, 16)
    device.loop()
    device.stop()
    device.close()

# === Jeu Pygame ===
def game_loop(emg_queue):
    pygame.init()
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 100, 0)
    RED = (200, 0, 0)
    BLUE = (0, 0, 200)

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de Foot EMG")

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
    ball_launched = False

    goalkeeper_speed = 5
    goalkeeper_direction = 1

    min_time = 3000
    max_time = 5000
    last_change_time = pygame.time.get_ticks()
    randomized_speed = goalkeeper_speed

    score = 0
    game_over = False

    def reset_ball():
        nonlocal ball_x, ball_y, ball_speed_x, ball_speed_y, ball_launched
        ball_x = WIDTH // 2
        ball_y = HEIGHT - 100
        ball_speed_x = 0
        ball_speed_y = 0
        ball_launched = False

    def check_goal(ball_x, ball_y):
        return goal_x <= ball_x <= goal_x + goal_width and goal_y <= ball_y <= goal_y + goal_height

    while not game_over:
        screen.fill(GREEN)
        pygame.draw.rect(screen, BLUE, (goal_x, goal_y, goal_width, goal_height))
        pygame.draw.rect(screen, RED, (goalkeeper_x, goalkeeper_y, goalkeeper_width, goalkeeper_height))
        pygame.draw.circle(screen, BLACK, (ball_x, ball_y), ball_radius)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # Récupère EMG si dispo et déclenche tir
        if not ball_launched and not emg_queue.empty():
            emg_value = emg_queue.get()
            if emg_value > 500:
                ball_speed_y = -5
                ball_launched = True

        ball_x += ball_speed_x
        ball_y += ball_speed_y

        if ball_y <= 0:
            ball_launched = False
        if ball_y > HEIGHT:
            reset_ball()

        current_time = pygame.time.get_ticks()
        if current_time - last_change_time >= random.randint(min_time, max_time):
            randomized_speed = goalkeeper_speed + random.uniform(-2, 2)
            last_change_time = current_time

        goalkeeper_x += randomized_speed * goalkeeper_direction
        if goalkeeper_x <= 200:
            goalkeeper_direction = 1
        elif goalkeeper_x >= WIDTH - goalkeeper_width - 200:
            goalkeeper_direction = -1

        if goalkeeper_y <= ball_y + ball_radius <= goalkeeper_y + goalkeeper_height and \
           goalkeeper_x <= ball_x <= goalkeeper_x + goalkeeper_width:
            ball_speed_y = -ball_speed_y
            ball_speed_x = random.choice([-5, 5])

        if check_goal(ball_x, ball_y):
            score += 1
            print("But ! Score:", score)
            reset_ball()

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# === Lancement multithread ===
if __name__ == "__main__":
    emg_queue = Queue()

    thread_game = threading.Thread(target=game_loop, args=(emg_queue,))
    thread_emg = threading.Thread(target=exampleAcquisition, args=(emg_queue,))

    thread_game.start()
    thread_emg.start()

    thread_game.join()
    thread_emg.join()
