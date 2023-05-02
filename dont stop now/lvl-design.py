# Importing the library
import pygame

# Initializing Pygame
pygame.init()

# Initializing surface

screen = pygame.display.set_mode()
x,y = screen.get_size()
print(x,y)

# Initializing Color
white = (255,255,255)
purple = (255,0,255)
black = (0,0,0)
cyan = (0,255,255)

# Drawing Rectangle
# pygame.draw.rect(screen, color, pygame.Rect(30, 30, 60, 60))
# pygame.display.update()

running = True

while running:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    pass
                elif event.key == pygame.K_LEFT:
                    pass
                elif event.key == pygame.K_DOWN:
                    pass
                elif event.key == pygame.K_UP:
                    pass
    
    screen.fill(white)

    pygame.draw.rect(screen, purple, pygame.Rect(100, 100, 15, 15))# player
    pygame.draw.rect(screen, black, pygame.Rect(80, 190, 220, 20))# spawn platform
    pygame.draw.rect(screen, black, pygame.Rect(380, 590, 220, 20))# platform 1
    pygame.draw.rect(screen, black, pygame.Rect(670, 240, 510, 20))# platform 2

    pygame.draw.rect(screen, black, pygame.Rect(x-25, -5, 30, 220))# ending platform 1
    pygame.draw.rect(screen, black, pygame.Rect(x-25, y//2 - 15, 30, y))# ending platform 2
    pygame.draw.rect(screen, cyan, pygame.Rect(x-15, 215, 30, 130))# win condition
    pygame.display.update()

pygame.quit()