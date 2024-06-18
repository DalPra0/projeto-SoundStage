import PySimpleGUI as sg
import random
import time
import os

acordes_guitarra = {
    'C': 'C.png',
    'D': 'D.png',
    'E': 'E.png',
    'F': 'F.png',
    'G': 'G.png',
    'A': 'A.png',
    'B': 'B.png'
}

acordes_baixo = {
    'C': 'C_bass.png',
    'D': 'D_bass.png',
    'E': 'E_bass.png',
    'F': 'F_bass.png',
    'G': 'G_bass.png',
    'A': 'A_bass.png',
    'B': 'B_bass.png'
}

acordes_violino = {
    'C': 'C_violin.png',
    'D': 'D_violin.png',
    'E': 'E_violin.png',
    'F': 'F_violin.png',
    'G': 'G_violin.png',
    'A': 'A_violin.png',
    'B': 'B_violin.png'
}

acordes_piano = {
    'C': 'C_piano.png',
    'D': 'D_piano.png',
    'E': 'E_piano.png',
    'F': 'F_piano.png',
    'G': 'G_piano.png',
    'A': 'A_piano.png',
    'B': 'B_piano.png'
}

diretorio_imagens = 'imagens_acordes'

def tela_escolha_instrumento():
    layout_escolha = [
        [sg.Text('Escolha o instrumento:')],
        [sg.Radio('Guitarra', 'instrumento', key='-GUITARRA-', default=True),
         sg.Radio('Baixo', 'instrumento', key='-BAIXO-'),
         sg.Radio('Violino', 'instrumento', key='-VIOLINO-'),
         sg.Radio('Piano', 'instrumento', key='-PIANO-')],
        [sg.Button('OK'), sg.Button('Sair')]
    ]

    window_escolha = sg.Window('Escolha do Instrumento', layout_escolha)

    while True:
        event, values = window_escolha.read()
        if event in (sg.WINDOW_CLOSED, 'Sair'):
            window_escolha.close()
            return None
        if event == 'OK':
            if values['-GUITARRA-']:
                instrumento = 'guitarra'
            elif values['-BAIXO-']:
                instrumento = 'baixo'
            elif values['-VIOLINO-']:
                instrumento = 'violino'
            else:
                instrumento = 'piano'
            window_escolha.close()
            return instrumento

def exibir_acordes(instrumento):
    if instrumento == 'guitarra':
        acordes = acordes_guitarra
        tempo_minimo_acorde = 5
    elif instrumento == 'baixo':
        acordes = acordes_baixo
        tempo_minimo_acorde = 5
    elif instrumento == 'violino':
        acordes = acordes_violino
        tempo_minimo_acorde = 2
    else:
        acordes = acordes_piano
        tempo_minimo_acorde = 5

    layout_acordes = [
        [sg.Image(filename='', key='-ACORDE-')],
        [sg.Button('Sair')]
    ]

    tamanho_janela = (180, 270) if instrumento == 'violino' else (None, None)
    window_acordes = sg.Window(f'Acordes de {instrumento.capitalize()}', layout_acordes, finalize=True, size=tamanho_janela, element_justification='center')

    def atualizar_imagem_acorde():
        try:
            acorde = random.choice(list(acordes.keys()))
            imagem_acorde = os.path.join(diretorio_imagens, acordes[acorde])
            if not os.path.exists(imagem_acorde):
                raise FileNotFoundError(f"Arquivo {imagem_acorde} não encontrado.")
            window_acordes['-ACORDE-'].update(filename=imagem_acorde)
        except Exception as e:
            sg.popup_error("Erro ao atualizar a imagem:", str(e))

    while True:
        event, values = window_acordes.read(timeout=100)
        if event in (sg.WINDOW_CLOSED, 'Sair'):
            window_acordes.close()
            return

        atualizar_imagem_acorde()
        
        if instrumento == 'violino':
            tempo_exibicao = random.randint(2, 5)
        else:
            tempo_exibicao = max(tempo_minimo_acorde, random.randint(5, 10))
        
        inicio_exibicao = time.time()

        while True:
            event, values = window_acordes.read(timeout=100)
            if event in (sg.WINDOW_CLOSED, 'Sair'):
                window_acordes.close()
                return
            if time.time() - inicio_exibicao >= tempo_exibicao:
                break

while True:
    instrumento = tela_escolha_instrumento()
    if instrumento is None:
        break
    exibir_acordes(instrumento)