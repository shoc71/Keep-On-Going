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
                0 < self.player.jumps:
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump
            self.player.jump_sound_1.play()
            self.player.jumps += 1

        for every_key in pressed:
            """   removed the instant return to menu, this will be apart of the
            pause menu now
            """
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive:
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
        if not self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.player.xpos = self.x_spawn
            self.player.ypos = self.y_spawn
            self.player.direction = "right"

        if 580 + self.player.height < self.player.ypos:
            self.player.alive = False
            self.deaths += 1

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
        #start_spawn
        current_spawn = TutorialLevel1(12, 320, 1) # Added this in so it's less painful to find spawn
        current_spawn = EasyLevel4(12, 552, 1)
        self.options = [current_spawn, Filler(), Filler(), Filler()]
        #SPEANWNSS
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

    def input(self, pressed, held):
        """Do not use LevelScene for input since we don't want to control
        the character on the menu"""
        for every_key in pressed:
            if every_key in [pygame.K_SPACE, pygame.K_w]:
                self.victory_counter = len(self.victory_text)
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
        self.player.alive = True
        self.victory_counter = len(self.victory_text)
        if (random.randint(1, 2500) <= 15) and not self.player.enable_gravity:
            self.player.jumps += 1
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle
        LevelScene.render_text(self, screen)  # Text or Front-most
        screen.blit(self.title_splash.text_img, self.title_splash.text_rect)
        screen.blit(self.title_text.text_img, self.title_text.text_rect)
        screen.blit(self.title_text_2.text_img, self.title_text_2.text_rect)
        screen.blit(self.title_text_s1.text_img, self.title_text_s1.text_rect)
        screen.blit(self.title_text_s2.text_img, self.title_text_s2.text_rect)
        screen.blit(self.title_text_s3.text_img, self.title_text_s3.text_rect)
        screen.blit(self.title_text_s4.text_img, self.title_text_s4.text_rect)

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

        pygame.draw.rect(screen, DARK_RED, self.option_select[self.option_count], 2)


class Filler(dsnclass.Scene):
    def __init__(self):
        dsnclass.Scene.__init__(self)
        self.level_id = -1
        self.filler_text = dsnclass.Text("THERE'S NOTHING HERE, PRESS R TO GO BACK",
                          (540, 213), 50, "impact", DARK_RED, None)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360, 0))

    def render(self, screen):
        screen.fill(WHITE)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)


class LevelSelect(dsnclass.Scene):
    def __init__(self):
        dsnclass.Scene.__init__(self)
        self.filler_text = dsnclass.Text("Choose A Level",
                          (540, 153), 50, "impact", YELLOW, None)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360, 0))

    def render(self, screen):
        screen.fill(WHITE)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)


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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 308, 20, 40])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 288, 1100, 20]),  # spawn platform extended
                          pygame.draw.rect(screen, BLACK, [0, 348, 1100, 20])   # mid-platform
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 528, 20, 40])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 90, 800, 40]),  # spawn platform extended
                          pygame.draw.rect(screen, BLACK, [200, 308, 880, 40]),  # mid-platform
                          pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10])   # floor
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 278, 20, 40])]


        pygame.draw.rect(screen, BLACK, [0, 310, 1080, 576])    # visual-only, no collision necessary
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

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


#####################################################################################
###################################   easy levels   #################################
#####################################################################################


# left to right order for numbering platforms


class EasyLevel1(LevelScene):   # candles
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img, self.Tut1_text.text_rect) # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.death_zones = [pygame.draw.rect(screen, LIGHT_RED, [125, 110, 10, 20]), # candle light 1
                            pygame.draw.rect(screen, LIGHT_RED, [425, 110, 10, 20]), # candle light 2
                            pygame.draw.rect(screen, LIGHT_RED, [725, 110, 10, 20]), # candle light 3
                            pygame.draw.rect(screen, LIGHT_RED, [990, 110, 10, 20]), # candle light 4
                            ]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]), # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]), # roof
                          pygame.draw.rect(screen, BLACK, [0, 300, 1100, 276]), # block - cut
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 90]), # block - cut
                          pygame.draw.rect(screen, BLACK, [40, 270, 200, 10]), # plat 1
                          pygame.draw.rect(screen, BLACK, [340, 240, 200, 10]), # plat 2
                          pygame.draw.rect(screen, BLACK, [640, 210, 200, 10]), # plat 3
                          pygame.draw.rect(screen, BLACK, [940, 180, 100, 10]) # plat 4
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]), # side wall right
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]), # side wall left
                      pygame.draw.rect(screen, BLACK, [125, 130, 10, 120]), # candle stick 1
                      pygame.draw.rect(screen, BLACK, [425, 130, 10, 90]), # candle stick 2
                      pygame.draw.rect(screen, BLACK, [725, 120, 10, 70]), # candle stick 3
                      pygame.draw.rect(screen, BLACK, [990, 120, 10, 40]), # candle stick 4]
                      ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 190, 20, 30])]

