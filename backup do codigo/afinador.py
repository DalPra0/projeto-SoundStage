import pyaudio
import numpy as np
import tkinter as tk
from tkinter import messagebox

# Configurações do PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Função para detectar a frequência dominante
def detect_frequency(data):
    # Aplica a Transformada de Fourier ao sinal de entrada
    fft_data = np.fft.fft(data)
    # Calcula as amplitudes das frequências
    magnitude = np.abs(fft_data)
    # Encontra o índice da maior amplitude (frequência dominante)
    index = np.argmax(magnitude)
    # Calcula a frequência correspondente ao índice
    freq = index * RATE / CHUNK
    return freq

# Função para converter a frequência em nome da nota musical
def freq_to_note(frequency):
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    A4_freq = 440  # Frequência da nota A4 (440 Hz)
    # Calcula o número de semitons de distância entre a frequência fornecida e a frequência de A4
    semitones_from_A4 = 12 * np.log2(frequency / A4_freq)
    # Calcula o índice da nota na lista de notas
    note_index = int(round(semitones_from_A4)) % 12
    return notes[note_index]

class TunerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Afinador Universal")
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)
        
        self.start_button = tk.Button(self.frame, text="Iniciar", command=self.start_tuner)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = tk.Button(self.frame, text="Parar", command=self.stop_tuner, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.note_label = tk.Label(self.frame, text="Nota:")
        self.note_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        self.stream = None
        self.p = pyaudio.PyAudio()
        self.running = False
    
    def start_tuner(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
        
        self.update_tuner()
    
    def stop_tuner(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
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
            self.note_label.config(text=f"Nota: {note} ({freq:.2f} Hz)")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
        if self.running:
            self.root.after(100, self.update_tuner)

# Criando a aplicação Tkinter
root = tk.Tk()
app = TunerApp(root)
root.mainloop()