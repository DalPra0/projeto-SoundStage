import pyaudio
import numpy as np
import pygame
import time
import tkinter as tk
from threading import Thread

BPM_CHOICES = [30, 60, 120, 180, 200, 220, 280, 360]
TIME_SIGNATURES = {'3/4': 3, '4/4': 4}
MARGIN_OF_ERROR = 300

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

running = False
volume = 0
last_beat_time = 0
use_microphone = False
bpm = 60
time_signature = 4
score = 0
start_time = 0

p = pyaudio.PyAudio()

def audio_input_stream_callback(in_data, frame_count, time_info, status):
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    peak = np.abs(audio_data).mean()
    global volume
    volume = peak
    return (in_data, pyaudio.paContinue)

audio_stream = p.open(format=FORMAT, channels=CHANNELS,
                      rate=RATE, input=True,
                      frames_per_buffer=CHUNK,
                      stream_callback=audio_input_stream_callback)

def play_metronome(bpm, time_signature):
    interval = 60 / bpm
    try:
        metronome_sound = pygame.mixer.Sound("tick.wav")
        beat_counter = 0

        while running:
            metronome_sound.play()
            beat_counter = (beat_counter + 1) % time_signature
            time.sleep(interval)
    except FileNotFoundError:
        print("O arquivo 'tick.wav' não foi encontrado. Certifique-se de que ele está no diretório correto.")

pygame.mixer.init()
if not pygame.mixer.get_init():
    pygame.mixer.init()

def start_game():
    global running, volume, use_microphone, bpm, time_signature, score, start_time
    running = True
    volume = 0
    score = 0

    bpm = int(bpm_var.get())
    time_signature = TIME_SIGNATURES[time_sig_var.get()]

    use_microphone = method_var.get() == 'Microfone'

    metronome_thread = Thread(target=play_metronome, args=(bpm, time_signature))
    metronome_thread.start()

    if use_microphone:
        audio_stream.start_stream()

    start_time = time.time()
    root.bind("<space>", on_space_press)
    update_game()

def stop_game():
    global running
    running = False
    audio_stream.stop_stream()
    pygame.mixer.stop()
    root.unbind("<space>")

def update_game():
    global start_time, score, running, last_beat_time

    if not running:
        return

    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= (60 / bpm):
        last_beat_time = current_time
        
        if use_microphone:
            if volume > MARGIN_OF_ERROR:
                score += 1
                score_label.config(text=f"Pontuação: {score}")
        
        start_time = current_time

    root.after(10, update_game)

def on_space_press(event):
    global score, last_beat_time

    current_time = time.time()

    if abs(current_time - last_beat_time) <= (60 / bpm) * MARGIN_OF_ERROR / 1000:
        score += 1
        score_label.config(text=f"Pontuação: {score}")

def on_exit():
    global running
    running = False
    audio_stream.stop_stream()
    audio_stream.close()
    p.terminate()
    print(score)
    pygame.quit()
    root.quit()

def test_microphone():
    global running
    test_window = tk.Toplevel(root)
    test_window.title("Testar Microfone")
    
    tk.Label(test_window, text="Teste o volume do microfone").pack()
    
    vol_label = tk.Label(test_window, text="Volume: 0.00")
    vol_label.pack()
    
    def update_volume():
        vol_label.config(text=f"Volume: {volume:.2f}")
        if running:
            test_window.after(100, update_volume)
    
    if not running:
        audio_stream.start_stream()
        running = True
        update_volume()
        
    def close_test():
        global running
        running = False
        audio_stream.stop_stream()
        test_window.destroy()
    
    test_window.protocol("WM_DELETE_WINDOW", close_test)

root = tk.Tk()
root.title("Jogo de Ritmo")

tk.Label(root, text="Escolha o BPM:").grid(row=0, column=0)
bpm_var = tk.StringVar(value=str(BPM_CHOICES[0]))
bpm_menu = tk.OptionMenu(root, bpm_var, *BPM_CHOICES)
bpm_menu.grid(row=0, column=1)

tk.Label(root, text="Escolha o compasso:").grid(row=1, column=0)
time_sig_var = tk.StringVar(value='4/4')
time_sig_menu = tk.OptionMenu(root, time_sig_var, *TIME_SIGNATURES.keys())
time_sig_menu.grid(row=1, column=1)

tk.Label(root, text="Escolha o método de entrada:").grid(row=2, column=0)
method_var = tk.StringVar(value='Espaço')
tk.Radiobutton(root, text="Espaço", variable=method_var, value='Espaço').grid(row=2, column=1)
tk.Radiobutton(root, text="Microfone", variable=method_var, value='Microfone').grid(row=2, column=2)

tk.Button(root, text="Iniciar", command=start_game).grid(row=3, column=0, columnspan=3)
tk.Button(root, text="Parar", command=stop_game).grid(row=3, column=3, columnspan=3)
tk.Button(root, text="Testar Microfone", command=test_microphone).grid(row=4, column=0, columnspan=3)

global score_label
score_label = tk.Label(root, text="Pontuação: 0")
score_label.grid(row=5, column=0, columnspan=3)

root.protocol("WM_DELETE_WINDOW", on_exit)

root.mainloop()
