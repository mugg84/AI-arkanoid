import pygame

pygame.init()


class Blocks:
    block_colour_list = [
        "blue",
        "red",
        "green",
        "yellow",
        "grey",
        "purple",
    ]
    blocks = []

    def __init__(self, screen):
        self.screen = screen
        self.rows = 5
        self.colums = 11

    def draw(self):
        for row in self.blocks:
            for block in row:
                self.screen.blit(block[0], block[1])

    def create_blocks(self):
        for row in range(self.rows):
            row_blocks = []  # Create a new list for the blocks in the current row
            for column in range(self.colums):
                image = pygame.image.load(
                    f"images/element_{self.block_colour_list[row]}_rectangle.png"
                )
                width, height = image.get_width(), image.get_height()
                image_rect = pygame.Rect(
                    8 + (width * column) + (8 * column),
                    8 + (height * row) + (8 * row),
                    width,
                    height,
                )
                row_blocks.append(
                    [image, image_rect]
                )  # Append the block to the current row list
            self.blocks.append(
                row_blocks
            )  # Append the current row list to the blocks list
        return self.blocks

    def reset(self):
        self.blocks = []
        return self.create_blocks()
