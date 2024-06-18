import pygame
import sys
import random
import time

# Inicialização do pygame
pygame.init()

# Configurações principais
WIDTH, HEIGHT = 800, 600
FPS = 60
LEVELS = 10
ADMIN_CODE = "amominhanamoradajujulindaperfeita"

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fontes
FONT = pygame.font.SysFont("arial", 32)

# Sons
pygame.mixer.init()
tick_sound = pygame.mixer.Sound("tick.wav")

# Estados do jogo
MENU, GAME, LEVEL_SELECT, SETTINGS = range(4)
game_state = MENU

# Configurações de nível
current_level = 0
unlocked_levels = 1
admin_unlocked = False

# Funções auxiliares
def draw_text(screen, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    screen.blit(text_obj, (x, y))

def check_admin_code(input_code):
    global unlocked_levels, admin_unlocked
    if input_code == ADMIN_CODE:
        unlocked_levels = LEVELS
        admin_unlocked = True

def generate_rhythm(level):
    rhythm = []
    for _ in range(level + 3):  # Aumenta a complexidade com o nível
        rhythm.append(random.choice(["♪", "♫"]))
    return rhythm

def play_rhythm(screen, rhythm):
    screen.fill(WHITE)
    draw_text(screen, "Reproduza o ritmo!", FONT, BLACK, 200, 100)
    pygame.display.flip()
    x = 200
    for note in rhythm:
        if note == "♪":
            draw_text(screen, note, FONT, BLACK, x, 200)
            tick_sound.play()
            pygame.display.flip()
            pygame.time.delay(500)  # Meio segundo por batida
        elif note == "♫":
            draw_text(screen, note, FONT, BLACK, x, 200)
            tick_sound.play()
            pygame.display.flip()
            pygame.time.delay(250)  # Um quarto de segundo por batida
            tick_sound.play()
            pygame.time.delay(250)
        x += 40  # Avança a posição x para a próxima nota
    pygame.time.delay(1000)  # Pausa antes de começar a fase de entrada do jogador

def countdown(screen):
    for i in range(4, 0, -1):
        screen.fill(WHITE)
        draw_text(screen, str(i), FONT, BLACK, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(1000)

def check_player_input(screen, rhythm):
    countdown(screen)
    
    index = 0
    correct_hits = 0
    total_notes = len(rhythm)
    start_time = time.time()
    time_offsets = [0] * total_notes  # Inicializa com zero para todas as notas

    bar_speed = 40 / 0.5  # Velocidade da barra (40 pixels em 0.5 segundos)
    bar_x = 180  # Posição inicial da barra
    bar_index = 0  # Índice da nota correspondente à barra

    while bar_index < total_notes:
        screen.fill(WHITE)
        draw_text(screen, "Reproduza o ritmo!", FONT, BLACK, 200, 100)
        x = 200
        for i in range(total_notes):
            color = GREEN if i < index else BLACK
            draw_text(screen, rhythm[i], FONT, color, x, 200)
            x += 40

        # Desenhar a barra que passa por cima das notas
        pygame.draw.rect(screen, RED, (bar_x, 180, 40, 60), 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if index < total_notes:  # Verificação de limite
                    current_time = time.time()
                    time_offsets[index] = current_time - start_time  # Calcula o tempo de resposta

                    note_position_time = index * 0.5  # Tempo em que a barra deve estar na posição da nota
                    margin_of_error = 0.25  # 250ms de margem de erro

                    if event.key == pygame.K_SPACE:
                        if rhythm[index] == "♪" and abs(time_offsets[index] - note_position_time) <= margin_of_error:
                            correct_hits += 1
                            draw_text(screen, "Acertou!", FONT, GREEN, 200, 400)
                        else:
                            draw_text(screen, "Errou!", FONT, RED, 200, 400)
                        tick_sound.play()
                        index += 1
                    elif event.key == pygame.K_TAB:
                        if rhythm[index] == "♫" and abs(time_offsets[index] - note_position_time) <= margin_of_error:
                            correct_hits += 1
                            draw_text(screen, "Acertou!", FONT, GREEN, 200, 400)
                        else:
                            draw_text(screen, "Errou!", FONT, RED, 200, 400)
                        tick_sound.play()
                        index += 1
                if event.key == pygame.K_9:
                    return False

        # Atualiza a posição da barra
        bar_x += bar_speed / FPS
        if bar_x >= 200 + (bar_index + 1) * 40:
            bar_index += 1
            bar_x = 180 + bar_index * 40

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    return correct_hits >= (total_notes * 0.7)  # O jogador deve acertar 70% das notas

# Inicialização da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Ritmo Musical")
clock = pygame.time.Clock()

# Função principal
def main():
    global game_state, current_level, unlocked_levels
    input_code = ""
    is_fullscreen = False
    level_input = ""
    level_start_time = 0

    while True:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                elif game_state == SETTINGS:
                    if event.key == pygame.K_RETURN:
                        check_admin_code(input_code)
                        input_code = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_code = input_code[:-1]
                    else:
                        input_code += event.unicode
                elif game_state == LEVEL_SELECT:
                    if event.key == pygame.K_BACKSPACE:
                        level_input = level_input[:-1]
                    elif event.unicode.isdigit():
                        level_input += event.unicode
                        level_start_time = time.time()

        if game_state == MENU:
            draw_text(screen, "Jogo de Ritmo Musical", FONT, BLACK, 200, 100)
            draw_text(screen, "1. Iniciar Jogo", FONT, BLACK, 200, 200)
            draw_text(screen, "2. Seleção de Nível", FONT, BLACK, 200, 300)
            draw_text(screen, "3. Configurações", FONT, BLACK, 200, 400)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                game_state = GAME
                current_level = 0
            elif keys[pygame.K_2]:
                game_state = LEVEL_SELECT
                level_input = ""
            elif keys[pygame.K_3]:
                game_state = SETTINGS

        elif game_state == LEVEL_SELECT:
            draw_text(screen, "Selecione um Nível (1-10)", FONT, BLACK, 200, 100)
            draw_text(screen, "Digite o número do nível:", FONT, BLACK, 200, 200)
            draw_text(screen, level_input, FONT, BLACK, 200, 300)
            draw_text(screen, "Pressione ESC para voltar", FONT, BLACK, 200, 400)

            # Mostrar os níveis disponíveis na esquerda da tela
            for i in range(LEVELS):
                color = GREEN if i < unlocked_levels else BLACK
                draw_text(screen, f"Nível {i+1}", FONT, color, 50, 100 + i * 40)

            if level_input.isdigit() and 1 <= int(level_input) <= unlocked_levels:
                if time.time() - level_start_time > 3:  # 3 segundos para digitar o número
                    current_level = int(level_input) - 1
                    game_state = GAME
            pygame.display.flip()

        elif game_state == SETTINGS:
            draw_text(screen, "Configurações", FONT, BLACK, 200, 100)
            draw_text(screen, "Digite o código de administrador:", FONT, BLACK, 200, 200)
            draw_text(screen, input_code, FONT, BLACK, 200, 300)
            draw_text(screen, "Pressione ESC para voltar", FONT, BLACK, 200, 400)

        elif game_state == GAME:
            rhythm = generate_rhythm(current_level)
            play_rhythm(screen, rhythm)
            if check_player_input(screen, rhythm):
                current_level += 1
                if current_level >= unlocked_levels and current_level < LEVELS:
                    unlocked_levels = current_level + 1
            game_state = MENU  # Voltar ao menu após tocar o ritmo

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
