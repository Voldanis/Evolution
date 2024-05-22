import random
import time
import pygame


class Server:
    def __init__(self):
        # константы
        self.const_cell = 'k'
        # среда
        env_width = 2
        env_height = 2
        self.environment = [['.' for _ in range(env_width)] for _ in range(env_height)]  # environment[y][x]
        # окно
        win_width = 950  # сделать от среды
        win_height = 950
        self.cell_size = win_width // env_width
        self.window = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption('Evolution')
        self.delay = 0
        self.running = True
        # цвета
        self.color_cyan = (200, 200, 255)
        self.color_blue = (0, 0, 255)
        # клетки
        self.cells = dict()
        for i in range(env_height):
            self.cells[i] = dict()
        # создание клетки
        cx = random.randint(0, env_width - 1)
        cy = random.randint(0, env_height - 1)
        self.cells[cy][cx] = Cell(cy, cx)
        self.environment[cy][cx] = self.const_cell

    def run(self):
        print(self.environment)
        while self.running:
            t = time.time()
            self.process_events()
            self.draw()
            tc = time.time()
            if tc - t < self.delay:
                time.sleep(self.delay - (tc - t))
        pygame.quit()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def draw(self):
        self.window.fill(self.color_cyan)
        for y in range(len(self.environment)):
            line = self.environment[y]
            for x in range(len(line)):
                obj = line[x]
                if obj == self.const_cell:
                    pygame.draw.rect(self.window, self.color_blue, (x * self.cell_size,
                                                                    y * self.cell_size,
                                                                    self.cell_size,
                                                                    self.cell_size), 0)
        pygame.display.flip()


class Cell:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.energy = 10


if __name__ == "__main__":
    server = Server()
    server.run()
