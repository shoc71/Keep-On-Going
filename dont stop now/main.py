import random
import pygame
import dsn_levels as dsnlevel


class Program:

    def __init__(self) -> None:
        self.running = True

    def run(self, width, height, current_scene, current_music):
        """
        self.scene = self.scene.this_scene updates the scene. If the scene is
        changed, then this line will update it accordingly.
        """
        screen = pygame.display.set_mode([width, height])
        scene = current_scene
        music = current_music
        while self.running:
            keys_pressed = []
            keys_held = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Quit condition if you press the X on the top right
                    self.running = False
                    scene.run_scene = False
                if event.type == pygame.KEYDOWN:
                    keys_pressed.append(event.key)

            if not scene.run_scene:
                # Stop the game using other conditions
                scene.close_game()
                self.running = False
            else:
                scene.input(keys_pressed, keys_held)
                scene.update()
                scene.render(screen)
                scene = scene.this_scene

            fps.tick(500)
            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    fps = pygame.time.Clock()
    start_music = Music()
    start_game = Program()
    start_scene = MenuScene(40, 460)
    start_game.run(1080, 576, start_scene, start_music)
    pygame.quit()
