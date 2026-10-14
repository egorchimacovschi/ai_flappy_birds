import pygame

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, pipe_gap, scroll_speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./data/img/pipe.png')
        self.rect = self.image.get_rect()
        self.pipe_gap = pipe_gap
        self.scroll_speed = scroll_speed
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(self.pipe_gap / 2)]

        if position == -1:
            self.rect.topleft = [x, y + int(self.pipe_gap / 2)]

    def update(self):
        self.rect.x -= self.scroll_speed
        if self.rect.right < 0:
            self.kill()

pipe_group = pygame.sprite.Group()