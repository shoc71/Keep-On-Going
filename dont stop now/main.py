import pygame


class Scene:
    def __init__(self):
        """
        self.this_scene will tell the current scene it's on at that moment.
        Currently, it's set to itself, which means the
        current scene is this one.
        """
        self.this_scene = self
        self.run_scene = True

    def input(self, pressed, held):
        # this will be overridden in subclasses
        pass

    def update(self):
        # this will be overridden in subclasses
        pass

    def render(self, screen):
        # this will be overridden in subclasses
        pass

    def change_scene(self, next_scene):
        """
        This function is used in the main pygame loop
        """
        self.this_scene = next_scene

    def close_game(self):
        """
        Set the current scene to nothing and is used to stop the game.
        """
        self.change_scene(None)


class MenuScene(Scene):

    def __init__(self):
        """
        Set the current scene to this scene by passing this classes self to
        initialize it.
        """
        Scene.__init__(self)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_w:
                self.change_scene(LevelScene())

    def update(self):
        pass

    def render(self, screen):
        screen.fill((181, 60, 177))


class LevelScene(Scene):

    def __init__(self):
        """
        Set the current scene to this scene by passing this classes self to
        initialize it.
        """
        Scene.__init__(self)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_w:
                self.change_scene(MenuScene())

    def update(self):
        pass

    def render(self, screen):
        screen.fill((255, 255, 255))


class Program:

    def __init__(self) -> None:
        self.running = True
        
    def run(self, width, height, current_scene):
        """
        self.scene = self.scene.this_scene updates the scene. If the scene is
        changed, then this line will update it accordingly.
        """
        pygame.init()
        screen = pygame.display.set_mode([width, height])
        scene = current_scene
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

            pygame.display.update()


if __name__ == "__main__":
    start_game = Program()
    start_scene = MenuScene()
    start_game.run(640, 480, start_scene)
    pygame.quit()
