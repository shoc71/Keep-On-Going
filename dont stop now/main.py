import pygame
pygame.init()

class Program:

    def __init__(self) -> None:
        self.running = True
        pass
    
    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    pass
                elif event.key == pygame.K_LEFT:
                    pass
                elif event.key == pygame.K_DOWN:
                    pass
                elif event.key == pygame.K_UP:
                    pass

    def update(self):
        pass

    def render(self):

        pygame.display.update()

    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
        pass

program = Program()
if __name__ == "__main__":
    program.run()
