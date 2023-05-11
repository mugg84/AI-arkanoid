import pygame
import random

pygame.init()


class Ball:
    def __init__(self, screen, x, y):
        self.x = x
        self.y = y
        self.surf, self.rect = self.create_ball()
        self.screen = screen
        self.x_speed = [-4, -3, -2, -1, 1, 2, 3, 4][random.randrange(0, 7)]
        self.y_speed = -5
        self.height = self.rect.height
        self.width = self.rect.width

    def move(self):
        self.x += self.x_speed
        self.y += self.y_speed
        self.rect.x = self.x
        self.rect.y = self.y

    def reset(self, x, y):
        self.x = self.rect.x = x
        self.y = self.rect.y = y
        self.x_speed = [-4, -3, -2, -1, 1, 2, 3, 4][random.randrange(0, 7)]
        self.y_speed = -5

    def create_ball(self):
        image = pygame.image.load("images/ballBlue.png")
        width, height = image.get_width(), image.get_height()
        image_rect = pygame.Rect(self.x, self.y, width, height)
        return (image, image_rect)

    def draw(self):
        self.screen.blit(self.surf, self.rect)
