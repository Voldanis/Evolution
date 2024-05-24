import random
import time
import pygame


class Server:
    def __init__(self):
        # константы
        self.color_cyan = (200, 200, 255)
        self.color_blue = (0, 0, 255)
        self.color_lime = (0, 200, 0)
        # окно
        win_width = 950  # сделать от среды
        win_height = 950
        self.window = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption('Evolution')
        self.delay = 0.25
        self.running = True
        # среда
        self.env_width = 2
        self.env_height = 2
        self.environment = [['' for _ in range(self.env_width)] for _ in range(self.env_height)]  # environment[y][x]
        self.free_cells = dict()
        for i in range(self.env_height):
            self.free_cells[i] = set()
            for j in range(self.env_width):
                self.free_cells[i].add(j)
        self.cell_size = win_width // self.env_width
        # очередь обработки
        self.processing_queue = ['server']
        self.processing_index = 0
        # объекты
        self.objects = Objects()
        self.generate_cell()

    def generate_cell(self, y=-1, x=-1):
        if len(self.free_cells.keys()) == 0:
            print('Error: no free cells')
        if y == -1:
            y = random.choice(list(self.free_cells.keys()))
        if x == -1:
            x = random.choice(list(self.free_cells[y]))

        key = generate_key(self.objects.cells.keys())
        self.objects.cells[key] = Cell(y, x)
        self.environment[y][x] = key
        self.free_cells[y].remove(x)
        if len(self.free_cells[y]) == 0:
            del self.free_cells[y]
        self.processing_queue.append(key)

    def generate_food(self, y=-1, x=-1, energy=6):
        if len(self.free_cells.keys()) == 0:
            print('Error: no free cells')
        if y == -1:
            y = random.choice(list(self.free_cells.keys()))
        if x == -1:
            x = random.choice(list(self.free_cells[y]))

        key = generate_key(self.objects.food.keys())
        self.objects.food[key] = Food(y, x, energy)
        self.environment[y][x] = key
        self.free_cells[y].remove(x)
        if len(self.free_cells[y]) == 0:
            del self.free_cells[y]

    def run(self):
        while self.running:
            t = time.time()
            self.process_player_events()
            self.process_game_events()
            self.draw()
            tc = time.time()
            if tc - t < self.delay:
                time.sleep(self.delay - (tc - t))
        pygame.quit()

    def process_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def process_game_events(self):
        self.processing_index += 1
        if self.processing_index >= len(self.processing_queue):
            self.processing_index = 0
        while len(self.processing_queue) > 0 and self.processing_queue[self.processing_index] != 'server' and \
                self.processing_queue[self.processing_index] not in self.objects.cells.keys():
            self.processing_queue.pop(self.processing_index)
            if self.processing_index >= len(self.processing_queue):
                self.processing_index = 0

        if len(self.processing_queue) > 0:
            if self.processing_queue[self.processing_index] == 'server':
                if len(self.free_cells.keys()) > 0:
                    self.generate_food()
            else:
                self.objects.cells[self.processing_queue[self.processing_index]].energy -= 1
                if self.objects.cells[self.processing_queue[self.processing_index]].energy <= 0:
                    y = self.objects.cells[self.processing_queue[self.processing_index]].y
                    x = self.objects.cells[self.processing_queue[self.processing_index]].x
                    self.environment[y][x] = ''
                    if y not in self.free_cells.keys():
                        self.free_cells[y] = set()
                    self.free_cells[y].add(x)
                    del self.objects.cells[self.processing_queue[self.processing_index]]
                    self.generate_food(y, x, 1)

    def draw(self):
        self.window.fill(self.color_cyan)
        for y in range(len(self.environment)):
            line = self.environment[y]
            for x in range(len(line)):
                obj = line[x]
                if obj in self.objects.cells.keys():
                    pygame.draw.rect(self.window, self.color_blue, (x * self.cell_size,
                                                                    y * self.cell_size,
                                                                    self.cell_size,
                                                                    self.cell_size), 0)
                elif obj in self.objects.food.keys():
                    pygame.draw.rect(self.window, self.color_lime, (x * self.cell_size,
                                                                    y * self.cell_size,
                                                                    self.cell_size,
                                                                    self.cell_size), 0)
        pygame.display.flip()


class Objects:
    def __init__(self):
        self.cells = dict()
        self.food = dict()


class Cell:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.energy = 10


class Food:
    def __init__(self, y, x, energy):
        self.y = y
        self.x = x
        self.energy = energy


def generate_key(values):
    key = str(random.randint(0, 999999999))
    while key in values:
        key = str(random.randint(0, 999999999))
    return key


if __name__ == "__main__":
    server = Server()
    server.run()
