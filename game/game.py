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
        self.paddle = Paddle(self.screen, screen_width // 2 + 48, 500)
        self.ball = Ball(self.screen, screen_width // 2, 500)
        self.blocks = Blocks(self.screen)
        self.blocks_list = self.blocks.create_blocks()
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.score = 0
        self.ball_hit = 0
        self.training_AI = False
        pygame.mixer.init()
        self.bounce_sound = pygame.mixer.Sound(
            "./sounds/mixkit-small-hit-in-a-game-2072.wav"
        )

    def draw(self):
        self.paddle.draw()
        self.ball.draw()
        self.blocks.draw()
        self.display_score()

    def loop(self, training=False):
        self.reset_game()
        self.training_AI = training
        self.ball.move()
        collision_occurred = self.handle_collision()
        game_info = GameInformation(self.score, self.ball_hit, collision_occurred)
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
        if (
            self.ball.x + self.ball.rect.width >= self.screen_width
            or self.ball.x + self.ball.x_speed <= 0
        ):
            self.ball.x_speed *= -1
            if not self.training_AI:
                self.bounce_sound.play()

        # ball hitting screen ceiling
        if self.ball.y <= 0:
            self.ball.y_speed *= -1
            if not self.training_AI:
                self.bounce_sound.play()

        # ball/paddle collision

        if (
            self.ball.rect.colliderect(self.paddle.rect)
            and self.ball.y_speed > 0
            and self.ball.rect.centery < self.paddle.rect.bottom
        ):
            paddle_hit_position = (
                self.ball.rect.centerx - self.paddle.rect.left
            ) / self.paddle.width

            if (
                self.ball.rect.left - self.ball.x_speed >= self.paddle.rect.right
                or self.ball.rect.right - self.ball.x_speed <= self.paddle.rect.left
            ):
                self.ball.x_speed *= -1.1
                self.ball.y_speed *= -1
            elif self.ball.rect.bottom >= self.paddle.rect.top:
                self.ball.y_speed *= -1

            # check if the ball hit the sides of the paddle (0.25 and 0.75 are somewhat arbitrary, adjust as needed)
            if paddle_hit_position < 0.25 or paddle_hit_position > 0.75:
                self.ball.x_speed *= 1.1  # increase the ball speed by 10%

            # ensure the ball speed doesn't get too high
            self.ball.x_speed = min(
                max(self.ball.x_speed, -10), 10
            )  # limit the speed between -10 and 10

            self.ball_hit += 1
            if not self.training_AI:
                self.bounce_sound.play()

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
                    if dx <= dy:
                        self.ball.x_speed *= -1
                    else:
                        self.ball.y_speed *= -1

                    collision_occurred = True
                    if not self.training_AI:
                        self.bounce_sound.play()
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
        pygame.time.wait(2000)

    def reset_game(self):
        if (
            self.ball.y + self.ball.height // 2 >= self.screen_height + self.ball.height
            or self.score == 550
        ):
            if not self.training_AI:
                if self.score == 550:
                    self.display_result("You won!!")
                else:
                    self.display_result("You lost")

            self.paddle.reset(self.screen_width // 2 + 48, 500)
            self.ball.reset(self.screen_width // 2, 470)
            self.blocks_list = self.blocks.reset()
            self.score = 0
            self.ball_hit = 0
