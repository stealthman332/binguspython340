import pygame

pygame.init()

################################################################################################
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
pygame.display.set_caption("Brick Break - Multiplayer")
player_pos = pygame.Vector2(display_surface.get_width() / 2,
                            display_surface.get_height() / 2)

###############################################################################################
class Ball:
    # default constructor
    def __init__(self, radius, x_pos, y_pos, x_vel=0, y_vel=0):
        self.radius = radius
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_vel = x_vel
        self.y_vel = y_vel

    def draw_ball(self, surface, color):
        pygame.draw.circle(surface, color,
                           (int(self.x_pos), int(self.y_pos)),
                           self.radius)


class Paddle:
    def __init__(self, x_pos, y_pos, length, width, color,
                 controls, x_vel=0, y_vel=0, speed=5):
        self.rect = pygame.Rect(x_pos, y_pos, length, width)
        self.color = color
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.speed = speed

        if controls is None:
            controls = {}
        self.controls = controls

    def inputs(self):
        keys = pygame.key.get_pressed()

        if keys[self.controls.get("left", 0)]:
            self.x_pos -= self.speed * dt
        if keys[self.controls.get("right", 0)]:
            self.x_pos += self.speed * dt

        # sync rect with logical position
        self.rect.x = int(self.x_pos)
        self.rect.y = int(self.y_pos)


class Brick:
    def __init__(self, x_pos, y_pos, length, width, color, max_health):
        self.rect = pygame.Rect(x_pos, y_pos, length, width)
        self.color = color
        self.max_health = max_health
        self.health = max_health

    def take_damage(self, amount):
        self.health = max(self.health - amount, 0)

    def is_dead(self):
        return self.health <= 0

###############################################################################################

ballXVelocity, ballYVelocity = 0, 0

# controls from message1
player1_controls = {
    "right": pygame.K_d,
    "left": pygame.K_a
}

player2_controls = {
    "right": pygame.K_RIGHT,
    "left": pygame.K_LEFT
}

# paddles
player1Paddle = Paddle(450, 100, 100, 25, "white", player1_controls, speed=300)
player2Paddle = Paddle(450, 500, 100, 25, "red", player2_controls, speed=300)

# ball and brick
defaultBall = pygame.Rect(500, 500, 25, 25)
# if you want to actually use the Brick class:
# brick = Brick(300, 600, 20, 10, "darkred", max_health=1)
defaultBrick = pygame.Rect(300, 600, 20, 10)

# positions
player1_posx = player1Paddle.x_pos
player1_posy = player1Paddle.y_pos
player2_posx = player2Paddle.x_pos
player2_posy = player2Paddle.y_pos

# scores (typo fixed)
player1_score = 0
player2_score = 0

# ball velocity
ballXVelocity = 2.5
ballYVelocity = 2.5
brickDestroyed = False

# font for scores from message2
font = pygame.font.SysFont(None, 55)

##################################################################################################

# main game loop, runs every frame
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    display_surface.fill("black")

    # score text
    p1_text = font.render(f"P1: {player1_score}", True, "white")
    p2_text = font.render(f"P2: {player2_score}", True, "red")

    # draw scores on screen
    display_surface.blit(p1_text, (20, 20))
    display_surface.blit(p2_text, (WINDOW_WIDTH - 200, 20))

    # draw ball
    pygame.draw.rect(display_surface, "red", defaultBall)

    # draw brick if not destroyed
    if not brickDestroyed:
        pygame.draw.rect(display_surface, "darkred", defaultBrick)

    # move ball
    defaultBall.x += ballXVelocity
    defaultBall.y += ballYVelocity

    # PLAYER 1
    player1Paddle.x_pos = player1_posx
    player1Paddle.y_pos = player1_posy
    player1Paddle.inputs()
    player1_posx = player1Paddle.x_pos
    player1_posy = player1Paddle.y_pos

    pygame.draw.rect(display_surface, "white", player1Paddle.rect)

    # collision with ball
    if player1Paddle.rect.colliderect(defaultBall):
        ballYVelocity *= -1
        player1_score += 1

    # stop going off-screen
    if player1Paddle.rect.left <= 0:
        player1Paddle.rect.left = 0
        player1_posx = player1Paddle.rect.x
    if player1Paddle.rect.right >= WINDOW_WIDTH:
        player1Paddle.rect.right = WINDOW_WIDTH
        player1_posx = player1Paddle.rect.x

    # PLAYER 2
    player2Paddle.x_pos = player2_posx
    player2Paddle.y_pos = player2_posy
    player2Paddle.inputs()
    player2_posx = player2Paddle.x_pos
    player2_posy = player2Paddle.y_pos

    pygame.draw.rect(display_surface, "red", player2Paddle.rect)

    if player2Paddle.rect.colliderect(defaultBall):
        ballYVelocity *= -1
        player2_score += 1

    # ball bounds
    if defaultBall.top <= 0 or defaultBall.bottom >= WINDOW_HEIGHT:
        ballYVelocity *= -1

    if defaultBall.left <= 0 or defaultBall.right >= WINDOW_WIDTH:
        ballXVelocity *= -1

    # PLAYER 2 bounds
    if player2Paddle.rect.left <= 0:
        player2Paddle.rect.left = 0
        player2_posx = player2Paddle.rect.x
    if player2Paddle.rect.right >= WINDOW_WIDTH:
        player2Paddle.rect.right = WINDOW_WIDTH
        player2_posx = player2Paddle.rect.x

    # brick hit
    if defaultBall.colliderect(defaultBrick) and not brickDestroyed:
        brickDestroyed = True
        ballYVelocity *= -1
        # if using Brick object, call take_damage here

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()