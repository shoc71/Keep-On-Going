import random
import pygame
import dsn_class as dsnclass

DARK_RED = (139, 0, 0)
YELLOW = (235, 195, 65)
BLACK = (0, 0, 0)
CYAN = (47, 237, 237)
RED = (194, 57, 33)
LIME_GREEN = (50, 205, 50)
LIGHT_RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)
LIGHT_PINK = (255, 182, 193)
EDIT_DARK_GREEN = (1, 100, 32)
PURPLE = (181, 60, 177)

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
        self.respawn_zones = []  # todo: add new respawn zones to levels

        self.x_spawn = x_spawn
        self.y_spawn = y_spawn
        self.player = dsnclass.SquareMe(self.x_spawn, self.y_spawn,
                                        10, 10, PURPLE)
        self.deaths = 0
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
        self.pause_text_4 = dsnclass.Text("Press r to return to menu",
                                          (540, 350), 30,
                                          "impact", DARK_RED, None)

    def input(self, pressed, held):
        if (held[pygame.K_SPACE] or held[pygame.K_w] or held[pygame.K_UP]) \
                and not self.player.enable_gravity and self.player.alive and \
                0 < self.player.jumps and not self.player.freeze:
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump
            self.player.jump_sound_1.play()
            self.player.jumps += 1

        for every_key in pressed:
            """   removed the instant return to menu, this will be apart of the
            pause menu now
            """
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive and not \
                    self.player.freeze:
                self.player.jump_ability = True
                self.player.jump_boost = self.player.max_jump
                self.player.jump_sound_1.play()
                self.player.jumps += 1
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] \
                    and not self.player.alive:
                self.player.alive = True
            if every_key == pygame.K_ESCAPE and not self.level_condition:
                self.player.freeze = not self.player.freeze
            if every_key == pygame.K_q and self.player.freeze:
                self.run_scene = False
            if self.player.freeze and every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360, 0))

    def update(self):
        if self.player.square_render is None:  # very important, else game crashes
            return None

        if self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.deaths += self.player.death(self.death_zones)
            self.player.collision_plat(self.platforms + self.walls)
            self.player.collision_wall(self.platforms + self.walls)
            self.player.move()
            # Respawn for square players
        if not self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.player.xpos = self.x_spawn
            self.player.ypos = self.y_spawn
            self.player.direction = 1
            self.player.gravity_counter = self.player.max_gravity
        if 580 + self.player.height < self.player.ypos:
            self.player.alive = False
            self.deaths += 1

        if self.player.alive and \
                self.player.square_render.collidelist(self.win_zones) != -1:
            self.level_condition = True
            self.player.alive = False

        # Respawn block collision
        if self.player.alive and \
                self.player.square_render.collidelist(self.respawn_zones) != -1:
            respawn_block = self.player.square_render.collidelist(self.respawn_zones)
            self.x_spawn = self.respawn_zones[respawn_block].x + (self.respawn_zones[respawn_block].width / 4)
            self.y_spawn = self.respawn_zones[respawn_block].y + (self.respawn_zones[respawn_block].height / 4)

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

    def render_level(self, screen):
        """ This function will be altered in the child class (the individual
        levels)"""
        pass

    def render_text(self, screen):
        """ This function will be altered in the child class (the individual
        levels)"""
        self.player.render(screen)

        if self.player.freeze:
            screen.blit(self.pause_text.text_img,
                        self.pause_text.text_rect)  # big bold for pausing
            screen.blit(self.pause_text_2.text_img,
                        self.pause_text_2.text_rect)  # instructions to unpause
            screen.blit(self.pause_text_3.text_img,
                        self.pause_text_3.text_rect)  # drawing quitting text
            # adding quitting thing draw here as well
            screen.blit(self.pause_text_4.text_img, self.pause_text_4.text_rect)
            # added a way to formally return to the main menu

        if self.level_condition:
            self.victory(screen)
        else:
            self.play_time = pygame.time.get_ticks()
            self.victory_time = pygame.time.get_ticks()


class MenuScene(LevelScene):
    def __init__(self, xspawn, yspawn, music_value):
        LevelScene.__init__(self, xspawn, yspawn)
        self.level_id = 0
        self.option_count = 0
        # start_spawn
        current_spawn = TutorialLevel1(12, 320,
                                       1)  # Added this in so it's less painful to find spawn
        current_spawn = TutorialLevel4(12, 200, 1)
        # current_spawn = EasyLevel5(37, 518, 1)
        # current_spawn = EasyLevel6(12, 12, 1)
        self.options = [LevelSelect(), Filler(), Filler(), Filler()]
        # SPEANWNSS
        '''
        filler content to identify current_spawn
        JASLKDKALSDKAd
        aaskjdajsdkajsdk
        akjsdjaklsdjad
        aksjdalskdjalsdja
        sddkalsdjalsjdloakdja;dsjkad
        ajsdkajdslkasjldk
        '''
        self.mid_jump = False
        self.title_splash = dsnclass.Text("DON'T STOP NOW", (540, 100), 100,
                                          "impact", YELLOW, None)
        self.title_text = dsnclass.Text("Press Space or W To Start", (530, 170),
                                        50, "impact",
                                        YELLOW, None)
        self.title_text_2 = dsnclass.Text("Press esc to pause", (530, 220), 30,
                                          "impact",
                                          YELLOW, None)
        self.title_text_s1 = dsnclass.Text("Level Select", (216, 490), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s2 = dsnclass.Text("Options", (432, 490), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s3 = dsnclass.Text("Filler 1", (648, 490), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s4 = dsnclass.Text("Filler 2", (864, 490), 30,
                                           "impact",
                                           YELLOW, None)
        self.option_select = [
            [self.title_text_s1.text_rect.x - 5,
             self.title_text_s1.text_rect.y - 5,
             self.title_text_s1.text_rect.width + 10,
             self.title_text_s1.text_rect.height + 10],
            [self.title_text_s2.text_rect.x - 5,
             self.title_text_s2.text_rect.y - 5,
             self.title_text_s2.text_rect.width + 10,
             self.title_text_s2.text_rect.height + 10],
            [self.title_text_s3.text_rect.x - 5,
             self.title_text_s3.text_rect.y - 5,
             self.title_text_s3.text_rect.width + 10,
             self.title_text_s3.text_rect.height + 10],
            [self.title_text_s4.text_rect.x - 5,
             self.title_text_s4.text_rect.y - 5,
             self.title_text_s4.text_rect.width + 10,
             self.title_text_s4.text_rect.height + 10]
        ]

        self.music = dsnclass.Music(music_value)

        """self.title_guy = dsnclass.SquareMe(xspawn, yspawn,
                                        10, 10, (181, 60, 177))"""

    def input(self, pressed, held):
        """Do not use LevelScene for input since we don't want to control
        the character on the menu"""
        for every_key in pressed:
            if every_key in [pygame.K_SPACE, pygame.K_w]:
                self.change_scene(self.options[self.option_count])
            if every_key is pygame.K_d:
                self.option_count += 1
                if len(self.options) - 1 < self.option_count:
                    self.option_count = 0
            if every_key is pygame.K_a:
                self.option_count -= 1
                if self.option_count < 0:
                    self.option_count = len(self.options) - 1

    def update(self):
        LevelScene.update(self)
        """if self.title_guy.square_render is not None:
            self.title_guy.alive = True
            if self.title_guy.alive and not self.title_guy.freeze and \
                    not self.level_condition:
                self.deaths += self.title_guy.death(self.death_zones)
                self.title_guy.collision_plat(self.platforms + self.walls)
                self.title_guy.collision_wall(self.platforms + self.walls)
                self.title_guy.move()
            if not self.title_guy.alive and not self.title_guy.freeze and \
                    not self.level_condition:
                self.title_guy.xpos = self.x_spawn
                self.title_guy.ypos = self.y_spawn
                self.title_guy.direction = 1
                self.title_guy.gravity_counter = self.player.max_gravity"""

        self.player.alive = True
        if (random.randint(1, 2500) <= 15) and not self.player.enable_gravity:
            self.victory_counter = len(self.victory_text)
            self.player.jumps += 1
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump
        else:
            self.victory_counter = 0

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle
        # Text or Front-most
        screen.blit(self.title_splash.text_img, self.title_splash.text_rect)
        screen.blit(self.title_text.text_img, self.title_text.text_rect)
        screen.blit(self.title_text_2.text_img, self.title_text_2.text_rect)
        screen.blit(self.title_text_s1.text_img, self.title_text_s1.text_rect)
        screen.blit(self.title_text_s2.text_img, self.title_text_s2.text_rect)
        screen.blit(self.title_text_s3.text_img, self.title_text_s3.text_rect)
        screen.blit(self.title_text_s4.text_img, self.title_text_s4.text_rect)

        LevelScene.render_text(self, screen)
        # self.title_guy.render(screen)

    def render_level(self, screen):
        # No death zones
        self.death_zones = []

        # No win zones
        self.win_zones = []

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 566, 1080, 10]),
                          pygame.draw.rect(screen, BLACK, [0, 400, 1080, 10]),
                          pygame.draw.rect(screen, BLACK, [200, 375, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [400, 360, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [600, 345, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [800, 330, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [200, 375, 810, 10])
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [0, 0, 10, 576]),
                      pygame.draw.rect(screen, BLACK, [1070, 0, 10, 576]),
                      pygame.draw.rect(screen, BLACK, [200, 365, 10, 10]),
                      pygame.draw.rect(screen, BLACK, [400, 350, 10, 10]),
                      pygame.draw.rect(screen, BLACK, [600, 335, 10, 10]),
                      pygame.draw.rect(screen, BLACK, [800, 320, 10, 10]),
                      pygame.draw.rect(screen, BLACK, [1000, 330, 10, 45])
                      ]

        pygame.draw.rect(screen, DARK_RED,
                         self.option_select[self.option_count], 2)


class Filler(dsnclass.Scene):
    def __init__(self):
        dsnclass.Scene.__init__(self)
        self.level_id = -1
        self.filler_text = dsnclass.Text(
            "THERE'S NOTHING HERE, PRESS R TO GO BACK",
            (540, 213), 50, "impact", DARK_RED, None)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360, 0))

    def render(self, screen):
        screen.fill(WHITE)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)


