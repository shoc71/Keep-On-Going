import random
import pygame
import dsn_class as dsnclass

DARK_RED = (139, 0, 0)
YELLOW = (235, 195, 65)
BLACK = (0, 0, 0)
CYAN = (47, 237, 237)
RED = (194, 57, 33)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)


class LevelScene(dsnclass.Scene):
    def __init__(self, x_spawn, y_spawn):
        """
        Set the current scene to this scene by passing this classes self to
        initialize it.
        """
        dsnclass.Scene.__init__(self)
        self.platforms = []
        self.walls = []
        self.death_zones = []
        self.win_zones = []

        self.x_spawn = x_spawn
        self.y_spawn = y_spawn
        self.player = dsnclass.SquareMe(self.x_spawn, self.y_spawn,
                               10, 10, (181, 60, 177))
        self.respawns = -1
        self.play_time = 0
        self.level_condition = False
        self.victory_time = 0
        self.victory_counter = 0
        self.victory_text = [
            dsnclass.Text("DON'T", (310, 100), 100, "impact", YELLOW, None),
            dsnclass.Text("STOP", (570, 100), 100, "impact", YELLOW, None),
            dsnclass.Text("NOW", (820, 100), 100, "impact", YELLOW, None)
        ]
        self.pause_text = dsnclass.Text("PAUSED", (540, 213),
                               100, "impact", DARK_RED, None)
        self.pause_text_2 = dsnclass.Text("Press esc to unpause", (540, 280),
                               30, "impact", DARK_RED, None)
        self.pause_text_3 = dsnclass.Text("Press q to quit", (540, 315),
                               30, "impact", DARK_RED, None)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_c:
                self.change_scene(MenuScene(40, 340, 0))
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive:
                self.player.jump_ability = True
                self.player.jump_boost = self.player.max_jump
                self.player.jump_sound_1.play()
            if (every_key == pygame.K_SPACE or every_key == pygame.K_w) \
                    and not self.player.alive:
                self.respawns += 1
                self.player.alive = True
            if every_key == pygame.K_ESCAPE:
                self.player.freeze = not self.player.freeze
            if (every_key == pygame.K_q) and self.player.freeze:
                self.close_game()

    def update(self):
        if self.player.alive and not self.player.freeze and 0 <= self.respawns\
                and not self.level_condition:
            self.player.death(self.death_zones)
            self.player.collision_plat(self.platforms)
            self.player.collision_wall(self.platforms + self.walls)
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
        screen.fill(WHITE)
        self.player.render(screen)

    def render_level(self, screen):
        """ This function will be altered in the child class (the individual
        levels)"""
        pass

    def render_text(self, screen):
        """ This function will be altered in the child class (the individual
        levels)"""
        if self.player.freeze:
            screen.blit(self.pause_text.text_img, self.pause_text.text_rect)# big bold for pausing
            screen.blit(self.pause_text_2.text_img, self.pause_text_2.text_rect)# instructions to unpause
            screen.blit(self.pause_text_3.text_img, self.pause_text_3.text_rect)# drawing quitting text
            # adding quitting thing draw here as well

        if self.level_condition:
            self.victory(screen)
        else:
            self.play_time = pygame.time.get_ticks()
            self.victory_time = pygame.time.get_ticks()


class MenuScene(LevelScene):
    def __init__(self, xspawn, yspawn, music_value):
        LevelScene.__init__(self, xspawn, yspawn)
        self.options = []
        self.respawns += 1
        self.mid_jump = False
        self.title_text = dsnclass.Text("Press Space or W To Start", (530, 100), 50, "impact",
                          YELLOW, None)
        self.title_text_2 = dsnclass.Text("Press esc to pause", (530, 150), 30, "impact",
                          YELLOW, None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        """Do not use LevelScene for input since we don't want to control
        the character on the menu"""
        for every_key in pressed:
            if every_key in [pygame.K_SPACE, pygame.K_w]:
                self.change_scene(TutorialLevel1(40, 280, 1))

    def update(self):
        LevelScene.update(self)
        self.player.alive = True
        if (random.randint(1, 2500) <= 10) and not self.player.enable_gravity:
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump

    def render(self, screen):
        LevelScene.render(self, screen)         # Background Colors or Back-most
        self.render_level(screen)               # Level Elements or Middle
        LevelScene.render_text(self, screen)    # Text or Front-most
        screen.blit(self.title_text.text_img, self.title_text.text_rect)
        screen.blit(self.title_text_2.text_img, self.title_text_2.text_rect)

    def render_level(self, screen):
        # No death zones
        self.death_zones = []

        # No win zones
        self.win_zones = []

        platform1 = pygame.draw.rect(screen, BLACK, [0, 566, 1080, 10])
        platform2 = pygame.draw.rect(screen, BLACK, [0, 500, 1080, 10])
        platform3 = pygame.draw.rect(screen, BLACK, [200, 475, 200, 10])
        platform4 = pygame.draw.rect(screen, BLACK, [400, 460, 200, 10])
        platform5 = pygame.draw.rect(screen, BLACK, [600, 445, 200, 10])
        platform6 = pygame.draw.rect(screen, BLACK, [800, 430, 200, 10])
        platform7 = pygame.draw.rect(screen, BLACK, [200, 475, 810, 10])

        self.platforms = [platform1, platform2, platform3, platform4, platform5,
                          platform6, platform7]

        wall1 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
        wall2 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 576])
        wall3 = pygame.draw.rect(screen, BLACK, [200, 465, 10, 10])
        wall4 = pygame.draw.rect(screen, BLACK, [400, 450, 10, 10])
        wall5 = pygame.draw.rect(screen, BLACK, [600, 435, 10, 10])
        wall6 = pygame.draw.rect(screen, BLACK, [800, 420, 10, 10])
        wall7 = pygame.draw.rect(screen, BLACK, [1000, 430, 10, 45])
        self.walls = [wall1, wall2, wall3, wall4, wall5, wall6, wall7]


