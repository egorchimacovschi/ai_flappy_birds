import pygame
import sys
import random
import scripts.bird as entity
import scripts.pipe as pipe
import scripts.button as button
from scripts.pipe import pipe_group
from scripts.bird import bird_group




class Game:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        self.display_size = pygame.display.Info()

        self.monitor_width = 864
        self.monitor_height = 936

        self.screen_width = int(self.monitor_width * 0.8)
        self.screen_height = int(self.monitor_height * 0.8)


        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.SCALED
        )
        pygame.display.set_caption("My Flappy Birds")

        self.font = pygame.font.SysFont('Bauhaus 93', 60)
        self.color = (255, 255, 255)

        self.ground_scroll = 0
        self.scroll_speed = 4
        self.flying = False
        self.game_over = False
        self.pipe_gap = 150
        self.pipe_frequency = 1500 #milliseconds
        self.last_pipe = pygame.time.get_ticks() - self.pipe_frequency
        self.pipe_stop = False
        self.score = 0
        self.pass_pipe = False

        self.background_img = pygame.image.load(
            "./data/img/bg.png"
        ).convert()
        self.background_img = pygame.transform.scale(self.background_img, (self.screen_width, self.screen_height))
        self.ground_img = pygame.image.load(
            "./data/img/ground.png"
        )
        self.button_img = pygame.image.load(
            "./data/img/restart.png"
        )

        self.ground_img = pygame.transform.scale(self.ground_img, (self.screen_width + self.screen_width * 0.04, self.screen_height * 0.1))

        self.flappy  = entity.Bird(100, self.screen_height // 2, self.screen_height * 0.91, self.flying, self.game_over)
        bird_group.add(self.flappy)

        self.button = button.Button(self.screen_width // 2 - 50, self.screen_height // 2 -100, self.button_img)

    def reset_game(self):
        pipe_group.empty()

        # put the bird back in the middle, same as in __init__
        self.flappy.rect.center = [100, self.screen_height // 2]
        self.flappy.velocity = 0
        self.flappy.flying = False
        self.flappy.game_over = False

        # reset the game's own state
        self.flying = False
        self.game_over = False
        self.pipe_stop = False
        self.pass_pipe = False
        self.score = 0
        self.last_pipe = pygame.time.get_ticks() - self.pipe_frequency

    def draw_text(self, text, font, text_color, x, y):
        img = font.render(text, True, text_color)
        self.screen.blit(img, (x, y))

    def draw(self, button):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if the mouse is over the button
        if button.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        self.screen.blit(button.image, (button.rect.x, button.rect.y))

        return action
   
    def run(self):
        while self.running:

            #draw the background
            self.screen.blit(self.background_img, (0, 0))


            bird_group.draw(self.screen)
            bird_group.update()

            pipe_group.draw(self.screen)
            if self.pipe_stop == False:
                pipe_group.update()

            #draw and ground
            self.screen.blit(self.ground_img, (self.ground_scroll, self.screen_height * 0.92))

            #check the score
            if len(pipe_group) > 0:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                    and self.pass_pipe == False:
                    self.pass_pipe = True
                if self.pass_pipe == True:
                    if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                        self.score += 1
                        self.pass_pipe = False


            self.draw_text(str(self.score), self.font, self.color, int(self.screen_width / 2), 20)

            #look for collision
            #look for collision
            if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or self.flappy.rect.top < 0:
                self.game_over = True
                self.flappy.game_over = True
                self.pipe_stop = True

            
            #check if the birds hits the ground
            if self.flappy.rect.bottom >= self.flappy.ground_border:
                self.game_over = True
                self.flappy.game_over = True
                self.flying = self.flappy.flying = False

            if self.game_over == False and self.flying == True:
                #generate new pipes
                time_now = pygame.time.get_ticks()
                if time_now - self.last_pipe > self.pipe_frequency:
                    pipe_height = random.randint(-100, 100)
                    self.bottom_pipe = pipe.Pipe(self.screen_width, int(self.screen_height // 2) + pipe_height, -1, self.pipe_gap, self.scroll_speed)
                    self.top_pipe = pipe.Pipe(self.screen_width, int(self.screen_height // 2) + pipe_height, 1, self.pipe_gap, self.scroll_speed)
                    pipe_group.add(self.bottom_pipe)
                    pipe_group.add(self.top_pipe)
                    self.last_pipe = time_now
        
                #draw and scroll the ground
                self.ground_scroll -= self.scroll_speed
                if abs(self.ground_scroll) > self.screen_width * 0.04:
                    self.ground_scroll = 0


            #check for the game over and reset
            if self.game_over == True:
                if self.draw(self.button) == True:
                    self.reset_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.type == pygame.MOUSEBUTTONDOWN and self.flying == False and self.game_over == False:
                    self.flying = True
                    self.flappy.flying = True


            pygame.display.flip()
            self.clock.tick(self.fps)


Game().run()