class LevelSelect(LevelScene):
    def __init__(self):
        LevelScene.__init__(self, (1080 / 2) - (10 / 2), 576 / 2)
        self.filler_text = dsnclass.Text("Choose A Level",
                                         (540, 153), 50, "impact", YELLOW, None)
        self.disclaimer_text2 = dsnclass.Text("ONLY A PROOF OF CONCEPT",
                                             (540, 60), 50, "impact", RED, None)
        self.disclaimer_text = dsnclass.Text("ALL LEVELS LEAD TO LEVEL 1, PRESS JUMP TO START",
                                             (540, 110), 50, "impact", RED, None)

        self.blockmation_time = 0
        self.text_x = 0
        self.direction = 0
        self.choose_id = 0

        self.first_level = TutorialLevel1(12, 320, 1)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360, 0))
            if every_key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w]:
                self.change_scene(self.first_level)
            if every_key in [pygame.K_a, pygame.K_d] and \
                    self.player.jump_ability and \
                    not self.player.enable_gravity and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.player.jump_boost = self.player.max_jump
                self.player.jump_sound_1.play()
                self.player.jumps += 1

                if every_key == pygame.K_a and 0 < self.choose_id:
                    self.blockmation_time = pygame.time.get_ticks()
                    self.direction = 1
                if every_key == pygame.K_d and self.choose_id < 999:
                    self.blockmation_time = pygame.time.get_ticks()
                    self.direction = -1

    def update(self):
        LevelScene.update(self)
        self.player.alive = True
        self.player.xpos = self.x_spawn
        if self.y_spawn <= self.player.ypos:
            self.player.ypos = self.y_spawn
            self.player.enable_gravity = False
            self.player.gravity_counter = self.player.max_gravity
            self.player.jump_ability = True

    def render(self, screen):
        LevelScene.render(self, screen)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)
        screen.blit(self.disclaimer_text2.text_img,
                    self.disclaimer_text2.text_rect)
        screen.blit(self.disclaimer_text.text_img,
                    self.disclaimer_text.text_rect)

        LevelScene.render_text(self, screen)


        left_text = dsnclass.Text(str(self.choose_id - 1),
                                       [(1080 / 2) - 200 + self.text_x,
                                        (576 / 2) + 39], 40, "impact", YELLOW,
                                       None)
        middle_text = dsnclass.Text(str(self.choose_id),
                                         [(1080 / 2) + self.text_x,
                                          (576 / 2) + 39],
                                         40, "impact", YELLOW, None)
        right_text = dsnclass.Text(str(self.choose_id + 1),
                                        [(1080 / 2) + 200 + self.text_x,
                                         (576 / 2) + 39], 40, "impact", YELLOW,
                                        None)

        scroll_text = [left_text, middle_text, right_text]

        for texts in scroll_text:
            if (1080 / 2) - 225 < texts.text_rect.x < (1080 / 2) + 195 and \
                    -1 < int(texts.text):
                screen.blit(texts.text_img, texts.text_rect)
                pygame.draw.rect(screen, (0, 0, 0), [texts.text_rect.x - 20,
                                                     texts.text_rect.y - 5,
                                                     texts.text_rect.width + 40,
                                                     texts.text_rect.height + 10], 4)

        if pygame.time.get_ticks() - self.blockmation_time < 400:
            if self.direction == 1:
                self.text_x += 2.3

            if self.direction == -1:
                self.text_x -= 2.3
        else:
            if self.text_x != 0:
                self.choose_id += -1 * self.direction
            self.text_x = 0

        # 4 Sides surrounding level select
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) - 250, (576 / 2) - 100, 500, 10])
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) - 250, (576 / 2) + 100, 500, 10])
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) - 250, (576 / 2) - 100, 70, 200])
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) + 250 - 70, (576 / 2) - 100, 70, 200])


########################################################################################
################################  tutorial levels   ####################################
########################################################################################


class TutorialLevel1(LevelScene):  # Hallway
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 1
        self.Tut6_text = dsnclass.Text("Hallway", (600, 400), 45, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel2(12, 80, 1))  # spawn for next level

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 308, 20, 40])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 288, 1100, 20]),
                          # spawn platform extended
                          pygame.draw.rect(screen, BLACK, [0, 348, 1100, 20])
                          # mid-platform
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 308]),
                      pygame.draw.rect(screen, BLACK, [1070, 348, 10, 250]),
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
                      ]


class TutorialLevel2(LevelScene):  # DropGuide to Solution
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 2
        self.Tut6_text = dsnclass.Text("Guide to Solution", (600, 400), 45,
                                       "impact", GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(
                TutorialLevel3(12, 297, 1))  # spawn for next level

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 528, 20, 40])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 90, 800, 40]),
                          # spawn platform extended
                          pygame.draw.rect(screen, BLACK, [200, 308, 880, 40]),
                          # mid-platform
                          pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10])
                          # floor
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 528]),
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
                      ]


class TutorialLevel3(LevelScene):  # jump over box
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 3
        self.Tut6_text = dsnclass.Text("Hit Space/up/w to jump", (600, 400), 45,
                                       "impact", GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel4(12, 200, 1))  # tut level 4 spawn

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 278, 20, 40])]

        pygame.draw.rect(screen, BLACK, [0, 310, 1080,
                                         576])  # visual-only, no collision necessary
        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 310, 1100, 10]),
                          pygame.draw.rect(screen, BLACK, [350, 290, 300, 30])
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 278]),
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 320])
                      ]


class TutorialLevel4(LevelScene):  # mind the gap
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 4
        self.Tut6_text = dsnclass.Text("Mind the Gap", (600, 400), 45, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel1(12, 292, 1))  # easy level 1 spawn

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, CYAN, [1070, 180, 20, 30])
        self.win_zones = [win1]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 210, 490, 366]),
                          pygame.draw.rect(screen, BLACK, [540, 210, 540, 366])
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 180]),
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 210])
                      ]

        self.respawn_zones = [
            pygame.draw.rect(screen, LIME_GREEN, [270, 180, 20, 20])]


#####################################################################################
###################################   easy levels   #################################
#####################################################################################

# left to right order for numbering platforms

class EasyLevel1(LevelScene):  # candles
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 5
        self.Tut1_text = dsnclass.Text("candles", (210, 400), 75, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel2(132, 282, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.death_zones = [
            pygame.draw.rect(screen, LIGHT_RED, [125, 110, 10, 20]),
            # candle light 1
            pygame.draw.rect(screen, LIGHT_RED, [425, 110, 10, 20]),
            # candle light 2
            pygame.draw.rect(screen, LIGHT_RED, [725, 110, 10, 20]),
            # candle light 3
            pygame.draw.rect(screen, LIGHT_RED, [990, 110, 10, 20]),
            # candle light 4
        ]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]),
                          # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]),
                          # roof
                          pygame.draw.rect(screen, BLACK, [0, 300, 1100, 276]),
                          # block - cut
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 90]),
                          # block - cut
                          pygame.draw.rect(screen, BLACK, [40, 270, 200, 10]),
                          # plat 1
                          pygame.draw.rect(screen, BLACK, [340, 240, 200, 10]),
                          # plat 2
                          pygame.draw.rect(screen, BLACK, [640, 210, 200, 10]),
                          # plat 3
                          pygame.draw.rect(screen, BLACK, [940, 180, 100, 10])
                          # plat 4
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]),
                      # side wall right
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]),
                      # side wall left
                      pygame.draw.rect(screen, BLACK, [125, 130, 10, 120]),
                      # candle stick 1
                      pygame.draw.rect(screen, BLACK, [425, 130, 10, 90]),
                      # candle stick 2
                      pygame.draw.rect(screen, BLACK, [725, 120, 10, 70]),
                      # candle stick 3
                      pygame.draw.rect(screen, BLACK, [990, 120, 10, 40]),
                      # candle stick 4]
                      ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 190, 20, 30])]