class TutorialLevel1(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut6_text = dsnclass.Text("Ta dudorial", (600, 400), 45, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel2(40, 540, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, CYAN, [1070, 278, 20, 40])
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, BLACK, [0, 310, 1100, 10])
        platform2 = pygame.draw.rect(screen, BLACK, [350, 290, 300, 30])
        self.platforms = [platform1, platform2]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 278])
        wall2 = pygame.draw.rect(screen, BLACK, [350, 290, 10, 30])
        wall3 = pygame.draw.rect(screen, BLACK, [640, 290, 10, 30])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 320])
        self.walls = [wall1, wall2, wall3, wall4]


class TutorialLevel2(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut5_text = dsnclass.Text("The mAze...", (210, 400), 75, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel3(0, 300, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut5_text.text_img, self.Tut5_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, CYAN, [650, 546, 10, 20])
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, BLACK, [0, 566, 1100, 10])
        platform2 = pygame.draw.rect(screen, BLACK, [0, 446, 406, 10])
        platform3 = pygame.draw.rect(screen, BLACK, [510, 536, 90, 10])
        platform4 = pygame.draw.rect(screen, BLACK, [380, 506, 90, 10])
        platform5 = pygame.draw.rect(screen, BLACK, [510, 476, 90, 10])
        platform6 = pygame.draw.rect(screen, BLACK, [380, 446, 90, 10])
        platform7 = pygame.draw.rect(screen, BLACK, [510, 416, 90, 10])
        platform8 = pygame.draw.rect(screen, BLACK, [380, 386, 90, 10])
        platform9 = pygame.draw.rect(screen, BLACK, [510, 356, 90, 10])
        platform10 = pygame.draw.rect(screen, BLACK, [380, 326, 90, 10])
        platform11 = pygame.draw.rect(screen, BLACK, [510, 296, 90, 10])
        platform12 = pygame.draw.rect(screen, BLACK, [380, 266, 90, 10])
        platform13 = pygame.draw.rect(screen, BLACK, [510, 236, 90, 10])
        platform14 = pygame.draw.rect(screen, BLACK, [380, 206, 90, 10])
        platform15 = pygame.draw.rect(screen, BLACK, [510, 176, 90, 10])
        platform16 = pygame.draw.rect(screen, BLACK, [380, 146, 90, 10])
        platform17 = pygame.draw.rect(screen, BLACK, [510, 116, 90, 10])
        platform18 = pygame.draw.rect(screen, BLACK, [380, 86, 90, 10])
        platform19 = pygame.draw.rect(screen, BLACK, [510, 56, 90, 10])
        platform20 = pygame.draw.rect(screen, BLACK, [380, 26, 90, 10])
        platform21 = pygame.draw.rect(screen, BLACK, [0, 326, 380,
                                                      10])  # this is intentional, move this around  # this is intentional, move this around
        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6, platform7, platform8,
                          platform9, platform10, platform11, platform12,
                          platform13, platform14, platform15, platform16,
                          platform17, platform18, platform19, platform20,
                          platform21]

        wall1 = pygame.draw.rect(screen, BLACK, [600, 36, 10,
                                                 1340])  # x,y , width/hieght - big right
        wall2 = pygame.draw.rect(screen, BLACK, [380, 0, 10, 266])
        wall3 = pygame.draw.rect(screen, BLACK, [650, 0, 10, 546])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
        wall5 = pygame.draw.rect(screen, BLACK, [380, 326, 10, 186])
        self.walls = [wall1, wall2, wall3, wall4, wall5]
        # that was outdated collision logic sorry


