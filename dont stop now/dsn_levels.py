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
        if not self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.player.xpos = self.x_spawn
            self.player.ypos = self.y_spawn
            self.player.direction = 1

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
        current_spawn = EasyLevel5(37, 518, 1)
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
            self.change_scene(EasyLevel4(37, 489, 1))

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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms =  [
            pygame.draw.rect(screen, BLACK, [0, 547, 1080, 29]), # roof
            pygame.draw.rect(screen, BLACK, [0, 0, 1078, 29]), # floor
            pygame.draw.rect(screen, BLACK, [0, 0, 26, 575]), # left wall
            pygame.draw.rect(screen, BLACK, [168, 487, 40, 64]), # bottom A stand 1
            pygame.draw.rect(screen, BLACK, [0, 512, 178, 41]), # right wall
            pygame.draw.rect(screen, BLACK, [325, 487, 40, 64]), # bottom A stand 2
            pygame.draw.rect(screen, BLACK, [168, 477, 197, 16]), # bottom A platform
            pygame.draw.rect(screen, BLACK, [547, 248, 59, 116]), # bottom G stand pt.3
            pygame.draw.rect(screen, BLACK, [714, 418, 87, 22]), # botttom G hook
            pygame.draw.rect(screen, BLACK, [626, 455, 152, 23]), # bottom G hanging thing
            pygame.draw.rect(screen, BLACK, [736, 428, 42, 80]), # botoom G hook stand
            pygame.draw.rect(screen, BLACK, [566, 503, 212, 44]), # bottom G base 
            pygame.draw.rect(screen, BLACK, [168, 338, 41, 91]), # left side A top
            pygame.draw.rect(screen, BLACK, [326, 338, 41, 91]), # right side A top
            pygame.draw.rect(screen, BLACK, [168, 413, 197, 16]), # top A bottom part
            pygame.draw.rect(screen, BLACK, [851, 378, 206, 38]), # below e platform
            pygame.draw.rect(screen, BLACK, [822, 212, 38, 136]), # e stand
            pygame.draw.rect(screen, BLACK, [550, 478, 55, 91]), # bottom G stand pt.1
            pygame.draw.rect(screen, BLACK, [547, 314, 59, 116]), # bottom G stand pt.2
            pygame.draw.rect(screen, BLACK, [936, 309, 125, 15]), # bottom E teeth jump
            pygame.draw.rect(screen, BLACK, [899, 238, 160, 14]), # top E teeth jump
            pygame.draw.rect(screen, BLACK, [1057, 0, 26, 575]), # second right wall
            pygame.draw.rect(screen, BLACK, [821, 198, 200, 18]), # top E
            pygame.draw.rect(screen, BLACK, [717, 236, 61, 73]), # bottom G jumping to hook block
            pygame.draw.rect(screen, BLACK, [388, 309, 142, 98]), # platform inbewteen A and G
            pygame.draw.rect(screen, BLACK, [547, 182, 231, 70]), # bottom G top 
            pygame.draw.rect(screen, BLACK, [421, 139, 82, 23]), # top g hook
            pygame.draw.rect(screen, BLACK, [821, 340, 199, 21]), # bottom E
            pygame.draw.rect(screen, BLACK, [821, 272, 199, 21]), # middle E
            pygame.draw.rect(screen, BLACK, [168, 287, 199, 91]), # top part of A
            pygame.draw.rect(screen, BLACK, [443, 158, 28, 47]), # top G hook stand
            pygame.draw.rect(screen, BLACK, [201, 198, 270, 37]), # top down G block
            pygame.draw.rect(screen, BLACK, [201, 17, 43, 126]), # top g hieght
            pygame.draw.rect(screen, BLACK, [520, 108, 49, 23]), # left side big O
            pygame.draw.rect(screen, BLACK, [775, 108, 49, 23]), # right side big O
            pygame.draw.rect(screen, BLACK, [520, 128, 304, 23]), # big O bottom
            pygame.draw.rect(screen, BLACK, [520, 8, 304, 57]), # top big O
            pygame.draw.rect(screen, BLACK, [12, 225, 54, 15]), # JUMPINNG O TO G TO O
            pygame.draw.rect(screen, LIGHT_RED, [257, 311, 14, 96]), # eye of A
            pygame.draw.rect(screen, BLACK, [866, 97, 21, 77]), # bottom F
            pygame.draw.rect(screen, BLACK, [882, 121, 47, 21]), # F hieght
            pygame.draw.rect(screen, BLACK, [866, 90, 192, 21]), # top F
            pygame.draw.rect(screen, BLACK, [444, 512, 42, 38]), # SUPER ANNOYING BLOCK - dont remove
            pygame.draw.rect(screen, BLACK, [67, 254, 111, 12]), # below O platform
            pygame.draw.rect(screen, BLACK, [166, 192, 14, 35]), #right side O
            pygame.draw.rect(screen, BLACK, [111, 194, 15, 32]), # left side O
            pygame.draw.rect(screen, BLACK, [111, 218, 68, 10]), # bottom O
            pygame.draw.rect(screen, BLACK, [111, 189, 69, 12]), # top side O
            pygame.draw.rect(screen, BLACK, [201, 174, 42, 50]), # top G enterance
            pygame.draw.rect(screen, BLACK, [295, 170, 175, 15])
        ]

        self.win_zones = [pygame.draw.rect(screen, CYAN, [1057, 55, 27, 35])]


class EasyLevel5(LevelScene):  # letters
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
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms =  [
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

class EasyLevel6(LevelScene):  # letters
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

        # if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
        #         self.victory_time:
        #     self.change_scene(EasyLevel6(21, 21, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img,
                    self.Tut1_text.text_rect)  # draw text on screen

    def render_level(self, screen):
        LevelScene.render(self, screen)

        self.platforms =  [
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
