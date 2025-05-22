import pyautogui
import time

print("Posicione o mouse e aguarde...")
time.sleep(3)

while True:
    x, y = pyautogui.position()
    print(f"Posição atual do mouse: X={x}, Y={y}", end="\r")
    time.sleep(0.1)
