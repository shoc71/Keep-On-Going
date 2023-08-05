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
ORANGE = (255, 165, 0)
BLUE = (30, 144, 255)
GREY = (125, 125, 125)
LIGHT_PINK = (255, 182, 193)
EDIT_DARK_GREEN = (1, 100, 32)
PURPLE = (181, 60, 177)
BROWN = (150, 75, 0)

dont_image_text = pygame.image.load("dont (custom).png")  # ratio is 15:8
stop_image_text = pygame.image.load("stop (custom).png")
now_image_text = pygame.image.load("now (custom).png")

class LevelScene(dsnclass.Scene):
    def __init__(self, x_spawn, y_spawn, level_memory):
        """
        Set the current scene to this scene by passing this classes self to
        initialize it.
        """
        dsnclass.Scene.__init__(self)
        self.platforms = []
        self.death_zones = []
        self.win_zones = []
        self.respawn_zones = []  # todo: add new respawn zones to levels

        self.x_spawn = x_spawn
        self.y_spawn = y_spawn
        self.player = dsnclass.SquareMe(self.x_spawn, self.y_spawn,
                                        10, 10, PURPLE,
                                        level_memory.diff_lookup[
                                            level_memory.diff_value])
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
        self.pause_text_4 = dsnclass.Text("Press b to return to menu",
                                          (540, 350), 30,
                                          "impact", DARK_RED, None)
        self.pause_text_5 = dsnclass.Text("Press r to restart the level",
                                          (540, 385), 30,
                                          "impact", DARK_RED, None)

        self.memory = level_memory
        if level_memory is not None:
            self.level_data, self.level_elements = level_memory.level_set, level_memory.ls_elements
            self.start_time = pygame.time.get_ticks()

        self.jump_timer = pygame.time.get_ticks()

    def input(self, pressed, held):
        for every_key in pressed:
            """   removed the instant return to menu, this will be apart of the
            pause menu now
            """
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive and not \
                    self.player.freeze and 100 <= pygame.time.get_ticks() - self.jump_timer:
                self.player.jump_ability = True
                self.player.jump_boost = self.player.max_jump
                self.player.jump_sound_1.play()
                self.player.jumps += 1
                self.jump_timer = pygame.time.get_ticks()
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] \
                    and not self.player.alive:
                self.player.alive = True
                self.jump_timer = pygame.time.get_ticks()
            if every_key == pygame.K_ESCAPE and not self.level_condition:
                self.player.freeze = not self.player.freeze
            if every_key == pygame.K_q and self.player.freeze:
                self.run_scene = False
            if self.player.freeze and every_key == pygame.K_r:
                self.player.alive = False
                self.player.freeze = False
                self.deaths += 1
            if self.player.freeze and every_key == pygame.K_b:
                self.change_scene(MenuScene(40, 360, self.memory))

        if (held[pygame.K_SPACE] or held[pygame.K_w] or held[pygame.K_UP]) \
                and not self.player.enable_gravity and self.player.alive and \
                0 < self.player.jumps and not self.player.freeze and 100 <= pygame.time.get_ticks() - self.jump_timer:
            self.player.jump_ability = True
            self.player.jump_boost = self.player.max_jump
            self.player.jump_sound_1.play()
            self.player.jumps += 1

    def update(self):
        if self.player.square_render is None:  # very important, else game crashes
            return None

        if self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.deaths += self.player.death(self.death_zones)
            self.player.collision_plat(self.platforms)
            self.player.collision_wall(self.platforms)
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
            respawn_block = self.player.square_render.collidelist(
                self.respawn_zones)
            self.x_spawn = self.respawn_zones[respawn_block].x + \
                           (self.respawn_zones[respawn_block].width / 2) - 5
            self.y_spawn = self.respawn_zones[respawn_block].y + \
                           (self.respawn_zones[respawn_block].height / 2) - 5

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
            screen.blit(self.pause_text_4.text_img,
                        self.pause_text_4.text_rect)
            # added a way to formally return to the main menu
            screen.blit(self.pause_text_5.text_img,
                        self.pause_text_5.text_rect)

        if self.level_condition:
            self.victory(screen)
        else:
            self.play_time = pygame.time.get_ticks()
            self.victory_time = pygame.time.get_ticks()