class EasyLevel2(LevelScene):  # mouse
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut1_text = dsnclass.Text("mouse", (120, 400), 75, "impact",
                                       GREY,
                                       None)
        self.level_id = 6
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel3(12, 12, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 300, 1100, 277]),
                          # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]),
                          # roof
                          pygame.draw.rect(screen, BLACK, [350, 130, 500, 200]),
                          # mouse body
                          pygame.draw.rect(screen, YELLOW, [0, 200, 100, 100]),
                          # cheese
                          pygame.draw.rect(screen, BLACK, [230, 270, 120, 30]),
                          # mouse arm
                          pygame.draw.rect(screen, BLACK, [120, 235, 100, 10]),
                          # platform above arm
                          pygame.draw.rect(screen, LIGHT_PINK,
                                           [320, 180, 30, 30]),  # mouse nose
                          pygame.draw.rect(screen, BLACK, [140, 160, 100, 10]),
                          # platform above above the cheese
                          pygame.draw.rect(screen, BLACK, [450, 100, 50, 30]),
                          # mouse ear
                          pygame.draw.rect(screen, LIGHT_PINK,
                                           [850, 240, 300, 25])  # mouse tail
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]),
                      # side wall right
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]),
                      # side wall left
                      ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 190, 20,
                                                          30])]  # win condition

        self.draw = [pygame.draw.rect(screen, WHITE, [385, 165, 20, 20]),
                     # mouse eye
                     pygame.draw.rect(screen, LIGHT_PINK, [260, 270, 90, 30]),
                     # mouse arm detail
                     pygame.draw.rect(screen, LIGHT_PINK, [460, 110, 25, 20]),
                     # mouse ear detail
                     pygame.draw.rect(screen, BLACK, [30, 210, 15, 20]),
                     # cheese black hole - left hole
                     pygame.draw.rect(screen, BLACK, [15, 270, 20, 20]),
                     # cheese black hole - left square
                     pygame.draw.rect(screen, BLACK, [50, 240, 15, 20]),
                     # cheese black hole - middle hole
                     pygame.draw.rect(screen, BLACK, [70, 270, 15, 20]),
                     # cheese black hole - big left
                     pygame.draw.line(screen, WHITE, [360, 200], [450, 190], 5),
                     # mouse whisker #1
                     pygame.draw.line(screen, WHITE, [360, 210], [450, 215], 5),
                     # mouse whisker #2
                     pygame.draw.line(screen, WHITE, [360, 220], [450, 245], 5),
                     # mouse whisker #3
                     pygame.draw.rect(screen, BLACK, [870, 240, 10, 25]),
                     # mouse tail detail #1
                     pygame.draw.rect(screen, BLACK, [900, 240, 10, 25]),
                     # mouse tail detail #2
                     pygame.draw.rect(screen, BLACK, [930, 240, 10, 25]),
                     # mouse tail detail #3
                     pygame.draw.rect(screen, BLACK, [960, 240, 10, 25]),
                     # mouse tail detail #4
                     pygame.draw.rect(screen, BLACK, [990, 240, 10, 25]),
                     # mouse tail detail #5
                     pygame.draw.rect(screen, BLACK, [1020, 240, 10, 25]),
                     # mouse tail detail #6
                     pygame.draw.rect(screen, BLACK, [1050, 240, 10, 25]),
                     # mouse tail detail #7
                     ]


class EasyLevel3(LevelScene):  # block maze 5
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 7
        self.Tut1_text = dsnclass.Text("block maze 5", (210, 400), 75, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel4(37, 489, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]),
                          # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]),
                          # roof
                          pygame.draw.rect(screen, BLACK,
                                           [0, 300, 1100, 276]),  # block - cut
                          pygame.draw.rect(screen, BLACK,
                                           [250, 40, 600, 10]),
                          # plat 2 - x250/y40
                          pygame.draw.rect(screen, BLACK,
                                           [900, 60, 50, 10]),
                          # plat 1 - x900/y60
                          pygame.draw.rect(screen, BLACK,
                                           [1000, 70, 100, 10]),
                          # plat 1 - x1000/y70
                          pygame.draw.rect(screen, BLACK,
                                           [950, 40, 50, 20]),
                          # block - y40/y80
                          pygame.draw.rect(screen, BLACK,
                                           [0, 85, 150, 10]),  # plat 1 - x0/y85
                          pygame.draw.rect(screen, BLACK,
                                           [200, 85, 675, 10]),
                          # plat 1 - x200/y85
                          pygame.draw.rect(screen, BLACK,
                                           [550, 50, 200, 35]),
                          # block - x400/y50
                          pygame.draw.rect(screen, BLACK,
                                           [250, 130, 300, 10]),
                          # plat 1 - x250/y130
                          pygame.draw.rect(screen, BLACK,
                                           [0, 85, 125, 55]),  # block - x0/y85
                          pygame.draw.rect(screen, BLACK,
                                           [650, 150, 450, 10]),
                          # plat 1 - x650/y150
                          pygame.draw.rect(screen, BLACK, [0, 180, 450, 10]),
                          pygame.draw.rect(screen, BLACK, [50, 265, 300, 10]),
                          pygame.draw.rect(screen, BLACK, [500, 180, 150, 10]),
                          pygame.draw.rect(screen, BLACK, [850, 120, 250, 30]),
                          pygame.draw.rect(screen, BLACK, [665, 265, 450, 10]),
                          pygame.draw.rect(screen, BLACK, [800, 230, 220, 10]),
                          pygame.draw.rect(screen, BLACK, [675, 200, 100, 10]),
                          pygame.draw.rect(screen, BLACK, [850, 275, 100, 25]),
                          pygame.draw.rect(screen, BLACK, [450, 280, 125, 20]),
                          pygame.draw.rect(screen, BLACK, [480, 240, 62, 20]),
                          pygame.draw.rect(screen, BLACK, [0, 40, 200, 10])
                          # plat 1 - x0/y40
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK,
                                       [1070, 0, 10, 580]),  # side wall right
                      pygame.draw.rect(screen, BLACK,
                                       [0, 0, 10, 580]),  # side wall left
                      pygame.draw.rect(screen, BLACK,
                                       [400, 0, 10, 40]),  # wall - x400/y0
                      pygame.draw.rect(screen, BLACK,
                                       [940, 40, 10, 20]),  # wall - x940/y40
                      pygame.draw.rect(screen, BLACK,
                                       [990, 40, 10, 40]),  # wall - x990/y40
                      pygame.draw.rect(screen, BLACK,
                                       [500, 140, 10, 40]),  # candle stick 4
                      pygame.draw.rect(screen, BLACK, [400, 104, 10, 20])
                      ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 50, 20, 20])]


