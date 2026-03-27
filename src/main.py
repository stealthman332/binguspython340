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

#list for extra balls from upgrades
extra_balls = []

# lasers
player1_lasers = []
player2_lasers = []

#players score
player1_score = 0
player2_score = 0

#laser cooldowns
player1_laser_cooldown = 0
player2_laser_cooldown = 0

# money
players_money = 0

#these hold the last position of the ball for every frame to know which way it came from
prev_ball_x =  game_ball.x_pos
prev_ball_y = game_ball.y_pos

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
#lvlthree DENSE
    ["010101", "111100", "211112"],
#lvlfour X
    ["100001", "020020", "112211", "020020", "100001"],
#lvlFive
    ["010101", "010101", "010101", "010101"],
#BoSS level
    ["111111", "122221", "123321", "123321", "122221", "111111"]
]

level_index = 0
level_number = 1
bricks = []

#upgrade menu
upgrades = {
    "laser_cooldown": {"label": "Laser Speed", "cost" : 50, "level" : 0, "max" : 5},
    "multi_ball": {"label": "Add Balls", "cost" : 100, "level" : 0, "max" : 5},
    "laser_damage": {"label": "Laser Damage", "cost" : 75, "level" : 0, "max" : 5}
}
upgrade_buttons = []

##################################################################################################
#draws the upgrade panel UI
def draw_upgrade_panel(surface, money, upgrades, font):
    panel_x = WINDOW_WIDTH - 195
    button_height = 60
    padding = 10
    small_font = pygame.font.SysFont(None, 25)
    title_font = pygame.font.SysFont(None, 35)
#blits and creates the title 
    title = title_font.render("UPGRADES", True, "Cyan") #creates and blits the title
    surface.blit(title, (panel_x + 10, 10))
#an array storing th ebuttons
    buttons = []
    for i, (key, upg) in enumerate(upgrades.items()) :
        y = 80 + i * (button_height + padding) #first button 80, each button is scaled downward
        rect = pygame.Rect(panel_x + 5, y, 185, button_height)

        #button color based on affordability
        if upg["level"] >= upg["max"]:
            color = (60, 60, 60) #maxed out color
        elif money >= upg["cost"]:
            color = (30, 80, 30)
        else:
            color = (80, 30, 30)
        #draws the buttons
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, "cyan", rect, 1, border_radius=6)
        #draws the labels on the buttons
        label = small_font.render(upg["label"], True, "White")
        surface.blit(label, (rect.x + 8, rect.y + 8))
        #draws the MAXED on the screen
        if upg["level"] >= upg["max"]:
            sub = small_font.render("MAXED", True, "Yellow")
        else: 
            sub = small_font.render(f"Cost: ${upg['cost']}", True, "Lightgray")
        surface.blit(sub, (rect.x +8, rect.y + 32))
        #appends the upgrades
        buttons.append((rect,key))
    
    return buttons



