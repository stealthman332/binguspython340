import pygame

class Ball:
    # Circle-based ball
    def __init__(self, radius, x_pos, y_pos, x_vel=0, y_vel=0):
        self.radius = radius
        self.x_pos = float(x_pos)
        self.y_pos = float(y_pos)
        self.x_vel = float(x_vel)
        self.y_vel = float(y_vel)

    def draw(self, surface, color):
        pygame.draw.circle(surface, color,
                           (int(self.x_pos), int(self.y_pos)),
                           self.radius)

    def move(self, dt):
        self.x_pos += self.x_vel * dt
        self.y_pos += self.y_vel * dt


class Paddle:
    def __init__(self, x_pos, y_pos, length, width, color,
                 controls, speed=5):
        self.rect = pygame.Rect(x_pos, y_pos, length, width)
        self.color = color
        self.x_pos = float(x_pos)
        self.y_pos = float(y_pos)
        self.speed = speed
        self.controls = controls or {}

    def inputs(self, dt):
        keys = pygame.key.get_pressed()
        shot = False

        if keys[self.controls.get("left", 0)]:
            self.x_pos -= self.speed * dt
        if keys[self.controls.get("right", 0)]:
            self.x_pos += self.speed * dt
        if keys[self.controls.get("shoot", 0)]:
            shot = True

        # sync rect with logical position
        self.rect.x = int(self.x_pos)
        self.rect.y = int(self.y_pos)
        return shot

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Brick:
    def __init__(self, x_pos, y_pos, length, width, color, max_health=1):
        self.rect = pygame.Rect(x_pos, y_pos, length, width)
        self.color = color
        self.max_health = max_health
        self.health = max_health

    def take_damage(self, amount):
        self.health = max(self.health - amount, 0)

    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Laser:
    def __init__(self, x_pos, y_pos,
                 length=5, width=2,
                 color="red", speed=-600):
        self.rect = pygame.Rect(x_pos, y_pos, length, width)
        self.color = color
        self.speed = speed  # pixels per second

    def update(self, dt):
        self.rect.y += int(self.speed * dt)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)