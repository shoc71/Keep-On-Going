import random
import pygame

#important initializers - could be moved with pygame.init()
fps = pygame.time.Clock()
pygame.mixer.init()

#colors
DARK_RED = (139,0,0)
YELLOW = (235, 195, 65)
BLACK = (0, 0, 0)
CYAN = (47, 237, 237)
RED = (194, 57, 33)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)
IMPACT_FONT = "impact"

c_key = False # this only exists becuz I need the c key to work

# Load sound effects
filepath_sfx = ("assets/audio/jump_sfx.wav")
jump_sound_1 = pygame.mixer.Sound(filepath_sfx)
jump_sound_1.set_volume(0.02) #out of 1 = 100%
# collect_coin_sound = pygame.mixer.Sound("collect_coin_sound.wav")

# Load background music
current_track_index = 0
music_tracks = [
    "assets/audio/main-menu.wav",
    "assets/audio/level-loop1_v2.wav",
    "assets/audio/work_around_lead_edited.wav",
    "assets/audio/credits.wav"
]
pygame.mixer.music.load(music_tracks[current_track_index])
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)  # Play the background music on a loop

# Function to switch background music based on level completion
def switch_music(level_complete):
    global current_track_index

    # if level_complete 
    if c_key == False:
        if level_complete:
            current_track_index += 1 # Increment the track index

            # Check if all tracks have been played, then loop back to the first track
            if current_track_index >= len(music_tracks):
                current_track_index = 0
            
            # Load and play the new background music track
            pygame.mixer.music.load(music_tracks[current_track_index])
            if current_track_index == 2:
                pygame.mixer.music.set_volume(0.15)
            if current_track_index == 3:
                pygame.mixer.music.set_volume(1.5)
            pygame.mixer.music.play(-1)  # Play the background music on a loop
    else:
        current_track_index = 0


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
            Text("DON'T", (310, 100), 100, IMPACT_FONT, YELLOW, None),
            Text("STOP", (570, 100), 100, IMPACT_FONT, YELLOW, None),
            Text("NOW", (820, 100), 100, IMPACT_FONT, YELLOW, None)
        ]
        self.pause_text = Text("PAUSED", (540, 213),
                               100, IMPACT_FONT, DARK_RED, None)
        self.pause_text_2 = Text("Press esc to unpause", (540, 280),
                               30, IMPACT_FONT, DARK_RED, None)
        self.pause_text_3 = Text("Press q to quit", (540, 315),
                               30, IMPACT_FONT, DARK_RED, None)

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_c:
                self.change_scene(MenuScene(40, 340))
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive:
                self.player.jump_ability = True
                self.player.jump_boost = self.player.max_jump
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
            self.player.collision_wall(self.platforms)
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
    def __init__(self, xspawn, yspawn):
        LevelScene.__init__(self, xspawn, yspawn)
        self.options = []
        self.respawns += 1
        self.mid_jump = False
        self.title_text = Text("Press Space or W To Start", (530, 100), 50, IMPACT_FONT,
                          YELLOW, None)
        self.title_text_2 = Text("Press esc to pause", (530, 150), 30, IMPACT_FONT,
                          YELLOW, None)# 

    def input(self, pressed, held):
        """Do not use LevelScene for input since we don't want to control
        the character on the menu"""
        for every_key in pressed:
            if every_key in [pygame.K_SPACE, pygame.K_w]:
                self.change_scene(TutorialLevel1(40, 280))

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
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)
        level_complete = True
        switch_music(level_complete)
        self.Tut6_text = Text("Ta dudorial", (600, 400), 45, IMPACT_FONT, GREY, None)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel2(40, 540))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

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

        screen.blit(self.Tut6_text.text_img, self.Tut6_text.text_rect)

class TutorialLevel2(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut5_text = Text("The mAze...", (210, 400), 75, IMPACT_FONT, GREY, None)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel3(0, 300))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

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
        platform21 = pygame.draw.rect(screen, BLACK, [0, 326, 380, 10]) # this is intentional, move this around
        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6, platform7, platform8,
                          platform9, platform10, platform11, platform12,
                          platform13, platform14, platform15, platform16,
                          platform17, platform18, platform19, platform20,
                          platform21]

        wall1 = pygame.draw.rect(screen, BLACK, [600, 36, 10, 1340])#x,y , width/hieght - big right
        wall2 = pygame.draw.rect(screen, BLACK, [380, 0, 10, 266])
        wall3 = pygame.draw.rect(screen, BLACK, [650, 0, 10, 546])
        wall4 = pygame.draw.rect(screen, BLACK, [0, 0, 10, 576])
        wall5 = pygame.draw.rect(screen, BLACK, [380, 306, 10, 226])#small wall
        self.walls = [wall1, wall2, wall3, wall4, platform3, platform4,
                      platform5, platform6, platform7, platform8,
                      platform9, wall5] #why is this like this
        
        screen.blit(self.Tut5_text.text_img, self.Tut5_text.text_rect)


