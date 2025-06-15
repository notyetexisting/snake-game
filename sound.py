import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.eat_sound = pygame.mixer.Sound("assets/sounds/eat.wav")
        self.gameover_sound = pygame.mixer.Sound("assets/sounds/gameover.wav")
        self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")

    def play_eat_sound(self):
        self.eat_sound.play()

    def play_gameover_sound(self):
        self.gameover_sound.play()

    def play_move_sound(self):
        self.move_sound.play()