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
                self.player.alive = True
            if every_key == pygame.K_ESCAPE:
                self.player.freeze = not self.player.freeze
            if (every_key == pygame.K_q) and self.player.freeze:
                self.close_game()

        if not (pygame.K_w in pressed or pygame.K_SPACE in pressed or
            pygame.K_UP in pressed) and (held[pygame.K_SPACE] or
            held[pygame.K_w] or held[pygame.K_UP]) and \
                not self.player.enable_gravity and self.player.alive:
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump
            self.player.jump_sound_1.play()

    def update(self):
        if self.player.square_render is None:   # very important, else game crashes
            return None

        if self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.deaths += self.player.death(self.death_zones)
            # print(self.deaths)    # todo: add death counter in render_text class
            # @shoc71 - commented out cuz its annoying for me
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
                self.change_scene(TutorialLevel1(12, 320, 1)) # MAKE NOTE OF THIS
                # self.change_scene (EasyLevel2(12, 12, 1)) # changing the spawn to skip the tutorials

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

########################################################################################
################################  tutorial levels   ####################################
########################################################################################

class TutorialLevel1(LevelScene): # Hallway
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut6_text = dsnclass.Text("Hallway", (600, 400), 45, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel2(12, 80, 1)) # spawn for next level

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, CYAN, [1070, 308, 20, 40])
        self.win_zones = [win1]

        platform3 = pygame.draw.rect(screen, BLACK, [0, 288, 1100, 20]) # spawn platform extended
        platform4 = pygame.draw.rect(screen, BLACK, [0, 348, 1100, 20]) # mid-platform
        self.platforms = [platform3, platform4]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 308])
        wall2 = pygame.draw.rect(screen, BLACK, [1070, 348, 10, 250])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
        self.walls = [wall1, wall2, wall4]

class TutorialLevel2(LevelScene): # DropGuide to Solution
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut6_text = dsnclass.Text("Guide to Solution", (600, 400), 45, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel3(12, 297, 1)) # spawn for next level

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

    def render_level(self, screen):
        # No death zones in this level!
        self.death_zones = []

        win1 = pygame.draw.rect(screen, CYAN, [1070, 528, 20, 40])
        self.win_zones = [win1]

        platform3 = pygame.draw.rect(screen, BLACK, [0, 90, 800, 40]) # spawn platform extended
        platform4 = pygame.draw.rect(screen, BLACK, [200, 308, 880, 40]) # mid-platform
        platform1 = pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]) # floor
        self.platforms = [platform1, platform3, platform4]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 528])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
        self.walls = [wall1, wall4]

class TutorialLevel3(LevelScene): # jump over box
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut6_text = dsnclass.Text("Hit Space/up/w to jump", (600, 400), 45, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel4(12, 200, 1)) # tut level 4 spawn

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

        # visual-only, no collision necessary
        block1 = pygame.draw.rect(screen, BLACK, [0, 310, 1080, 576])

        self.platforms = [platform1, platform2]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 278])
        wall2 = pygame.draw.rect(screen, BLACK, [350, 290, 10, 30])
        wall3 = pygame.draw.rect(screen, BLACK, [640, 290, 10, 30])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 320])
        self.walls = [wall1, wall2, wall3, wall4]


class TutorialLevel4(LevelScene): # mind the gap
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut6_text = dsnclass.Text("Mind the Gap", (600, 400), 45, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel1(12, 292, 1)) # easy level 1 spawn

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

        platform1 = pygame.draw.rect(screen, BLACK, [0, 210, 490, 366])
        platform2 = pygame.draw.rect(screen, BLACK, [540, 210, 540, 366])

        self.platforms = [platform1, platform2]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 180])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 210])
        self.walls = [wall1, wall4]


#####################################################################################
###################################   easy levels   #################################
#####################################################################################

# left to right order for numbering platforms

