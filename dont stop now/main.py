import pygame


# todo: move text class to it's own py file
class Text:
    def __init__(self, text, text_pos, font_size, font_type,
                 font_color, text_other):

        self.text = text
        self.position = text_pos
        self.font_size = font_size
        self.font_type = font_type
        self.color = font_color

        self.other = text_other
        self.font = None
        self.text_rect = None
        self.text_img = None

        self.setup()
        self.render()

    def setup(self):
        self.font = pygame.font.SysFont(self.font_type, self.font_size)

    def render(self):
        self.text_img = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_img.get_rect()
        self.text_rect.center = self.position


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
                self.change_scene(TutorialLevel1(40, 300))

    def update(self):
        pass

    def render(self, screen):
        screen.fill((181, 60, 177))


class LevelScene(Scene):

    def __init__(self, x_spawn, y_spawn):
        """
        Set the current scene to this scene by passing this classes self to
        initialize it.
        """
        Scene.__init__(self)
        self.platforms = []
        self.walls = []
        self.death_zones = []
        self.win_zones = []

        self.x_spawn = x_spawn
        self.y_spawn = y_spawn
        self.player = SquareMe(self.x_spawn, self.y_spawn,
                               10, 10, (181, 60, 177))
        self.respawns = -1
        self.play_time = 0
        self.level_condition = False
        self.victory_time = 0
        self.victory_counter = 0
        self.victory_text = [
            Text("DON'T", (310, 100), 100, "impact", (235, 195, 65), None),
            Text("STOP", (570, 100), 100, "impact", (235, 195, 65), None),
            Text("NOW", (820, 100), 100, "impact", (235, 195, 65), None)
        ]

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_c:
                self.change_scene(MenuScene())
            if every_key in [pygame.K_w, pygame.KEYUP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive:
                self.player.jump_ability = True
                self.player.jump_boost = self.player.max_jump
            if every_key == pygame.K_SPACE and not self.player.alive:
                self.respawns += 1
                self.player.alive = True
            if every_key == pygame.K_ESCAPE:
                self.player.freeze = not self.player.freeze

    def update(self):
        if self.player.alive and not self.player.freeze and 0 <= self.respawns\
                and not self.level_condition:
            self.player.death(self.death_zones)
            self.player.collision_plat(self.platforms)
            self.player.collision_wall(self.walls)
            self.player.move()
        if not self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.player.xpos = self.x_spawn
            self.player.ypos = self.y_spawn
            self.player.direction = "right"

        if 580 + self.player.height < self.player.ypos:
            self.player.alive = False

        if self.player.alive and \
                self.player.square_render.collidelist(self.win_zones) != -1:
            self.level_condition = True
            self.player.alive = False

    def victory(self, screen):
        if 500 <= pygame.time.get_ticks() - self.victory_time and \
                self.victory_counter < 3:
            self.victory_time = pygame.time.get_ticks()
            self.victory_counter += 1
        for x in range(self.victory_counter):
            screen.blit(self.victory_text[x].text_img,
                        self.victory_text[x].text_rect)

    def render(self, screen):
        screen.fill((255, 255, 255))
        self.player.render(screen)

        if self.level_condition:
            self.victory(screen)
        else:
            self.play_time = pygame.time.get_ticks()
            self.victory_time = pygame.time.get_ticks()


class TutorialLevel1(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - self.victory_time:
            self.change_scene(TutorialLevel2(40, 540))

    def render(self, screen):
        LevelScene.render(self, screen)

        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, (47, 237, 237), [1070, 278, 20, 40])
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, (0, 0, 0), [0, 310, 1100, 10])
        platform2 = pygame.draw.rect(screen, (0, 0, 0), [350, 290, 300, 30])
        self.platforms = [platform1, platform2]

        wall1 = pygame.draw.rect(screen, (0, 0, 0), [1070, 0, 10, 278])
        wall2 = pygame.draw.rect(screen, (0, 0, 0), [350, 290, 10, 30])
        wall3 = pygame.draw.rect(screen, (0, 0, 0), [640, 290, 10, 30])
        wall4 = pygame.draw.rect(screen, (0, 0, 0), [0, 0, 10, 320])
        self.walls = [wall1, wall2, wall3, wall4]