class EasyLevel4(LevelScene):  # letters
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("letters", (660, 212), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel5(30, 518, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, BLACK, [0, 547, 1080, 29]),  # roof
            pygame.draw.rect(screen, BLACK, [0, 0, 1078, 29]),  # floor
            pygame.draw.rect(screen, BLACK, [0, 0, 26, 575]),  # left wall
            pygame.draw.rect(screen, BLACK, [168, 487, 40, 64]),
            # bottom A stand 1
            pygame.draw.rect(screen, BLACK, [0, 512, 178, 41]),  # right wall
            pygame.draw.rect(screen, BLACK, [325, 487, 40, 64]),
            # bottom A stand 2
            pygame.draw.rect(screen, BLACK, [168, 477, 197, 16]),
            # bottom A platform
            pygame.draw.rect(screen, BLACK, [547, 248, 59, 116]),
            # bottom G stand pt.3
            pygame.draw.rect(screen, BLACK, [714, 418, 87, 22]),
            # botttom G hook
            pygame.draw.rect(screen, BLACK, [626, 455, 152, 23]),
            # bottom G hanging thing
            pygame.draw.rect(screen, BLACK, [736, 428, 42, 80]),
            # botoom G hook stand
            pygame.draw.rect(screen, BLACK, [566, 503, 212, 44]),
            # bottom G base
            pygame.draw.rect(screen, BLACK, [168, 338, 41, 91]),
            # left side A top
            pygame.draw.rect(screen, BLACK, [326, 338, 41, 91]),
            # right side A top
            pygame.draw.rect(screen, BLACK, [168, 413, 197, 16]),
            # top A bottom part
            pygame.draw.rect(screen, BLACK, [851, 378, 206, 38]),
            # below e platform
            pygame.draw.rect(screen, BLACK, [822, 212, 38, 136]),  # e stand
            pygame.draw.rect(screen, BLACK, [550, 478, 55, 91]),
            # bottom G stand pt.1
            pygame.draw.rect(screen, BLACK, [547, 314, 59, 116]),
            # bottom G stand pt.2
            pygame.draw.rect(screen, BLACK, [936, 309, 125, 15]),
            # bottom E teeth jump
            pygame.draw.rect(screen, BLACK, [899, 238, 160, 14]),
            # top E teeth jump
            pygame.draw.rect(screen, BLACK, [1057, 0, 26, 575]),
            # second right wall
            pygame.draw.rect(screen, BLACK, [821, 198, 200, 18]),  # top E
            pygame.draw.rect(screen, BLACK, [717, 236, 61, 73]),
            # bottom G jumping to hook block
            pygame.draw.rect(screen, BLACK, [388, 309, 142, 98]),
            # platform inbewteen A and G
            pygame.draw.rect(screen, BLACK, [547, 182, 231, 70]),
            # bottom G top
            pygame.draw.rect(screen, BLACK, [421, 139, 82, 23]),  # top g hook
            pygame.draw.rect(screen, BLACK, [821, 340, 199, 21]),  # bottom E
            pygame.draw.rect(screen, BLACK, [821, 272, 199, 21]),  # middle E
            pygame.draw.rect(screen, BLACK, [168, 287, 199, 91]),
            # top part of A
            pygame.draw.rect(screen, BLACK, [443, 158, 28, 47]),
            # top G hook stand
            pygame.draw.rect(screen, BLACK, [201, 198, 270, 37]),
            # top down G block
            pygame.draw.rect(screen, BLACK, [201, 17, 43, 126]),  # top g hieght
            pygame.draw.rect(screen, BLACK, [520, 108, 49, 23]),
            # left side big O
            pygame.draw.rect(screen, BLACK, [775, 108, 49, 23]),
            # right side big O
            pygame.draw.rect(screen, BLACK, [520, 128, 304, 23]),
            # big O bottom
            pygame.draw.rect(screen, BLACK, [520, 8, 304, 57]),  # top big O
            pygame.draw.rect(screen, BLACK, [12, 225, 54, 15]),
            # JUMPINNG O TO G TO O
            pygame.draw.rect(screen, LIGHT_RED, [257, 311, 14, 96]),  # eye of A
            pygame.draw.rect(screen, BLACK, [866, 97, 21, 77]),  # bottom F
            pygame.draw.rect(screen, BLACK, [882, 121, 47, 21]),  # F hieght
            pygame.draw.rect(screen, BLACK, [866, 90, 192, 21]),  # top F
            pygame.draw.rect(screen, BLACK, [444, 512, 42, 38]),
            # SUPER ANNOYING BLOCK - dont remove
            pygame.draw.rect(screen, BLACK, [67, 254, 111, 12]),
            # below O platform
            pygame.draw.rect(screen, BLACK, [166, 192, 14, 35]),  # right side O
            pygame.draw.rect(screen, BLACK, [111, 194, 15, 32]),  # left side O
            pygame.draw.rect(screen, BLACK, [111, 218, 68, 10]),  # bottom O
            pygame.draw.rect(screen, BLACK, [111, 189, 69, 12]),  # top side O
            pygame.draw.rect(screen, BLACK, [201, 174, 42, 50]),
            # top G enterance
            pygame.draw.rect(screen, BLACK, [295, 170, 175, 15])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1057, 55, 27, 35])]


class EasyLevel5(LevelScene):  # staggers
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("staggers", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel6(21, 21, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, BLACK, [0, 560, 1080, 16]),
            pygame.draw.rect(screen, BLACK, [0, 0, 1080, 16]),
            pygame.draw.rect(screen, BLACK, [0, 0, 16, 573]),
            pygame.draw.rect(screen, BLACK, [0, 543, 1079, 20]),
            pygame.draw.rect(screen, BLACK, [139, 525, 940, 20]),
            pygame.draw.rect(screen, BLACK, [273, 508, 800, 20]),
            pygame.draw.rect(screen, BLACK, [411, 489, 660, 20]),
            pygame.draw.rect(screen, BLACK, [550, 471, 520, 20]),
            pygame.draw.rect(screen, BLACK, [686, 452, 380, 20]),
            pygame.draw.rect(screen, BLACK, [827, 434, 240, 20]),
            pygame.draw.rect(screen, BLACK, [965, 416, 101, 20]),
            pygame.draw.rect(screen, BLACK, [10, 379, 950, 15]),
            pygame.draw.rect(screen, BLACK, [10, 369, 830, 12]),
            pygame.draw.rect(screen, BLACK, [10, 359, 710, 12]),
            pygame.draw.rect(screen, BLACK, [10, 348, 590, 12]),
            pygame.draw.rect(screen, BLACK, [10, 337, 470, 12]),
            pygame.draw.rect(screen, BLACK, [10, 326, 350, 12]),
            pygame.draw.rect(screen, BLACK, [10, 315, 230, 12]),
            pygame.draw.rect(screen, BLACK, [10, 305, 110, 12]),
            pygame.draw.rect(screen, BLACK, [164, 270, 904, 20]),
            pygame.draw.rect(screen, BLACK, [294, 252, 774, 20]),
            pygame.draw.rect(screen, BLACK, [423, 234, 644, 20]),
            pygame.draw.rect(screen, BLACK, [553, 215, 514, 20]),
            pygame.draw.rect(screen, BLACK, [683, 196, 384, 20]),
            pygame.draw.rect(screen, BLACK, [817, 177, 254, 20]),
            pygame.draw.rect(screen, BLACK, [943, 158, 124, 20]),
            pygame.draw.rect(screen, BLACK, [7, 121, 928, 15]),
            pygame.draw.rect(screen, BLACK, [7, 110, 779, 13]),
            pygame.draw.rect(screen, BLACK, [7, 98, 664, 13]),
            pygame.draw.rect(screen, BLACK, [7, 86, 455, 13]),
            pygame.draw.rect(screen, BLACK, [7, 73, 203, 13]),
            pygame.draw.rect(screen, BLACK, [246, 42, 824, 13]),
            pygame.draw.rect(screen, BLACK, [1064, 0, 16, 573]),
            pygame.draw.rect(screen, BLACK, [14, 128, 198, 30]),
            pygame.draw.rect(screen, BLACK, [208, 118, 198, 30]),
            pygame.draw.rect(screen, BLACK, [396, 125, 353, 16]),
            pygame.draw.rect(screen, BLACK, [0, 384, 756, 16]),
            pygame.draw.rect(screen, BLACK, [0, 395, 569, 16]),
            pygame.draw.rect(screen, BLACK, [0, 406, 402, 16]),
            pygame.draw.rect(screen, BLACK, [5, 418, 318, 16]),
            pygame.draw.rect(screen, BLACK, [8, 430, 186, 16]),
            pygame.draw.rect(screen, BLACK, [399, 284, 668, 16]),
            pygame.draw.rect(screen, BLACK, [549, 296, 523, 16]),
            pygame.draw.rect(screen, BLACK, [760, 309, 316, 16]),
            pygame.draw.rect(screen, BLACK, [894, 321, 178, 16]),
            pygame.draw.rect(screen, BLACK, [354, 51, 720, 16]),
            pygame.draw.rect(screen, BLACK, [729, 65, 348, 16]),
            pygame.draw.rect(screen, BLACK, [851, 77, 222, 16]),
            pygame.draw.rect(screen, BLACK, [985, 90, 84, 16])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1064, 16, 17, 26])]


