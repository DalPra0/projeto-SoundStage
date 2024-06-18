import customtkinter as ctk
from tkinter import messagebox
import os
import json
import subprocess

CONFIG_FILE = "configMain.json"

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação Musical")
        self.geometry("400x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.load_user_settings()

        if not self.user_settings.get("name") or not self.user_settings.get("age"):
            self.ask_user_info()

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.main_frame, text="Bem-vindo à Aplicação Musical!", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        ctk.CTkButton(self.main_frame, text="Afinador", command=self.open_afinador).pack(pady=5)
        ctk.CTkButton(self.main_frame, text="Metrônomo", command=self.open_metronome).pack(pady=5)
        ctk.CTkButton(self.main_frame, text="Leitor de Partituras", command=self.open_partitura).pack(pady=5)
        ctk.CTkButton(self.main_frame, text="Jogo", command=self.open_jogo).pack(pady=5)
        ctk.CTkButton(self.main_frame, text="Acordes", command=self.open_acordes).pack(pady=5)
        ctk.CTkButton(self.main_frame, text="Configurações", command=self.open_settings).pack(pady=5)

    def ask_user_info(self):
        def save_info():
            name = name_var.get()
            age = age_var.get()
            if name and age.isdigit():
                self.user_settings["name"] = name
                self.user_settings["age"] = int(age)
                self.save_user_settings()
                info_window.destroy()
            else:
                messagebox.showerror("Erro", "Por favor, insira um nome válido e uma idade numérica.")

        info_window = ctk.CTkToplevel(self)
        info_window.title("Informações do Usuário")

        ctk.CTkLabel(info_window, text="Nome:").pack(pady=5)
        name_var = ctk.StringVar()
        ctk.CTkEntry(info_window, textvariable=name_var).pack(pady=5)

        ctk.CTkLabel(info_window, text="Idade:").pack(pady=5)
        age_var = ctk.StringVar()
        ctk.CTkEntry(info_window, textvariable=age_var).pack(pady=5)

        ctk.CTkButton(info_window, text="Salvar", command=save_info).pack(pady=10)

    def open_afinador(self):
        subprocess.Popen(["python", "afinador.py"])

    def open_metronome(self):
        subprocess.Popen(["python", "metronomo.py"])

    def open_partitura(self):
        subprocess.Popen(["python", "partitura.py"])

    def open_settings(self):
        Settings(self)

    def open_jogo(self):
        subprocess.Popen(["python", "jogo.py"])

    def open_acordes(self):
        subprocess.Popen(["python", "acordes.py"])

    def load_user_settings(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.user_settings = json.load(file)
        else:
            self.user_settings = {"name": "", "age": 0}

    def save_user_settings(self):
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.user_settings, file)


class Settings(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configurações")

        self.master = master
        self.user_settings = master.user_settings

        ctk.CTkLabel(self, text="Nome:").pack(pady=5)
        self.name_var = ctk.StringVar(value=self.user_settings["name"])
        ctk.CTkEntry(self, textvariable=self.name_var).pack(pady=5)

        ctk.CTkLabel(self, text="Idade:").pack(pady=5)
        self.age_var = ctk.StringVar(value=str(self.user_settings["age"]))
        ctk.CTkEntry(self, textvariable=self.age_var).pack(pady=5)

        ctk.CTkButton(self, text="Salvar", command=self.save_settings).pack(pady=10)

    def save_settings(self):
        name = self.name_var.get()
        age = self.age_var.get()
        if name and age.isdigit():
            self.master.user_settings["name"] = name
            self.master.user_settings["age"] = int(age)
            self.master.save_user_settings()
            self.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, insira um nome válido e uma idade numérica.")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()