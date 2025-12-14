import pygame
import random
import sys

# Menginisialisasi Pygame
pygame.init()
try:
    pygame.mixer.init() # Menginisialisasi modul dari suara
except Exception:
    print("Warning: mixer init failed, sound disabled.")

# Konstanta untuk Game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
ASSET_FOLDER = "asset"  # Tempat asset menyimpan gambar dan suara

# Warna RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# ============= ENCAPSULATION =============
class GameObject:
    def __init__(self, x, y, width, height):
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__speed = 5
        self.__is_active = True # Mengecek apakah objek masih aktif
        self.image = None

    # Getter methods
    def get_x(self):
        return self.__x
    def get_y(self):
        return self.__y
    def get_width(self):
        return self.__width
    def get_height(self):
        return self.__height
    def get_speed(self):
        return self.__speed
    def is_active(self):
        return self.__is_active

    # Setter methods
    def set_x(self, x):
        self.__x = x
    def set_y(self, y):
        self.__y = y
    def set_speed(self, speed):
        self.__speed = speed
    def set_active(self, status):
        self.__is_active = status

    def get_rect(self): # collision detection
        return pygame.Rect(int(self.__x), int(self.__y), self.__width, self.__height)

    def update(self): # update objek (di override oleh class turunan)
        pass

    def draw(self, screen): # Menggambar objek
        pass


# ============= INHERITANCE =============
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 150, 120)  # Mewarisi GameObject
        self.__health = 100               # Atribut Khusus
        self.__max_health = 100
        self.__score = 0
        self.set_speed(7) # Kecepatan Player

    # Getter healt dan score untuk membaca nilai yang bersifat private
    def get_health(self):
        return self.__health
    def get_max_health(self):
        return self.__max_health
    def get_score(self):
        return self.__score
    def add_score(self, points):
        self.__score += points
    
    def take_damage(self, damage): 
        self.__health -= damage
        if self.__health <= 0:
            self.__health = 0
            self.set_active(False) # Setter untuk status 

    def heal(self, amount):
        self.__health = min(self.__health + amount, self.__max_health)

    # Gerakan player dengan batasan layar yang ditentukan
    def move_left(self):
        new_x = self.get_x() - self.get_speed()
        if new_x >= 0:
            self.set_x(new_x)

    def move_right(self):
        new_x = self.get_x() + self.get_speed()
        if new_x <= SCREEN_WIDTH - self.get_width():
            self.set_x(new_x)

    def move_up(self):
        new_y = self.get_y() - self.get_speed()
        if new_y >= 0:
            self.set_y(new_y)

    def move_down(self):
        new_y = self.get_y() + self.get_speed()
        if new_y <= SCREEN_HEIGHT - self.get_height():
            self.set_y(new_y)

    def update(self): # Movement di handle di event loop
        pass

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.get_x(), self.get_y()))


# ============= INHERITANCE & POLYMORPHISM =============
class Enemy(GameObject): # Semua musuh
    def __init__(self, x, y, width, height, points):
        super().__init__(x, y, width, height)
        self.__points = points
        self.set_speed(random.randint(2, 4)) # Random untuk speed musuh

    def get_points(self):
        return self.__points

    def update(self): 
        self.set_y(self.get_y() + self.get_speed())
        if self.get_y() > SCREEN_HEIGHT: # Bergerak ke bawah
            self.set_active(False) # Nonaktif jika keluar layar

    def draw(self, screen):
        pass


# ============= POLYMORPHISM =============
class BasicEnemy(Enemy): # Musuh biasa (tetap)
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, 10)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.get_x(), self.get_y()))

class FastEnemy(Enemy): # Musuh dengan speed cepat
    def __init__(self, x, y):
        super().__init__(x, y, 35, 35, 20)
        self.set_speed(random.randint(5, 7))

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.get_x(), self.get_y()))