class EasyLevel6(LevelScene):  # spiral
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("spiral", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel7(37, 527, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, BLACK, [0, 0, 1080, 15]),
            pygame.draw.rect(screen, BLACK, [0, 0, 15, 573]),
            pygame.draw.rect(screen, BLACK, [1065, 0, 15, 573]),
            pygame.draw.rect(screen, BLACK, [12, 62, 988, 15]),
            pygame.draw.rect(screen, BLACK, [986, 63, 15, 442]),
            pygame.draw.rect(screen, BLACK, [77, 126, 15, 375]),
            pygame.draw.rect(screen, BLACK, [77, 126, 847, 14]),
            pygame.draw.rect(screen, BLACK, [909, 126, 15, 323]),
            pygame.draw.rect(screen, BLACK, [143, 435, 781, 15]),
            pygame.draw.rect(screen, BLACK, [143, 193, 15, 255]),
            pygame.draw.rect(screen, BLACK, [143, 192, 704, 15]),
            pygame.draw.rect(screen, BLACK, [833, 192, 15, 190]),
            pygame.draw.rect(screen, BLACK, [203, 367, 644, 15]),
            pygame.draw.rect(screen, BLACK, [203, 266, 15, 113]),
            pygame.draw.rect(screen, BLACK, [203, 265, 572, 16]),
            pygame.draw.rect(screen, BLACK, [253, 321, 522, 15]),
            pygame.draw.rect(screen, BLACK, [35, 424, 53, 13]),
            pygame.draw.rect(screen, BLACK, [0, 396, 53, 13]),
            pygame.draw.rect(screen, BLACK, [37, 365, 53, 13]),
            pygame.draw.rect(screen, BLACK, [37, 365, 53, 13]),
            pygame.draw.rect(screen, BLACK, [81, 467, 49, 32]),
            pygame.draw.rect(screen, BLACK, [120, 436, 48, 14]),
            pygame.draw.rect(screen, BLACK, [79, 405, 44, 14]),
            pygame.draw.rect(screen, BLACK, [39, 303, 50, 13]),
            pygame.draw.rect(screen, BLACK, [5, 273, 53, 13]),
            pygame.draw.rect(screen, BLACK, [38, 243, 53, 13]),
            pygame.draw.rect(screen, BLACK, [3, 211, 53, 13]),
            pygame.draw.rect(screen, BLACK, [36, 180, 53, 13]),
            pygame.draw.rect(screen, BLACK, [3, 151, 50, 13]),
            pygame.draw.rect(screen, BLACK, [0, 460, 55, 14]),
            pygame.draw.rect(screen, BLACK, [37, 126, 50, 13]),
            pygame.draw.rect(screen, BLACK, [39, 492, 65, 14]),
            pygame.draw.rect(screen, BLACK, [108, 377, 48, 14]),
            pygame.draw.rect(screen, BLACK, [10, 528, 111, 35]),
            pygame.draw.rect(screen, BLACK, [10, 528, 111, 35]),
            pygame.draw.rect(screen, BLACK, [0, 334, 53, 13]),
            pygame.draw.rect(screen, BLACK, [80, 346, 53, 13]),
            pygame.draw.rect(screen, BLACK, [106, 316, 50, 13]),
            pygame.draw.rect(screen, BLACK, [79, 289, 50, 13]),
            pygame.draw.rect(screen, BLACK, [106, 260, 50, 13]),
            pygame.draw.rect(screen, BLACK, [179, 369, 43, 13]),
            pygame.draw.rect(screen, BLACK, [213, 347, 74, 23]),
            pygame.draw.rect(screen, BLACK, [764, 267, 12, 63]),
            pygame.draw.rect(screen, BLACK, [83, 231, 44, 13]),
            pygame.draw.rect(screen, BLACK, [114, 204, 42, 13]),
            pygame.draw.rect(screen, BLACK, [145, 339, 39, 13]),
            pygame.draw.rect(screen, BLACK, [178, 307, 38, 13]),
            pygame.draw.rect(screen, BLACK, [146, 275, 40, 13]),
            pygame.draw.rect(screen, BLACK, [146, 238, 40, 13]),
            pygame.draw.rect(screen, BLACK, [12, 39, 881, 24]),
            pygame.draw.rect(screen, BLACK, [12, 39, 967, 24]),
            pygame.draw.rect(screen, BLACK, [21, 39, 967, 24]),
            pygame.draw.rect(screen, BLACK, [77, 491, 924, 15]),
            pygame.draw.rect(screen, BLACK, [0, 561, 1080, 15])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [762, 280, 12, 41])]