class TutorialLevel2(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - self.victory_time:
            self.change_scene(TutorialLevel3(0, 300))

    def render(self, screen):
        LevelScene.render(self, screen)

        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, (47, 237, 237), [650, 546, 10, 20])
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, (0, 0, 0), [0, 566, 1100, 10])
        platform2 = pygame.draw.rect(screen, (0, 0, 0), [0, 446, 406, 10])
        platform3 = pygame.draw.rect(screen, (0, 0, 0), [510, 536, 90, 10])
        platform4 = pygame.draw.rect(screen, (0, 0, 0), [380, 506, 90, 10])
        platform5 = pygame.draw.rect(screen, (0, 0, 0), [510, 476, 90, 10])
        platform6 = pygame.draw.rect(screen, (0, 0, 0), [380, 446, 90, 10])
        platform7 = pygame.draw.rect(screen, (0, 0, 0), [510, 416, 90, 10])
        platform8 = pygame.draw.rect(screen, (0, 0, 0), [380, 386, 90, 10])
        platform9 = pygame.draw.rect(screen, (0, 0, 0), [510, 356, 90, 10])
        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6, platform7, platform8,
                          platform9]

        wall1 = pygame.draw.rect(screen, (0, 0, 0), [600, 356, 10, 220])
        wall2 = pygame.draw.rect(screen, (0, 0, 0), [380, 0, 10, 516])
        wall3 = pygame.draw.rect(screen, (0, 0, 0), [650, 0, 10, 546])
        wall4 = pygame.draw.rect(screen, (0, 0, 0), [0, 0, 10, 576])
        self.walls = [wall1, wall2, wall3, wall4, platform3, platform4,
                      platform5, platform6, platform7, platform8,
                      platform9]


class TutorialLevel3(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

    def render(self, screen):
        LevelScene.render(self, screen)

        death1 = pygame.draw.rect(screen, (194, 57, 33), [0, 550, 1080, 30])
        self.death_zones = [death1]

        win1 = pygame.draw.rect(screen, (47, 237, 237), [1060, 275, 20, 40])
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, (0, 0, 0), [0, 310, 200, 10])
        platform2 = pygame.draw.rect(screen, (0, 0, 0), [200, 360, 200, 10])
        platform3 = pygame.draw.rect(screen, (0, 0, 0), [500, 360, 150, 10])
        platform4 = pygame.draw.rect(screen, (0, 0, 0), [700, 335, 330, 10])
        self.platforms = [platform1, platform2, platform3, platform4]

        wall1 = pygame.draw.rect(screen, (0, 0, 0), [1070, 0, 10, 278])
        wall2 = pygame.draw.rect(screen, (0, 0, 0), [1070, 308, 10, 288])
        self.walls = [wall1, wall2]


class SquareMe:

    def __init__(self, x_spawn, y_spawn, width, height, rgb):
        """
        self.square parameters: [
        [x_spawn, y_spawn],
        [width, height]
        [RGB value],
        ]
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
        self.max_jump = 130
        self.jump_boost = -1 * (self.max_jump - 1)
        self.direction = "right"
        self.gravity_counter = 50

    def move(self):
        if self.direction == "right":
            self.xpos += 0.5
        elif self.direction == "left":
            self.xpos -= 0.5

        self.gravity()
        self.jump()

    def jump(self):
        if self.jump_ability and 0 <= self.jump_boost:
            self.ypos -= (self.jump_boost ** 2) * 0.00005
            self.jump_boost -= 1
        else:
            self.jump_ability = False

    def render(self, screen):
        self.square_render = pygame.draw.rect(screen, self.color, [self.xpos,
                                                                   self.ypos,
                                                                   self.width,
                                                                   self.height])

    def collision_plat(self, object_list: [pygame.Rect]):
        if len(object_list) < 1:
            return None

        collide_id = self.square_render.collidelist(object_list)
        collide_x = object_list[collide_id].x
        collide_y = object_list[collide_id].y
        collide_width = object_list[collide_id].width
        # collide_height = object_list[collide_id].height

        if collide_id != -1 and \
                collide_x - self.width - collide_width < self.xpos and \
                self.xpos + self.width < \
                collide_x + collide_width + self.width and \
                collide_y < self.ypos + self.height:
            self.enable_gravity = False
            self.jump_ability = True
            self.gravity_counter = 50
        else:
            self.enable_gravity = True

    def collision_wall(self, object_list: [pygame.Rect]):
        if len(object_list) < 1:
            return None

        collide_id = self.square_render.collidelist(object_list)
        collide_x = object_list[collide_id].x
        collide_y = object_list[collide_id].y
        collide_width = object_list[collide_id].width
        # collide_height = object_list[collide_id].height

        if collide_id != -1 and \
                (collide_y + 2 < self.ypos + self.height) and \
                self.direction == "right" and \
                self.xpos + self.width <= collide_x + 1:
            self.direction = "left"
        if collide_id != -1 and \
                (collide_y + 2 < self.ypos + self.height - 1) and \
                self.direction == "left" and \
                collide_x + collide_width - 1 < self.xpos:
            self.direction = "right"

    def gravity(self):
        if self.enable_gravity and not self.jump_ability:
            self.ypos += (self.gravity_counter ** 2) * 0.000005

        if self.gravity_counter < 600:
            self.gravity_counter += 1

    def death(self, death_list: [pygame.Rect]):
        if len(death_list) < 1:
            return None
        collide_id = self.square_render.collidelist(death_list)
        if collide_id != -1:
            self.alive = False


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
