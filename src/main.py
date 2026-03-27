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

# lasers
player1_lasers = []
player2_lasers = []

#laser cooldowns
player1_laser_cooldown = 0
player2_laser_cooldown = 0

# money
players_money = 0

##################################################################################################
#brick handling

BRICK_WIDTH = 70
BRICK_HEIGHT = 25
BRICK_COLOR = "lightgreen"

#brick patterns

LEVELS = [
#lvlzero
    ["111111","111111"],
#lvlone
    ["111010", "101010"],
#lvltwo
    ["010101", "111100"],
]

level_index = 0
bricks = []





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
def resolve_ball_to_rect_collision(ball, prev_x, prev_y, collision_rect):
    ball_rect = pygame.Rect(
            ball.x_pos - ball.radius,
            ball.y_pos - ball.radius,
            ball.radius * 2,
            ball.radius * 2,
        )
    if not collision_rect.colliderect(ball_rect):
        return
    
    prev_rect = pygame.Rect(
            prev_x - ball.radius,
            prev_y - ball.radius,
            ball.radius * 2,
            ball.radius * 2,
        )
    
    was_left = prev_rect.right <= collision_rect.left
    was_right = prev_rect.left >= collision_rect.right
    was_above= prev_rect.bottom <= collision_rect.top
    was_below = prev_rect.top >= collision_rect.bottom

    if was_above:
        ball.y_pos = collision_rect.top -ball.radius
        ball.y_vel *= -1
    elif was_below:
        ball.y_pos = collision_rect.bottom + ball.radius
        ball.y_vel *= -1
    elif was_left:
        ball.x_pos = collision_rect.left - ball.radius
        ball.x_vel *= -1
    elif was_right:
        ball.x_pos = collision_rect.right + ball.radius
        ball.x_vel *= -1
    else:
        if ball.y_vel > 0:
            ball.y_pos = collision_rect.top - ball.radius
        else:
            ball.y_pos = collision_rect.bottom + ball.radius
        ball.y_vel *= -1
##################################################################################################
def build_level(level_index):
    global bricks
    bricks = []
    layout = LEVELS[level_index %  len(LEVELS)]

    start_x = 300
    start_y = 350
    padding = 10

    level_number = level_index + 1
    health_scale = 1 + 0.5 * level_number

    for row_i, row in enumerate(layout):
        for col_i, ch in enumerate(row):
            if ch != "0":
                base = int(ch)
                max_health = int(base * health_scale)
                x = start_x + col_i * (BRICK_WIDTH + padding)
                y = start_y + row_i * (BRICK_HEIGHT + padding)
                brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color="white", max_health=max_health)
                bricks.append(brick)
##################################################################################################

build_level(level_index)
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

        # Draw brick layout
        for brick in bricks:
            brick.draw(display_surface, font)
        

        # create ball rect for collisions
        ball_rect = pygame.Rect(
            game_ball.x_pos - game_ball.radius,
            game_ball.y_pos - game_ball.radius,
            game_ball.radius * 2,
            game_ball.radius * 2,
        )

        # PLAYER 1
        shot1 = player1Paddle.inputs(dt)
        player1_laser_cooldown = max(0, player1_laser_cooldown-dt) # countdown
        if shot1 and player1_laser_cooldown == 0:
            x1 = player1Paddle.rect.centerx - 2
            y1 = player1Paddle.rect.top + 12
            player1_lasers.append(
                Laser(x1, y1, length=4, width=12, color="red", speed=+600)
            )
            player1_laser_cooldown = 1


        for laser in player1_lasers:
            laser.update(dt)
        player1_lasers = [laser for laser in player1_lasers if laser.rect.top < WINDOW_HEIGHT]
        for laser in player1_lasers:
            laser.draw(display_surface)

        player1Paddle.draw(display_surface)

        # ball–paddle 1
        resolve_ball_to_rect_collision(game_ball, prev_ball_x, prev_ball_y, player1Paddle.rect)

        # paddle 1 bounds
        if player1Paddle.rect.left <= 0:
            player1Paddle.rect.left = 0
            player1Paddle.x_pos = 0
        if player1Paddle.rect.right >= WINDOW_WIDTH - 200:
            player1Paddle.rect.right = WINDOW_WIDTH - 200
            player1Paddle.x_pos = WINDOW_WIDTH - 200 - player1Paddle.rect.width

        # PLAYER 2
        shot2 = player2Paddle.inputs(dt)
        player2_laser_cooldown = max(0, player2_laser_cooldown-dt) # countdown

        if shot2 and player2_laser_cooldown == 0:
            x2 = player2Paddle.rect.centerx - 2
            y2 = player2Paddle.rect.top - 12
            player2_lasers.append(
                Laser(x2, y2, length=4, width=12, color="red", speed=-600)
            )
            player2_laser_cooldown = 1 #cooldown, once it has been shot it has a one second cooldwon

        for laser in player2_lasers:
            laser.update(dt)
        player2_lasers = [laser for laser in player2_lasers
                          if laser.rect.top < WINDOW_HEIGHT]
        for laser in player2_lasers:
            laser.draw(display_surface)

        player2Paddle.draw(display_surface)

        # ball–paddle 2
        resolve_ball_to_rect_collision(game_ball, prev_ball_x, prev_ball_y, player2Paddle.rect)

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
        hit_bricks = []
        for brick in bricks:
            if ball_rect.colliderect(brick.rect):
                resolve_ball_to_rect_collision(game_ball, prev_ball_x, prev_ball_y, brick.rect)
                hit_bricks.append(brick)

        for brick in hit_bricks:
            brick.take_damage(game_ball.power)
            
            print(brick.is_dead())
            if brick.is_dead():
                bricks.remove(brick)
            players_money += 10

        #laser collision section
        lasers_to_remove = []
        #loops through every laser
        for laser in player1_lasers:
            for brick in bricks[:]: #copy to remove bricks safely
                if laser.rect.colliderect(brick.rect): #checks if the laser collides with the brick
                    brick.take_damage(1)
                    lasers_to_remove.append(laser)
                    if brick.is_dead():
                        bricks.remove(brick)
                        players_money += 10
                    break #one brick per laser
        player1_lasers = [l for l in player1_lasers if l not in lasers_to_remove]
        #laser collision section
        lasers_to_remove = []
        #loops through every laser
        for laser in player2_lasers:
            for brick in bricks[:]: #copy to remove bricks safely
                if laser.rect.colliderect(brick.rect): #checks if the laser collides with the brick
                    brick.take_damage(1)
                    lasers_to_remove.append(laser)
                    if brick.is_dead():
                        bricks.remove(brick)
                        players_money += 10
                    break #one brick per laser
        player2_lasers = [l for l in player2_lasers if l not in lasers_to_remove]





    
        #check end of level
        if not bricks:
            level_index += 1
            if level_index >= len(LEVELS):
                level_index = 0
            build_level(level_index)
            

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()