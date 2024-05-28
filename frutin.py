import pygame
import random
import sys
from pygame import mixer

# Dimensiones del campo de juego (aumentadas)
ROWS = 10
COLS = 10
CELL_SIZE = 80  # Aumentado el tamaño de la celda
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)  # Color para las marcas del jugador

# Definición de tipos de frutas y sus valores
FRUITS = {
    "apple": {"value": 10, "image": "apple.png"},
    "mango": {"value": 20, "image": "mango.png"},
    "blueberry": {"value": 15, "image": "blueberry.png"}
}

mixer.init()
mixer.music.load("background.mp3")
mixer.music.set_volume(0.5)  # Ajusta el volumen según tus preferencias
mixer.music.play(-1, 0, 5000)  # Reproduce la música en bucle

fruit_sounds = {
    "apple": mixer.Sound("apple.mp3"),
    "mango": mixer.Sound("mango.mp3"),
    "blueberry": mixer.Sound("blueberry.mp3"),
    "win": mixer.Sound("win.mp3")
}

# Función para reproducir el sonido de una fruta
def play_fruit_sound(fruit_type):
    fruit_sounds[fruit_type].play()

def play_win_sound():
    fruit_sounds["win"].play()

# Función para cargar imágenes y redimensionarlas
def load_images():
    images = {}
    for fruit_type in FRUITS:
        image = pygame.image.load(FRUITS[fruit_type]["image"])
        image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        images[fruit_type] = image
    return images

# Clase para representar el jugador
class Player:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.score = 0
        self.path = []  # Lista para almacenar las posiciones visitadas
        self.image = pygame.image.load("player.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def move(self, drow, dcol):
        new_row = self.row + drow
        new_col = self.col + dcol
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            self.row = new_row
            self.col = new_col
            self.path.append((self.row, self.col))  # Agregar la posición actual a la lista de posiciones visitadas

    def draw(self, screen):
        screen.blit(self.image, (self.col * CELL_SIZE, self.row * CELL_SIZE))
        # Dibujar las marcas del jugador en el camino
        for row, col in self.path:
            pygame.draw.circle(screen, LIGHT_BLUE, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 8)

# Clase para representar las frutas
class Fruit:
    def __init__(self, row, col, fruit_type):
        self.row = row
        self.col = col
        self.type = fruit_type
        self.value = FRUITS[fruit_type]["value"]
        self.image = pygame.image.load(FRUITS[fruit_type]["image"])
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def draw(self, screen):
        screen.blit(self.image, (self.col * CELL_SIZE, self.row * CELL_SIZE))

# Función para generar frutas aleatoriamente
def generate_fruits(num_fruits):
    fruits = []
    for _ in range(num_fruits):
        row = random.randint(0, ROWS - 1)
        col = random.randint(0, COLS - 1)
        fruit_type = random.choice(list(FRUITS.keys()))
        fruits.append(Fruit(row, col, fruit_type))
    return fruits

# Función para construir el grafo del campo de juego
def build_graph():
    graph = {}
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = []
            if row > 0:
                neighbors.append((row - 1, col))  # Arriba
            if row < ROWS - 1:
                neighbors.append((row + 1, col))  # Abajo
            if col > 0:
                neighbors.append((row, col - 1))  # Izquierda
            if col < COLS - 1:
                neighbors.append((row, col + 1))  # Derecha
            graph[(row, col)] = neighbors
    return graph

# Función para calcular la distancia en el grafo entre dos posiciones
def graph_distance(graph, start, end):
    visited = set()
    queue = [(start, 0)]
    while queue:
        node, distance = queue.pop(0)
        if node == end:
            return distance
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append((neighbor, distance + 1))

# Función principal del juego
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("FRUTIN")
    clock = pygame.time.Clock()

    player = Player(ROWS // 2, COLS // 2)
    fruits = generate_fruits(10)
    time_remaining = 60
    attempts_remaining = 3
    images = load_images()
    graph = build_graph()

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(-1, 0)  # Arriba
                elif event.key == pygame.K_DOWN:
                    player.move(1, 0)   # Abajo
                elif event.key == pygame.K_LEFT:
                    player.move(0, -1)  # Izquierda
                elif event.key == pygame.K_RIGHT:
                    player.move(0, 1)   # Derecha

        # Verificar si el jugador recolectó una fruta
        for fruit in fruits[:]:
            if fruit.row == player.row and fruit.col == player.col:
                player.score += fruit.value
                play_fruit_sound(fruit.type)
                fruits.remove(fruit)

        # Dibujar al jugador y las frutas
        player.draw(screen)
        for fruit in fruits:
            fruit.draw(screen)

        # Mostrar puntaje y tiempo restante en la pantalla
        font = pygame.font.Font(None, 48)  # Tamaño de fuente aumentado
        score_text = font.render("Score: " + str(player.score), True, WHITE)
        screen.blit(score_text, (10, 10))
        time_text = font.render("Time: " + str(int(time_remaining)), True, WHITE)
        screen.blit(time_text, (10, 70))
        attempts_text = font.render("Attempts: " + str(attempts_remaining), True, WHITE)
        screen.blit(attempts_text, (10, 130))

        # Actualizar el tiempo restante
        time_remaining -= 1 / 60

        # Verificar si se acabó el tiempo o se recolectaron todas las frutas
        if time_remaining <= 0:
            attempts_remaining -= 1
            time_remaining = 60
            if attempts_remaining <= 0:
                font = pygame.font.Font(None, 72)
                game_over_text = font.render("Game Over", True, RED)
                screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(3000)  # Mostrar el mensaje durante 3 segundos
                pygame.quit()
                sys.exit()
            else:
                fruits = generate_fruits(10)
        elif not fruits:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GANASTE!!!!", True, GREEN)
            play_win_sound()
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)  # Mostrar el mensaje durante 3 segundos
            pygame.quit()
            sys.exit()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()







