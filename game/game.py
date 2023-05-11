import pygame
from game.paddle import Paddle
from game.ball import Ball
from game.blocks import Blocks


class GameInformation:
    def __init__(self, score, ball_hit, collision_occurred):
        self.score = score
        self.ball_hit = ball_hit
        self.collision_occurred = collision_occurred


class Game:
    def __init__(self, screen, screen_height, screen_width):
        self.screen = screen
        self.paddle = Paddle(self.screen, screen_width // 2 + 118, 500)
        self.ball = Ball(self.screen, screen_width // 2, 500)
        self.blocks = Blocks(self.screen)
        self.blocks_list = self.blocks.create_blocks()
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.score = 0
        self.ball_hit = 0

    def draw(self):
        self.paddle.draw()
        self.ball.draw()
        self.blocks.draw()
        self.display_score()

    def loop(self):
        collision_occurred = self.handle_collision()
        self.ball.move()
        self.reset_game()
        game_info = GameInformation(
            self.score, self.ball_hit, collision_occurred)
        return game_info

    def move_paddle(self, left_right):

        if left_right == 0:
            if self.paddle.x - self.paddle.x_speed >= 0:
                self.paddle.move(left_right)
            else:
                return False
        else:
            if (
                self.paddle.x + self.paddle.width + self.paddle.x_speed
                <= self.screen_width
            ):
                self.paddle.move(left_right)
            else:
                return False
        return True

    def handle_collision(self):
        # ball hitting screen sides
        if self.ball.x + self.ball.rect.width >= self.screen_width or self.ball.x <= 0:
            self.ball.x_speed *= -1

        # ball hitting screen ceiling
        if self.ball.y <= 0:
            self.ball.y_speed *= -1

        # ball/paddle collision
        if (
            self.ball.rect.colliderect(self.paddle.rect)
            and self.ball.y_speed > 0
            and self.ball.rect.centery < self.paddle.rect.bottom
        ):
            if (
                self.ball.rect.left - self.ball.x_speed >= self.paddle.rect.right
                or self.ball.rect.right - self.ball.x_speed <= self.paddle.rect.left
            ):
                self.ball.x_speed *= -1.1
                self.ball.y_speed *= -1

            elif self.ball.rect.bottom >= self.paddle.rect.top:
                self.ball.y_speed *= -1

            self.ball_hit += 1

        # block collision
        collision_occurred = False
        for row in self.blocks_list:
            for block in row:
                if self.ball.rect.colliderect(block[1]):
                    row.remove(block)
                    self.score += 10

                    # Calculate the overlap between the ball and the block
                    dx = min(
                        block[1].right - self.ball.rect.left,
                        self.ball.rect.right - block[1].left,
                    )
                    dy = min(
                        block[1].bottom - self.ball.rect.top,
                        self.ball.rect.bottom - block[1].top,
                    )

                    # Determine if the collision is horizontal or vertical, and update the ball speed accordingly
                    if dx < dy:
                        self.ball.x_speed *= -1.1
                    else:
                        self.ball.y_speed *= -1

                    collision_occurred = True
                    break
            if collision_occurred:
                return True
        return False

    def display_score(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (600, 50))

    def display_result(self, text):
        font = pygame.font.Font(None, 72)
        text = font.render(f"{text}", True, (255, 255, 255))
        self.screen.blit(
            text,
            (
                self.screen_width // 2 - text.get_width() // 2,
                self.screen_height // 2 - text.get_height() // 2,
            ),
        )
        pygame.display.flip()
        pygame.time.wait(1500)

    def reset_game(self, training=False):
        if (
            self.ball.y + self.ball.height // 2 >= self.screen_height +
                self.ball.height or self.score == 550
            or training
        ):

            if self.score == 550:
                self.display_result('You won!!')
            elif training == False:
                self.display_result('You lost')

            self.paddle.reset(self.screen_width // 2 + 118, 500)  # 48
            self.ball.reset(self.screen_width // 2, 470)
            self.blocks_list = self.blocks.reset()
            self.score = 0
            self.ball_hit = 0
