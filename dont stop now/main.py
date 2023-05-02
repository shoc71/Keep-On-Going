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
            if every_key == pygame.K_c:
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
        self.platforms = []
        self.walls = []
        self.death_zones = []
        self.win_zones = None

        self.player = SquareMe(0, 250, 20, 20, (181, 60, 177))

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_c:
                self.change_scene(MenuScene())
            if every_key in [pygame.K_w, pygame.KEYUP, pygame.K_SPACE] and not self.player.enable_gravity:
                print("jump")
                self.player.jump_ability = True
                self.player.jump_boost = self.player.max_jump

    def update(self):
        if self.player.alive:
            self.player.collision(self.platforms + self.walls)
            self.player.move()

    def render(self, screen):
        screen.fill((255, 255, 255))
        platform1 = pygame.draw.rect(screen, (0, 0, 0), [0, 300, 200, 15])
        platform2 = pygame.draw.rect(screen, (0, 0, 0), [200, 350, 200, 15])
        platform3 = pygame.draw.rect(screen, (0, 0, 0), [500, 350, 150, 15])
        platform4 = pygame.draw.rect(screen, (0, 0, 0), [700, 325, 350, 15])
        self.platforms = [platform1, platform2, platform3, platform4]

        wall1 = pygame.draw.rect(screen, (0, 0, 0), [1065, 0, 15, 258])
        wall2 = pygame.draw.rect(screen, (0, 0, 0), [1065, 298, 15, 288])
        self.walls = [wall1, wall2]

        self.death_zones = []

        self.player.render(screen)
        self.player.alive = True


class SquareMe:

    def __init__(self, x_spawn, y_spawn, width, height, rgb):
        """
        """
        self.xpos = x_spawn
        self.ypos = y_spawn
        self.width = width
        self.height = height
        self.color = rgb
        self.square_render = None
        self.alive = False
        self.freeze = False

        self.jump_ability = False
        self.enable_gravity = True
        self.max_jump = 200
        self.jump_boost = -self.max_jump - 1
        self.direction = "right"
        self.collide = False
        self.fall_time = 0

    def move(self):
        if self.freeze:
            pass

        if self.direction == "right":
            self.xpos += 0.25
        elif self.direction == "left":
            self.xpos -= 0.25

        self.gravity()
        self.jump()

    def jump(self):
        if self.jump_ability and 0 <= self.jump_boost:
            self.ypos -= (self.jump_boost * abs(self.jump_boost)) * 0.00005
            self.jump_boost -= 1
        else:
            self.jump_ability = False

    def render(self, screen):
        self.square_render = pygame.draw.rect(screen, self.color, [self.xpos,
                                                                   self.ypos,
                                                                   self.width,
                                                                   self.height])

    def collision(self, object_list: [pygame.Rect]):
        collide_id = self.square_render.collidelist(object_list)
        collide_x = object_list[collide_id].x
        collide_y = object_list[collide_id].y
        collide_width = object_list[collide_id].width
        collide_height = object_list[collide_id].height

        self.collide = True
        if self.collide and collide_id != -1 and \
                (collide_y < self.ypos + self.height - 1) and \
                self.direction == "right" and self.xpos < collide_x:
            self.direction = "left"
            self.collide = False
            print("swtich")
        if self.collide and collide_id != -1 and \
                (collide_y < self.ypos + self.height - 1) and \
                self.direction == "left" and collide_x + collide_width - 1 < self.xpos:
            self.direction = "right"
            self.collide = False

        if collide_id != -1 and \
                collide_x - self.width - collide_width < self.xpos and \
                self.xpos + self.width < \
                collide_x + collide_width + self.width and \
                collide_y < self.ypos + self.height:
            self.enable_gravity = False
            self.jump_ability = True
            self.fall_time = pygame.time.get_ticks()
        else:
            self.enable_gravity = True
        """if collide_y + 1 < self.ypos + self.height and collide_x < (self.xpos + self.height / 6) < collide_x + collide_width:
            self.ypos = collide_y - self.height"""


    def gravity(self):
        if self.enable_gravity and not self.jump_ability and self.collide:
            self.ypos += 0.0009 * (pygame.time.get_ticks() - self.fall_time)


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
    start_game.run(1080, 576, start_scene)
    pygame.quit()