class TutorialLevel3(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel4(10, 100))

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
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)
        self.Tut7_text = Text("sandwich", (110, 400), 75, IMPACT_FONT, GREY, None)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel5(0, 140))

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        death1 = pygame.draw.rect(screen, RED, [475, 370, 180, 600])# bottom red block 1
        death2 = pygame.draw.rect(screen, RED, [475, 0, 180, 330])# top red block 1
        death3 = pygame.draw.rect(screen, RED, [750, 350, 250, 230])# bottom red block 2
        death4 = pygame.draw.rect(screen, RED, [750, 0, 250, 280])# top red block 2
        self.death_zones = [death1, death2, death3, death4]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 278, 10, 30]) # win box 1
        self.win_zones = [win1]

        platform1 = pygame.draw.rect(screen, BLACK, [10, 110, 75, 10])# spawn platform
        platform2 = pygame.draw.rect(screen, BLACK, [310, 360, 100, 10]) # dorp platfomr
        platform3 = pygame.draw.rect(screen, BLACK, [475, 360, 180, 10]) # sandwich bottom 1
        platform4 = pygame.draw.rect(screen, BLACK, [750, 340, 250, 10]) # sandwich bottom 2
        platform5 = pygame.draw.rect(screen, BLACK, [475, 330, 180, 10]) # sandwich top 1
        platform6 = pygame.draw.rect(screen, BLACK, [750, 280, 250, 10]) # sandwich top 2
        self.platforms = [platform1, platform2, platform3, platform4,
                          platform5, platform6]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 278])# win wall 1
        wall2 = pygame.draw.rect(screen, BLACK, [1070, 308, 10, 288])# win wall 2
        self.walls = [wall1, wall2]

        screen.blit(self.Tut7_text.text_img, self.Tut7_text.text_rect)

class TutorialLevel5(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)
        level_complete = True
        # current_track_index = 0
        switch_music(level_complete)
        self.Tut4_text = Text("This is not the same spot", (800, 100), 15, IMPACT_FONT, YELLOW, None)

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.change_scene(TutorialLevel6(0, 120)) 

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)
        LevelScene.render_text(self, screen)

        screen.blit(self.Tut4_text.text_img, self.Tut4_text.text_rect)

    def render_level(self, screen):
        LevelScene.render(self, screen)

        # death1 = pygame.draw.rect(screen, RED, [0, 550, 1080, 30])# death floor
        # self.death_zones = [death1]

        platform1 = pygame.draw.rect(screen, BLACK, [0, 150, 200, 10])# spawn platform
        platform2 = pygame.draw.rect(screen, BLACK, [200, 100, 200, 10])
        # platform3 = pygame.draw.rect(screen, BLACK, [500, 500, 200, 10])
        platform4 = pygame.draw.rect(screen, BLACK, [870, 530, 100, 10])
        platform5 = pygame.draw.rect(screen, BLACK, [445, 300, 270, 10])# new land 
        self.platforms = [platform1, platform2, #platform3, 
                          platform4,
                          platform5]

        win1 = pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])# win box
        self.win_zones = [win1]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 480])# win wall 1
        wall2 = pygame.draw.rect(screen, BLACK, [1070, 510, 10, 288])# win wall 2
        self.walls = [wall1, wall2]

class TutorialLevel6(LevelScene):
    def __init__(self, x_spawn, y_spawn):
        LevelScene.__init__(self, x_spawn, y_spawn)
        # level_complete = True
        # # current_track_index = 0
        # switch_music(level_complete)
        self.Tut4_text = Text("Jump under platform", (800, 100), 15, IMPACT_FONT, YELLOW, None)

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

        win1 = pygame.draw.rect(screen, CYAN, [1070, 480, 10, 30])# win box
        self.win_zones = [win1]

        wall1 = pygame.draw.rect(screen, BLACK, [1070, 0, 10, 480])# win wall 1
        wall2 = pygame.draw.rect(screen, BLACK, [1070, 510, 10, 288])# win wall 2
        self.walls = [wall1, wall2]

class SquareMe: #lil purple dude

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
            jump_sound_1.play()
        else:
            self.jump_ability = False

    def render(self, screen):
        self.square_render = pygame.draw.rect(screen, self.color, [self.xpos,
                                                                   self.ypos,
                                                                   self.width,
                                                                   self.height])

    def collision_plat(self, object_list: [pygame.Rect]):
        collisions = self.square_render.collidelistall(object_list)
        if len(collisions) < 1:
            self.enable_gravity = True

        for collide_id in collisions:
            collide_x = object_list[collide_id].x
            collide_y = object_list[collide_id].y
            collide_width = object_list[collide_id].width
            collide_height = object_list[collide_id].height

            if collide_x - self.width - collide_width < self.xpos and \
                    self.xpos + self.width < \
                    collide_x + collide_width + self.width and \
                    collide_y < self.ypos + self.height:
                self.enable_gravity = False
                self.jump_ability = True
                self.gravity_counter = 50

            # Bottom Platform Collision
            # Todo: separate into own function later: collision_bottom
            if collide_x - self.width - collide_width < self.xpos and \
                    self.xpos + self.width < \
                    collide_x + collide_width + self.width and \
                    collide_y + 5 < self.ypos < collide_y + collide_height:
                self.jump_ability = False
                self.jump_boost = -1
                self.enable_gravity = True

    def collision_wall(self, object_list: [pygame.Rect]):
        collisions = self.square_render.collidelistall(object_list)
        for collide_id in collisions:
            collide_x = object_list[collide_id].x
            collide_y = object_list[collide_id].y
            collide_width = object_list[collide_id].width
            collide_height = object_list[collide_id].height

            if collide_id != -1 and \
                    (collide_y + 2 <= self.ypos + self.height - 1) and \
                    (self.ypos <= collide_y + collide_height + 2) and \
                    self.direction == "right" and \
                    self.xpos + self.width <= collide_x + 1:
                self.direction = "left"

            if collide_id != -1 and \
                    (collide_y + 2 <= self.ypos + self.height - 1) and \
                    (self.ypos <= collide_y + collide_height + 2) and \
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

            fps.tick(1000)
            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    start_game = Program()
    start_scene = MenuScene(40, 460)
    start_game.run(1080, 576, start_scene)
    pygame.quit()
