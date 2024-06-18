import pyaudio
import numpy as np
import customtkinter as ctk
from tkinter import messagebox

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def detect_frequency(data):
    fft_data = np.fft.fft(data)
    magnitude = np.abs(fft_data)
    magnitude = magnitude[:len(magnitude) // 2]
    index = np.argmax(magnitude)
    freq = index * RATE / CHUNK
    return freq

def freq_to_note(frequency):
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    A4_freq = 440.0
    C0_freq = A4_freq * 2**(-4.75)
    semitones_from_C0 = 12 * np.log2(frequency / C0_freq)
    note_index = int(round(semitones_from_C0)) % 12
    return notes[note_index]

class TunerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Afinador Universal")
        self.geometry("400x200")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.create_widgets()
        self.stream = None
        self.p = pyaudio.PyAudio()
        self.running = False

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        self.start_button = ctk.CTkButton(self.main_frame, text="Iniciar", command=self.start_tuner)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ctk.CTkButton(self.main_frame, text="Parar", command=self.stop_tuner, state=ctk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.note_label = ctk.CTkLabel(self.main_frame, text="Nota:")
        self.note_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def start_tuner(self):
        self.running = True
        self.start_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)

        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)

        self.update_tuner()

    def stop_tuner(self):
        self.running = False
        self.start_button.configure(state=ctk.NORMAL)
        self.stop_button.configure(state=ctk.DISABLED)

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()

    def update_tuner(self):
        if self.stream is None or not self.running:
            return

        try:
            audio_data = self.stream.read(CHUNK)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            freq = detect_frequency(audio_array)
            note = freq_to_note(freq)
            self.note_label.configure(text=f"Nota: {note} ({freq:.2f} Hz)")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

        if self.running:
            self.after(100, self.update_tuner)

if __name__ == "__main__":
    app = TunerApp()
    app.mainloop()