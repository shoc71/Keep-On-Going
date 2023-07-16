import pygame
import dsn_levels as dsnlevel
import dsn_class as dsnclass


class Program:

    def __init__(self) -> None:
        self.running = True
        self.memory = dsnclass.Memory()
        self.memory.load_levels("levels.txt")
        self.current_level = 0

    def run(self, width, height, current_scene):
        """
        self.scene = self.scene.this_scene updates the scene. If the scene is
        changed, then this line will update it accordingly.
        """
        screen = pygame.display.set_mode([width, height])
        scene = current_scene
        while self.running:
            keys_pressed = []
            keys_held = pygame.key.get_pressed()
            for event in pygame.event.get():
                # Quit condition if you press the X on the top right
                if event.type == pygame.QUIT:
                    self.running = False
                    scene.run_scene = False
                if event.type == pygame.KEYDOWN:
                    keys_pressed.append(event.key)

            # Stop the game using other conditions
            if self.running and not scene.run_scene:
                self.running = False
                scene.close_game()
            else:
                # Check for a valid level, then if level done, record data
                if (0 < scene.level_id and 3 <= scene.victory_counter and
                        500 <= pygame.time.get_ticks() - scene.victory_time):
                    # Update level memory or menu memory
                    self.memory.update_mem(scene.level_id, scene.deaths,
                                           scene.player.jumps)
                    scene.level_id += 1
                elif scene.level_id == 0 and 3 <= scene.victory_counter:
                    self.memory.update_mem(scene.level_id, scene.deaths,
                                           scene.player.jumps)

                scene.input(keys_pressed, keys_held)
                scene.update()
                scene.render(screen)
                scene = scene.this_scene

            fps.tick(120)
            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    fps = pygame.time.Clock()
    start_game = Program()
    start_scene = dsnlevel.MenuScene(40, 360, 0, start_game.memory.level_set,
                                     start_game.memory.ls_elements)
    start_game.run(1080, 576, start_scene)
    pygame.quit()