class TutorialLevel3(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel4(10, 100, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])
        self.death_zones = [death1]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 278, 10, 30])
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, BLACK, [0, 310, 200, 10])
        platform2 = pygame.draw.rect(screen, BLACK, [200, 360, 200, 10])
        platform3 = pygame.draw.rect(screen, BLACK, [500, 360, 150, 10])
        platform4 = pygame.draw.rect(screen, BLACK, [700, 335, 330, 10])
        self.platforms = [platform1, platform2, platform3, platform4]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 278])
        wall2 = pygame.draw.rect(screen, BLACK, [1070, 308, 10, 288])
        self.walls = [wall1, wall2]


class TutorialLevel4(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut7_text = dsnclass.Text("sandwich", (110, 400), 75, "impact", GREY, None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel5(0, 140, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut7_text.text_img, self.Tut7_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        death1 = pygame.draw.rect(screen, RED,
                                  [475, 370, 180, 600])  # bottom red block 1
        death2 = pygame.draw.rect(screen, RED,
                                  [475, 0, 180, 330])  # top red block 1
        death3 = pygame.draw.rect(screen, RED,
                                  [750, 350, 250, 230])  # bottom red block 2
        death4 = pygame.draw.rect(screen, RED,
                                  [750, 0, 250, 280])  # top red block 2
        self.death_zones = [death1, death2, death3, death4]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 278, 10, 30])  # win box 1
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, BLACK,
                                     [10, 110, 75, 10])  # spawn platform
        platform2 = pygame.draw.rect(screen, BLACK,
                                     [310, 360, 100, 10])  # dorp platfomr
        platform3 = pygame.draw.rect(screen, BLACK,
                                     [475, 360, 180, 10])  # sandwich bottom 1
        platform4 = pygame.draw.rect(screen, BLACK,
                                     [750, 340, 250, 10])  # sandwich bottom 2
        platform5 = pygame.draw.rect(screen, BLACK,
                                     [475, 330, 180, 10])  # sandwich top 1
        platform6 = pygame.draw.rect(screen, BLACK,
                                     [750, 280, 250, 10])  # sandwich top 2
        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6]

        wall1 = pygame.draw.rect(screen, BLACK,
                                 [1070, 0, 10, 278])  # win wall 1
        wall2 = pygame.draw.rect(screen, BLACK,
                                 [1070, 308, 10, 288])  # win wall 2
        self.walls = [wall1, wall2]


class TutorialLevel5(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut4_text = dsnclass.Text("This is not the same spot", (800, 100), 15,
                              "impact", YELLOW, None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel6(0, 120, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        # death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])# death floor
        # self.death_zones = [death1]

        platform1 = pygame.draw.rect(screen, BLACK,
                                     [0, 150, 200, 10])  # spawn platform
        platform2 = pygame.draw.rect(screen, BLACK, [200, 100, 200, 10])
        # platform3 = pygame.draw.rect(screen, BLACK, [500, 500, 200, 10])
        platform4 = pygame.draw.rect(screen, BLACK, [870, 530, 100, 10])
        platform5 = pygame.draw.rect(screen, BLACK,
                                     [445, 300, 270, 10])  # new land
        self.platforms = [platform1, platform2,  # platform3,
                          platform4,
                          platform5]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])  # win box
        self.win_zones = [win1]

        wall1 = pygame.draw.rect(screen, BLACK,
                                 [1070, 0, 10, 480])  # win wall 1
        wall2 = pygame.draw.rect(screen, BLACK,
                                 [1070, 510, 10, 288])  # win wall 2
        self.walls = [wall1, wall2]


class TutorialLevel6(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut4_text = dsnclass.Text("Jump under platform", (800, 100), 15,
                              "impact", YELLOW, None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(TutorialLevel5(0, 300))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        # death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])# death floor
        # self.death_zones = [death1]

        platform1 = pygame.draw.rect(screen, BLACK, [0, 150, 200, 10])
        platform2 = pygame.draw.rect(screen, BLACK, [200, 100, 200, 10])
        platform3 = pygame.draw.rect(screen, BLACK, [500, 500, 200, 10])
        platform4 = pygame.draw.rect(screen, BLACK, [700, 500, 270, 10])
        self.platforms = [platform1, platform2, platform3, platform4]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])  # win box
        self.win_zones = [win1]

        wall1 = pygame.draw.rect(screen, BLACK,
                                 [1070, 0, 10, 480])  # win wall 1
        wall2 = pygame.draw.rect(screen, BLACK,
                                 [1070, 510, 10, 288])  # win wall 2
        self.walls = [wall1, wall2]

