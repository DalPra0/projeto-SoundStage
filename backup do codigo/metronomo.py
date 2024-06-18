import tkinter as tk
from tkinter import ttk, messagebox
import time
import pygame
from threading import Thread
import json
import os

class Metronome:
    def __init__(self, root):
        self.root = root
        self.root.title("Metronome")

        self.running = False

        self.bpm = tk.IntVar(value=120)
        self.time_signature = tk.StringVar(value="4/4")

        self.load_settings()
        self.create_widgets()
        pygame.mixer.init()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="BPM:").grid(row=0, column=0, sticky=tk.W)
        self.bpm_entry = ttk.Entry(frame, textvariable=self.bpm, width=5)
        self.bpm_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Ritmo:").grid(row=1, column=0, sticky=tk.W)
        self.time_signature_combo = ttk.Combobox(frame, textvariable=self.time_signature, values=["3/4", "4/4"])
        self.time_signature_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))
        self.time_signature_combo.state(['readonly'])

        self.start_button = ttk.Button(frame, text="Iniciar", command=self.start_metronome)
        self.start_button.grid(row=2, column=0, sticky=tk.W)
        
        self.stop_button = ttk.Button(frame, text="Parar", command=self.stop_metronome, state='disabled')
        self.stop_button.grid(row=2, column=1, sticky=tk.W)

    def start_metronome(self):
        try:
            bpm = int(self.bpm.get())
            if not (1 <= bpm <= 360):
                raise ValueError("BPM deve estar entre 1 e 360")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        self.metronome_thread = Thread(target=self.run_metronome)
        self.metronome_thread.start()

    def stop_metronome(self):
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def run_metronome(self):
        bpm = self.bpm.get()
        time_signature = self.time_signature.get()

        beat_duration = 60.0 / bpm

        beats_per_measure = int(time_signature.split('/')[0])

        high_tick_sound = pygame.mixer.Sound("sons/high_tick.wav")
        tick_sound = pygame.mixer.Sound("sons/tick.wav")

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

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.bpm.set(settings.get("bpm", 120))
                self.time_signature.set(settings.get("time_signature", "4/4"))

    def save_settings(self):
        settings = {
            "bpm": self.bpm.get(),
            "time_signature": self.time_signature.get()
        }
        with open("settings.json", "w") as file:
            json.dump(settings, file)

    def on_closing(self):
        self.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Metronome(root)
    root.mainloop()
