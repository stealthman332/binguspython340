import pygame

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
pygame.display.set_caption("Brick Break - Multiplayer")
player_pos = pygame.Vector2(display_surface.get_width() / 2, display_surface.get_height() / 2)


#################################################################################################
ballXVelocity,ballYVelocity=0,0

playerPaddle = pygame.Rect(450,100,100,25)
defaultBall = pygame.Rect(500,500,25,25)
defaultBrick = pygame.Rect(300,600,20,10)
player_pos.x = 560
player_pos.y = 680
ballXVelocity = 2.5
ballYVelocity = 2.5
brickDestroyed = False
##################################################################################################

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  display_surface.fill("black")

  pygame.draw.rect(display_surface, "white", playerPaddle)
  pygame.draw.rect(display_surface, "red", defaultBall)
  if brickDestroyed == False:
    pygame.draw.rect(display_surface, "darkred", defaultBrick)

  defaultBall.x += ballXVelocity
  defaultBall.y += ballYVelocity


  playerPaddle.x = player_pos.x
  playerPaddle.y = player_pos.y

  #pygame.draw.rect(display_surface, "red", (30, 30, 30, 30))
  
  keys=pygame.key.get_pressed()
  if keys[pygame.K_w]:
    player_pos.y -= 300 * dt
  if keys[pygame.K_a]:
    player_pos.x -= 300 * dt
  if keys[pygame.K_s]:
    player_pos.y += 300 * dt
  if keys[pygame.K_d]:
    player_pos.x += 300 * dt

  
  if playerPaddle.colliderect(defaultBall):
    ballYVelocity *= -1

  if defaultBall.top <= 0 or defaultBall.bottom >= WINDOW_HEIGHT:
    ballYVelocity *= -1

  if defaultBall.left <= 0 or defaultBall.right >= WINDOW_WIDTH:
    ballXVelocity *= -1


  if defaultBall.colliderect(defaultBrick):
    brickDestroyed = True
    ballYVelocity *= -1
  
  pygame.display.flip()

  dt = clock.tick(60) / 1000

  

pygame.quit()