class BossEnemy(Enemy): # Musuh yang healtnya banyak
    def __init__(self, x, y):
        super().__init__(x, y, 80, 60, 50)
        self.__health = 5
        self.set_speed(2)

    def get_health(self):
        return self.__health

    def take_damage(self):
        self.__health -= 1 # kehilangan 1 healt setiap tembakan
        if self.__health <= 0:
            self.set_active(False)

    def draw(self, screen):
        if self.image:
            img = pygame.transform.scale(self.image, (self.get_width(), self.get_height()))
            screen.blit(img, (self.get_x(), self.get_y()))


# ================= BULLET & POWERUP =================
class Bullet(GameObject): 
    def __init__(self, x, y):
        super().__init__(x, y, 20, 30)
        self.set_speed(10)

    def update(self):
        self.set_y(self.get_y() - self.get_speed())
        if self.get_y() < 0:
            self.set_active(False)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.get_x(), self.get_y()))

class PowerUp(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.set_speed(3)

    def update(self):
        self.set_y(self.get_y() + self.get_speed())
        if self.get_y() > SCREEN_HEIGHT:
            self.set_active(False)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.get_x(), self.get_y()))


# ============= GAME MANAGER CLASS =============
class Game: # Mengatur jalannya permainan
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Galaxy Shooter - By Dyah Hayuningrum_086")
        self.clock = pygame.time.Clock()

        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 150)
        self.bullets = []
        self.enemies = []
        self.powerups = []

        # Game state
        self.running = True
        self.game_over = False
        self.paused = False

        # Spawn timers
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0

        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Background stars
        self.stars = [
            (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            for _ in range(100)
        ]

        # Sound effects
        self.sounds = self._load_sounds()

        # Load images
        self._load_images()

    def _load_sounds(self):
        sounds = {}
        try:
            sounds['shoot'] = pygame.mixer.Sound(f"{ASSET_FOLDER}/shoot.wav")
            sounds['powerup'] = pygame.mixer.Sound(f"{ASSET_FOLDER}/powerup.wav")

            pygame.mixer.music.load(f"{ASSET_FOLDER}/background.wav")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) # Loop
        except Exception as e:
            print("Sound files not found or failed to load:", e)
            sounds = {'shoot': None, 'powerup': None}
        return sounds

    def _load_images(self):
        # Load player image
        try:
            p = pygame.image.load(f"{ASSET_FOLDER}/Pesawat.png").convert_alpha()
            self.player.image = pygame.transform.scale(
                p, (self.player.get_width(), self.player.get_height()))
        except Exception as e:
            print("Player image not found or failed to load:", e)

        # Load enemy image
        try:
            self.enemy_image = pygame.image.load(f"{ASSET_FOLDER}/Alien.png").convert_alpha()
        except Exception as e:
            self.enemy_image = None
            print("Enemy image not found or failed to load:", e)

        # Load bullet image
        try:
            b = pygame.image.load(f"{ASSET_FOLDER}/Bullet.png").convert_alpha()
            self.bullet_image = pygame.transform.scale(b, (20, 30))
        except Exception as e:
            self.bullet_image = None
            print("Bullet image not found or failed to load:", e)

        # Load powerup image
        try:
            p = pygame.image.load(f"{ASSET_FOLDER}/PowerUP.png").convert_alpha()
            self.powerup_image = pygame.transform.scale(p, (30, 30))
        except Exception as e:
            self.powerup_image = None
            print("PowerUp image not found or failed to load:", e)


