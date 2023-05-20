import pygame
import math
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
        collision_occurred = self.handle_collision()
        self.ball.move()
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

            # Convert hit position to a range between -1 and 1
            relative_intersect = (paddle_hit_position - 0.5) * 2

            # Define maximum bounce angle (here we use 60 degrees, but it can be adjusted as needed)
            max_bounce_angle = math.radians(60)

            # Calculate new direction (this will be between -max_bounce_angle and max_bounce_angle)
            angle = relative_intersect * max_bounce_angle

            # Update ball speeds based on this angle and the ball's overall speed
            old_speed = math.sqrt(self.ball.x_speed**2 + self.ball.y_speed**2)
            self.ball.x_speed = old_speed * math.sin(angle)
            self.ball.y_speed = -old_speed * math.cos(angle)

            # Normalize the ball's speed (remove accumulated floating point errors)
            magnitude = math.sqrt(self.ball.x_speed**2 + self.ball.y_speed**2)
            self.ball.x_speed = (self.ball.x_speed / magnitude) * old_speed
            self.ball.y_speed = (self.ball.y_speed / magnitude) * old_speed

            # Move the ball's position after the speed has been updated
            self.ball.rect.bottom = self.paddle.rect.top

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
                    # print(self.score)

                    # Check which side of the block the ball hit
                    ball_center = self.ball.rect.center
                    block_center = block[1].center

                    # Determine if the collision was more horizontal or vertical
                    dx = (
                        abs(ball_center[0] - block_center[0])
                        - (block[1].width + self.ball.rect.width) / 2
                    )
                    dy = (
                        abs(ball_center[1] - block_center[1])
                        - (block[1].height + self.ball.rect.height) / 2
                    )

                    if dx > dy:
                        # Horizontal collision, flip x speed
                        self.ball.x_speed *= -1
                    else:
                        # Vertical collision, flip y speed
                        self.ball.y_speed *= -1

                    collision_occurred = True
                    if not self.training_AI:
                        self.bounce_sound.play()

        return collision_occurred

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