class EasyLevel2(LevelScene):   # mouse
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img, self.Tut1_text.text_rect) # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 300, 1100, 277]), # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]), # roof
                          pygame.draw.rect(screen, BLACK, [350, 130, 500, 200]), # mouse body
                          pygame.draw.rect(screen, YELLOW, [0, 200, 100, 100]), # cheese
                          pygame.draw.rect(screen, BLACK, [230, 270, 120, 30]), # mouse arm
                          pygame.draw.rect(screen, BLACK, [120, 235, 100, 10]), # platform above arm
                          pygame.draw.rect(screen, LIGHT_PINK, [320, 180, 30, 30]), # mouse nose
                          pygame.draw.rect(screen, BLACK, [140, 160, 100, 10]), # platform above above the cheese
                          pygame.draw.rect(screen, BLACK, [450, 100, 50, 30]), # mouse ear
                          pygame.draw.rect(screen, LIGHT_PINK, [850, 240, 300, 25]) # mouse tail
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]), # side wall right
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]), # side wall left
                      ]
        
        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 190, 20, 30])] # win condition

        self.draw = [pygame.draw.rect(screen, WHITE, [385, 165, 20, 20]), # mouse eye
                     pygame.draw.rect(screen, LIGHT_PINK, [260, 270, 90, 30]), # mouse arm detail
                     pygame.draw.rect(screen, LIGHT_PINK, [460, 110, 25, 20]), # mouse ear detail
                     pygame.draw.rect(screen, BLACK, [30, 210, 15, 20]), # cheese black hole - left hole
                     pygame.draw.rect(screen, BLACK, [15, 270, 20, 20]), # cheese black hole - left square
                     pygame.draw.rect(screen, BLACK, [50, 240, 15, 20]), # cheese black hole - middle hole
                     pygame.draw.rect(screen, BLACK, [70, 270, 15, 20]), # cheese black hole - big left
                     pygame.draw.line(screen, WHITE, [360, 200], [450, 190], 5), # mouse whisker #1
                     pygame.draw.line(screen, WHITE, [360, 210], [450, 215], 5), # mouse whisker #2
                     pygame.draw.line(screen, WHITE, [360, 220], [450, 245], 5), # mouse whisker #3
                     pygame.draw.rect(screen, BLACK, [870, 240, 10, 25]), # mouse tail detail #1
                     pygame.draw.rect(screen, BLACK, [900, 240, 10, 25]), # mouse tail detail #2
                     pygame.draw.rect(screen, BLACK, [930, 240, 10, 25]), # mouse tail detail #3
                     pygame.draw.rect(screen, BLACK, [960, 240, 10, 25]), # mouse tail detail #4
                     pygame.draw.rect(screen, BLACK, [990, 240, 10, 25]), # mouse tail detail #5
                     pygame.draw.rect(screen, BLACK, [1020, 240, 10, 25]), # mouse tail detail #6
                     pygame.draw.rect(screen, BLACK, [1050, 240, 10, 25]), # mouse tail detail #7
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
            self.change_scene(EasyLevel4(12, 12, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]) , # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]),  # roof
                          pygame.draw.rect(screen, BLACK,
                                                  [0, 300, 1100, 276]),  # block - cut
                          pygame.draw.rect(screen, BLACK,
                                                     [250, 40, 600, 10]), # plat 2 - x250/y40
                          pygame.draw.rect(screen, BLACK,
                                                     [900, 60, 50, 10]),  # plat 1 - x900/y60
                          pygame.draw.rect(screen, BLACK,
                                                     [1000, 70, 100, 10]),  # plat 1 - x1000/y70
                          pygame.draw.rect(screen, BLACK,
                                                  [950, 40, 50, 20]),  # block - y40/y80
                          pygame.draw.rect(screen, BLACK,
                                                     [0, 85, 150, 10]),  # plat 1 - x0/y85
                          pygame.draw.rect(screen, BLACK,
                                                     [200, 85, 675, 10]),  # plat 1 - x200/y85
                          pygame.draw.rect(screen, BLACK,
                                                  [550, 50, 200, 35]),  # block - x400/y50
                          pygame.draw.rect(screen, BLACK,
                                                     [250, 130, 300, 10]),  # plat 1 - x250/y130
                          pygame.draw.rect(screen, BLACK,
                                                  [0, 85, 125, 55]),  # block - x0/y85
                          pygame.draw.rect(screen, BLACK,
                                                      [650, 150, 450, 10]),  # plat 1 - x650/y150
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


class EasyLevel4(LevelScene):  # block maze 5
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.level_id = 8
        self.Tut1_text = dsnclass.Text("incomplete lvl. letter", (410, 400), 60, "impact",
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]) , # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]),  # roof
                          pygame.draw.rect(screen, BLACK, [150, 536, 200, 40]), # bottom A
                        #   pygame.draw.rect(screen, BLACK, [500, 546, 150, 30]), # bottom G1
                          pygame.draw.rect(screen, BLACK, [500, 526, 50, 50]), # bottom G jump
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK,
                                 [1070, 0, 10, 580]),  # side wall right
                      pygame.draw.rect(screen, BLACK,
                                             [0, 0, 10, 580]),  # side wall left
                    #   pygame.draw.rect(screen, EDIT_DARK_GREEN, [645, 496, 5, 50]) # bottom G wall
                      ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 50, 20, 20])]

        guideline_x_100 = pygame.draw.line(screen, LIME_GREEN, [100,0], [100,600], 2)
        guideline_x_200 = pygame.draw.line(screen, LIME_GREEN, [200,0], [200,600], 2)
        guideline_x_300 = pygame.draw.line(screen, LIME_GREEN, [300,0], [300,600], 2)
        guideline_x_400 = pygame.draw.line(screen, LIME_GREEN, [400,0], [400,600], 2)
        guideline_x_500 = pygame.draw.line(screen, LIME_GREEN, [500,0], [500,600], 2)
        guideline_x_600 = pygame.draw.line(screen, LIME_GREEN, [600,0], [600,600], 2)
        guideline_x_700 = pygame.draw.line(screen, LIME_GREEN, [700,0], [700,600], 2)
        guideline_x_800 = pygame.draw.line(screen, LIME_GREEN, [800,0], [800,600], 2)
        guideline_x_900 = pygame.draw.line(screen, LIME_GREEN, [900,0], [900,600], 2)
        guideline_x_1000 = pygame.draw.line(screen, LIME_GREEN, [1000,0], [1000,600], 2)
        guideline_x_50 = pygame.draw.line(screen, LIME_GREEN, [50,0], [50,600], 2)
        guideline_x_150 = pygame.draw.line(screen, LIME_GREEN, [150,0], [150,600], 2)
        guideline_x_250 = pygame.draw.line(screen, LIME_GREEN, [250,0], [250,600], 2)
        guideline_x_350 = pygame.draw.line(screen, LIME_GREEN, [350,0], [350,600], 2)
        guideline_x_450 = pygame.draw.line(screen, LIME_GREEN, [450,0], [450,600], 2)
        guideline_x_550 = pygame.draw.line(screen, LIME_GREEN, [550,0], [550,600], 2)
        guideline_x_650 = pygame.draw.line(screen, LIME_GREEN, [650,0], [650,600], 2)
        guideline_x_750 = pygame.draw.line(screen, LIME_GREEN, [750,0], [750,600], 2)
        guideline_x_850 = pygame.draw.line(screen, LIME_GREEN, [850,0], [850,600], 2)
        guideline_x_950 = pygame.draw.line(screen, LIME_GREEN, [950,0], [950,600], 2)
        guideline_x_1050 = pygame.draw.line(screen, LIME_GREEN, [1050,0], [1050,600], 2)
        guideline_y_100 = pygame.draw.line(screen, LIME_GREEN, [0,100], [1100,100], 2)
        guideline_y_200 = pygame.draw.line(screen, LIME_GREEN, [0,200], [1100,200], 2)
        guideline_y_300 = pygame.draw.line(screen, LIME_GREEN, [0,300], [1100,300], 2)
        guideline_y_400 = pygame.draw.line(screen, LIME_GREEN, [0,400], [1100,400], 2)
        guideline_y_500 = pygame.draw.line(screen, LIME_GREEN, [0,500], [1100,500], 2)
        guideline_y_50 = pygame.draw.line(screen, LIME_GREEN, [0,50], [1100,50], 2)
        guideline_y_150 = pygame.draw.line(screen, LIME_GREEN, [0,150], [1100,150], 2)
        guideline_y_250 = pygame.draw.line(screen, LIME_GREEN, [0,250], [1100,250], 2)
        guideline_y_350 = pygame.draw.line(screen, LIME_GREEN, [0,350], [1100,350], 2)
        guideline_y_450 = pygame.draw.line(screen, LIME_GREEN, [0,450], [1100,450], 2)
        guideline_y_550 = pygame.draw.line(screen, LIME_GREEN, [0,550], [1100,550], 2)


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
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut5_text.text_img, self.Tut5_text.text_rect)

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
                          pygame.draw.rect(screen, BLACK, [0, 326, 380, 10])    # this is intentional, move this around
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [600, 36, 10, 1340]),  # x,y , width/hieght - big right
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


