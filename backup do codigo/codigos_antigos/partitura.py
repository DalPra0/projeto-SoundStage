import PySimpleGUI as sg
import fitz  # PyMuPDF
import os

# Diretórios de partituras
scores_dir = 'partituras'

# Lista de partituras e seus arquivos PDF correspondentes
scores = {
    'Sweet Child of Mine': 'sweet.pdf',
    'No More Tears': 'no_more_tears.pdf'\
    
    # Adicione mais partituras aqui
}

# Função que cria e exibe a janela da partitura
def show_score_window(selected_score):
    pdf_path = os.path.join(scores_dir, scores[selected_score])

    # Carregar a primeira página da partitura
    doc = fitz.open(pdf_path)
    page_count = doc.page_count
    current_page = 0

    # Função para atualizar a imagem da página
    def update_image(page_number):
        pix = doc.load_page(page_number).get_pixmap()
        image_bytes = pix.tobytes()
        window_partitura['-SCORE IMAGE-'].update(data=image_bytes)

    # Layout da janela da partitura
    layout_partitura = [
        [sg.Image(key='-SCORE IMAGE-', size=(800, 600))],
        [sg.Button('Voltar', key='-PREV-'), sg.Button('Avançar', key='-NEXT-'), sg.Button('Fechar', key='-CLOSE-')]
    ]
    window_partitura = sg.Window(selected_score, layout_partitura, finalize=True, element_justification='center', resizable=True)
    update_image(current_page)
    
    # Loop da janela da partitura
    while True:
        event, values = window_partitura.read()
        if event == sg.WINDOW_CLOSED or event == '-CLOSE-':
            window_partitura.close()
            break
        elif event == '-PREV-' or event == sg.KEYDOWN and values['_KEYBOARD_'] == 'Up':
            if current_page > 0:
                current_page -= 1
                update_image(current_page)
        elif event == '-NEXT-' or event == sg.KEYDOWN and values['_KEYBOARD_'] == 'Down':
            if current_page < page_count - 1:
                current_page += 1
                update_image(current_page)

# Layout da janela principal
layout = [
    [sg.Text('Selecione uma partitura:')],
    [sg.Listbox(values=list(scores.keys()), size=(30, 10), key='-SCORE LIST-')],
    [sg.Button('Abrir'), sg.Button('Sair')]
]

# Criação da janela principal
window = sg.Window('Visualizador de Partituras', layout)

# Loop da janela principal
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Sair':
        break
    elif event == 'Abrir':
        selected_score = values['-SCORE LIST-'][0] if values['-SCORE LIST-'] else None
        if selected_score:
            show_score_window(selected_score)

window.close()
