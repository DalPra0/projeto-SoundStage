import customtkinter as ctk
import pyaudio
import numpy as np
import pygame
import time
import json
from threading import Thread
from tkinter import simpledialog, messagebox

BPM_CHOICES = [30, 60, 120, 180, 200, 220, 280, 360]
TIME_SIGNATURES = {'3/4': 3, '4/4': 4}
MARGIN_OF_ERROR_MICROPHONE = 1500
MARGIN_OF_ERROR_SPACE = 400

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
calibrated_volume = 0

scores_frame = None

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

audio_stream.start_stream()

def save_score(name, mode, bpm, rhythm, score):
    if score == 0:
        print("Pontuação zero. Nada será salvo.")
        return

    score_data = {
        "Name": name,
        "Mode": mode,
        "BPM": bpm,
        "Rhythm": rhythm,
        "Score": score
    }

    try:
        scores = []
        with open("pontuacao.json", "r") as file:
            for line in file:
                if line.strip():
                    score_entry = json.loads(line.strip())
                    scores.append(score_entry)

        player_exists = False
        for existing_score in scores:
            if existing_score["Name"] == name:
                if existing_score["Mode"] == mode:
                    existing_score.update(score_data)
                else:
                    scores.append(score_data)
                player_exists = True
                break

        if not player_exists:
            scores.append(score_data)

        with open("pontuacao.json", "w") as file:
            for score_entry in scores:
                json.dump(score_entry, file)
                file.write("\n")

        print("Pontuação salva com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar a pontuação: {e}")

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

def calibrate_microphone():
    global calibrated_volume
    calib_label.configure(text="Calibrando microfone... Por favor, mantenha silêncio.")
    max_volume = 0
    start_calibration = time.time()
    
    while time.time() - start_calibration < 5:
        if volume > max_volume:
            max_volume = volume
        calib_label.configure(text=f"Calibrando... Volume atual: {volume:.2f}")
        root.update()
        time.sleep(0.1)

    calibrated_volume = max_volume + 500
    calib_label.configure(text=f"Calibração concluída. Volume de referência: {calibrated_volume}")

def start_game():
    global running, volume, use_microphone, bpm, time_signature, score, start_time
    running = True
    volume = 0
    score = 0

    bpm = int(bpm_var.get())
    time_signature = TIME_SIGNATURES[time_sig_var.get()]

    if use_microphone:
        calibrate_microphone()

    metronome_thread = Thread(target=play_metronome, args=(bpm, time_signature))
    metronome_thread.start()

    start_time = time.time()
    root.bind("<space>", on_space_press)
    update_game()

def stop_game():
    global running
    running = False
    pygame.mixer.stop()
    root.unbind("<space>")

    handle_game_stop()

def handle_game_stop():
    global score
    score_label.configure(text=f"Pontuação final: {score}")
    
    mode = "Microfone" if use_microphone else "Espaco"
    name = ask_for_name(mode)

    if name:
        save_score(name, mode, bpm, time_sig_var.get(), score)

    score = 0
    score_label.configure(text="Pontuação: 0")

def update_game():
    global start_time, score, running, last_beat_time

    if not running:
        return

    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= (60 / bpm):
        last_beat_time = current_time
        start_time = current_time
        
        if use_microphone and volume > calibrated_volume:
            check_microphone_beat(current_time)

    volume_label.configure(text=f"Volume: {volume:.2f}")
    root.after(10, update_game)

def check_microphone_beat(current_time):
    global score
    if abs(current_time - last_beat_time) <= (60 / bpm) * MARGIN_OF_ERROR_MICROPHONE / 1000:
        score += 1
        score_label.configure(text=f"Pontuação: {score}")

def on_space_press(event):
    global score, last_beat_time

    current_time = time.time()

    if abs(current_time - last_beat_time) <= (60 / bpm) * MARGIN_OF_ERROR_SPACE / 1000:
        score += 1
        score_label.configure(text=f"Pontuação: {score}")

def on_exit():
    global running
    running = False
    audio_stream.stop_stream()
    audio_stream.close()
    p.terminate()

    print(score)
    pygame.mixer.quit()
    pygame.quit()

    root.quit()

def ask_for_name(mode=None):
    if mode == "Microfone":
        return ctk.CTkInputDialog(title="Nome", text="Por favor, digite seu nome (modo Microfone):").get_input()
    elif mode == "Espaco":
        return ctk.CTkInputDialog(title="Nome", text="Por favor, digite seu nome (modo Espaco):").get_input()
    else:
        return ctk.CTkInputDialog(title="Nome", text="Por favor, digite seu nome:").get_input()

