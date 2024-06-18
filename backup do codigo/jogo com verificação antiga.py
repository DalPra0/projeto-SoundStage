import pyaudio
import numpy as np
import pygame
import time
import tkinter as tk
import json
from tkinter import simpledialog, messagebox
from threading import Thread

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
                score_entry = json.loads(line.strip())
                scores.append(score_entry)

        # Verifica se o jogador já existe na lista de scores
        player_exists = False
        for existing_score in scores:
            if existing_score["Name"] == name:
                if existing_score["Mode"] == mode:
                    # Se for a mesma pessoa e mesmo modo, reescreve a pontuação
                    existing_score.update(score_data)
                else:
                    # Se for a mesma pessoa, mas modo diferente, adiciona nova entrada
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
    calib_label.config(text="Calibrando microfone... Por favor, mantenha silêncio.")
    max_volume = 0
    start_calibration = time.time()
    
    while time.time() - start_calibration < 5:
        if volume > max_volume:
            max_volume = volume
        calib_label.config(text=f"Calibrando... Volume atual: {volume:.2f}")
        root.update()  # Atualiza a interface gráfica
        time.sleep(0.1)

    calibrated_volume = max_volume + 200  # Adicionando um valor para garantir que os sons maiores sejam capturados
    calib_label.config(text=f"Calibração concluída. Volume de referência: {calibrated_volume}")

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

    # Chamando a função para lidar com o fim do jogo e salvar a pontuação
    handle_game_stop()

def handle_game_stop():
    global score
    score_label.config(text=f"Pontuação final: {score}")
    
    mode = "Microfone" if use_microphone else "Espaco"  # Determina o modo usado
    name = ask_for_name(mode)  # Solicita o nome do jogador com base no modo usado

    if name:  # Verifica se um nome foi digitado
        save_score(name, mode, bpm, time_sig_var.get(), score)  # Salva a pontuação

    # Resetando os valores globais
    score = 0
    score_label.config(text="Pontuação: 0")

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

    volume_label.config(text=f"Volume: {volume:.2f}")
    root.after(10, update_game)

def check_microphone_beat(current_time):
    global score
    if abs(current_time - last_beat_time) <= (60 / bpm) * MARGIN_OF_ERROR_MICROPHONE / 1000:
        score += 1
        score_label.config(text=f"Pontuação: {score}")

def on_space_press(event):
    global score, last_beat_time

    current_time = time.time()

    if abs(current_time - last_beat_time) <= (60 / bpm) * MARGIN_OF_ERROR_SPACE / 1000:
        score += 1
        score_label.config(text=f"Pontuação: {score}")

def on_exit():
    global running
    running = False  # Define running como False para parar o loop principal do jogo
    audio_stream.stop_stream()  # Para o stream de áudio
    audio_stream.close()  # Fecha o stream de áudio
    p.terminate()  # Encerra o PyAudio

    print(score)  # Apenas para depuração
    pygame.mixer.quit()  # Encerra o mixer do Pygame
    pygame.quit()  # Encerra o Pygame

    root.quit()  # Sai do loop principal do tkinter

def ask_for_name(mode=None):
    if mode == "Microfone":
        return tk.simpledialog.askstring("Nome", "Por favor, digite seu nome (modo Microfone):")
    elif mode == "Espaco":
        return tk.simpledialog.askstring("Nome", "Por favor, digite seu nome (modo Espaco):")
    else:
        return tk.simpledialog.askstring("Nome", "Por favor, digite seu nome:")

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
    global scores_frame  # Indica que estamos utilizando a variável global scores_frame
    if scores_frame:  # Verifica se scores_frame está definido e não é None
        scores_frame.pack_forget()  # Esconde o frame da pontuação, se estiver visível
    game_frame.pack_forget()  # Esconde o frame do jogo, se estiver visível
    selection_frame.pack()  # Mostra o frame de seleção

def select_space_method():
    global use_microphone
    use_microphone = False
    show_game_screen()

def select_microphone_method():
    global use_microphone
    use_microphone = True
    show_game_screen()

def show_scores_screen(root):
    global scores_frame  # Indica que estamos utilizando a variável global scores_frame
    selection_frame.pack_forget()
    scores_frame = tk.Frame(root)  # Cria o frame para exibir as pontuações
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
                        score_data = json.loads(score_line.strip())
                        tk.Label(scores_frame, text=f"{idx}. {score_data['Name']}: {score_data['Mode']} - BPM: {score_data['BPM']}, Rhythm: {score_data['Rhythm']}, Score: {score_data['Score']}").pack()
                    except json.JSONDecodeError as e:
                        print(f"Erro ao carregar pontuação: {e}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar o arquivo de pontuação: {e}")

    tk.Label(scores_frame, text="Pontuações").pack()
    display_scores()
    tk.Button(scores_frame, text="Voltar", command=back_to_main_screen).pack()

root = tk.Tk()
root.title("Jogo de Ritmo")

selection_frame = tk.Frame(root)
game_frame = tk.Frame(root)

tk.Label(selection_frame, text="Escolha o método de entrada:").pack()
tk.Button(selection_frame, text="Espaço", command=select_space_method).pack()
tk.Button(selection_frame, text="Microfone", command=select_microphone_method).pack()
tk.Button(selection_frame, text="Pontuações", command=lambda: show_scores_screen(root)).pack()
tk.Button(selection_frame, text="Testar Microfone", command=test_microphone).pack()

# Adicionando o botão de voltar na tela de seleção
back_button = tk.Button(selection_frame, text="Voltar", command=back_to_main_screen)
back_button.pack()

# Tela do Jogo
tk.Label(game_frame, text="Escolha o BPM:").grid(row=0, column=0)
bpm_var = tk.StringVar(value=str(BPM_CHOICES[0]))
bpm_menu = tk.OptionMenu(game_frame, bpm_var, *BPM_CHOICES)
bpm_menu.grid(row=0, column=1)

tk.Label(game_frame, text="Escolha o compasso:").grid(row=1, column=0)
time_sig_var = tk.StringVar(value='4/4')
time_sig_menu = tk.OptionMenu(game_frame, time_sig_var, *TIME_SIGNATURES.keys())
time_sig_menu.grid(row=1, column=1)

tk.Button(game_frame, text="Iniciar", command=start_game).grid(row=2, column=0, columnspan=2)
tk.Button(game_frame, text="Parar", command=stop_game).grid(row=3, column=0, columnspan=2)

global score_label
score_label = tk.Label(game_frame, text="Pontuação: 0")
score_label.grid(row=4, column=0, columnspan=2)

calib_label = tk.Label(game_frame, text="Calibração: Não iniciada")
calib_label.grid(row=5, column=0, columnspan=2)

volume_label = tk.Label(game_frame, text="Volume: 0.00")
volume_label.grid(row=6, column=0, columnspan=2)

# Adicionando o botão de voltar na tela do jogo
back_button = tk.Button(game_frame, text="Voltar", command=back_to_main_screen)
back_button.grid(row=7, column=0, columnspan=2)

root.protocol("WM_DELETE_WINDOW", on_exit)

show_selection_screen()

root.mainloop()
