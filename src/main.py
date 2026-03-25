import pygame
from objects import Ball, Paddle, Brick, Laser

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
game_state = "intro"  # other is "playing"

# font for UI
font = pygame.font.SysFont(None, 55)

###############################################################################################

# controls
player1_controls = {
    "right": pygame.K_d,
    "left": pygame.K_a,
    "shoot": pygame.K_w,
}

player2_controls = {
    "right": pygame.K_RIGHT,
    "left": pygame.K_LEFT,
    "shoot": pygame.K_UP,
}

# paddles
player1Paddle = Paddle(450, 100, 100, 25, "cyan", player1_controls, speed=300)
player2Paddle = Paddle(450, WINDOW_HEIGHT - 100, 100, 25, "violet", player2_controls, speed=300)

# ball
game_ball = Ball(10, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 200, 200)

# brick (plain rect for now)
defaultBrick = pygame.Rect(300, 600, 20, 10)
brickDestroyed = False

# lasers
player1_lasers = []
player2_lasers = []

# money
players_money = 0

##################################################################################################

def draw_intro(surface):
    big_font = pygame.font.SysFont(None, 150)
    med_font = pygame.font.SysFont(None, 50)
    small_font = pygame.font.SysFont(None, 25)

    title_text = big_font.render("Brick Break", True, "Cyan")
    surface.blit(
        title_text,
        (WINDOW_WIDTH // 2 - title_text.get_width() // 2,
         WINDOW_HEIGHT // 2 - 200),
    )

    subtitle_text = med_font.render("Cyberpunk Edition", True, "violet")
    surface.blit(
        subtitle_text,
        (WINDOW_WIDTH // 2 - subtitle_text.get_width() // 2,
         WINDOW_HEIGHT // 2),
    )

    if pygame.time.get_ticks() % 1000 < 500:
        subsubtitle_text = small_font.render("Press any key to start", True, "white")
        surface.blit(
            subsubtitle_text,
            (WINDOW_WIDTH // 2 - subsubtitle_text.get_width() // 2,
             WINDOW_HEIGHT // 2 + 150),
        )

prev_ball_x =  game_ball.x_pos
prev_ball_y = game_ball.y_pos

##################################################################################################
def resolve_ball_paddle_collision(ball, prev_x, prev_y, paddle_rect):
    ball_rect = pygame.Rect(
            ball.x_pos - ball.radius,
            ball.y_pos - ball.radius,
            ball.radius * 2,
            ball.radius * 2,
        )
    if not paddle_rect.colliderect(ball_rect):
        return
    
    prev_rect = pygame.Rect(
            prev_x - ball.radius,
            prev_y - ball.radius,
            ball.radius * 2,
            ball.radius * 2,
        )
    
    was_left = prev_rect.right <= paddle_rect.left
    was_right = prev_rect.left >= paddle_rect.right
    was_above= prev_rect.bottom <= paddle_rect.top
    was_below = prev_rect.top >= paddle_rect.bottom

    if was_above:
        ball.y_pos = paddle_rect.top -ball.radius
        ball.y_vel *= -1
    elif was_below:
        ball.y_pos = paddle_rect.bottom + ball.radius
        ball.y_vel *= -1
    elif was_left:
        ball.x_pos = paddle_rect.left - ball.radius
        ball.x_vel *= -1
    elif was_right:
        ball.x_pos = paddle_rect.right + ball.radius
        ball.x_vel *= -1
    else:
        if ball.y_vel > 0:
            ball.y_pos = paddle_rect.top - ball.radius
        else:
            ball.y_pos = paddle_rect.bottom + ball.radius
        ball.y_vel *= -1

##################################################################################################
# main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "intro" and event.type == pygame.KEYDOWN:
            game_state = "playing"

    # background
    display_surface.fill((10, 15, 40))

    if game_state == "intro":
        draw_intro(display_surface)

    elif game_state == "playing":
        # UI
        p_text = font.render(f"Money: {players_money}", True, "white")
        display_surface.blit(p_text, (20, 20))
        pygame.draw.line(
            display_surface,
            "cyan",
            (WINDOW_WIDTH - 200, 0),
            (WINDOW_WIDTH - 200, WINDOW_HEIGHT),
            5,
        )

        prev_ball_x =  game_ball.x_pos
        prev_ball_y = game_ball.y_pos

        # ball
        game_ball.move(dt)
        game_ball.draw(display_surface, "cyan")

        # brick
        if not brickDestroyed:
            pygame.draw.rect(display_surface, "hotpink", defaultBrick)

        # create ball rect for collisions
        ball_rect = pygame.Rect(
            game_ball.x_pos - game_ball.radius,
            game_ball.y_pos - game_ball.radius,
            game_ball.radius * 2,
            game_ball.radius * 2,
        )

        # PLAYER 1
        shot1 = player1Paddle.inputs(dt)
        if shot1:
            x1 = player1Paddle.rect.centerx - 2
            y1 = player1Paddle.rect.top - 12
            player1_lasers.append(
                Laser(x1, y1, length=4, width=12, color="red", speed=-600)
            )

        for laser in player1_lasers:
            laser.update(dt)
        player1_lasers = [laser for laser in player1_lasers if laser.rect.bottom > 0]
        for laser in player1_lasers:
            laser.draw(display_surface)

        player1Paddle.draw(display_surface)

        # ball–paddle 1
        resolve_ball_paddle_collision(game_ball, prev_ball_x, prev_ball_y, player1Paddle.rect)

        # paddle 1 bounds
        if player1Paddle.rect.left <= 0:
            player1Paddle.rect.left = 0
            player1Paddle.x_pos = 0
        if player1Paddle.rect.right >= WINDOW_WIDTH - 200:
            player1Paddle.rect.right = WINDOW_WIDTH - 200
            player1Paddle.x_pos = WINDOW_WIDTH - 200 - player1Paddle.rect.width

        # PLAYER 2
        shot2 = player2Paddle.inputs(dt)
        if shot2:
            x2 = player2Paddle.rect.centerx - 2
            y2 = player2Paddle.rect.top - 12
            player2_lasers.append(
                Laser(x2, y2, length=4, width=12, color="red", speed=-600)
            )

        for laser in player2_lasers:
            laser.update(dt)
        player2_lasers = [laser for laser in player2_lasers
                          if laser.rect.top < WINDOW_HEIGHT]
        for laser in player2_lasers:
            laser.draw(display_surface)

        player2Paddle.draw(display_surface)

        # ball–paddle 2
        resolve_ball_paddle_collision(game_ball, prev_ball_x, prev_ball_y, player2Paddle.rect)

        # ball bounds (circle)
        # vertical
        if game_ball.y_pos - game_ball.radius <= 0:
            game_ball.y_pos = game_ball.radius
            game_ball.y_vel *= -1
        if game_ball.y_pos + game_ball.radius >= WINDOW_HEIGHT:
            game_ball.y_pos = WINDOW_HEIGHT - game_ball.radius
            game_ball.y_vel *= -1

        # horizontal
        if game_ball.x_pos - game_ball.radius <= 0:
            game_ball.x_pos = game_ball.radius
            game_ball.x_vel *= -1
        if game_ball.x_pos + game_ball.radius >= WINDOW_WIDTH - 200:
            game_ball.x_pos = WINDOW_WIDTH - 200 - game_ball.radius
            game_ball.x_vel *= -1

        # paddle 2 bounds
        if player2Paddle.rect.left <= 0:
            player2Paddle.rect.left = 0
            player2Paddle.x_pos = 0
        if player2Paddle.rect.right >= WINDOW_WIDTH - 200:
            player2Paddle.rect.right = WINDOW_WIDTH - 200
            player2Paddle.x_pos = WINDOW_WIDTH - 200 - player2Paddle.rect.width

        # brick hit
        if ball_rect.colliderect(defaultBrick) and not brickDestroyed:
            brickDestroyed = True
            game_ball.y_vel *= -1

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()