class MenuScene(LevelScene):
    def __init__(self, xspawn, yspawn, level_memory):
        LevelScene.__init__(self, xspawn, yspawn, level_memory)
        self.level_id = 0
        self.option_count = 0
        self.options = [LevelSelect(level_memory), OptionsPage(level_memory),
                        StatsPage(level_memory), Filler(level_memory)]

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
        self.title_text_s3 = dsnclass.Text("Stats", (648, 490), 30,
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

        """self.title_guy = dsnclass.SquareMe(xspawn, yspawn,
                                        10, 10, (181, 60, 177))"""

    def input(self, pressed, held):
        """Do not use LevelScene for input since we don't want to control
        the character on the menu"""
        for every_key in pressed:
            if every_key in [pygame.K_SPACE, pygame.K_w]:
                self.memory.update_mem(self.level_id, self.deaths,
                                       self.player.jumps, self.start_time)
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
        screen.blit(dont_image_text, (90, 10))
        screen.blit(stop_image_text, (410, 10))
        screen.blit(now_image_text, (720, 10))
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
                          pygame.draw.rect(screen, BLACK, [200, 375, 810, 10]),
                          pygame.draw.rect(screen, BLACK, [0, 0, 10, 576]),
                          pygame.draw.rect(screen, BLACK, [1070, 0, 10, 576]),
                          pygame.draw.rect(screen, BLACK, [200, 365, 10, 10]),
                          pygame.draw.rect(screen, BLACK, [400, 350, 10, 10]),
                          pygame.draw.rect(screen, BLACK, [600, 335, 10, 10]),
                          pygame.draw.rect(screen, BLACK, [800, 320, 10, 10]),
                          pygame.draw.rect(screen, BLACK, [1000, 330, 10, 45])]

        # Menu selector box highlight
        pygame.draw.rect(screen, DARK_RED,
                         self.option_select[self.option_count], 2)


class Filler(dsnclass.Scene):
    def __init__(self, level_memory):
        dsnclass.Scene.__init__(self)
        self.level_id = -1
        self.filler_text = dsnclass.Text(
            "THERE'S NOTHING HERE, PRESS R TO GO BACK",
            (540, 213), 50, "impact", DARK_RED, None)
        self.memory = level_memory

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360, self.memory))

    def render(self, screen):
        screen.fill(WHITE)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)


# todo: Optimize OptionsPage option selecting
class OptionsPage(LevelScene):
    def __init__(self, level_memory):
        LevelScene.__init__(self, -50, -50, level_memory)
        self.setting_options = {
            0: level_memory.diff_lookup,
            1: level_memory.musi_lookup
        }

        self.num_to_diff = {0.6: "Easy", 0.8: "Medium", 1.0: "Hard"}
        self.setting_words = []
        self.update_text()

        self.choose_setting = 0
        self.change_setting = self.memory.diff_value

        self.option_title = dsnclass.Text("OPTIONS", ((1080 / 2), 50), 50,
                                          "impact", DARK_RED, None)
        self.return_text = dsnclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", YELLOW, None)

    def input(self, pressed, held):
        for action in pressed:
            if action in [pygame.K_s, pygame.K_DOWN]:
                self.choose_setting += 1
            elif action in [pygame.K_w, pygame.K_UP]:
                self.choose_setting -= 1

            if action in [pygame.K_s, pygame.K_DOWN, pygame.K_w, pygame.K_UP]:
                if self.choose_setting == 0:
                    self.change_setting = self.memory.diff_value
                elif self.choose_setting == 1:
                    self.change_setting = self.memory.musi_value

            if action in [pygame.K_a, pygame.K_LEFT]:
                self.change_setting -= 1
            elif action in [pygame.K_d, pygame.K_RIGHT]:
                self.change_setting += 1

            if action is pygame.K_r:
                self.change_scene(MenuScene(40, 360, self.memory))

    def update(self):
        if self.choose_setting < 0:
            self.choose_setting = len(self.setting_options) - 1
        elif len(self.setting_options) - 1 < self.choose_setting:
            self.choose_setting = 0
        if self.change_setting < 0:
            self.change_setting = len(
                self.setting_options[self.choose_setting]) - 1
        elif len(self.setting_options[
                     self.choose_setting]) - 1 < self.change_setting:
            self.change_setting = 0

        # Apply those changes
        if self.choose_setting == 0:
            self.memory.diff_value = self.change_setting
        elif self.choose_setting == 1:
            self.memory.musi_value = self.change_setting

        self.update_text()

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle

        for text_index in range(len(self.setting_words)):
            screen.blit(self.setting_words[text_index].text_img,
                        self.setting_words[text_index].text_rect)

        # Render option_title
        screen.blit(self.option_title.text_img, self.option_title.text_rect)
        screen.blit(self.return_text.text_img, self.return_text.text_rect)
        hl_rect = self.setting_words[self.choose_setting].text_rect
        pygame.draw.rect(screen, DARK_RED,
                         [hl_rect.x - 4, hl_rect.y - 1,
                          hl_rect.width + 8, hl_rect.height + 2], 2)

        LevelScene.render_text(self, screen)

    def update_text(self):
        self.setting_words = [
            dsnclass.Text("Difficulty: " + str(self.num_to_diff[
                                                   self.memory.diff_lookup[
                                                       self.memory.diff_value]]),
                          ((1080 / 2), 300), 50, "impact",
                          YELLOW, None),
            dsnclass.Text("Music: " + str(self.memory.musi_value),
                          ((1080 / 2), 375), 50, "impact",
                          YELLOW, None)
        ]