class TutorialLevel5(LevelScene):  #sanwich
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
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut7_text.text_img, self.Tut7_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.death_zones = [pygame.draw.rect(screen, RED, [505, 370, 180, 600]),  # bottom red block 1
                            pygame.draw.rect(screen, RED, [505, 0, 180, 330]),  # top red block 1
                            pygame.draw.rect(screen, RED, [750, 350, 250, 230]),  # bottom red block 2
                            pygame.draw.rect(screen, RED, [750, 0, 250, 280]),  # top red block 2
                            ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 278, 10, 30])] # win box 1

        self.platforms = [pygame.draw.rect(screen, BLACK,
                                     [10, 110, 75, 10]),  # spawn platform
                          pygame.draw.rect(screen, BLACK,
                                     [310, 360, 100, 10]),  # dorp platfomr
                          pygame.draw.rect(screen, BLACK,
                                     [505, 360, 180, 10]),  # sandwich bottom 1
                          pygame.draw.rect(screen, BLACK,
                                     [750, 340, 250, 10]),  # sandwich bottom 2
                          pygame.draw.rect(screen, BLACK,
                                     [505, 330, 180, 10]),  # sandwich top 1
                          pygame.draw.rect(screen, BLACK,
                                     [750, 280, 250, 10])  # sandwich top 2
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
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])]  # win box

        # death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])# death floor
        # self.death_zones = [death1]

        self.platforms = [pygame.draw.rect(screen, BLACK,
                                     [0, 150, 200, 10]),  # spawn platform
                          pygame.draw.rect(screen, BLACK, [200, 100, 200, 10]),
        # platform3 = pygame.draw.rect(screen, BLACK, [500, 500, 200, 10])
                          pygame.draw.rect(screen, BLACK, [870, 530, 100, 10]),
                          pygame.draw.rect(screen, BLACK, [445, 300, 270, 10])  # new land
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
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

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
                                 [1070, 0, 10, 480]) , # win wall 1
                      pygame.draw.rect(screen, BLACK,
                                 [1070, 510, 10, 288])  # win wall 2
                      ]

