import tkinter as tk
import numpy as np
import pyaudio
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

RATE = 44100 
BUFFER_SIZE = 4096 
FORMAT = pyaudio.paInt16 

NOTE_FREQS = {
    "C0": (16.35, 17.31), "C#0": (17.32, 18.34), "D0": (18.35, 19.44), "D#0": (19.45, 20.59), "E0": (20.60, 21.83), 
    "F0": (21.83, 23.12), "F#0": (23.12, 24.50), "G0": (24.50, 25.96), "G#0": (25.96, 27.50), "A0": (27.50, 29.14), 
    "A#0": (29.14, 30.87), "B0": (30.87, 32.70), "C1": (32.70, 34.65), "C#1": (34.65, 36.71), "D1": (36.71, 38.89), 
    "D#1": (38.89, 41.20), "E1": (41.20, 43.65), "F1": (43.65, 46.25), "F#1": (46.25, 49.00), "G1": (49.00, 51.91), 
    "G#1": (51.91, 55.00), "A1": (55.00, 58.27), "A#1": (58.27, 61.74), "B1": (61.74, 65.41), "C2": (65.41, 69.30), 
    "C#2": (69.30, 73.42), "D2": (73.42, 77.78), "D#2": (77.78, 82.41), "E2": (82.41, 87.31), "F2": (87.31, 92.50), 
    "F#2": (92.50, 98.00), "G2": (98.00, 103.83), "G#2": (103.83, 110.00), "A2": (110.00, 116.54), "A#2": (116.54, 123.47), 
    "B2": (123.47, 130.81), "C3": (130.81, 138.59), "C#3": (138.59, 146.83), "D3": (146.83, 155.56), "D#3": (155.56, 164.81), 
    "E3": (164.81, 174.61), "F3": (174.61, 185.00), "F#3": (185.00, 196.00), "G3": (196.00, 207.65), "G#3": (207.65, 220.00), 
    "A3": (220.00, 233.08), "A#3": (233.08, 246.94), "B3": (246.94, 261.63), "C4": (261.63, 277.18), "C#4": (277.18, 293.66), 
    "D4": (293.66, 311.13), "D#4": (311.13, 329.63), "E4": (329.63, 349.23), "F4": (349.23, 369.99), "F#4": (369.99, 392.00), 
    "G4": (392.00, 415.30), "G#4": (415.30, 440.00), "A4": (440.00, 466.16), "A#4": (466.16, 493.88), "B4": (493.88, 523.25), 
    "C5": (523.25, 554.37), "C#5": (554.37, 587.33), "D5": (587.33, 622.25), "D#5": (622.25, 659.25), "E5": (659.25, 698.46), 
    "F5": (698.46, 739.99), "F#5": (739.99, 783.99), "G5": (783.99, 830.61), "G#5": (830.61, 880.00), "A5": (880.00, 932.33), 
    "A#5": (932.33, 987.77), "B5": (987.77, 1046.50), "C6": (1046.50, 1108.73), "C#6": (1108.73, 1174.66), "D6": (1174.66, 1244.51), 
    "D#6": (1244.51, 1318.51), "E6": (1318.51, 1396.91), "F6": (1396.91, 1479.98), "F#6": (1479.98, 1567.98), "G6": (1567.98, 1661.22), 
    "G#6": (1661.22, 1760.00), "A6": (1760.00, 1864.66), "A#6": (1864.66, 1975.53), "B6": (1975.53, 2093.00), "C7": (2093.00, 2217.46), 
    "C#7": (2217.46, 2349.32), "D7": (2349.32, 2489.02), "D#7": (2489.02, 2637.02), "E7": (2637.02, 2793.83), "F7": (2793.83, 2959.96), 
    "F#7": (2959.96, 3135.96), "G7": (3135.96, 3322.44), "G#7": (3322.44, 3520.00), "A7": (3520.00, 3729.31), "A#7": (3729.31, 3951.07), 
    "B7": (3951.07, 4186.01), "C8": (4186.01, 4434.92), "C#8": (4434.92, 4698.63), "D8": (4698.63, 4978.03), "D#8": (4978.03, 5274.04)
}

def find_closest_note_freq(freq):
    for note, (low, high) in NOTE_FREQS.items():
        if low <= freq <= high:
            return note, (low + high) / 2
    return None, 0

class TunerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Afinador")
        
        self.note_label = tk.Label(self, text="Afinador", font=("Helvetica", 32))
        self.note_label.pack(pady=20)

        self.freq_label = tk.Label(self, text="", font=("Helvetica", 24))
        self.freq_label.pack(pady=20)

        self.start_button = tk.Button(self, text="Iniciar", command=self.start_tuning)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Parar", command=self.stop_tuning, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.running = False
        self.p = pyaudio.PyAudio()

    def start_tuning(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stream = self.p.open(format=FORMAT,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=BUFFER_SIZE)
        self.update_tuner()

    def stop_tuning(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stream.stop_stream()
        self.stream.close()

    def update_tuner(self):
        if self.running:
            data = np.frombuffer(self.stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.int16)
            freq = self.detect_frequency(data)
            if freq > 0:
                note, closest_freq = find_closest_note_freq(freq)
                if note:
                    self.note_label.config(text=note)
                    self.freq_label.config(text=f"Freq: {freq:.2f} Hz")
                else:
                    self.note_label.config(text="N/A")
                    self.freq_label.config(text=f"Freq: {freq:.2f} Hz")
            else:
                self.note_label.config(text="N/A")
                self.freq_label.config(text="Freq: N/A")

            self.after(100, self.update_tuner)

    def detect_frequency(self, data):
        N = len(data)
        windowed = data * np.hanning(N)
        spectrum = np.abs(fft(windowed))[:N // 2]
        frequencies = fftfreq(N, 1 / RATE)[:N // 2]
        
        peak_indices, _ = find_peaks(spectrum, height=np.max(spectrum)/5) 
        if peak_indices.size > 0:
            peak_freq = frequencies[peak_indices[np.argmax(spectrum[peak_indices])]]
            return peak_freq
        return 0

if __name__ == "__main__":
    app = TunerApp()
    app.mainloop()
