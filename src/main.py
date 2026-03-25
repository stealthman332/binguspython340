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
game_state = "intro" #only other one is "playing"

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
        pygame.draw.circle(surface, color, (int(self.x_pos), int(self.y_pos)), self.radius)
    
    def move(self): 
        self.x_pos += self.x_vel * dt
        self.y_pos += self.y_vel * dt


class Paddle:
    def __init__(self, x_pos, y_pos, length, width, color,
                 controls, x_vel=0, y_vel=0, speed=5):
        self.rect = pygame.Rect(x_pos, y_pos, length, width)
        self.color = color
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.x_pos = float(x_pos)
        self.y_pos = float(y_pos)
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
player1Paddle = Paddle(450, 100, 100, 25, "cyan", player1_controls, speed=300)
player2Paddle = Paddle(450, WINDOW_HEIGHT-100, 100, 25, "violet", player2_controls, speed=300)

# ball 
game_ball = Ball(10, WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 200, 200)

# if you want to actually use the Brick class:
# brick = Brick(300, 600, 20, 10, "darkred", max_health=1)
defaultBrick = pygame.Rect(300, 600, 20, 10)



# scores (typo fixed)
players_money = 0


brickDestroyed = False

# font for scores from message2
font = pygame.font.SysFont(None, 55)

##################################################################################################

# main game loop, runs every frame
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    #if the "intro is going and they press any key it turns ot playing"
    if game_state == "intro" and event.type == pygame.KEYDOWN:
        game_state = "playing"

    #draws the background
    display_surface.fill((10, 15, 40))

    #displays the intro
    if game_state == "intro" :
        #creates the font variables
        big_font = pygame.font.SysFont(None, 150)
        med_font = pygame.font.SysFont(None, 50)
        small_font = pygame.font.SysFont(None, 25)

        title_text = big_font.render("Brick Break", True, "Cyan")
        display_surface.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2-200))

        subtitle_text = med_font.render("Cyberpunk Edition", True, "violet")
        display_surface.blit(subtitle_text, (WINDOW_WIDTH//2 - subtitle_text.get_width()//2, WINDOW_HEIGHT//2))

        #flashing "press any key" title
        if pygame.time.get_ticks() % 1000 < 500:
            subsubtitle_text = small_font.render("Press any key to start", True, "white")
            display_surface.blit(subsubtitle_text, (WINDOW_WIDTH//2 - subsubtitle_text.get_width()//2, WINDOW_HEIGHT//2+150))


    elif(game_state == "playing"):
        #draws UI
        p_text = font.render(f"Money: {players_money}", True, "white")
        display_surface.blit(p_text, (20, 20))
        pygame.draw.line(display_surface, "cyan", (WINDOW_WIDTH-200, 0), (WINDOW_WIDTH-200, WINDOW_HEIGHT), 5)


        # draw ball
        game_ball.draw_ball(display_surface, "cyan")

        #moves the ball
        game_ball.move()

        # draw brick if not destroyed
        if not brickDestroyed:
            pygame.draw.rect(display_surface, "hotpink", defaultBrick)




        # PLAYER 1 ####################################################################################
        player1Paddle.inputs()


        #draws the paddle
        pygame.draw.rect(display_surface, "cyan", player1Paddle.rect)

        #temp rectangle to do the ball collision
        ball_rect = pygame.Rect(game_ball.x_pos - game_ball.radius, game_ball.y_pos - game_ball.radius, game_ball.radius * 2, game_ball.radius * 2)

        # collision with ball
        if player1Paddle.rect.colliderect(ball_rect):
            game_ball.y_vel *= -1


        # stop going off-screen
        if player1Paddle.rect.left <= 0:
            player1Paddle.rect.left = 0
            player1Paddle.x_pos = 0

        if player1Paddle.rect.right >= WINDOW_WIDTH-200:
            player1Paddle.rect.right = WINDOW_WIDTH-200
            player1Paddle.x_pos = WINDOW_WIDTH-200-player1Paddle.rect.width

            

        # PLAYER 2 ######################################################################################
        player2Paddle.inputs()


        #draws the 2nd player paddle 
        pygame.draw.rect(display_surface, "purple", player2Paddle.rect)




        if player2Paddle.rect.colliderect(ball_rect):
            game_ball.y_vel *= -1


        # ball bounds
        if game_ball.y_pos - game_ball.radius <= 0:
            game_ball.y_pos = game_ball.radius
            game_ball.y_vel *= -1
        if game_ball.y_pos + game_ball.radius >= WINDOW_HEIGHT:
            game_ball.y_pos = WINDOW_HEIGHT - game_ball.radius
            game_ball.y_vel *= -1

        if game_ball.x_pos - game_ball.radius <= 0:
            game_ball.x_pos = game_ball.radius
            game_ball.x_vel *= -1
        if game_ball.x_pos + game_ball.radius >= WINDOW_WIDTH - 200:
            game_ball.x_pos = WINDOW_WIDTH - 200 - game_ball.radius
            game_ball.x_vel *= -1



        # PLAYER 2 bounds
        if player2Paddle.rect.left <= 0:
            player2Paddle.rect.left = 0
            player2Paddle.x_pos = 0
        if player2Paddle.rect.right >= WINDOW_WIDTH-200:
            player2Paddle.rect.right = WINDOW_WIDTH-200
            player2Paddle.x_pos = WINDOW_WIDTH-200-player2Paddle.rect.width
        
        # brick hit
        if ball_rect.colliderect(defaultBrick) and not brickDestroyed:
            brickDestroyed = True
            game_ball.y_vel *= -1
            # if using Brick object, call take_damage here

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()