class StatsPage(LevelScene):
    def __init__(self, level_memory):
        # For now, leave the player clone out of bounds
        LevelScene.__init__(self, -50, -50, level_memory)
        self.memory.level_progress.sort()
        self.level_id = -1
        self.memory = level_memory
        if len(self.memory.level_progress) == 0:
            self.select_level = None
            self.render_stats = []
            self.nothing_text = dsnclass.Text(
                "GO COMPLETE SOME LEVELS FIRST!", (1080 / 2, (576 / 2)), 50,
                "impact", DARK_RED, None)
        else:
            self.select_level = 0
            self.update_stats()

        self.return_text = dsnclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", YELLOW, None)

    def input(self, pressed, held):
        if self.select_level is not None:
            for action in pressed:
                if action == pygame.K_a:
                    self.select_level -= 1
                elif action == pygame.K_d:
                    self.select_level += 1

        for action in pressed:
            if action == pygame.K_r:
                self.change_scene(MenuScene(40, 360, self.memory))

    def update(self):
        if self.select_level is not None:
            if len(self.memory.level_progress) - 1 < self.select_level:
                self.select_level = 0
            elif self.select_level < 0:
                self.select_level = len(self.memory.level_progress) - 1

            self.update_stats()

    def update_stats(self):
        get_time = self.memory.level_times[
            self.memory.level_progress[self.select_level]]
        total_time = dsnclass.convert_time(pygame.time.get_ticks())
        self.render_stats = [
            dsnclass.Text(
                "LEVEL: " + str(self.memory.level_progress[self.select_level]),
                (1080 / 2, (576 / 2) - 25), 25, "impact", YELLOW, None),
            dsnclass.Text("Deaths: " + str(self.memory.level_deaths[
                                               self.memory.level_progress[
                                                   self.select_level]]),
                          (1080 / 2, (576 / 2)), 25, "impact", YELLOW, None),
            dsnclass.Text("Jumps: " + str(self.memory.level_jumps[
                                              self.memory.level_progress[
                                                  self.select_level]]),
                          (1080 / 2, (576 / 2) + 25), 25, "impact", YELLOW,
                          None),
            dsnclass.Text("Total Deaths: " + str(self.memory.total_deaths),
                          ((1080 / 4), 50), 25, "impact", YELLOW, None),
            dsnclass.Text("Total Jumps: " + str(self.memory.total_jumps),
                          ((1080 / 4 * 3), 50), 25, "impact", YELLOW, None),
            dsnclass.Text("Total Time:",
                          ((1080 / 4 * 2), 50), 25, "impact", YELLOW, None),
            dsnclass.Text(
                str(total_time[0]) + ":" + str(total_time[1]) + ":" + str(
                    total_time[2]),
                ((1080 / 4 * 2), 100), 25, "impact", YELLOW, None),
            dsnclass.Text("Level Time: " + str(get_time[0]) + ":" + str(
                get_time[1]) + ":" + str(get_time[2]),
                          ((1080 / 4 * 2), (576 / 2) + 50), 25, "impact",
                          YELLOW, None)
        ]

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle

        if self.select_level is not None:
            for stat_text in self.render_stats:
                screen.blit(stat_text.text_img, stat_text.text_rect)
        else:
            screen.blit(self.nothing_text.text_img, self.nothing_text.text_rect)

        screen.blit(self.return_text.text_img, self.return_text.text_rect)
        LevelScene.render_text(self, screen)


