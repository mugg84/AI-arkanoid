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
        # Set up game screen and load assets
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.image = pygame.image.load("images/background.jpg")
        self.game = Game(
            self.screen,
            SCREEN_HEIGHT,
            SCREEN_WIDTH,
        )
        self.ball = self.game.ball
        self.paddle = self.game.paddle
        pygame.mixer.init()
        pygame.mixer.music.load("./sounds/S31-Night Prowler.ogg")

    def main(self):
        """
        Start and manage the main game loop for a single player game.
        """

        # Initialize game display and start music
        pygame.display.set_caption("Arkanoid")
        pygame.mixer.music.play(-1)
        clock = pygame.time.Clock()

        # Main game loop
        running = True

        while running:
            clock.tick(FPS)
            self.screen.blit(self.image, (0, 0))

            # Event handling loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    running = False
                    break

            # Update game state and display
            self.game.draw()
            self.game.loop()

            # Key press handling for player input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.game.move_paddle(0)
            if keys[pygame.K_RIGHT]:
                self.game.move_paddle(1)

            pygame.display.update()

    def test_ai(self, net):
        """
        Test the trained AI in the game.
        """

        # Game loop for AI
        clock = pygame.time.Clock()
        pygame.mixer.music.play(-1)
        running = True

        while running:
            clock.tick(60)
            self.screen.blit(self.image, (0, 0))
            self.game.draw()
            self.game.loop()

            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    running = False
                    break

            # AI decision making based on the current game state
            paddle_x_normalized = self.paddle.x / SCREEN_WIDTH
            ball_x_normalized = self.ball.x / SCREEN_WIDTH
            ball_y_normalized = self.ball.y / SCREEN_HEIGHT
            distance_x_ball_paddle = abs(paddle_x_normalized - ball_x_normalized)

            # Determine the AI's move based on the network's output
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
            elif decision == 1:  # AI moves paddle to the left
                self.game.move_paddle(0)
            elif decision == 2:  # AI moves paddle to the right
                self.game.move_paddle(1)

            pygame.display.update()

    def train_ai(self, genome, config):
        """
        Train the AI using NEAT.
        """

        # Game loop for AI training
        running = True
        last_score_time = time.time()
        clock = pygame.time.Clock()

        # Create a feed-forward neural network for the current genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome

        while running:
            # for real-time visualization, comment it out
            # clock.tick(60)

            # comment these two lines to increase training speed
            self.screen.blit(self.image, (0, 0))
            self.game.draw()

            # Event handling loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

            # Update game state and record last scoring time if a collision occurred
            game_info = self.game.loop(True)

            if game_info.collision_occurred:
                last_score_time = time.time()

            # Decide AI move based on current game state
            self.move_ai_paddle(net)

            pygame.display.update()

            # Calculate time since last score
            time_since_last_score = time.time() - last_score_time

            # Terminate current session if no score in 10 seconds
            if time_since_last_score > 10:
                self.calculate_fitness(game_info.score, game_info.ball_hit)
                self.game.reset_game()
                break
            if (
                self.ball.y + self.ball.height // 2 >= SCREEN_HEIGHT + self.ball.height
                or game_info.score == 550
            ):
                # Calculate and record fitness of the genome
                self.calculate_fitness(game_info.score, game_info.ball_hit)
                break
        return False

    def move_ai_paddle(self, net):
        # Normalize game state data for the AI's decision-making process
        paddle_x_normalized = self.paddle.x / SCREEN_WIDTH
        ball_x_normalized = self.ball.x / SCREEN_WIDTH
        ball_y_normalized = self.ball.y / SCREEN_HEIGHT
        distance_x_ball_paddle = abs(paddle_x_normalized - ball_x_normalized)

        # Determine the AI's move based on the network's output
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

        if decision == 0:  # AI does nothing
            pass
        elif decision == 1:  # AI moves paddle to the left
            valid = self.game.move_paddle(0)
        else:  # AI moves paddle to the right
            valid = self.game.move_paddle(1)

        # Penalize the genome if the AI tries to move outside the screen borders
        if not valid:
            self.genome.fitness -= 1

    def calculate_fitness(self, score, ball_hit):
        # Reward the genome for hitting the ball and achieving high scores
        # Penalize low scoring genomes and highly reward high scoring genomes
        if score <= 30:
            self.genome.fitness += ball_hit / 20
            self.genome.fitness += score / 20
        else:
            self.genome.fitness += ball_hit / 10
            self.genome.fitness += score / 10

        # Adjust for possible random points at the beginnig of the game
        self.genome.fitness -= 1

        if score > 150:
            self.genome.fitness += 20
        if score > 400:
            self.genome.fitness += 40
        if score == 550:
            self.genome.fitness += 60

        self.game.reset_game()


# Run each genome through the game until the fitness threshold is reached or the epoch limit is hit
def eval_genomes(genomes, config):
    pygame.display.set_caption("Ark")

    for _, genome in genomes:
        genome.fitness = 0 if genome.fitness is None else genome.fitness

        force_quit = ark.train_ai(genome, config)
        if force_quit:
            quit()


# Create and initialize a NEAT population and run the genetic algorithm
def run_neat(config):
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))

    # Run the algorithm for up to 1000 generations and save the best genome
    winner = p.run(eval_genomes)

    with open("best.pickle", "wb") as f:
        # Save the best genome for future use
        pickle.dump(winner, f)


def test_best_network(config):
    # Load the best genome and create a network from it
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    # Display the game window
    pygame.display.set_caption("Arkanoid")

    # Test the AI network
    ark.test_ai(winner_net)


if __name__ == "__main__":
    # Determine path to configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    # Load the configuration
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )
    ark = Ark()

    # Uncomment the following lines to run the game, train the AI, or test the AI respectively:
    # run game as player
    # ark.main()

    # train the AI
    run_neat(config)

    # test the AI
    # test_best_network(config)