# =================== LOGIKA UNTUK GAME ===================
    def play_sound(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"Failed to play sound {sound_name}: {e}")

    def spawn_enemy(self):
        x = random.randint(0, SCREEN_WIDTH - 40)
        enemy_type = random.randint(1, 100)

        if enemy_type <= 60:
            enemy = BasicEnemy(x, -40)
        elif enemy_type <= 90:
            enemy = FastEnemy(x, -35)
        else:
            enemy = BossEnemy(x, -60)

        # Assign image jika ada
        if self.enemy_image:
            try:
                enemy.image = pygame.transform.scale(
                    self.enemy_image, (enemy.get_width(), enemy.get_height())
                )
            except Exception:
                enemy.image = None

        self.enemies.append(enemy)

    def spawn_powerup(self):
        x = random.randint(0, SCREEN_WIDTH - 30)
        powerup = PowerUp(x, -30)
        
        if self.powerup_image:
            powerup.image = self.powerup_image
            
        self.powerups.append(powerup)

    def shoot_bullet(self):
        bullet = Bullet(
            self.player.get_x() + self.player.get_width() // 2 - 10,
            self.player.get_y())
        
        if self.bullet_image:
            bullet.image = self.bullet_image
            
        self.bullets.append(bullet)
        self.play_sound('shoot')

    def check_collisions(self):
        # Bullet vs Enemy
        for bullet in self.bullets[:]:
            if not bullet.is_active():
                continue

            for enemy in self.enemies[:]:
                if not enemy.is_active():
                    continue

                if bullet.get_rect().colliderect(enemy.get_rect()):
                    bullet.set_active(False)

                    # Boss butuh beberapa hit
                    if isinstance(enemy, BossEnemy):
                        enemy.take_damage()
                        if not enemy.is_active():
                            self.player.add_score(enemy.get_points())
                            self.play_sound('explosion')
                    else:
                        enemy.set_active(False)
                        self.player.add_score(enemy.get_points())
                        self.play_sound('explosion')

        # Enemy vs Player
        for enemy in self.enemies[:]:
            if not enemy.is_active():
                continue

            if enemy.get_rect().colliderect(self.player.get_rect()):
                enemy.set_active(False)
                self.player.take_damage(20)
                self.play_sound('explosion')

                if not self.player.is_active():
                    self.game_over = True

        # PowerUp vs Player 
        for powerup in self.powerups[:]:
            if not powerup.is_active():
                continue

            if powerup.get_rect().colliderect(self.player.get_rect()):
                powerup.set_active(False)
                self.player.heal(20) 
                self.play_sound('powerup')

    def update(self):
        if self.game_over or self.paused:
            return

        # Update player
        self.player.update()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_active():
                self.bullets.remove(bullet)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if not enemy.is_active():
                self.enemies.remove(enemy)

        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if not powerup.is_active():
                self.powerups.remove(powerup)

        # Update background stars
        self.stars = [(x, (y + 2) % SCREEN_HEIGHT) for x, y in self.stars]

        # Spawn enemies setiap 1 detik
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 60:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

        # Spawn powerups setiap 5 detik
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer > 300:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0

        # Check collisions
        self.check_collisions()

    def draw(self):
        # Background
        self.screen.fill(BLACK)

        # Draw stars
        for x, y in self.stars:
            pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), 1)

        # Draw game objects
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

        # Draw pause screen
        if self.paused:
            self.draw_pause()

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.font.render(
            f"Score: {self.player.get_score()}", True, WHITE
        )
        self.screen.blit(score_text, (10, 10))

        # Health bar
        bar_x = 10
        bar_y = 50
        bar_width = 200
        bar_height = 20

        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(
            (self.player.get_health() / self.player.get_max_health()) * bar_width
        )
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, health_width, bar_height))

        health_text = self.small_font.render(
            f"Health: {self.player.get_health()}", True, WHITE
        )
        self.screen.blit(health_text, (bar_x + 5, bar_y + 2))

# ================ TAMPILAN GAME OVER ==================
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER!", True, RED)
        score_text = self.font.render(
            f"Final Score: {self.player.get_score()}", True, WHITE
        )
        restart_text = self.small_font.render(
            "Press Q to Quit", True, WHITE
        )

        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50)
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2)
        )
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50)
        )

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("PAUSED", True, YELLOW)
        continue_text = self.small_font.render("Press P to Continue", True, WHITE)

        self.screen.blit(
            pause_text,
            (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20)
        )
        self.screen.blit(
            continue_text,
            (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20)
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.shoot_bullet()

                if event.key == pygame.K_p:
                    self.paused = not self.paused

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart game
                    elif event.key == pygame.K_q:
                        self.running = False

        # Continuous movement
        if not self.game_over and not self.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.move_up()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.move_down()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ============= MAIN PROGRAM =============
if __name__ == "__main__":
    game = Game()
    game.run()