class LevelSelect(LevelScene):
    def __init__(self, level_memory):
        LevelScene.__init__(self, (1080 / 2) - (10 / 2), 576 / 2, level_memory)
        self.filler_text = dsnclass.Text("Choose A Level",
                                         (540, 153), 50, "impact", YELLOW, None)
        self.disclaimer_text2 = dsnclass.Text("ONLY A PROOF OF CONCEPT",
                                              (540, 60), 50, "impact", RED,
                                              None)
        self.disclaimer_text = dsnclass.Text(
            "ALL LEVELS LEAD TO LEVEL 1, PRESS JUMP TO START",
            (540, 110), 50, "impact", RED, None)

        self.blockmation_time = 0
        self.text_x = 0
        self.direction = 0
        self.choose_id = 1

        self.memory = level_memory

        self.repjump_time = 0
        self.speed_jump = 1

    def input(self, pressed, held):
        for every_key in pressed:
            if every_key == pygame.K_r:
                self.change_scene(MenuScene(40, 360,self.memory))
            if every_key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w] and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.change_scene(PlayLevel(self.level_data[self.choose_id][0],
                                            self.level_data[self.choose_id][1],
                                            self.memory, self.choose_id))
            if every_key in [pygame.K_a, pygame.K_d] and \
                    self.player.jump_ability and \
                    not self.player.enable_gravity and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.player.jump_boost = self.player.max_jump
                self.player.jump_sound_1.play()
                self.player.jumps += 1

                if every_key == pygame.K_a and 1 < self.choose_id:
                    self.blockmation_time = pygame.time.get_ticks()
                    self.direction = 1
                if every_key == pygame.K_d and self.choose_id < len(
                        self.level_data):
                    self.blockmation_time = pygame.time.get_ticks()
                    self.direction = -1

        if held[pygame.K_a] and 1 < self.choose_id and \
                self.player.jump_ability and \
                not self.player.enable_gravity and \
                (
                        405 / self.speed_jump) < pygame.time.get_ticks() - self.blockmation_time:
            self.player.jump_boost = self.player.max_jump
            self.player.jump_sound_1.play()
            self.player.jumps += 1

            self.blockmation_time = pygame.time.get_ticks()
            self.direction = 1
        elif held[pygame.K_d] and self.choose_id < len(self.level_data) and \
                self.player.jump_ability and \
                not self.player.enable_gravity and \
                (
                        405 / self.speed_jump) < pygame.time.get_ticks() - self.blockmation_time:
            self.player.jump_boost = self.player.max_jump
            self.player.jump_sound_1.play()
            self.player.jumps += 1

            self.blockmation_time = pygame.time.get_ticks()
            self.direction = -1

        if not held[pygame.K_a] and not held[pygame.K_d]:
            self.repjump_time = pygame.time.get_ticks()

    def update(self):
        LevelScene.update(self)
        self.player.alive = True
        self.player.xpos = self.x_spawn
        self.player.diff_factor = self.speed_jump
        if self.y_spawn <= self.player.ypos:
            self.player.ypos = self.y_spawn
            self.player.enable_gravity = False
            self.player.gravity_counter = self.player.max_gravity
            self.player.jump_ability = True

        if 3000 <= pygame.time.get_ticks() - self.repjump_time:
            self.speed_jump = 2
        else:
            self.speed_jump = 1

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
                    0 < int(texts.text) <= len(self.level_data):
                screen.blit(texts.text_img, texts.text_rect)
                pygame.draw.rect(screen, (0, 0, 0), [texts.text_rect.x - 20,
                                                     texts.text_rect.y - 5,
                                                     texts.text_rect.width + 40,
                                                     texts.text_rect.height + 10],
                                 4)

        if pygame.time.get_ticks() - self.blockmation_time < 400 / self.speed_jump:
            if self.direction == 1:
                self.text_x += 4.4

            if self.direction == -1:
                self.text_x -= 4.4
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


class PlayLevel(LevelSelect):
    def __init__(self, x_spawn, y_spawn,
                 level_memory, play_id):
        LevelScene.__init__(self, x_spawn, y_spawn, level_memory)
        self.level_id = play_id
        self.element_names = list(self.level_elements[self.level_id].keys())
        self.collision_objects = {"self.platforms": self.platforms,
                                  "self.death_zones": self.death_zones,
                                  "self.win_zones": self.win_zones,
                                  "self.respawn_zones": self.respawn_zones}
        self.render_objects = []
        for name in self.element_names:
            if name != "Text" and name in self.level_elements[self.level_id]:
                for element in self.level_elements[self.level_id][name]:
                    if name in self.collision_objects:
                        self.collision_objects[name] += [element.shape]
                    self.render_objects += [element]

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def update(self):
        LevelScene.update(self)
        if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                self.victory_time:
            self.memory.update_mem(self.level_id, self.deaths,
                                   self.player.jumps, self.start_time)
            self.level_id += 1

            self.change_scene(PlayLevel(self.level_data[self.level_id][0],
                                        self.level_data[self.level_id][1],
                                        self.memory,
                                        self.level_id))  # spawn for next level

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        # Text Rendering
        if "Text" in self.level_elements[self.level_id]:
            for text in self.level_elements[self.level_id]["Text"]:
                screen.blit(text.text_img, text.text_rect)

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        # No death zones in this level!
        for element in self.render_objects:
            if element.type == "rect":
                pygame.draw.rect(screen, element.color, element.shape)
            else:
                pygame.draw.line(screen, element.color,
                                 [element.shape[0], element.shape[1]],
                                 [element.shape[2], element.shape[3]],
                                 element.shape[4])