class HardLevel1(LevelScene):
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut1_text = dsnclass.Text("small steps", (210, 400), 75, "impact", GREY,
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img, self.Tut1_text.text_rect) # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1070, 60, 20, 30])]

        self.platforms = [pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]), # floor
                          pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]), # roof
                          pygame.draw.rect(screen, BLACK, [700, 540, 150, 10]), # plat 1
                          pygame.draw.rect(screen, BLACK, [510, 510, 150, 10]), # plat 2
                          pygame.draw.rect(screen, BLACK, [320, 480, 150, 10]), # plat 3
                          pygame.draw.rect(screen, BLACK, [130, 450, 150, 10]), # plat 4
                          pygame.draw.rect(screen, BLACK, [0, 460, 150, 10]), # plat 4.5
                          pygame.draw.rect(screen, BLACK, [320, 420, 150, 10]), # plat 5
                          pygame.draw.rect(screen, BLACK, [510, 390, 150, 10]), # plat 6
                          pygame.draw.rect(screen, BLACK, [700, 360, 150, 10]), # plat 7
                          pygame.draw.rect(screen, BLACK, [900, 330, 100, 10]), # plat 8
                          pygame.draw.rect(screen, BLACK, [1000, 340, 180, 10]), # plat 8.5
                          pygame.draw.rect(screen, BLACK, [700, 300, 150, 10]), # plat 9
                          pygame.draw.rect(screen, BLACK, [510, 270, 150, 10]), # plat 10
                          pygame.draw.rect(screen, BLACK, [320, 240, 150, 10]), # plat 11
                          pygame.draw.rect(screen, BLACK, [130, 210, 150, 10]), # plat 12
                          pygame.draw.rect(screen, BLACK, [0, 220, 150, 10]), # plat 12.5
                          pygame.draw.rect(screen, BLACK, [320, 180, 150, 10]), # plat 13
                          pygame.draw.rect(screen, BLACK, [510, 150, 150, 10]), # plat 14
                          pygame.draw.rect(screen, BLACK, [700, 120, 150, 10]), # plat 15
                          pygame.draw.rect(screen, BLACK, [900, 90, 150, 10]) # plat 16
                          ]

        self.walls = [pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]), # side wall right
                      pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]) # side wall left
                      ]
