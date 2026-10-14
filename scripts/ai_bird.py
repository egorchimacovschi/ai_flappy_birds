import pygame
from scripts.bird import Bird

class AIBird(Bird):
    def __init__(self, x, y, ground_border, genome, net):
        super().__init__(x, y, ground_border, flying=True, game_over=False)
        self.genome = genome #NEAT genome
        self.net = net #neural network
        self.fitness = 0.0
        self.output = 0.0

    
    def jump(self):
        self.velocity = -10

    def update(self):
        self.velocity += 0.5
        if self.velocity > 8:
            self.velocity = 8
        if self.rect.bottom < self.ground_border:
            self.rect.y += int(self.velocity)

        self.counter += 1
        flap_cooldown = 5

        if self.counter > flap_cooldown:
            self.counter = 0
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
        self.image = pygame.transform.rotate(self.images[self.image_index], - 2 * self.velocity)
    