class EasyLevel1(LevelScene): # candles
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut1_text = dsnclass.Text("candles", (210, 400), 75, "impact", GREY,
                              None)
        self.music = dsnclass.Music(music_value)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)
    
    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(EasyLevel2(12, 12, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)
        screen.blit(self.Tut1_text.text_img, self.Tut1_text.text_rect) # draw text on screen
    
    def render_level(self, screen):
        LevelScene.render(self, screen)

        death1 = pygame.draw.rect(screen, LIGHT_RED, [125, 110, 10, 20]) # candle light 1
        death2 = pygame.draw.rect(screen, LIGHT_RED, [425, 110, 10, 20]) # candle light 2
        death3 = pygame.draw.rect(screen, LIGHT_RED, [725, 110, 10, 20]) # candle light 3
        death4 = pygame.draw.rect(screen, LIGHT_RED, [990, 110, 10, 20]) # candle light 4
        self.death_zones = [death1, death2, death3, death4]

        platform1 = pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]) # floor
        platform2 = pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]) # roof
        block1 = pygame.draw.rect(screen, BLACK, [0, 300, 1100, 276]) # block - cut
        block2 = pygame.draw.rect(screen, BLACK, [0, 0, 1100, 90]) # block - cut
        platform3 = pygame.draw.rect(screen, BLACK, [40, 270, 200, 10]) # plat 1
        platform4 = pygame.draw.rect(screen, BLACK, [340, 240, 200, 10]) # plat 2
        platform5 = pygame.draw.rect(screen, BLACK, [640, 210, 200, 10]) # plat 3
        platform6 = pygame.draw.rect(screen, BLACK, [940, 180, 100, 10]) # plat 4

        self.platforms = [platform1, platform2, block1, platform3,
                          platform4, platform5, platform6, block2]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]) # side wall right
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]) # side wall left
        wall2 = pygame.draw.rect(screen, BLACK, [125, 130, 10, 120]) # candle stick 1
        wall3 = pygame.draw.rect(screen, BLACK, [425, 130, 10, 90]) # candle stick 2
        wall5 = pygame.draw.rect(screen, BLACK, [725, 120, 10, 70]) # candle stick 3
        wall6 = pygame.draw.rect(screen, BLACK, [990, 120, 10, 40]) # candle stick 4
        self.walls = [wall1, wall4, wall2, wall3, wall5, wall6]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 190, 20, 30])
        self.win_zones = [win1]

