import pygame
import neat
import os
import time
import pickle
from game.game import Game

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 0)
BLOCKS_ROWS = 4
FPS = 60


class Ark:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.image = pygame.image.load("images/background.jpg")
        self.game = Game(
            self.screen,
            SCREEN_HEIGHT,
            SCREEN_WIDTH,
        )
        self.ball = self.game.ball
        self.paddle = self.game.paddle

    def main(self):
        """
        Play game 
        """

        pygame.display.set_caption("Arkanoid")
        clock = pygame.time.Clock()

        running = True

        while running:
            clock.tick(FPS)
            self.screen.blit(self.image, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            self.game.draw()
            self.game.loop()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.game.move_paddle(0)
            if keys[pygame.K_RIGHT]:
                self.game.move_paddle(1)

            pygame.display.update()

    def test_ai(self, net):
        """
        Test the AI to make sure
        """

        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)
            self.screen.blit(self.image, (0, 0))
            self.game.draw()
            self.game.loop()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            paddle_x_normalized = self.paddle.x / SCREEN_WIDTH
            ball_x_normalized = self.ball.x / SCREEN_WIDTH
            ball_y_normalized = self.ball.y / SCREEN_HEIGHT
            distance_x_ball_paddle = abs(
                paddle_x_normalized - ball_x_normalized)

            output = net.activate(
                (
                    paddle_x_normalized,
                    ball_x_normalized,
                    ball_y_normalized,
                    distance_x_ball_paddle,
                )
            )
            decision = output.index(max(output))

            if decision == 0:  # AI doesn't move
                pass
            elif decision == 1:  # AI moves left
                self.game.move_paddle(0)
            elif decision == 2:  # AI moves right
                self.game.move_paddle(1)

            pygame.display.update()

    def train_ai(
        self,
        genome,
        config,
    ):
        """
        Train AI
        """

        running = True
        last_score_time = time.time()
        clock = pygame.time.Clock()

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome
        self.game.reset_game()

        while running:
            # clock.tick(60)
            # self.screen.blit(self.image, (0, 0))
            # self.game.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

            game_info = self.game.loop()
            if game_info.collision_occurred:
                last_score_time = time.time()

            self.move_ai_paddle(net)

            pygame.display.update()

            time_since_last_score = time.time() - last_score_time

            if (
                self.ball.y >= SCREEN_HEIGHT
                or time_since_last_score > 10
                or game_info.score == 550
            ):
                self.calculate_fitness(game_info.score, game_info.ball_hit)
                self.game.reset_game(True)
                break

        return False

    def move_ai_paddle(self, net):
        paddle_x_normalized = self.paddle.x / SCREEN_WIDTH
        ball_x_normalized = self.ball.x / SCREEN_WIDTH
        ball_y_normalized = self.ball.y / SCREEN_HEIGHT
        distance_x_ball_paddle = abs(paddle_x_normalized - ball_x_normalized)

        output = net.activate(
            (
                paddle_x_normalized,
                ball_x_normalized,
                ball_y_normalized,
                distance_x_ball_paddle,
            )
        )
        decision = output.index(max(output))

        valid = True

        if decision == 0:  # do nothing
            self.genome.fitness -= 0.1
        elif decision == 1:  # move left
            valid = self.game.move_paddle(0)
        else:  # move right
            valid = self.game.move_paddle(1)

        if not valid:  # tries to move outside screen borders
            self.genome.fitness -= 1

    def calculate_fitness(self, score, ball_hit):

        self.genome.fitness += ball_hit / 20
        self.genome.fitness += score / 20

        if score <= 30:
            self.genome.fitness -= 2

        if score > 400:
            self.genome.fitness += 20

        if score == 550:
            self.genome.fitness += 40


def eval_genomes(genomes, config):
    """
    Run each genome until one reaches the fitness treshold or the number of epoch
    """

    pygame.display.set_caption("Ark")
    ark = Ark()

    for _, genome in genomes:
        genome.fitness = 0 if genome.fitness == None else genome.fitness

        force_quit = ark.train_ai(genome, config)
        if force_quit:
            quit()


def run_neat(config):
    # p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-124")
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))

    winner = p.run(eval_genomes, 1000)

    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


def test_best_network(config):
    with open("best.pickle-2", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    pygame.display.set_caption("Arkanoid")
    ark = Ark()
    ark.test_ai(winner_net)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )
    #Ark().main()
    #run_neat(config)
    test_best_network(config)
