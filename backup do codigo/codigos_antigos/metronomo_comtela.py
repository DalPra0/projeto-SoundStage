import pygame
import time
import signal
import sys
import PySimpleGUI as sg

pygame.init()

def metronomo(bpm, ritmo, high_tick_sound_path):
    tempo_intervalo = 60.0 / bpm
    
    high_tick_sound = pygame.mixer.Sound(high_tick_sound_path)
    tick_sound = pygame.mixer.Sound("sons/tick.wav")

    while True:
        if ritmo == "4/4": 
            high_tick_sound.play()
            time.sleep(tempo_intervalo)

            for _ in range(3):
                tick_sound.play()
                time.sleep(tempo_intervalo)
        elif ritmo == "3/4":
            high_tick_sound.play()
            time.sleep(tempo_intervalo)

            for _ in range(2):
                tick_sound.play()
                time.sleep(tempo_intervalo)
        else:
            print("Ritmo não suportado.")
            break

def handle_ctrl_c(signal, frame):
    print("\nReiniciando o metrônomo...")
    main()

def main():
    layout = [
        [sg.Text('Digite o BPM desejado: '), sg.InputText(key='-BPM-')],
        [sg.Text('Digite o ritmo desejado (4/4 ou 3/4): '), sg.InputText(key='-RITMO-')],
        [sg.Button('Começar'), sg.Button('Sair')]
    ]

    window = sg.Window('Configurações do Metrônomo', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Sair':
            break
        if event == 'Começar':
            bpm = int(values['-BPM-'])
            ritmo = values['-RITMO-'].lower()
            high_tick_sound_path = "sons/high_tick.wav"
            metronomo(bpm, ritmo, high_tick_sound_path)

    window.close()

signal.signal(signal.SIGINT, handle_ctrl_c)

main()