##################################################################################################
#draws the intro screen
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
    #creates a loop that flashes text
    if pygame.time.get_ticks() % 1000 < 500:
        subsubtitle_text = small_font.render("Press any key to start", True, "white")
        surface.blit(
            subsubtitle_text,
            (WINDOW_WIDTH // 2 - subsubtitle_text.get_width() // 2,
             WINDOW_HEIGHT // 2 + 150),
        )

##################################################################################################
#resolves the ball and rectangle collisions
def resolve_ball_to_rect_collision(ball, prev_x, prev_y, collision_rect):
    #creates the hitbox for the balls
    ball_rect = pygame.Rect(
            ball.x_pos - ball.radius,
            ball.y_pos - ball.radius,
            ball.radius * 2,
            ball.radius * 2,
        )
    if not collision_rect.colliderect(ball_rect):
        return
    #this is the prev rectangle hitbox
    prev_rect = pygame.Rect(
            prev_x - ball.radius,
            prev_y - ball.radius,
            ball.radius * 2,
            ball.radius * 2,
        )
    
    #determins if the ball came from these directions, and allows us to bounce of that side of the rectangle or paddle
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
#this builds each level, 
def build_level(level_index):
    global bricks, level_number
    bricks = []
    #error checking for the level indexing
    try:
        layout = LEVELS[level_index %  len(LEVELS)]
    except IndexError:
        print("Level index out of range. Defaulting to level one.")
        layout = LEVELS[0]
    start_x = 300
    start_y = 350
    padding = 10

    level_number = level_index + 1
    health_scale = 1 + (2 * level_number)
    #this goes through each row and column and adds a brick there depending on if there is a 0 or a 1 
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
#this draws the win screen and displays who won
def draw_win_screen(surface, score1, score2):
    big_font = pygame.font.SysFont(None, 150)
    med_font = pygame.font.SysFont(None, 50)
    small_font = pygame.font.SysFont(None, 25)

    title = big_font.render("YOU WON!", True, "Cyan")
    surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

    winner = "Player 1" if score1 > score2 else "Player 2" if score2 > score1 else "Tie"
    winner_text = med_font.render(f"{winner} Wins!" if winner != "Tie" else "It's a Tie!", True, "White")
    surface.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, 220))

    p1 = med_font.render(f"Player 1 Score: {score1}", True, "pink")
    p2 = med_font.render(f"Player 2 Score: {score2}", True, "violet")
    surface.blit(p1, (WINDOW_WIDTH // 2 - p1.get_width() // 2, 340))
    surface.blit(p2, (WINDOW_WIDTH // 2 - p2.get_width() // 2, 420))

##################################################################################################
#this applies the upgrades to the level and game loop
def apply_upgrades(key, level):
    global game_ball
    #both are handled below
    if key == "laser_cooldown":
        pass
    elif key == "laser_damage":
        pass
    elif key == "multi_ball": #spawns in new balls
        from objects import Ball
        new_ball = Ball(10, game_ball.x_pos-10, game_ball.y_pos+10, -game_ball.x_vel, -game_ball.y_vel)
        extra_balls.append(new_ball)
                
##################################################################################################

build_level(level_index)
# main game loop
while running:
    #implementation to quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            #checks to see if the user presses a button, and if so it starts the game
        if game_state == "intro" and event.type == pygame.KEYDOWN:
            game_state = "playing"
        #This checks to see if a user buys a upgrade
        if event.type == pygame.MOUSEBUTTONDOWN and event.button ==  1:
            for rect, key in upgrade_buttons:
                if rect.collidepoint(event.pos):
                    upg = upgrades[key]
                    if players_money >= upg["cost"] and upg["level"] < upg["max"]:
                        players_money -= upg["cost"]
                        upg["level"] += 1
                        upg["cost"] = int(upg["cost"] * 1.25) #scales the cost
                        apply_upgrades(key, upg["level"])

    # background
    display_surface.fill((10, 15, 40))
    #This displays if the game state is in the intro
    if game_state == "intro":
        draw_intro(display_surface)
    #handles if the game state is "Win"
    elif game_state == "win":
        draw_win_screen(display_surface, player1_score, player2_score)
    #the rest of the code is for the playing game state
    elif game_state == "playing":
        # UI
        p1_text = font.render("Money:", True, "white")
        p2_text = font.render(f"${players_money}", True, "White")
        display_surface.blit(p1_text, (WINDOW_WIDTH-160, WINDOW_HEIGHT-250))
        display_surface.blit(p2_text, (WINDOW_WIDTH-130, WINDOW_HEIGHT-200))
        pygame.draw.line(
            display_surface,
            "cyan",
            (WINDOW_WIDTH - 200, 0),
            (WINDOW_WIDTH - 200, WINDOW_HEIGHT),
            5,
        )

        #display level infor
        font = pygame.font.SysFont(None, 55)
        level_text = font.render(f"LEVEL: {level_number}", True, "White")
        display_surface.blit(level_text, (20, 20))

        #sets the previous ball to the position of the game ball
        prev_ball_x =  game_ball.x_pos
        prev_ball_y = game_ball.y_pos


        # ball
        game_ball.move(dt)
        game_ball.draw(display_surface, "cyan")

        #adds extra balls
        for ball in extra_balls:
            ball.move(dt)
            ball.draw(display_surface, "cyan")

            #bounds checking for extra balls
            if ball.y_pos - ball.radius <= 0:
                ball.y_pos = ball.radius
                ball.y_vel *= -1
            if ball.y_pos + ball.radius >= WINDOW_HEIGHT:
                ball.y_pos = WINDOW_HEIGHT - ball.radius
                ball.y_vel *= -1

            # horizontal
            if ball.x_pos - ball.radius <= 0:
                ball.x_pos = ball.radius
                ball.x_vel *= -1
            if ball.x_pos + ball.radius >= WINDOW_WIDTH - 200:
                ball.x_pos = WINDOW_WIDTH - 200 - ball.radius
                ball.x_vel *= -1
            #this resolves the hitboxes and collision of the balls
            resolve_ball_to_rect_collision(ball, prev_ball_x, prev_ball_y, player2Paddle.rect)
            resolve_ball_to_rect_collision(ball, prev_ball_x, prev_ball_y, player2Paddle.rect)
            #loops through the brick and checks to see if the new spawned in balls collided with rectangles, and if so adds money
            for brick in bricks[:]:
                extra_ball_rect = pygame.Rect(
                    ball.x_pos - ball.radius, ball.y_pos - ball.radius, ball.radius * 2, ball.radius * 2
                )
                if extra_ball_rect.colliderect(brick.rect):
                    resolve_ball_to_rect_collision(ball, ball.x_pos, ball.y_pos, brick.rect)
                    brick.take_damage(game_ball.power)
                    if brick.is_dead():
                        bricks.remove(brick)
                        players_money += 10

        # Draw brick layout
        for brick in bricks:
            brick.draw(display_surface, font)

        #draw upgarde menu UI
        upgrade_buttons = draw_upgrade_panel(display_surface, players_money, upgrades, font)
        

        # create ball rect for collisions
        ball_rect = pygame.Rect(
            game_ball.x_pos - game_ball.radius,
            game_ball.y_pos - game_ball.radius,
            game_ball.radius * 2,
            game_ball.radius * 2,
        )



        # PLAYER 1 #######################################################################
        #implements the upgardes
        base_cooldown = 1
        laser_cooldown_time = max(.1, base_cooldown- upgrades["laser_cooldown"]["level"] * .25)
        laser_dmg = 1 + upgrades["laser_damage"]["level"]

        #handles the shooting of the laser
        shot1 = player1Paddle.inputs(dt)
        player1_laser_cooldown = max(0, player1_laser_cooldown-dt) # countdown
        if shot1 and player1_laser_cooldown == 0:
            x1 = player1Paddle.rect.centerx - 2
            y1 = player1Paddle.rect.top + 12
            player1_lasers.append(
                Laser(x1, y1, length=4, width=12, color="red", speed=+600)
            )
            player1_laser_cooldown = laser_cooldown_time

        #iterates through the laser array, and updates them, and despawns them when they go off the screen, and draws the lasers to the surface
        for laser in player1_lasers:
            laser.update(dt)
        player1_lasers = [laser for laser in player1_lasers if laser.rect.top < WINDOW_HEIGHT]
        for laser in player1_lasers:
            laser.draw(display_surface)


        #draws player 1s paddle to the surface
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

        # PLAYER 2 ########################################################################################
        shot2 = player2Paddle.inputs(dt)
        player2_laser_cooldown = max(0, player2_laser_cooldown-dt) # countdown

        #laser shooting implementation
        if shot2 and player2_laser_cooldown == 0:
            x2 = player2Paddle.rect.centerx - 2
            y2 = player2Paddle.rect.top - 12
            player2_lasers.append(
                Laser(x2, y2, length=4, width=12, color="red", speed=-600)
            )
            player2_laser_cooldown = laser_cooldown_time #cooldown, once it has been shot it has a one second cooldwon
        #handles the updating of the lasers, the despawning and draws the lasers
        for laser in player2_lasers:
            laser.update(dt)
        player2_lasers = [laser for laser in player2_lasers
                          if laser.rect.top < WINDOW_HEIGHT]
        for laser in player2_lasers:
            laser.draw(display_surface)


        #draws player 2s paddle
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

        #goes throught the hit_bricks array and makes them take damager
        for brick in hit_bricks:
            brick.take_damage(game_ball.power)
            #code for when a brick dies, removing it, adding money to the players
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
                    brick.take_damage(laser_dmg)
                    lasers_to_remove.append(laser)
                    if brick.is_dead():
                        bricks.remove(brick)
                        players_money += 10
                        player1_score += 1 #if laser from player 1 collides with a brick then player 1 gets a point
                    break #one brick per laser
        player1_lasers = [l for l in player1_lasers if l not in lasers_to_remove]
        #laser collision section
        lasers_to_remove = []
        #loops through every laser
        for laser in player2_lasers:
            for brick in bricks[:]: #copy to remove bricks safely
                if laser.rect.colliderect(brick.rect): #checks if the laser collides with the brick
                    brick.take_damage(laser_dmg)
                    lasers_to_remove.append(laser)
                    if brick.is_dead():
                        bricks.remove(brick)
                        players_money += 10
                        player2_score += 1
                    break #one brick per laser
        player2_lasers = [l for l in player2_lasers if l not in lasers_to_remove]

        #check end of level
        if not bricks:
            level_index += 1
            if level_index >= len(LEVELS):
                game_state = "win"
            else:
                build_level(level_index)
            
    #displays all of this code every frame
    pygame.display.flip()
    dt = clock.tick(60) / 1000

#quits pygame
pygame.quit()