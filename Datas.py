import time
import platform
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, sosfilt, sosfiltfilt
from collections import deque

#-----------ajout-----------------------------------
import threading

emg_signal = 0  # Variable pour stocker le signal EMG
resp_signal = 0  # Variable pour stocker le signal EMG
#-----------ajout-----------------------------------

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

        #-----------ajouter de chat-------------------------------------------------------------------------------------------
        global emg_signal
        emg_signal = abs(data[0])  # On récupère la valeur absolue de l'EMG
        print(f"EMG signal: {emg_signal}")
        #------------ajout----------------------------------------------------------------------------------------------------
        #-----------ajout-------------------------------------------------------------------------------------------
        global resp_signal
        ppg_signal = abs(data[1])  # On récupère la valeur absolue de l'EMG
        print(f"PPG signal: {ppg_signal}")
        #------------ajout----------------------------------------------------------------------------------------------------

        #-----------ajout-------------------------------------------------------------------------------------------
        global resp_signal
        resp_signal = abs(data[2])  # On récupère la valeur absolue de l'EMG
        print(f"RESP signal: {resp_signal}")
        #------------ajout----------------------------------------------------------------------------------------------------

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
    #il faudra que je verifie mais normalment cela recupère l'enseble des données qui nous interesse pas uniquement celle de l'emg
    #------------ajout----------------------------------------------------------------------------------------------------
    def start_emg_acquisition():
        thread = threading.Thread(target=exampleAcquisition, args=("BTH98:D3:C1:FE:03:04", 40, 10, [1]))
        thread.daemon = True
        thread.start()
    #------------ajout----------------------------------------------------------------------------------------------------


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
