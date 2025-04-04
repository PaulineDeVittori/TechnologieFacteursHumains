import time
import platform
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, sosfilt, sosfiltfilt
from collections import deque


osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
if platform.mac_ver()[0] != "":
    import subprocess
    from os import linesep

    p = subprocess.Popen("sw_vers", stdout=subprocess.PIPE)
    result = p.communicate()[0].decode("utf-8").split(str("\t"))[2].split(linesep)[0]
    if result.startswith("12."):
        print("macOS version is Monterrey!")
        osDic["Darwin"] = "MacOS/Intel310"
        if (
            int(platform.python_version().split(".")[0]) <= 3
            and int(platform.python_version().split(".")[1]) < 10
        ):
            print(f"Python version required is ≥ 3.10. Installed is {platform.python_version()}")
            exit()


sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

import plux

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        plux.SignalsDev.__init__(address)
        self.duration = 0
        self.frequency = 0
        self.x_data = []  # Liste pour les échantillons x
        self.y_data = []  # Liste pour les valeurs y (valeurs du signal)
        
        # Initialisation du graphique
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Affichage en temps réel des données")
        self.ax.set_xlabel("Échantillons")
        self.ax.set_ylabel("Valeur")
        plt.ion()

    def onRawFrame(self, nSeq, data):  # Traitement des données à chaque image
        self.x_data.append(nSeq)
        self.y_data.append((data[0],data[1],data[2]))  # Supposons que le signal EMG est dans data[0]

        y_emg = [d[0] for d in self.y_data]
        y_ppg = [d[1] for d in self.y_data]
        y_resp = [d[2] for d in self.y_data]


        
        # Effacer l'ancien graphique
        self.ax.plot(self.x_data, y_emg, label="EMG (Électromyogramme)", color="blue")
        self.ax.plot(self.x_data, y_ppg, label="Photopléthysmogramme", color="red")
        self.ax.plot(self.x_data, y_resp, label="capteur de respiration", color="green")
        self.ax.clear()

        # Mettre à jour le graphique avec les nouvelles données
        self.ax.legend()
        self.ax.plot(self.x_data, self.y_data, label="Affichage en temps réel : EMG + Photopléthysmogramme")
        self.ax.set_xlabel("Échantillons (n° de frame)")
        self.ax.set_ylabel("Amplitude du signal")
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        #self.ax.legend()

        # Mettre à jour l'affichage avec plt.pause() pour permettre la mise à jour en temps réel
        plt.pause(0.01)  # Délai pour l'affichage dynamique

        # Afficher les données dans le terminal
        print(f"Frame: {nSeq}, Signal: {data[0], data[1], data[2]}")

        return nSeq > self.duration * self.frequency


def exampleAcquisition(
    address="BTH98:D3:C1:FE:03:04",
    duration=40,
    frequency=10,
    active_ports=[1,2,3],
    data_callback=None,
):  # time acquisition for each frequency
    """
    Example acquisition.
    """



    device = NewDevice(address)
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.
    
    # Trigger the start of the data recording: https://www.downloads.plux.info/apis/PLUX-API-Python-Docs/classplux_1_1_signals_dev.html#a028eaf160a20a53b3302d1abd95ae9f1
    device.start(device.frequency, active_ports, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleAcquisition(*sys.argv[1:])


