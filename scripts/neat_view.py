import pygame

BG = (24, 26, 33)
BOX = (33, 36, 45)
LINE = (62, 66, 80)
TEXT = (228, 231, 238)
DIM = (140, 146, 162)
NEUTRAL = (58, 62, 76)
LOW = (70, 130, 255)       # (blue)
HIGH = (255, 196, 60)      # (yellow)
POS_LINK = (90, 220, 130)  # (green)
NEG_LINK = (235, 85, 85)   # (red)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def activation_color(v):
    """grey = 0, yellow = positive, blue = negative"""
    return lerp(NEUTRAL, HIGH if v >= 0 else LOW, abs(v))


class NetworkView:
    """Draws a NEAT feed-forward network and what it is 'thinking' right now.

    - circles   = neurons, coloured by their current activation
    - lines     = connections: green = positive weight, red = negative weight,
                  thicker = bigger weight, brighter = a signal is flowing through it right now
    """

    def __init__(self, rect, input_labels):
        self.rect = pygame.Rect(rect)
        self.input_labels = input_labels
        self.font = pygame.font.Font(None, 21)
        self.small = pygame.font.Font(None, 18)
        self.genome = None
        self.pos = {}
        self.edges = []

    def build(self, genome, genome_config):
        inputs = sorted(genome_config.input_keys, reverse=True)   # -1, -2, -3 ...
        outputs = list(genome_config.output_keys)
        links = [(a, b) for (a, b), c in genome.connections.items() if c.enabled]

        needed = set(outputs)
        grew = True
        while grew:
            grew = False
            for a, b in links:
                if b in needed and a not in needed and a not in inputs:
                    needed.add(a)
                    grew = True

        # depth of every neuron = longest chain of links back to an input
        depth = {k: 0 for k in inputs}

        def get_depth(n, seen=()):
            if n in depth:
                return depth[n]
            if n in seen:
                return 1
            depth[n] = 1 + max([get_depth(a, seen + (n,)) for a, b in links if b == n] or [0])
            return depth[n]

        for n in needed:
            get_depth(n)

        hidden_depths = sorted({depth[n] for n in needed if n not in outputs})
        columns = [inputs]
        for d in hidden_depths:
            columns.append(sorted(n for n in needed if n not in outputs and depth[n] == d))
        columns.append(outputs)

        r = self.rect
        x0, x1 = r.x + 100, r.right - 70
        self.pos = {}
        for i, col in enumerate(columns):
            x = x0 + (x1 - x0) * i / (len(columns) - 1)
            for j, node in enumerate(col):
                y = r.y + r.height * (j + 1) / (len(col) + 1)
                self.pos[node] = (int(x), int(y))

        self.edges = [(a, b, genome.connections[(a, b)].weight)
                      for a, b in links if a in self.pos and b in self.pos]
        self.genome = genome

    def draw(self, surface, genome, net, genome_config):
        if genome is not self.genome:
            self.build(genome, genome_config)
        values = net.values

        pygame.draw.rect(surface, BOX, self.rect, border_radius=8)

        for a, b, w in self.edges:
            signal = values.get(a, 0.0) * w
            glow = 0.2 + 0.8 * min(1.0, abs(signal))
            color = lerp(BOX, POS_LINK if w >= 0 else NEG_LINK, glow)
            width = 1 + int(min(4, abs(w) * 1.5))
            pygame.draw.line(surface, color, self.pos[a], self.pos[b], width)

        for node, (x, y) in self.pos.items():
            v = values.get(node, 0.0)
            fill = activation_color(v)
            pygame.draw.circle(surface, fill, (x, y), 17)
            pygame.draw.circle(surface, TEXT, (x, y), 17, 2)

            luminance = 0.3 * fill[0] + 0.59 * fill[1] + 0.11 * fill[2]
            number = self.small.render(f"{v:.1f}", True, (20, 20, 25) if luminance > 130 else TEXT)
            surface.blit(number, number.get_rect(center=(x, y)))

            if node < 0:
                label = self.font.render(self.input_labels[-node - 1], True, TEXT)
                surface.blit(label, label.get_rect(midright=(x - 24, y)))
            elif node in genome_config.output_keys:
                label = self.font.render("flap?", True, TEXT)
                surface.blit(label, label.get_rect(midleft=(x + 24, y)))

    def draw_decision(self, surface, rect, output):
        """A little gauge: the output neuron's value from -1 to +1, flap when it passes 0.5."""
        r = pygame.Rect(rect)
        flap = output > 0.5
        pygame.draw.rect(surface, BOX, r, border_radius=6)

        x = r.x + r.width * (max(-1.0, min(1.0, output)) + 1) / 2
        pygame.draw.rect(surface, HIGH if flap else LOW, (r.x, r.y, x - r.x, r.height), border_radius=6)
        tick = r.x + r.width * 1.5 / 2                      # the 0.5 threshold
        pygame.draw.line(surface, TEXT, (tick, r.y - 3), (tick, r.bottom + 3), 2)

        caption = self.font.render("output", True, DIM)
        surface.blit(caption, caption.get_rect(midright=(r.x - 12, r.centery)))
        status = self.font.render("FLAP!" if flap else "glide", True, HIGH if flap else DIM)
        surface.blit(status, status.get_rect(midleft=(r.right + 12, r.centery)))


def draw_chart(surface, rect, values, title, font):
    """Small line chart, used for 'best fitness per generation'."""
    r = pygame.Rect(rect)
    pygame.draw.rect(surface, BOX, r, border_radius=8)
    surface.blit(font.render(title, True, DIM), (r.x + 10, r.y + 7))
    if len(values) < 2:
        return
    top = max(max(values), 1e-9)
    points = [(r.x + 12 + (r.width - 24) * i / (len(values) - 1),
               r.bottom - 12 - (r.height - 42) * v / top)
              for i, v in enumerate(values)]
    pygame.draw.lines(surface, POS_LINK, False, points, 2)
    for p in points:
        pygame.draw.circle(surface, POS_LINK, p, 3)