class EasyLevel2(LevelScene): # block maze 5
    def __init__(self, x_spawn, y_spawn, music_value):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut1_text = dsnclass.Text("block maze 5", (210, 400), 75, "impact", GREY,
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

        platform1 = pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]) # floor
        platform2 = pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]) # roof
        block1 = pygame.draw.rect(screen, BLACK, [0, 300, 1100, 276]) # block - cut
        platform4 = pygame.draw.rect(screen, BLACK, [250, 40, 600, 10]) # plat 2 - x250/y40
        platform5 = pygame.draw.rect(screen, BLACK, [900, 60, 50, 10]) # plat 1 - x900/y60
        platform6 = pygame.draw.rect(screen, BLACK, [1000, 70, 100, 10]) # plat 1 - x1000/y70
        block2 = pygame.draw.rect(screen, BLACK, [950, 40, 50, 20]) # block - y40/y80
        platform7 = pygame.draw.rect(screen, BLACK, [0, 85, 150, 10]) # plat 1 - x0/y85
        platform8 = pygame.draw.rect(screen, BLACK, [200, 85, 675, 10]) # plat 1 - x200/y85
        block3 = pygame.draw.rect(screen, BLACK, [550, 50, 200, 35]) # block - x400/y50
        platform9 = pygame.draw.rect(screen, BLACK, [250, 130, 300, 10]) # plat 1 - x250/y130
        block4 = pygame.draw.rect(screen, BLACK, [0, 85, 125, 55]) # block - x0/y85
        platform10 = pygame.draw.rect(screen, BLACK, [650, 150, 450, 10]) # plat 1 - x650/y150
        platform11 = pygame.draw.rect(screen, BLACK, [0, 180, 450, 10])
        platform13 = pygame.draw.rect(screen, BLACK, [50, 265, 300, 10])
        platform12 = pygame.draw.rect(screen, BLACK, [500, 180, 150, 10])
        block5 = pygame.draw.rect(screen, BLACK, [850, 120, 250, 30])
        platform14 = pygame.draw.rect(screen, BLACK, [665, 265, 450, 10])
        platform15 = pygame.draw.rect(screen, BLACK, [800, 230, 220, 10])
        platform16 = pygame.draw.rect(screen, BLACK, [675, 200, 100, 10])
        block6 = pygame.draw.rect(screen, BLACK, [850, 275, 100, 25])
        block7 = pygame.draw.rect(screen, BLACK, [450, 280, 125, 20])
        block8 = pygame.draw.rect(screen, BLACK, [480, 240, 62, 20])

        self.platforms = [platform1, platform2, block1,
                          platform4, platform5, platform6, block2,
                          platform8, platform7, platform9, platform10,
                          platform11, platform12, block5, block3, block4,
                          platform13, platform14, block6, block7, block8,
                          platform15, platform16,
                          pygame.draw.rect(screen, BLACK, [0, 40, 200, 10]) # plat 1 - x0/y40
                          ]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]) # side wall right
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]) # side wall left
        wall2 = pygame.draw.rect(screen, BLACK, [400, 0, 10, 40]) # wall - x400/y0
        wall3 = pygame.draw.rect(screen, BLACK, [940, 40, 10, 20]) # wall - x940/y40
        wall5 = pygame.draw.rect(screen, BLACK, [990, 40, 10, 40]) # wall - x990/y40
        wall6 = pygame.draw.rect(screen, BLACK, [500, 140, 10, 40]) # candle stick 4
        wall7 = pygame.draw.rect(screen, BLACK, [400, 104, 10, 20])
        self.walls = [wall1, wall4, wall2, wall3, wall5, wall6, wall7]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 50, 20, 20])
        self.win_zones = [win1]

        # guideline_x_100 = pygame.draw.line(screen, LIME_GREEN, [100,0], [100,600], 2)
        # guideline_x_200 = pygame.draw.line(screen, LIME_GREEN, [200,0], [200,600], 2)
        # guideline_x_300 = pygame.draw.line(screen, LIME_GREEN, [300,0], [300,600], 2)
        # guideline_x_400 = pygame.draw.line(screen, LIME_GREEN, [400,0], [400,600], 2)
        # guideline_x_500 = pygame.draw.line(screen, LIME_GREEN, [500,0], [500,600], 2)
        # guideline_x_600 = pygame.draw.line(screen, LIME_GREEN, [600,0], [600,600], 2)
        # guideline_x_700 = pygame.draw.line(screen, LIME_GREEN, [700,0], [700,600], 2)
        # guideline_x_800 = pygame.draw.line(screen, LIME_GREEN, [800,0], [800,600], 2)
        # guideline_x_900 = pygame.draw.line(screen, LIME_GREEN, [900,0], [900,600], 2)
        # guideline_x_1000 = pygame.draw.line(screen, LIME_GREEN, [1000,0], [1000,600], 2)
        # guideline_x_50 = pygame.draw.line(screen, LIME_GREEN, [50,0], [50,600], 2)
        # guideline_x_150 = pygame.draw.line(screen, LIME_GREEN, [150,0], [150,600], 2)
        # guideline_x_250 = pygame.draw.line(screen, LIME_GREEN, [250,0], [250,600], 2)
        # guideline_x_350 = pygame.draw.line(screen, LIME_GREEN, [350,0], [350,600], 2)
        # guideline_x_450 = pygame.draw.line(screen, LIME_GREEN, [450,0], [450,600], 2)
        # guideline_x_550 = pygame.draw.line(screen, LIME_GREEN, [550,0], [550,600], 2)
        # guideline_x_650 = pygame.draw.line(screen, LIME_GREEN, [650,0], [650,600], 2)
        # guideline_x_750 = pygame.draw.line(screen, LIME_GREEN, [750,0], [750,600], 2)
        # guideline_x_850 = pygame.draw.line(screen, LIME_GREEN, [850,0], [850,600], 2)
        # guideline_x_950 = pygame.draw.line(screen, LIME_GREEN, [950,0], [950,600], 2)
        # guideline_x_1050 = pygame.draw.line(screen, LIME_GREEN, [1050,0], [1050,600], 2)
        # guideline_y_100 = pygame.draw.line(screen, LIME_GREEN, [0,100], [1100,100], 2)
        # guideline_y_200 = pygame.draw.line(screen, LIME_GREEN, [0,200], [1100,200], 2)
        # guideline_y_300 = pygame.draw.line(screen, LIME_GREEN, [0,300], [1100,300], 2)
        # guideline_y_400 = pygame.draw.line(screen, LIME_GREEN, [0,400], [1100,400], 2)
        # guideline_y_500 = pygame.draw.line(screen, LIME_GREEN, [0,500], [1100,500], 2)
        # guideline_y_50 = pygame.draw.line(screen, LIME_GREEN, [0,50], [1100,50], 2)
        # guideline_y_150 = pygame.draw.line(screen, LIME_GREEN, [0,150], [1100,150], 2)
        # guideline_y_250 = pygame.draw.line(screen, LIME_GREEN, [0,250], [1100,250], 2)
        # guideline_y_350 = pygame.draw.line(screen, LIME_GREEN, [0,350], [1100,350], 2)
        # guideline_y_450 = pygame.draw.line(screen, LIME_GREEN, [0,450], [1100,450], 2)
        # guideline_y_550 = pygame.draw.line(screen, LIME_GREEN, [0,550], [1100,550], 2)