def test_microphone():
    global running
    test_window = ctk.CTkToplevel(root)
    test_window.title("Testar Microfone")
    
    ctk.CTkLabel(test_window, text="Teste o volume do microfone").pack()
    
    vol_label = ctk.CTkLabel(test_window, text="Volume: 0.00")
    vol_label.pack()
    
    def update_volume():
        vol_label.configure(text=f"Volume: {volume:.2f}")
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

def back_to_main_screen():
    global running
    running = False
    if use_microphone:
        audio_stream.stop_stream()
    show_selection_screen()

def show_game_screen():
    selection_frame.pack_forget()
    game_frame.pack()

def show_selection_screen():
    global scores_frame
    if scores_frame:
        scores_frame.pack_forget()
    game_frame.pack_forget()
    selection_frame.pack()

def select_space_method():
    global use_microphone
    use_microphone = False
    show_game_screen()

def select_microphone_method():
    global use_microphone
    use_microphone = True
    show_game_screen()

def show_scores_screen(root):
    global scores_frame
    selection_frame.pack_forget()
    scores_frame = ctk.CTkFrame(root)
    scores_frame.pack()

    def load_scores():
        try:
            with open("pontuacao.json", "r") as file:
                scores = file.readlines()
                return scores
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar o arquivo de pontuação: {e}")
            return []

    def display_scores():
        try:
            with open("pontuacao.json", "r") as file:
                scores = file.readlines()
                for idx, score_line in enumerate(scores, start=1):
                    try:
                        score_data = json.loads(score_line)
                        ctk.CTkLabel(scores_frame, text=f"{idx}. {score_data['Name']} - {score_data['Mode']} - BPM: {score_data['BPM']} - {score_data['Rhythm']} - Pontuação: {score_data['Score']}").pack()
                    except json.JSONDecodeError as e:
                        print(f"Erro ao carregar pontuação: {e}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar o arquivo de pontuação: {e}")

    ctk.CTkLabel(scores_frame, text="Pontuações").pack()
    display_scores()
    ctk.CTkButton(scores_frame, text="Voltar", command=back_to_main_screen).pack()

root = ctk.CTk()
root.title("Jogo de Ritmo")

selection_frame = ctk.CTkFrame(root)
game_frame = ctk.CTkFrame(root)

ctk.CTkLabel(selection_frame, text="Escolha o método de entrada:").pack()
ctk.CTkButton(selection_frame, text="Espaço", command=select_space_method).pack(pady=2)
ctk.CTkButton(selection_frame, text="Microfone", command=select_microphone_method).pack(pady=2)
ctk.CTkButton(selection_frame, text="Pontuações", command=lambda: show_scores_screen(root)).pack(pady=2)
ctk.CTkButton(selection_frame, text="Testar Microfone", command=test_microphone).pack(pady=3)

back_button = ctk.CTkButton(selection_frame, text="Voltar", command=back_to_main_screen)
back_button.pack()

ctk.CTkLabel(game_frame, text="Escolha o BPM:").grid(row=0, column=0)
bpm_var = ctk.StringVar(value=str(BPM_CHOICES[0]))
bpm_menu = ctk.CTkOptionMenu(game_frame, variable=bpm_var, values=[str(bpm) for bpm in BPM_CHOICES])
bpm_menu.grid(row=0, column=1)

ctk.CTkLabel(game_frame, text="Escolha o compasso:").grid(row=1, column=0)
time_sig_var = ctk.StringVar(value='4/4')
time_sig_menu = ctk.CTkOptionMenu(game_frame, variable=time_sig_var, values=list(TIME_SIGNATURES.keys()))
time_sig_menu.grid(row=1, column=1)

ctk.CTkButton(game_frame, text="Iniciar", command=start_game).grid(row=2, column=0, columnspan=2)
ctk.CTkButton(game_frame, text="Parar", command=stop_game).grid(row=3, column=0, columnspan=2)

global score_label
score_label = ctk.CTkLabel(game_frame, text="Pontuação: 0")
score_label.grid(row=4, column=0, columnspan=2)

calib_label = ctk.CTkLabel(game_frame, text="Calibração: Não iniciada")
calib_label.grid(row=5, column=0, columnspan=2)

volume_label = ctk.CTkLabel(game_frame, text="Volume: 0.00")
volume_label.grid(row=6, column=0, columnspan=2)

back_button = ctk.CTkButton(game_frame, text="Voltar", command=back_to_main_screen)
back_button.grid(row=7, column=0, columnspan=2)

root.protocol("WM_DELETE_WINDOW", on_exit)

show_selection_screen()

root.mainloop()
