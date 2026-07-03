import os
import time
import threading
from datetime import datetime
import cv2
import numpy as np
import adbutils
import keyboard
import yaml

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

DEVICE_SERIAL = config["adbDevice"]
DATA_ROOT = config["dataRoot"]
CLASSES = config["classes"]
KEY_MAP = config["keys"]
EXIT_KEY = config["exitKey"]
DELAY = config["screenshotDelay"]

for cls in CLASSES:
    os.makedirs(os.path.join(DATA_ROOT, cls), exist_ok=True)

adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
device = adb.device(serial=DEVICE_SERIAL)

currentAction = "nothing"
running = True

def saveScreenshot():
    global currentAction, running

    while running:
        try:
            pilImg = device.screenshot()
            img = cv2.cvtColor(np.array(pilImg), cv2.COLOR_RGB2BGR)

            #Даем имя файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{timestamp}_{currentAction}.png"
            filepath = os.path.join(DATA_ROOT, currentAction, filename)

            #Сохраняем
            cv2.imwrite(filepath, img)

        except Exception as e:
            print(f"Error capturing screenshot: {e}")

        time.sleep(DELAY)

def keyListener():
    global currentAction, running

    #Сопоставляем клавиши с действиями
    keyToAction = {v: k for k, v in KEY_MAP.items()}

    print("_Data collection started_")
    print(f"Press {KEY_MAP['jump']} -> jump, {KEY_MAP['slide']} -> slide, {KEY_MAP['nothing']} -> nothing")
    print(f"Press {EXIT_KEY} to stop")

    while running:
        #Проверяем каждую клавишу
        for key, action in keyToAction.items():
            if keyboard.is_pressed(key):
                currentAction = action
                break
        if keyboard.is_pressed(EXIT_KEY):
            running = False
            break
        time.sleep(0.01)

if __name__ == "__main__":
    #Запускаем потоки
    screenshotThread = threading.Thread(target=saveScreenshot, daemon=True)
    keyThread = threading.Thread(target=keyListener, daemon=True)

    screenshotThread.start()
    keyThread.start()

    #Пока running == True
    keyThread.join()
    running = False
    time.sleep(0.5)
    print("_Data collection finished_")
