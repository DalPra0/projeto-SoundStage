import pygame
import sys
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
LEVELS = 10
ADMIN_CODE = "123456"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

FONT = pygame.font.SysFont("arial", 32)

pygame.mixer.init()
tick_sound = pygame.mixer.Sound("tick.wav")
metronome_tick = pygame.mixer.Sound("high_tick.wav")

MENU, GAME, LEVEL_SELECT, SETTINGS = range(4)
game_state = MENU

current_level = 0
unlocked_levels = 1
admin_unlocked = False

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
    for _ in range(level + 3):
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
            pygame.time.delay(500)
        elif note == "♫":
            draw_text(screen, note, FONT, BLACK, x, 200)
            tick_sound.play()
            pygame.display.flip()
            pygame.time.delay(250)
            tick_sound.play()
            pygame.time.delay(250)
        x += 40
    pygame.time.delay(1000)

def check_player_input(screen, rhythm):
    index = 0
    correct_hits = 0
    total_notes = len(rhythm)
    time_offsets = [0] * total_notes 

    # Esperar o jogador iniciar
    player_started = False
    start_time = None

    while index < total_notes:
        screen.fill(WHITE)
        draw_text(screen, "Reproduza o ritmo!", FONT, BLACK, 200, 100)
        x = 200
        for i in range(total_notes):
            color = GREEN if i < index else BLACK
            draw_text(screen, rhythm[i], FONT, color, x, 200)
            x += 40

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not player_started:
                    start_time = time.time()
                    player_started = True

                if index < total_notes and player_started:
                    current_time = time.time()
                    time_offsets[index] = current_time - start_time

                    note_position_time = index * 0.5
                    margin_of_error = 0.25

                    if event.key == pygame.K_SPACE:
                        if rhythm[index] == "♪" and abs(time_offsets[index] - note_position_time) <= margin_of_error:
                            correct_hits += 1
                            draw_text(screen, "Acertou!", FONT, GREEN, 200, 400)
                            if index + 1 < total_notes and rhythm[index + 1] == "♪":
                                index += 1
                        else:
                            draw_text(screen, "Errou!", FONT, RED, 200, 400)
                        tick_sound.play()
                        index += 1
                    elif event.key == pygame.K_TAB:
                        if rhythm[index] == "♫" and abs(time_offsets[index] - note_position_time) <= margin_of_error:
                            correct_hits += 1
                            draw_text(screen, "Acertou!", FONT, GREEN, 200, 400)
                            if index + 1 < total_notes and rhythm[index + 1] == "♫":
                                index += 1
                        else:
                            draw_text(screen, "Errou!", FONT, RED, 200, 400)
                        tick_sound.play()
                        index += 1
                if event.key == pygame.K_9:
                    return False

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    return correct_hits >= (total_notes * 0.7)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Ritmo Musical")
clock = pygame.time.Clock()

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

            for i in range(LEVELS):
                color = GREEN if i < unlocked_levels else BLACK
                draw_text(screen, f"Nível {i+1}", FONT, color, 50, 100 + i * 40)

            if level_input.isdigit() and 1 <= int(level_input) <= unlocked_levels:
                if time.time() - level_start_time > 3:
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
            game_state = MENU

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
