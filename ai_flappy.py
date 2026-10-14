import os
import pickle
import random
import sys

import neat
import pygame

from scripts.pipe import Pipe
from scripts.ai_bird import AIBird
from scripts.neat_view import NetworkView, draw_chart, BG, LINE, TEXT, DIM, HIGH

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config-feedforward.txt")
BEST_PATH = "best_genome.pkl"      
MAX_GENERATIONS = 100             
SCORE_LIMIT = 50                   
SPEEDS = (1, 5, 20)               
PANEL_WIDTH = 440                  
INPUT_LABELS = ("height", "speed", "pipe dx", "gap dy")


class Solved(Exception):
    """Raised when a bird reaches SCORE_LIMIT, to stop training."""


class AIGame:
    def __init__(self, population=None):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.monitor_width = 864
        self.monitor_height = 936
        self.screen_width = int(self.monitor_width * 0.8)
        self.screen_height = int(self.monitor_height * 0.8)
        self.panel_width = PANEL_WIDTH

        self.screen = pygame.display.set_mode(
            (self.screen_width + self.panel_width, self.screen_height), pygame.SCALED
        )
        self.game_surface = pygame.Surface((self.screen_width, self.screen_height))
        pygame.display.set_caption("My Flappy Birds - NEAT AI")

        self.font = pygame.font.SysFont('Bauhaus 93', 60)
        self.color = (255, 255, 255)
        self.title_font = pygame.font.Font(None, 30)
        self.panel_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        self.ground_scroll = 0
        self.scroll_speed = 4
        self.pipe_gap = 150
        self.pipe_frequency = 1500  
        self.pipe_frames = int(self.pipe_frequency / 1000 * self.fps)
        self.score = 0

        self.background_img = pygame.image.load("./data/img/bg.png").convert()
        self.background_img = pygame.transform.scale(self.background_img, (self.screen_width, self.screen_height))
        self.ground_img = pygame.image.load("./data/img/ground.png")
        self.ground_img = pygame.transform.scale(
            self.ground_img, (int(self.screen_width + self.screen_width * 0.04), int(self.screen_height * 0.1))
        )
        self.ground_border = self.screen_height * 0.91

        self.population = population
        self.config = None
        self.mode = "train"
        self.generation = 0
        self.speed_index = 0
        self.history = []
        self.best_fitness = 0.0
        self.best_score = 0
        self.best_genome = None
        self.birds = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.pairs = []
        self.next_pair = None
        self.followed = None

        px = self.screen_width
        self.view = NetworkView((px + 12, 44, self.panel_width - 24, 330), INPUT_LABELS)
        self.gauge_rect = (px + 100, 392, self.panel_width - 200, 20)

    def start_round(self, genomes, config):
        self.config = config
        self.pipes = pygame.sprite.Group()
        self.birds = pygame.sprite.Group()
        self.all_birds = []
        self.pairs = []
        self.next_pair = None
        self.followed = None
        self.score = 0
        self.ground_scroll = 0
        self.pipe_timer = self.pipe_frames
        self.total = len(genomes)

        for genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            bird = AIBird(100, self.screen_height // 2, self.ground_border, genome, net)
            self.birds.add(bird)
            self.all_birds.append(bird)

    def get_inputs(self, bird):
        """What the bird 'sees' - every value is scaled to roughly -1 ... 1."""
        if self.next_pair is None:
            dx, gap_dy = 1.0, 0.0
        else:
            bottom_pipe, top_pipe, _ = self.next_pair
            gap_center = (top_pipe.rect.bottom + bottom_pipe.rect.top) / 2
            gap_dy = (gap_center - bird.rect.centery) / (self.screen_height / 2)
            dx = (bottom_pipe.rect.right - bird.rect.left) / self.screen_width
        return [bird.rect.centery / self.screen_height, bird.velocity / 10, dx,gap_dy, ]

    def step(self):
        self.pipe_timer += 1
        if self.pipe_timer > self.pipe_frames:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(self.screen_width, int(self.screen_height // 2) + pipe_height, -1, self.pipe_gap, self.scroll_speed)
            top_pipe = Pipe(self.screen_width, int(self.screen_height // 2) + pipe_height, 1, self.pipe_gap, self.scroll_speed)
            self.pipes.add(bottom_pipe)
            self.pipes.add(top_pipe)
            self.pairs.append([bottom_pipe, top_pipe, False])
            self.pipe_timer = 0

        # scroll the ground
        self.ground_scroll -= self.scroll_speed
        if abs(self.ground_scroll) > self.screen_width * 0.04:
            self.ground_scroll = 0

        # the next pipe = the first one the birds have not passed yet 
        self.pairs = [p for p in self.pairs if p[0].alive()]
        bird_left = self.birds.sprites()[0].rect.left
        self.next_pair = next((p for p in self.pairs if p[0].rect.right >= bird_left), None)

        # every bird looks, thinks, and maybe flaps
        for bird in self.birds.sprites():
            bird.output = bird.net.activate(self.get_inputs(bird))[0]
            if bird.output > 0.5:
                bird.jump()
            bird.fitness += 0.1

        self.birds.update()
        self.pipes.update()

        # reward for passing a pipe 
        for pair in self.pairs:
            if not pair[2] and bird_left > pair[0].rect.right:
                pair[2] = True
                self.score += 1
                for bird in self.birds:
                    bird.fitness += 5

        for bird in self.birds.sprites():
            if (pygame.sprite.spritecollideany(bird, self.pipes)
                    or bird.rect.top < 0
                    or bird.rect.bottom >= bird.ground_border):
                bird.kill()

    def run_round(self, score_limit=None):
        """Returns True if the score limit was reached, False if all birds died."""
        while len(self.birds) > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    if event.key == pygame.K_SPACE:
                        self.speed_index = (self.speed_index + 1) % len(SPEEDS)
                    if event.key == pygame.K_n:
                        for bird in self.birds.sprites():
                            bird.kill()

            for _ in range(SPEEDS[self.speed_index]):
                if len(self.birds) == 0:
                    break
                self.step()
                if score_limit and self.score >= score_limit:
                    return True

            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)
        return False

    def eval_genomes(self, genomes, config):
        self.generation += 1
        self.start_round([genome for _, genome in genomes], config)
        solved = self.run_round(SCORE_LIMIT)

        for bird in self.all_birds:
            bird.genome.fitness = bird.fitness

        champion = max((genome for _, genome in genomes), key=lambda g: g.fitness)
        self.history.append(champion.fitness)
        self.best_score = max(self.best_score, self.score)
        if champion.fitness > self.best_fitness or self.best_genome is None:
            self.best_fitness = champion.fitness
            self.best_genome = champion
            with open(BEST_PATH, "wb") as f:
                pickle.dump(champion, f)

        if solved:
            raise Solved

    def play(self, genome, config):
        """Watch one saved bird fly forever (restarts by itself when it crashes)."""
        self.mode = "play"
        while True:
            self.start_round([genome], config)
            self.run_round()


    def draw_text(self, surface, text, font, text_color, x, y):
        img = font.render(text, True, text_color)
        surface.blit(img, (x, y))

    def draw(self):
        surface = self.game_surface

        surface.blit(self.background_img, (0, 0))
        self.birds.draw(surface)
        self.pipes.draw(surface)
        surface.blit(self.ground_img, (self.ground_scroll, int(self.screen_height * 0.92)))
        self.draw_text(surface, str(self.score), self.font, self.color, int(self.screen_width / 2), 20)

        if self.followed is None or not self.followed.alive():
            self.followed = next(iter(self.birds), None)
        bird = self.followed
        if bird is not None:
            if self.next_pair is not None:
                bottom_pipe, top_pipe, _ = self.next_pair
                target = (bottom_pipe.rect.centerx, (top_pipe.rect.bottom + bottom_pipe.rect.top) // 2)
                pygame.draw.line(surface, HIGH, bird.rect.center, target, 2)
                pygame.draw.circle(surface, HIGH, target, 6)
            pygame.draw.circle(surface, HIGH, bird.rect.center, 30, 3)

        self.screen.blit(surface, (0, 0))
        self.draw_panel(bird)

    def draw_panel(self, bird):
        px = self.screen_width
        self.screen.fill(BG, (px, 0, self.panel_width, self.screen_height))
        pygame.draw.line(self.screen, LINE, (px, 0), (px, self.screen_height), 2)
        self.draw_text(self.screen, "Brain of the circled bird", self.title_font, TEXT, px + 16, 14)

        hidden = 0
        links = 0
        if bird is not None:
            self.view.draw(self.screen, bird.genome, bird.net, self.config.genome_config)
            self.view.draw_decision(self.screen, self.gauge_rect, bird.output)
            hidden = len(bird.genome.nodes) - len(self.config.genome_config.output_keys)
            links = sum(1 for c in bird.genome.connections.values() if c.enabled)

        alive = len(self.birds)
        if self.mode == "train":
            species = len(self.population.species.species) if self.population else 0
            rows = [
                ("Generation", f"{self.generation} / {MAX_GENERATIONS}"),
                ("Alive", f"{alive} / {self.total}"),
                ("Score", f"{self.score} / {SCORE_LIMIT}   (best {self.best_score})"),
                ("Best fitness", f"{self.best_fitness:.1f}"),
                ("Species", str(species)),
                ("Network", f"{hidden} hidden neurons, {links} links"),
                ("Speed", f"x{SPEEDS[self.speed_index]}"),
            ]
        else:
            rows = [
                ("Mode", "watching the saved champion"),
                ("Score", str(self.score)),
                ("Network", f"{hidden} hidden neurons, {links} links"),
                ("Speed", f"x{SPEEDS[self.speed_index]}"),
            ]
        y = 436
        for name, value in rows:
            self.draw_text(self.screen, name, self.panel_font, DIM, px + 18, y)
            self.draw_text(self.screen, value, self.panel_font, TEXT, px + 150, y)
            y += 25

        if self.mode == "train":
            draw_chart(self.screen, (px + 12, 622, self.panel_width - 24, 84),
                       self.history, "best fitness per generation", self.small_font)
        self.draw_text(self.screen, "SPACE speed   N next generation   F11 fullscreen   ESC quit",
                       self.small_font, DIM, px + 16, self.screen_height - 26)


def load_config():
    return neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                       neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_PATH)


def train():
    config = load_config()
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    game = AIGame(population)

    try:
        population.run(game.eval_genomes, MAX_GENERATIONS)
    except Solved:
        print(f"\nSolved in generation {game.generation}: a bird passed {SCORE_LIMIT} pipes.")
    print(f"Best bird saved to {BEST_PATH}  (watch it again with: python ai_flappy.py --play)")

    game.play(game.best_genome, config)    

def watch():
    with open(BEST_PATH, "rb") as f:
        genome = pickle.load(f)
    AIGame().play(genome, load_config())


if __name__ == "__main__":
    if "--play" in sys.argv:
        watch()
    else:
        train()
