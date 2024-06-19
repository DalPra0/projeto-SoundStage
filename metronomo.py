import customtkinter as ctk
from tkinter import messagebox
import time
import pygame
from threading import Thread
import json
import os

CONFIG_FILE = "settings.json"
HISTORY_FILE = "history.json"

class Metronome(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Metronome")
        self.geometry("400x300")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.running = False
        self.unlimited_bpm = False

        self.bpm = ctk.IntVar(value=120)
        self.time_signature = ctk.StringVar(value="4/4")

        self.load_settings()
        self.create_widgets()
        pygame.mixer.init()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="BPM:").grid(row=0, column=0, sticky="w")
        self.bpm_entry = ctk.CTkEntry(self.main_frame, textvariable=self.bpm, width=50)
        self.bpm_entry.grid(row=0, column=1, sticky="we")

        ctk.CTkLabel(self.main_frame, text="Ritmo:").grid(row=1, column=0, sticky="w")
        self.time_signature_combo = ctk.CTkComboBox(self.main_frame, values=["3/4", "4/4"], variable=self.time_signature)
        self.time_signature_combo.grid(row=1, column=1, sticky="we")

        self.start_button = ctk.CTkButton(self.main_frame, text="Iniciar", command=self.start_metronome)
        self.start_button.grid(row=2, column=0, sticky="w")
        
        self.stop_button = ctk.CTkButton(self.main_frame, text="Parar", command=self.stop_metronome, state="disabled")
        self.stop_button.grid(row=2, column=1, sticky="w")

        self.save_bpm_button = ctk.CTkButton(self.main_frame, text="Salvar BPM", command=self.save_bpm)
        self.save_bpm_button.grid(row=3, column=0, columnspan=2, sticky="we")

        self.view_saved_button = ctk.CTkButton(self.main_frame, text="Ver Batidas Salvas", command=self.view_saved_bpms)
        self.view_saved_button.grid(row=4, column=0, columnspan=2, sticky="we")

        self.settings_button = ctk.CTkButton(self.main_frame, text="Configurações", command=self.open_settings)
        self.settings_button.grid(row=5, column=0, columnspan=2, sticky="we")

        self.bpm_detect_button = ctk.CTkButton(self.main_frame, text="Identificar BPM", command=self.start_bpm_detect)
        self.bpm_detect_button.grid(row=6, column=0, columnspan=2, sticky="we")

    def start_metronome(self):
        try:
            bpm = int(self.bpm.get())
            if not self.unlimited_bpm and not (1 <= bpm <= 360):
                raise ValueError("BPM deve estar entre 1 e 360")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        self.metronome_thread = Thread(target=self.run_metronome)
        self.metronome_thread.start()

    def stop_metronome(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def run_metronome(self):
        bpm = self.bpm.get()
        time_signature = self.time_signature.get()

        beat_duration = 60.0 / bpm

        beats_per_measure = int(time_signature.split('/')[0])

        high_tick_sound = pygame.mixer.Sound("sounds/high_tick.wav")
        tick_sound = pygame.mixer.Sound("sounds/tick.wav")

        while self.running:
            for beat in range(beats_per_measure):
                if not self.running:
                    break
                if beat == 0:
                    high_tick_sound.play()
                else:
                    tick_sound.play()
                time.sleep(beat_duration)

        pygame.mixer.stop()

    def save_bpm(self):
        bpm = self.bpm.get()
        music_name = ctk.CTkInputDialog(text="Nome da Música:", title="Salvar BPM").get_input()
        if not music_name:
            return

        history = self.load_history()
        history[music_name] = bpm
        with open(HISTORY_FILE, "w") as file:
            json.dump(history, file)
        messagebox.showinfo("Sucesso", f"BPM de {bpm} para '{music_name}' salvo com sucesso.")

    def view_saved_bpms(self):
        history = self.load_history()
        if not history:
            messagebox.showinfo("Informação", "Nenhum BPM salvo encontrado.")
            return

        top = ctk.CTkToplevel(self)
        top.title("Batidas Salvas")

        for music_name, bpm in history.items():
            button = ctk.CTkButton(top, text=f"{music_name}: {bpm} BPM", command=lambda b=bpm: self.set_bpm(b))
            button.pack(pady=5)

    def set_bpm(self, bpm):
        self.bpm.set(bpm)

    def open_settings(self):
        top = ctk.CTkToplevel(self)
        top.title("Configurações")

        clear_button = ctk.CTkButton(top, text="Deletar Histórico", command=self.clear_history)
        clear_button.pack(pady=5)

        remove_limit_button = ctk.CTkButton(top, text="Remover Limite de BPM", command=self.confirm_remove_limit)
        remove_limit_button.pack(pady=5)

    def clear_history(self):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        messagebox.showinfo("Sucesso", "Histórico deletado com sucesso.")

    def confirm_remove_limit(self):
        if messagebox.askyesno("Confirmação", "Você tem certeza que quer remover o limite de BPM? Isso pode causar problemas no programa."):
            if messagebox.askyesno("Confirmação", "Tem certeza mesmo? BPMs muito altos podem quebrar o programa."):
                self.unlimited_bpm = True
                messagebox.showinfo("Sucesso", "Limite de BPM removido. Use com cuidado!")

    def start_bpm_detect(self):
        self.tap_times = []
        self.bind("<space>", self.tap_bpm)
        messagebox.showinfo("Identificação de BPM", "Aperte a barra de espaço no ritmo da música.")

    def tap_bpm(self, event):
        current_time = time.time()
        self.tap_times.append(current_time)
        if len(self.tap_times) > 1:
            intervals = [j-i for i, j in zip(self.tap_times[:-1], self.tap_times[1:])]
            avg_interval = sum(intervals) / len(intervals)
            bpm = 60 / avg_interval
            self.bpm.set(int(bpm))

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                settings = json.load(file)
                self.bpm.set(settings.get("bpm", 120))
                self.time_signature.set(settings.get("time_signature", "4/4"))

    def save_settings(self):
        try:
            settings = {
                "bpm": int(self.bpm.get()),
                "time_signature": self.time_signature.get()
            }
            with open(CONFIG_FILE, "w") as file:
                json.dump(settings, file)
        except ValueError:
            pass

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as file:
                return json.load(file)
        return {}

    def on_closing(self):
        self.save_settings()
        self.destroy()

if __name__ == "__main__":
    app = Metronome()
    app.mainloop()