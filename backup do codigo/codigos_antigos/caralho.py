import pygame
import random
import time

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Jogo de Ritmo Musical')

tick_sound = pygame.mixer.Sound('tick.wav')

font = pygame.font.Font(None, 74)

def display_text(text, x, y):
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (x, y))

def generate_rhythm(level):
    rhythm = []
    for _ in range(level * 2):
        if random.choice([True, False]):
            rhythm.append('♪')
        else:
            rhythm.append('♫')
    return rhythm

def play_game():
    level = 1
    while level <= 10:
        rhythm = generate_rhythm(level)
        correct_hits = 0

        for note in rhythm:
            screen.fill((0, 0, 0))
            display_text(note, screen_width // 2 - 20, screen_height // 2 - 20)
            pygame.display.flip()
            
            tick_sound.play()
            time.sleep(0.5 if note == '♪' else 1.0)  # ♪ = 0.5s, ♫ = 1.0s
            
            hit = False
            start_time = time.time()
            while time.time() - start_time < 1.0:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            correct_hits += 1
                            hit = True
                            break
                        elif event.key == pygame.K_ESCAPE:
                            return
                if hit:
                    break

        if correct_hits >= 3:
            level += 1
        else:
            screen.fill((0, 0, 0))
            display_text("Errou! Aperte Espaço para tentar novamente", 50, screen_height // 2 - 20)
            pygame.display.flip()
            waiting_for_retry = True
            while waiting_for_retry:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting_for_retry = False
                        elif event.key == pygame.K_ESCAPE:
                            return

def show_start_screen():
    screen.fill((0, 0, 0))
    display_text("Jogo de Ritmo Musical", 100, screen_height // 2 - 100)
    display_text("Pressione Espaço para começar", 100, screen_height // 2)
    pygame.display.flip()

    waiting_for_start = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting_for_start = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

while True:
    show_start_screen()
    play_game()
    screen.fill((0, 0, 0))
    display_text("Parabéns! Você venceu!", 100, screen_height // 2 - 20)
    display_text("Pressione Esc para sair", 100, screen_height // 2 + 50)
    pygame.display.flip()
    
    waiting_for_exit = True
    while waiting_for_exit:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting_for_exit = False

    pygame.quit()
    quit()
