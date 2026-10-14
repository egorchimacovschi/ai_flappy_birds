import pygame 

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, ground_border, flying, game_over):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.image_index = 0
        self.counter = 0
        self.velocity = 0
        self.ground_border  = ground_border
        self.clicked = False
        self.flying = flying
        self.game_over = game_over

        for num in range(1, 4):
            img  = pygame.image.load(
                f"./data/img/bird{num}.png"
            )

            self.images.append(img)

        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        if self.flying == True:
            #gravity
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < self.ground_border:
                self.rect.y += int(self.velocity)

        if self.game_over == False:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.velocity = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False


            #handling the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.image_index += 1
                if self.image_index >= len(self.images):
                    self.image_index = 0
            self.image = self.images[self.image_index]

            #ritate the bird
            self.image = pygame.transform.rotate(self.images[self.image_index], -2 * self.velocity)
        else:
            self.image = pygame.transform.rotate(self.images[self.image_index], -90)
bird_group = pygame.sprite.Group()