class EasyLevel7(LevelScene):  # burger
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("burger", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel8(21, 258, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 556, 1080, 20]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 20]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 20, 575]),
            pygame.draw.rect(screen, (0, 0, 0), [1060, 0, 20, 575]),
            pygame.draw.rect(screen, (0, 0, 0), [74, 520, 921, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [57, 476, 148, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [886, 476, 148, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [148, 435, 374, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [583, 435, 374, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [73, 393, 326, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [671, 393, 326, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [647, 350, 83, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [378, 350, 83, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [257, 350, 83, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [5, 318, 105, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [971, 318, 105, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [70, 288, 929, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [121, 111, 832, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [80, 157, 52, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [946, 157, 52, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [948, 195, 52, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [948, 237, 52, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [81, 237, 52, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [81, 199, 52, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [153, 196, 764, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [173, 160, 728, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 219, 61, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 181, 61, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 132, 85, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [1014, 175, 57, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [1014, 221, 57, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [983, 129, 85, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [484, 482, 148, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [484, 482, 148, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [83, 353, 117, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [781, 350, 83, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [903, 352, 101, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [1022, 269, 51, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 269, 51, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 269, 51, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [495, 347, 109, 12]),
            pygame.draw.rect(screen, (0, 0, 0), [158, 246, 767, 12])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1058, 64, 13, 38])]


class EasyLevel8(LevelScene):  # Tip-toe
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("Tip-toe", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel9(37, 524, 1))

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel6(21, 21, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 551, 1080, 25]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 25]),
            pygame.draw.rect(screen, (0, 0, 0), [10, 269, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [142, 225, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [139, 303, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [288, 261, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [433, 261, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [560, 220, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [563, 303, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [716, 303, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [716, 214, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [859, 260, 98, 14]),
            pygame.draw.rect(screen, (0, 0, 0), [137, 224, 15, 55]),
            pygame.draw.rect(screen, (0, 0, 0), [224, 224, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [559, 222, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [643, 219, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [715, 281, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [716, 215, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [801, 281, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [799, 215, 15, 36]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 20, 566]),
            pygame.draw.rect(screen, (0, 0, 0), [1060, 0, 20, 566])
        ]

        self.death_zones = [
            pygame.draw.rect(screen, (139, 0, 0), [401, 223, 15, 32]),
            pygame.draw.rect(screen, (139, 0, 0), [401, 290, 15, 32]),
            pygame.draw.rect(screen, (139, 0, 0), [972, 283, 15, 268]),
            pygame.draw.rect(screen, (139, 0, 0), [20, 534, 1040, 17]),
            pygame.draw.rect(screen, (139, 0, 0), [20, 24, 1040, 17]),
            pygame.draw.rect(screen, (139, 0, 0), [20, 24, 15, 209]),
            pygame.draw.rect(screen, (139, 0, 0), [20, 283, 15, 255]),
            pygame.draw.rect(screen, (139, 0, 0), [1046, 25, 15, 164]),
            pygame.draw.rect(screen, (139, 0, 0), [1046, 316, 15, 234]),
            pygame.draw.rect(screen, (139, 0, 0), [972, 24, 15, 183]),
            pygame.draw.rect(screen, (139, 0, 0), [285, 39, 20, 125]),
            pygame.draw.rect(screen, (139, 0, 0), [553, 39, 20, 125]),
            pygame.draw.rect(screen, (139, 0, 0), [857, 39, 20, 125]),
            pygame.draw.rect(screen, (139, 0, 0), [133, 39, 20, 125]),
            pygame.draw.rect(screen, (139, 0, 0), [133, 372, 20, 163]),
            pygame.draw.rect(screen, (139, 0, 0), [300, 372, 20, 163]),
            pygame.draw.rect(screen, (139, 0, 0), [605, 372, 20, 163]),
            pygame.draw.rect(screen, (139, 0, 0), [777, 372, 20, 163]),
            pygame.draw.rect(screen, (139, 0, 0), [463, 372, 20, 163]),
            pygame.draw.rect(screen, (139, 0, 0), [686, 36, 20, 106]),
            pygame.draw.rect(screen, (139, 0, 0), [396, 36, 20, 106])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1060, 212, 15, 90])]


class EasyLevel9(LevelScene):  # Help
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("You're not alone", (900, 252), 60,
                                       "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel10(48, 53, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 556, 1080, 20]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 20]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 20, 572]),
            pygame.draw.rect(screen, (0, 0, 0), [1060, 0, 20, 572]),
            pygame.draw.rect(screen, (0, 0, 0), [183, 117, 380, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [661, 117, 17, 451]),
            pygame.draw.rect(screen, (0, 0, 0), [235, 479, 438, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [184, 521, 432, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [183, 436, 439, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [238, 394, 433, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [185, 353, 445, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [240, 312, 436, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [184, 272, 425, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [238, 232, 434, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [185, 192, 447, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [183, 118, 17, 416]),
            pygame.draw.rect(screen, (0, 0, 0), [451, 130, 113, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [451, 130, 113, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [182, 98, 10, 23]),
            pygame.draw.rect(screen, (0, 0, 0), [118, 549, 10, 22]),
            pygame.draw.rect(screen, (0, 0, 0), [22, 547, 10, 22]),
            pygame.draw.rect(screen, (0, 0, 0), [425, 469, 10, 22]),
            pygame.draw.rect(screen, (0, 0, 0), [425, 301, 10, 22]),
            pygame.draw.rect(screen, (0, 0, 0), [236, 158, 437, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [427, 145, 10, 22]),
            pygame.draw.rect(screen, (0, 0, 0), [118, 109, 11, 397]),
            pygame.draw.rect(screen, (0, 0, 0), [22, 108, 11, 401]),
            pygame.draw.rect(screen, (0, 0, 0), [22, 82, 68, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [704, 534, 13, 24]),
            pygame.draw.rect(screen, (0, 0, 0), [723, 534, 13, 24]),
            pygame.draw.rect(screen, (0, 0, 0), [743, 534, 13, 24]),
            pygame.draw.rect(screen, (0, 0, 0), [762, 534, 13, 24])
        ]

        self.death_zones = [
            pygame.draw.rect(screen, (139, 0, 0), [1026, 313, 39, 16]),
            pygame.draw.rect(screen, (139, 0, 0), [464, 300, 8, 14]),
            pygame.draw.rect(screen, (139, 0, 0), [816, 300, 8, 14]),
            pygame.draw.rect(screen, (139, 0, 0), [811, 96, 15, 154]),
            pygame.draw.rect(screen, (139, 0, 0), [627, 96, 15, 153]),
            pygame.draw.rect(screen, (139, 0, 0), [460, 96, 15, 152]),
            pygame.draw.rect(screen, (139, 0, 0), [293, 96, 15, 150]),
            pygame.draw.rect(screen, (139, 0, 0), [966, 95, 15, 63]),
            pygame.draw.rect(screen, (139, 0, 0), [217, 329, 15, 172]),
            pygame.draw.rect(screen, (139, 0, 0), [376, 328, 15, 172]),
            pygame.draw.rect(screen, (139, 0, 0), [546, 328, 15, 172]),
            pygame.draw.rect(screen, (139, 0, 0), [724, 328, 15, 172]),
            pygame.draw.rect(screen, (139, 0, 0), [903, 329, 15, 172]),
            pygame.draw.rect(screen, (139, 0, 0), [977, 516, 8, 14]),
            pygame.draw.rect(screen, (139, 0, 0), [568, 548, 8, 14]),
            pygame.draw.rect(screen, (139, 0, 0), [131, 96, 15, 147]),
            pygame.draw.rect(screen, (139, 0, 0), [134, 300, 8, 14]),
            pygame.draw.rect(screen, (139, 0, 0), [543, 53, 13, 13]),
            pygame.draw.rect(screen, (139, 0, 0), [532, 548, 8, 15]),
            pygame.draw.rect(screen, (139, 0, 0), [14, 71, 34, 15]),
            pygame.draw.rect(screen, (139, 0, 0), [13, 257, 34, 15])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [5, 544, 11, 32])]


class EasyLevel10(LevelScene):  # Hard Ritual
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("Ritaul", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel9(37, 524, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 15, 576]),
            pygame.draw.rect(screen, (0, 0, 0), [1065, 0, 15, 576]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 15]),
            pygame.draw.rect(screen, (0, 0, 0), [58, 71, 969, 15]),
            pygame.draw.rect(screen, (0, 0, 0), [140, 345, 15, 145]),
            pygame.draw.rect(screen, (0, 0, 0), [295, 345, 15, 145]),
            pygame.draw.rect(screen, (0, 0, 0), [460, 345, 15, 145]),
            pygame.draw.rect(screen, (0, 0, 0), [629, 345, 15, 145]),
            pygame.draw.rect(screen, (0, 0, 0), [813, 345, 15, 145]),
            pygame.draw.rect(screen, (0, 0, 0), [973, 345, 15, 145]),
            pygame.draw.rect(screen, (0, 0, 0), [143, 519, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [299, 519, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [464, 519, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [633, 519, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [817, 519, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [969, 300, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [632, 300, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [297, 300, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [901, 74, 15, 205]),
            pygame.draw.rect(screen, (0, 0, 0), [722, 73, 15, 205]),
            pygame.draw.rect(screen, (0, 0, 0), [544, 74, 15, 205]),
            pygame.draw.rect(screen, (0, 0, 0), [375, 74, 15, 205]),
            pygame.draw.rect(screen, (0, 0, 0), [58, 314, 969, 15]),
            pygame.draw.rect(screen, (0, 0, 0), [12, 528, 1019, 15]),
            pygame.draw.rect(screen, (0, 0, 0), [209, 77, 15, 205]),
            pygame.draw.rect(screen, (0, 0, 0), [46, 71, 15, 202])
        ]

        self.death_zones = [
            pygame.draw.rect(screen, (139, 0, 0), [678, 547, 179, 10]),
            pygame.draw.rect(screen, (139, 0, 0), [898, 547, 162, 10]),
            pygame.draw.rect(screen, (139, 0, 0), [426, 424, 10, 12]),
            pygame.draw.rect(screen, (139, 0, 0), [425, 261, 10, 12]),
            pygame.draw.rect(screen, (139, 0, 0), [427, 105, 10, 12]),
            pygame.draw.rect(screen, (139, 0, 0), [788, 36, 10, 12]),
            pygame.draw.rect(screen, (139, 0, 0), [181, 87, 11, 12]),
            pygame.draw.rect(screen, (139, 0, 0), [728, 548, 10, 8]),
            pygame.draw.rect(screen, (139, 0, 0), [423, 551, 10, 5])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [857, 547, 42, 10])]


class EasyLevel11(LevelScene):  # Reverse Lamp
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("REverse Lamp", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel9(37, 524, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [1061, 0, 19, 315]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1079, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 19, 315]),
            pygame.draw.rect(screen, (0, 0, 0), [157, 197, 99, 20]),
            pygame.draw.rect(screen, (0, 0, 0), [478, 70, 11, 67]),
            pygame.draw.rect(screen, (0, 0, 0), [579, 70, 11, 67]),
            pygame.draw.rect(screen, (0, 0, 0), [239, 89, 60, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [15, 121, 371, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [690, 121, 371, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [386, 155, 60, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [631, 155, 60, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [701, 179, 60, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [823, 197, 99, 20]),
            pygame.draw.rect(screen, (0, 0, 0), [12, 193, 61, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [1001, 193, 61, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [13, 223, 99, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [964, 223, 99, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [782, 89, 60, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [154, 264, 81, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [845, 264, 81, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [596, 313, 64, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [315, 179, 60, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [525, 71, 19, 285]),
            pygame.draw.rect(screen, (0, 0, 0), [382, 62, 315, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 353, 1080, 223]),
            pygame.draw.rect(screen, (0, 0, 0), [414, 312, 64, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [283, 287, 64, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [729, 287, 64, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [447, 129, 180, 11])
        ]

        self.death_zones = [
            pygame.draw.rect(screen, (139, 0, 0), [0, 313, 19, 41]),
            pygame.draw.rect(screen, (139, 0, 0), [315, 188, 60, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [386, 165, 60, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [239, 97, 60, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [782, 97, 60, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [631, 166, 60, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [701, 190, 60, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [544, 73, 37, 58]),
            pygame.draw.rect(screen, (139, 0, 0), [544, 493, 37, 73]),
            pygame.draw.rect(screen, (139, 0, 0), [489, 493, 37, 73]),
            pygame.draw.rect(screen, (139, 0, 0), [596, 324, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [596, 426, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [414, 323, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [414, 426, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [729, 296, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [729, 464, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [283, 297, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [283, 460, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [192, 217, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [192, 516, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [823, 527, 64, 6]),
            pygame.draw.rect(screen, (139, 0, 0), [823, 217, 64, 6])
        ]

        self.win_zones = [
            pygame.draw.rect(screen, (47, 237, 237), [489, 73, 37, 58]),
            pygame.draw.rect(screen, (47, 237, 237), [1061, 313, 19, 40]),
            pygame.draw.rect(screen, (47, 237, 237), [20, 235, 64, 6]),
            pygame.draw.rect(screen, (47, 237, 237), [996, 235, 64, 6]),
            pygame.draw.rect(screen, (47, 237, 237), [821, 132, 240, 6]),
            pygame.draw.rect(screen, (47, 237, 237), [19, 18, 281, 6]),
            pygame.draw.rect(screen, (47, 237, 237), [780, 18, 281, 6]),
            pygame.draw.rect(screen, (47, 237, 237), [525, 353, 19, 220]),
            pygame.draw.rect(screen, (47, 237, 237), [382, 565, 315, 11]),
            pygame.draw.rect(screen, (47, 237, 237), [448, 483, 179, 11])
        ]


class EasyLevel12(LevelScene):  # Propaganda
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("You are getting in my way", (900, 252),
                                       60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel9(37, 524, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 21, 576]),
            pygame.draw.rect(screen, (0, 0, 0), [1059, 0, 21, 576]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 555, 1080, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [539, 63, 442, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [94, 124, 442, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [589, 124, 470, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [18, 339, 470, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [541, 339, 474, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [586, 405, 474, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [68, 405, 474, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [16, 476, 971, 41]),
            pygame.draw.rect(screen, (0, 0, 0), [1028, 263, 31, 38]),
            pygame.draw.rect(screen, (0, 0, 0), [541, 331, 435, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [256, 366, 8, 27]),
            pygame.draw.rect(screen, (0, 0, 0), [320, 400, 8, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [320, 340, 8, 27]),
            pygame.draw.rect(screen, (0, 0, 0), [391, 364, 8, 27]),
            pygame.draw.rect(screen, (0, 0, 0), [190, 342, 8, 27]),
            pygame.draw.rect(screen, (0, 0, 0), [136, 391, 8, 27]),
            pygame.draw.rect(screen, (0, 0, 0), [76, 373, 8, 27]),
            pygame.draw.rect(screen, (0, 0, 0), [589, 115, 100, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [586, 463, 63, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [479, 463, 63, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [832, 52, 140, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [910, 111, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [19, 63, 462, 18]),
            pygame.draw.rect(screen, (0, 0, 0), [485, 72, 51, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [538, 133, 48, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [492, 349, 44, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [926, 102, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [895, 102, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [75, 27, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [160, 27, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [269, 27, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [375, 27, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [1007, 352, 8, 26]),
            pygame.draw.rect(screen, (0, 0, 0), [990, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [972, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [954, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [935, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [919, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [901, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [881, 352, 8, 21]),
            pygame.draw.rect(screen, (0, 0, 0), [858, 352, 8, 17]),
            pygame.draw.rect(screen, (0, 0, 0), [838, 352, 8, 17]),
            pygame.draw.rect(screen, (0, 0, 0), [817, 352, 8, 17]),
            pygame.draw.rect(screen, (0, 0, 0), [795, 352, 8, 17]),
            pygame.draw.rect(screen, (0, 0, 0), [772, 352, 8, 17]),
            pygame.draw.rect(screen, (0, 0, 0), [751, 352, 8, 17]),
            pygame.draw.rect(screen, (0, 0, 0), [728, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [708, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [689, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [666, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [645, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [623, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [600, 352, 8, 13]),
            pygame.draw.rect(screen, (0, 0, 0), [585, 352, 8, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [571, 352, 8, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [557, 352, 8, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [543, 352, 8, 10]),
            pygame.draw.rect(screen, (0, 0, 0), [40, 214, 1020, 50]),
            pygame.draw.rect(screen, (0, 0, 0), [325, 196, 44, 7]),
            pygame.draw.rect(screen, (0, 0, 0), [219, 197, 44, 7]),
            pygame.draw.rect(screen, (0, 0, 0), [117, 197, 44, 7]),
            pygame.draw.rect(screen, (0, 0, 0), [434, 195, 44, 7])
        ]

        self.death_zones = [
            pygame.draw.rect(screen, (139, 0, 0), [591, 21, 167, 18]),
            pygame.draw.rect(screen, (139, 0, 0), [1051, 190, 8, 25]),
            pygame.draw.rect(screen, (139, 0, 0), [324, 109, 8, 16]),
            pygame.draw.rect(screen, (139, 0, 0), [211, 109, 8, 16]),
            pygame.draw.rect(screen, (139, 0, 0), [117, 109, 8, 15]),
            pygame.draw.rect(screen, (139, 0, 0), [833, 264, 195, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [589, 142, 471, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [586, 423, 473, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [588, 194, 11, 21]),
            pygame.draw.rect(screen, (139, 0, 0), [626, 194, 11, 21]),
            pygame.draw.rect(screen, (139, 0, 0), [608, 201, 11, 14]),
            pygame.draw.rect(screen, (139, 0, 0), [445, 264, 401, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [972, 52, 9, 12]),
            pygame.draw.rect(screen, (139, 0, 0), [546, 468, 34, 8]),
            pygame.draw.rect(screen, (139, 0, 0), [423, 468, 34, 8]),
            pygame.draw.rect(screen, (139, 0, 0), [438, 108, 8, 16]),
            pygame.draw.rect(screen, (139, 0, 0), [485, 62, 51, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [538, 123, 48, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [492, 339, 44, 9]),
            pygame.draw.rect(screen, (139, 0, 0), [48, 264, 409, 9])
        ]

        self.win_zones = [
            pygame.draw.rect(screen, (47, 237, 237), [10, 517, 11, 38])
        ]


class EasyLevel13(LevelScene):  # Split path
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("split path", (900, 252), 60, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel9(37, 524, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 23]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 553, 1080, 23]),
            pygame.draw.rect(screen, (0, 0, 0), [34, 284, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [907, 459, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [907, 139, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [203, 251, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [203, 312, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [794, 443, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [794, 156, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [667, 424, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [667, 172, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [509, 395, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [509, 201, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [348, 358, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [348, 222, 104, 11]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 20, 576]),
            pygame.draw.rect(screen, (0, 0, 0), [1066, 0, 14, 576])
        ]

        self.death_zones = [
            pygame.draw.rect(screen, (139, 0, 0), [20, 530, 1046, 23]),
            pygame.draw.rect(screen, (139, 0, 0), [20, 22, 1046, 23])
        ]

        self.win_zones = [
            pygame.draw.rect(screen, (47, 237, 237), [1066, 62, 10, 66]),
            pygame.draw.rect(screen, (47, 237, 237), [1066, 487, 10, 20])
        ]


class EasyLevel14(LevelScene):  # uneven platforms
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("Uneven Platforms", (900, 252), 60,
                                       "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel9(37, 524, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [
            pygame.draw.rect(screen, (0, 0, 0), [0, 447, 1080, 129]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 1080, 114]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 210, 10, 114]),
            pygame.draw.rect(screen, (0, 0, 0), [1066, 210, 14, 114]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 109, 29, 104]),
            pygame.draw.rect(screen, (0, 0, 0), [1051, 110, 29, 104]),
            pygame.draw.rect(screen, (0, 0, 0), [1051, 320, 29, 131]),
            pygame.draw.rect(screen, (0, 0, 0), [0, 320, 29, 131]),
            pygame.draw.rect(screen, (0, 0, 0), [280, 379, 71, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [389, 410, 71, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [646, 410, 71, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [759, 382, 71, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [848, 353, 76, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [163, 353, 71, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [28, 330, 96, 9]),
            pygame.draw.rect(screen, (0, 0, 0), [943, 327, 92, 9])
        ]

        self.win_zones = [
            pygame.draw.rect(screen, (47, 237, 237), [1065, 214, 9, 106])
        ]

class EasyLevel15(LevelScene):  # LavaDrip
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("Lava drip", (900, 252), 60,
                                       "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel9(37, 524, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms =  [
            pygame.draw.rect(screen, (0, 0, 0), [0, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [127, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [248, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [373, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [498, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [608, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [719, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [834, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [948, 294, 63, 16]),
            pygame.draw.rect(screen, (0, 0, 0), [1064, 308, 16, 253]),
            pygame.draw.rect(screen, (0, 0, 0), [1064, 0, 16, 253])
        ]

        self.death_zones =  [
                pygame.draw.rect(screen, (139, 0, 0), [93, 520, 16, 56]),
                pygame.draw.rect(screen, (139, 0, 0), [206, 487, 16, 86]),
                pygame.draw.rect(screen, (139, 0, 0), [727, 490, 16, 86]),
                pygame.draw.rect(screen, (139, 0, 0), [881, 490, 16, 86]),
                pygame.draw.rect(screen, (139, 0, 0), [945, 490, 16, 86]),
                pygame.draw.rect(screen, (139, 0, 0), [409, 382, 16, 194]),
                pygame.draw.rect(screen, (139, 0, 0), [336, 284, 16, 292]),
                pygame.draw.rect(screen, (139, 0, 0), [87, 284, 16, 36]),
                pygame.draw.rect(screen, (139, 0, 0), [919, 284, 16, 36]),
                pygame.draw.rect(screen, (139, 0, 0), [0, 561, 1080, 15]),
                pygame.draw.rect(screen, (139, 0, 0), [0, 0, 1080, 15]),
                pygame.draw.rect(screen, (139, 0, 0), [686, 284, 16, 292]),
                pygame.draw.rect(screen, (139, 0, 0), [91, 0, 16, 189]),
                pygame.draw.rect(screen, (139, 0, 0), [917, 0, 16, 189]),
                pygame.draw.rect(screen, (139, 0, 0), [531, 0, 16, 189]),
                pygame.draw.rect(screen, (139, 0, 0), [233, 0, 16, 32]),
                pygame.draw.rect(screen, (139, 0, 0), [1024, 0, 16, 32]),
                pygame.draw.rect(screen, (139, 0, 0), [984, 128, 7, 32]),
                pygame.draw.rect(screen, (139, 0, 0), [388, 113, 9, 32]),
                pygame.draw.rect(screen, (139, 0, 0), [1009, 107, 9, 32]),
                pygame.draw.rect(screen, (139, 0, 0), [986, 37, 8, 47]),
                pygame.draw.rect(screen, (139, 0, 0), [777, 0, 16, 32]),
                pygame.draw.rect(screen, (139, 0, 0), [608, 0, 16, 94]),
                pygame.draw.rect(screen, (139, 0, 0), [441, 0, 16, 98]),
                pygame.draw.rect(screen, (139, 0, 0), [315, 7, 16, 101]),
                pygame.draw.rect(screen, (139, 0, 0), [187, 7, 16, 105]),
                pygame.draw.rect(screen, (139, 0, 0), [0, 310, 16, 266]),
                pygame.draw.rect(screen, (139, 0, 0), [0, 0, 16, 223]),
                pygame.draw.rect(screen, (139, 0, 0), [850, 0, 16, 230]),
                pygame.draw.rect(screen, (139, 0, 0), [267, 0, 16, 234]),
                pygame.draw.rect(screen, (139, 0, 0), [271, 363, 16, 205]),
                pygame.draw.rect(screen, (139, 0, 0), [807, 363, 16, 205]),
                pygame.draw.rect(screen, (139, 0, 0), [502, 325, 16, 245]),
                pygame.draw.rect(screen, (139, 0, 0), [478, 338, 16, 232]),
                pygame.draw.rect(screen, (139, 0, 0), [552, 350, 16, 219]),
                pygame.draw.rect(screen, (139, 0, 0), [431, 363, 16, 205]),
                pygame.draw.rect(screen, (139, 0, 0), [578, 363, 16, 205]),
                pygame.draw.rect(screen, (139, 0, 0), [573, 45, 8, 205]),
                pygame.draw.rect(screen, (139, 0, 0), [754, 23, 8, 205]),
                pygame.draw.rect(screen, (139, 0, 0), [134, 35, 8, 125]),
                pygame.draw.rect(screen, (139, 0, 0), [53, 112, 8, 125]),
                pygame.draw.rect(screen, (139, 0, 0), [58, 358, 8, 125]),
                pygame.draw.rect(screen, (139, 0, 0), [140, 358, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [175, 407, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [639, 407, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [639, 151, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [763, 452, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [915, 391, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [1023, 391, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [1003, 480, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [1052, 97, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [1052, 376, 8, 84]),
                pygame.draw.rect(screen, (139, 0, 0), [985, 370, 8, 58])
        ]

        self.win_zones =  [
                pygame.draw.rect(screen, (47, 237, 237), [1064, 252, 16, 56])
        ]


#####################################################################################
##############################   unorganized levels   ###############################
#####################################################################################

# unorganized levels

class TutorialLevel14(LevelScene):  # daz maze
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut5_text = dsnclass.Text("The mAze...", (210, 400), 75, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel24(0, 300, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut5_text.text_img, self.Tut5_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [650, 546, 10, 20])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 566, 1100, 10]),
                          pygame.draw.rect(screen, BLACK, [0, 446, 406, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 536, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 506, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 476, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 446, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 416, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 386, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 356, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 326, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 296, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 266, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 236, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 206, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 176, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 146, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 116, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 86, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [510, 56, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [380, 26, 90, 10]),
                          pygame.draw.rect(screen, BLACK, [0, 326, 380, 10])
                          # this is intentional, move this around
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [600, 36, 10, 1340]),
                      # x,y , width/hieght - big right
                      pygame.draw.rect(screen, BLACK, [380, 0, 10, 266]),
                      pygame.draw.rect(screen, BLACK, [650, 0, 10, 546]),
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 576]),
                      pygame.draw.rect(screen, BLACK, [380, 326, 10, 186])
                      ]
        # that was outdated collision logic sorry


class TutorialLevel24(LevelScene):  # red floor
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(TutorialLevel25(10, 100, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        # No text

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.death_zones = [pygame.draw.rect(screen, RED, [0, 550, 1080, 30])]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 278, 10, 30])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 310, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [200, 360, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [500, 360, 150, 10]),
                          pygame.draw.rect(screen, BLACK, [700, 335, 330, 10])
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 278]),
                      pygame.draw.rect(screen, BLACK, [1070, 308, 10, 288])
                      ]


class TutorialLevel5(LevelScene):  # sanwich
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut7_text = dsnclass.Text("sandwich", (110, 400), 75, "impact",
                                       GREY, None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel6(0, 140, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut7_text.text_img, self.Tut7_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.death_zones = [pygame.draw.rect(screen, RED, [505, 370, 180, 600]),
                            # bottom red block 1
                            pygame.draw.rect(screen, RED, [505, 0, 180, 330]),
                            # top red block 1
                            pygame.draw.rect(screen, RED, [750, 350, 250, 230]),
                            # bottom red block 2
                            pygame.draw.rect(screen, RED, [750, 0, 250, 280]),
                            # top red block 2
                            ]

        self.win_zones = [
            pygame.draw.rect(screen, CYAN, [1070, 278, 10, 30])]  # win box 1

        self.platforms = [pygame.draw.rect(screen, BLACK,
                                           [10, 110, 75, 10]),  # spawn platform
                          pygame.draw.rect(screen, BLACK,
                                           [310, 360, 100, 10]),
                          # dorp platfomr
                          pygame.draw.rect(screen, BLACK,
                                           [505, 360, 180, 10]),
                          # sandwich bottom 1
                          pygame.draw.rect(screen, BLACK,
                                           [750, 340, 250, 10]),
                          # sandwich bottom 2
                          pygame.draw.rect(screen, BLACK,
                                           [505, 330, 180, 10]),
                          # sandwich top 1
                          pygame.draw.rect(screen, BLACK,
                                           [750, 280, 250, 10])
                          # sandwich top 2
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK,
                                       [1070, 0, 10, 278]),  # win wall 1
                      pygame.draw.rect(screen, BLACK,
                                       [1070, 308, 10, 288])  # win wall 2
                      ]


class TutorialLevel6(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut4_text = dsnclass.Text("This is not the same spot", (800, 100),
                                       15,
                                       "impact", YELLOW, None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel7(0, 120, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.win_zones = [
            pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])]  # win box

        # death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])# death floor
        # self.death_zones = [death1]

        self.platforms = [pygame.draw.rect(screen, BLACK,
                                           [0, 150, 200, 10]),  # spawn platform
                          pygame.draw.rect(screen, BLACK, [200, 100, 200, 10]),
                          # platform3 = pygame.draw.rect(screen, BLACK, [500, 500, 200, 10])
                          pygame.draw.rect(screen, BLACK, [870, 530, 100, 10]),
                          pygame.draw.rect(screen, BLACK, [445, 300, 270, 10])
                          # new land
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK,
                                       [1070, 0, 10, 480]),  # win wall 1
                      pygame.draw.rect(screen, BLACK,
                                       [1070, 510, 10, 288])  # win wall 2
                      ]


class TutorialLevel7(LevelScene):
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

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])]

        # death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])# death floor
        # self.death_zones = [death1]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 150, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [200, 100, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [500, 500, 200, 10]),
                          pygame.draw.rect(screen, BLACK, [700, 500, 270, 10])
                          ]

        pygame.draw.rect(screen, BLACK,
                         [1070, 0, 10, 480])  # win wall 1
        pygame.draw.rect(screen, BLACK,
                         [1070, 510, 10, 288])  # win wall 2
        self.walls = [pygame.draw.rect(screen, BLACK,
                                       [1070, 0, 10, 480]),  # win wall 1
                      pygame.draw.rect(screen, BLACK,
                                       [1070, 510, 10, 288])  # win wall 2
                      ]


class HardLevel1(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut1_text = dsnclass.Text("small steps", (210, 400), 75, "impact",
                                       GREY,
                                       None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)

    #         if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
    #                 self.victory_time:
    #             self.change_scene(EasyLevel2(0, 300, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 60, 20, 30])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]),
                          # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]),
                          # roof
                          pygame.draw.rect(screen, BLACK, [700, 540, 150, 10]),
                          # plat 1
                          pygame.draw.rect(screen, BLACK, [510, 510, 150, 10]),
                          # plat 2
                          pygame.draw.rect(screen, BLACK, [320, 480, 150, 10]),
                          # plat 3
                          pygame.draw.rect(screen, BLACK, [130, 450, 150, 10]),
                          # plat 4
                          pygame.draw.rect(screen, BLACK, [0, 460, 150, 10]),
                          # plat 4.5
                          pygame.draw.rect(screen, BLACK, [320, 420, 150, 10]),
                          # plat 5
                          pygame.draw.rect(screen, BLACK, [510, 390, 150, 10]),
                          # plat 6
                          pygame.draw.rect(screen, BLACK, [700, 360, 150, 10]),
                          # plat 7
                          pygame.draw.rect(screen, BLACK, [900, 330, 100, 10]),
                          # plat 8
                          pygame.draw.rect(screen, BLACK, [1000, 340, 180, 10]),
                          # plat 8.5
                          pygame.draw.rect(screen, BLACK, [700, 300, 150, 10]),
                          # plat 9
                          pygame.draw.rect(screen, BLACK, [510, 270, 150, 10]),
                          # plat 10
                          pygame.draw.rect(screen, BLACK, [320, 240, 150, 10]),
                          # plat 11
                          pygame.draw.rect(screen, BLACK, [130, 210, 150, 10]),
                          # plat 12
                          pygame.draw.rect(screen, BLACK, [0, 220, 150, 10]),
                          # plat 12.5
                          pygame.draw.rect(screen, BLACK, [320, 180, 150, 10]),
                          # plat 13
                          pygame.draw.rect(screen, BLACK, [510, 150, 150, 10]),
                          # plat 14
                          pygame.draw.rect(screen, BLACK, [700, 120, 150, 10]),
                          # plat 15
                          pygame.draw.rect(screen, BLACK, [900, 90, 150, 10])
                          # plat 16
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]),
                      # side wall right
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 580])
                      # side wall left
                      ]
