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
        self.delay = 1
        self.running = True
        # среда
        self.env_width = 5
        self.env_height = 5
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
        self.generate_organism()

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
        self.tweak_index()
        if self.processing_queue[self.processing_index] == 'server':
            for _ in range(1):
                if len(self.free_cells.keys()) > 0:
                    self.generate_food()
        else:
            organism_key = self.processing_queue[self.processing_index]
            organism = self.objects.organisms[organism_key]
            cell_key = self.get_adjacent_cell(organism)
            self.organism_do_something(organism_key, cell_key)
            organism.energy -= 1
            print(organism.energy)
            if organism.energy <= 0:
                self.kill_organism(organism_key)

    def tweak_index(self):
        self.processing_index += 1
        if self.processing_index >= len(self.processing_queue):
            self.processing_index = 0
        while self.processing_queue[self.processing_index] != 'server' and \
                self.processing_queue[self.processing_index] not in self.objects.organisms.keys():
            self.processing_queue.pop(self.processing_index)
            if self.processing_index >= len(self.processing_queue):
                self.processing_index = 0

    def generate_organism(self, y=-1, x=-1):
        if len(self.free_cells.keys()) == 0:
            print('Error: no free organisms')
        if y == -1:
            y = random.choice(list(self.free_cells.keys()))
        if x == -1:
            x = random.choice(list(self.free_cells[y]))
        key = generate_key(self.objects.organisms.keys())
        self.objects.organisms[key] = Organism(y, x)
        self.environment[y][x] = key
        self.free_cells[y].remove(x)
        if len(self.free_cells[y]) == 0:
            del self.free_cells[y]
        self.processing_queue.append(key)

    def get_adjacent_cell(self, organism):
        if organism.direction == 'u':
            if organism.y > 0:
                return self.environment[organism.y - 1][organism.x]
            else:
                return 'border'
        elif organism.direction == 'd':
            if organism.y < self.env_height - 1:
                return self.environment[organism.y + 1][organism.x]
            else:
                return 'border'
        elif organism.direction == 'l':
            if organism.x > 0:
                return self.environment[organism.y][organism.x - 1]
            else:
                return 'border'
        else:
            if organism.x < self.env_width - 1:
                return self.environment[organism.y][organism.x + 1]
            else:
                return 'border'

    def organism_do_something(self, organism_key, cell_key):
        organism = self.objects.organisms[organism_key]
        if cell_key in self.objects.food.keys():
            self.organism_eat(organism_key, cell_key)
        elif cell_key != '':
            if organism.energy > organism.fin_energy_consumption + 1:
                self.organism_rotate(organism_key)
        else:
            if find_out_event_happened(organism.rotate_chance):
                if organism.energy > organism.fin_energy_consumption + 1:
                    self.organism_rotate(organism_key)

    def organism_rotate(self, organism_key):
        organism = self.objects.organisms[organism_key]
        r_i = Organism.directions.index(organism.direction)
        if r_i == len(Organism.directions) - 1:
            organism.direction = Organism.directions[0]
        else:
            organism.direction = Organism.directions[r_i + 1]
        organism.energy -= 1
        print('rotate: ', organism.direction)

    def organism_eat(self, organism_key, food_key):
        organism = self.objects.organisms[organism_key]
        food = self.objects.food[food_key]
        if food.energy <= organism.mouth_power:
            organism.energy += food.energy - organism.mouth_energy_consumption
            self.take_away_food(food_key)
        else:
            organism.energy += organism.mouth_power - organism.mouth_energy_consumption
            food.energy -= organism.mouth_power
        print('eat')

    def kill_organism(self, organism_key):
        organism = self.objects.organisms[organism_key]
        self.environment[organism.y][organism.x] = ''
        if organism.y not in self.free_cells.keys():
            self.free_cells[organism.y] = set()
        self.free_cells[organism.y].add(organism.x)
        del self.objects.organisms[organism_key]
        self.generate_food(organism.y, organism.x, 1)

    def generate_food(self, y=-1, x=-1, energy=18):
        if len(self.free_cells.keys()) == 0:
            print('Error: no free organisms')
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

    def take_away_food(self, food_key):
        food = self.objects.food[food_key]
        self.environment[food.y][food.x] = ''
        if food.y not in self.free_cells.keys():
            self.free_cells[food.y] = set()
        self.free_cells[food.y].add(food.x)
        del self.objects.food[food_key]

    def draw(self):
        self.window.fill(self.color_cyan)
        for y in range(len(self.environment)):
            line = self.environment[y]
            for x in range(len(line)):
                obj = line[x]
                if obj in self.objects.organisms.keys():
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
        self.organisms = dict()
        self.food = dict()


class Organism:
    directions = ['u', 'r', 'd', 'l']

    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.energy = 15
        self.direction = 'u'
        self.mouth_power = 6
        self.mouth_energy_consumption = 1
        self.fin_direction = "clockwise"
        self.fin_energy_consumption = 1
        self.rotate_chance = 0.25


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


def find_out_event_happened(chance):
    result = random.randint(0, 100) / 100
    if result <= chance:
        return True
    else:
        return False


if __name__ == "__main__":
    server = Server()
    server.run()
