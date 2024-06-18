import pygame
import time
import signal
import sys

pygame.init()

def metronomo(bpm, ritmo, high_tick_sound_path):
    tempo_intervalo = 60.0 / bpm
    
    high_tick_sound = pygame.mixer.Sound(high_tick_sound_path)
    tick_sound = pygame.mixer.Sound("tick.wav")

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
    try:
        bpm = int(input("Digite o BPM desejado: "))
        ritmo = input("Digite o ritmo desejado (4/4 ou 3/4): ")

        if ritmo.lower() == "sair":
            sys.exit("O programa foi encerrado pelo usuário.")
        
        high_tick_sound_path = "high_tick.wav"

        metronomo(bpm, ritmo, high_tick_sound_path)
    except KeyboardInterrupt:
        handle_ctrl_c(signal.SIGINT, None)

signal.signal(signal.SIGINT, handle_ctrl_c)

main()