#####################################################################################
##############################   unorganized levels   ###############################
#####################################################################################

# unorganized levels

class TutorialLevel14(LevelScene): # daz maze
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


class TutorialLevel24(LevelScene): # red floor
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


class TutorialLevel5(LevelScene): #sanwich
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
            self.change_scene(TutorialLevel6(0, 140, 1))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut7_text.text_img, self.Tut7_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        death1 = pygame.draw.rect(screen, RED,
                                  [505, 370, 180, 600])  # bottom red block 1
        death2 = pygame.draw.rect(screen, RED,
                                  [505, 0, 180, 330])  # top red block 1
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
                                     [505, 360, 180, 10])  # sandwich bottom 1
        platform4 = pygame.draw.rect(screen, BLACK,
                                     [750, 340, 250, 10])  # sandwich bottom 2
        platform5 = pygame.draw.rect(screen, BLACK,
                                     [505, 330, 180, 10])  # sandwich top 1
        platform6 = pygame.draw.rect(screen, BLACK,
                                     [750, 280, 250, 10])  # sandwich top 2
        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6]

        wall1 = pygame.draw.rect(screen, BLACK,
                                 [1070, 0, 10, 278])  # win wall 1
        wall2 = pygame.draw.rect(screen, BLACK,
                                 [1070, 308, 10, 288])  # win wall 2
        self.walls = [wall1, wall2]


class TutorialLevel6(LevelScene):
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
            self.change_scene(TutorialLevel7(0, 120, 1))

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

        platform1 = pygame.draw.rect(screen, BLACK, [0, 567, 1100, 10]) # floor
        platform2 = pygame.draw.rect(screen, BLACK, [0, 0, 1100, 10]) # roof
        platform3 = pygame.draw.rect(screen, BLACK, [700, 540, 150, 10]) # plat 1
        platform4 = pygame.draw.rect(screen, BLACK, [510, 510, 150, 10]) # plat 2
        platform5 = pygame.draw.rect(screen, BLACK, [320, 480, 150, 10]) # plat 3
        platform6 = pygame.draw.rect(screen, BLACK, [130, 450, 150, 10]) # plat 4
        platform11 = pygame.draw.rect(screen, BLACK, [0, 460, 150, 10]) # plat 4.5
        platform7 = pygame.draw.rect(screen, BLACK, [320, 420, 150, 10]) # plat 5
        platform8 = pygame.draw.rect(screen, BLACK, [510, 390, 150, 10]) # plat 6
        platform9 = pygame.draw.rect(screen, BLACK, [700, 360, 150, 10]) # plat 7
        platform10 = pygame.draw.rect(screen, BLACK, [900, 330, 100, 10]) # plat 8
        platform12 = pygame.draw.rect(screen, BLACK, [1000, 340, 180, 10]) # plat 8.5
        platform13 = pygame.draw.rect(screen, BLACK, [700, 300, 150, 10]) # plat 9
        platform14 = pygame.draw.rect(screen, BLACK, [510, 270, 150, 10]) # plat 10
        platform15 = pygame.draw.rect(screen, BLACK, [320, 240, 150, 10]) # plat 11
        platform16 = pygame.draw.rect(screen, BLACK, [130, 210, 150, 10]) # plat 12
        platform17 = pygame.draw.rect(screen, BLACK, [0, 220, 150, 10]) # plat 12.5
        platform18 = pygame.draw.rect(screen, BLACK, [320, 180, 150, 10]) # plat 13
        platform19 = pygame.draw.rect(screen, BLACK, [510, 150, 150, 10]) # plat 14
        platform20 = pygame.draw.rect(screen, BLACK, [700, 120, 150, 10]) # plat 15
        platform21 = pygame.draw.rect(screen, BLACK, [900, 90, 150, 10]) # plat 16

        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6, platform7, platform8,
                          platform9, platform10, platform11, platform12,
                          platform13, platform14, platform15, platform16,
                          platform17, platform18, platform19, platform20,
                          platform21]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 580]) # side wall right
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 580]) # side wall left
        self.walls = [wall1, wall4]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 60, 20, 30])
        self.win_zones = [win1]
