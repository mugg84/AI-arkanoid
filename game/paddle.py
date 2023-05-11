import pygame


pygame.init()


class Paddle:
    def __init__(self, screen, x, y):
        self.x = x
        self.y = y
        self.surf, self.rect = self.create_paddle()
        self.width = self.rect.width
        self.height = self.rect.height
        self.screen = screen
        self.x_speed = 8

    def move(self, left_right):
        if left_right == 0:
            self.x -= self.x_speed
            self.rect.x = self.x

        elif left_right == 1:
            self.x += self.x_speed
            self.rect.x = self.x

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def create_paddle(self):
        image = pygame.image.load("images/paddleBlu.png")
        width, height = image.get_width(), image.get_height()
        image_rect = pygame.Rect(self.x, self.y, width, height)
        return (image, image_rect)

    def draw(self):
        self.screen.blit(self.surf, self.rect)
