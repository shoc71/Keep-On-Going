import os
import random
import pygame
import kog_class as kogclass
import math

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
DARK_GREEN = (1, 100, 32)
PURPLE = (181, 60, 177)
BROWN = (150, 75, 0)
DARK_GREY = (52, 52, 52)
DARK_PURPLE = (80, 35, 105)
GOLDELLOW = (245, 180, 65)

# global variable
LVL_ID = -99
MENU_ID = -98
OPTIONS_ID = -97


class LevelScene(kogclass.Scene):
    """
    Base class used for any scene related to Don't Stop Now. This class contains
    basic requirements for the game to run, such as :
        - player movement, collision and inputs
        - level elements and text
        - pause menu and it's options
        - victory condition for beating the level
    One, some, or all of the classes below can be defined in the child class
    (using LevelScene as a parent class). For example in MenuScene,
    No input to control the player is desired, but it should keep it's rendering
    and update functions. That's why we call LevelScene.update and .render, but
    not LevelScene.input under MenuScene's update, render and input.
    """

    def __init__(self, x_spawn, y_spawn, level_memory):
        """
        Set the current scene to this scene by passing this classes self to
        initialize it.
        """
        kogclass.Scene.__init__(self)
        pygame.display.set_mode([1080, 576])
        self.platforms = []  # All platforms for that level (collision)
        self.death_zones = []  # All deaths for that level (death condition)
        self.win_zones = []  # All win areas for that level (win condition)
        self.respawn_zones = []  # todo: add new respawn zones to levels

        self.x_spawn = x_spawn * level_memory.res_width
        # x spawning location for player
        self.y_spawn = y_spawn * level_memory.res_height
        # y spawning location for player
        self.player = kogclass.SquareMe(self.x_spawn, self.y_spawn,
                                        10, 10, PURPLE,
                                        level_memory.diff_lookup[
                                            level_memory.diff_value],
                                        level_memory.res_width,
                                        level_memory.res_height,
                                        level_memory.sound_vol)
        """Initialize player variable in the level using the x and y spawn,
        constant widths and heights of 10, the color PURPLE, and the difficulty
        defined by level_memory (settings dependent)
        """
        self.deaths = 0  # Recorded deaths for that level instance
        self.play_time = 0  # Time accumulated in that level
        self.level_condition = False  # Check if player has won (touch win)
        self.victory_time = 0  # Time variable for victory text display
        self.victory_counter = 0  # The index of victory_text list
        self.victory_text = [
            kogclass.Text("KEEP", (310, 100), 100, "impact", YELLOW, None),
            kogclass.Text("ON", (570, 100), 100, "impact", YELLOW, None),
            kogclass.Text("GOING", (820, 100), 100, "impact", YELLOW, None)
        ]
        self.victory_text[0].scale(level_memory.res_width,
                                   level_memory.res_height)
        self.victory_text[1].scale(level_memory.res_width,
                                   level_memory.res_height)
        self.victory_text[2].scale(level_memory.res_width,
                                   level_memory.res_height)
        # Text displayed when winning (touch the win_zones), uses time/counter

        self.pause_text = kogclass.Text("PAUSED", (540, 213),
                                        100, "impact", DARK_RED, None)
        self.pause_text.scale(level_memory.res_width,
                              level_memory.res_height)
        self.pause_text_2 = kogclass.Text("Press esc to unpause", (540, 280),
                                          30, "impact", DARK_RED, None)
        self.pause_text_2.scale(level_memory.res_width,
                                level_memory.res_height)
        self.pause_text_3 = kogclass.Text("Restart",
                                          (540, 320), 30,
                                          "impact", DARK_RED, None)
        self.pause_text_3.scale(level_memory.res_width,
                                level_memory.res_height)
        self.pause_text_5 = kogclass.Text("Return to Menu",
                                          (540, 400), 30,
                                          "impact", DARK_RED, None)
        self.pause_text_5.scale(level_memory.res_width,
                                level_memory.res_height)
        self.pause_text_6 = kogclass.Text("Quit", (540, 440),
                                          30, "impact", DARK_RED, None)
        self.pause_text_6.scale(level_memory.res_width,
                                level_memory.res_height)
        self.pause_text_4 = kogclass.Text("Options", (540, 360),
                                          30, "impact", DARK_RED, None)
        self.pause_text_4.scale(level_memory.res_width,
                                level_memory.res_height)

        # Text displayed when player pauses the game (ESC)

        self.memory = level_memory
        self.pause = False

        # If condition to avoid loading memory if it's empty (failsafe)
        if level_memory is not None:
            self.level_data = level_memory.level_set
            self.level_elements = level_memory.ls_elements
            self.start_time = pygame.time.get_ticks()
            self.action_time = pygame.time.get_ticks()

        # Timer used to delay player jump
        self.jump_timer = pygame.time.get_ticks()

        # List holding when respawns are performed
        self.resp_jumps = []
        # List holding when jumps are performed
        self.hold_jumps = []

        self.loop_counter = 0

        self.element_names = []
        self.render_objects = []
        self.collision_objects = {}

        self.pause_options = {
            0: self.restart_death, 1: self.access_options,
            2: self.return_to_menu, 3: self.stop_level
        }

        """
        Here are the current pause options:
        - 0: Restart the level from pause menu, which counts as a death
        - 1: Return to the main menu
        - 2: If paused, press q to quit
        - 3: Toggle accessing the options page during the level
        """

        self.pause_index = 0

        self.pause_timer = pygame.time.get_ticks()
        # Timer controlling how fast player can scroll in pause screen

        # Useful to render an outline over these options
        # Should have the same length as pause_options

        self.pause_list = [
            self.pause_text_3,
            self.pause_text_4,
            self.pause_text_5,
            self.pause_text_6,
        ]

        self.options_page = False

    def input(self, pressed, held):
        for every_key in pressed:
            if not self.options_page:
                # Pressing/tapping and not holding jump key to jump
                if every_key in [pygame.K_w, pygame.K_UP,
                                 pygame.K_SPACE] and not \
                        self.player.enable_gravity and self.player.alive and not \
                        self.player.freeze and \
                        150 <= pygame.time.get_ticks() - self.jump_timer:
                    self.player.jump_ability = True  # Allow player to jump
                    self.player.jump_boost = self.player.max_jump  # Setup jump
                    self.player.jump_sound_1.play()  # Play jump sound
                    self.player.jumps += 1  # Add to a jump counter
                    self.jump_timer = pygame.time.get_ticks()  # Reset jump timer

                    self.hold_jumps += ["J" + str(self.loop_counter)]

                # Pressing the jump key to stop player freezing and start level
                # This also updates the replay linked list
                if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] \
                        and not self.player.alive:
                    if 0 < len(self.resp_jumps):
                        self.memory.update_temp(
                            self.resp_jumps + self.hold_jumps)
                        self.hold_jumps = []
                        self.resp_jumps = []
                    self.player.alive = True
                    self.jump_timer = pygame.time.get_ticks()

                    self.resp_jumps += ["R" + str(self.loop_counter)]

                # Pausing the game and stopping player movement/action
                if every_key == pygame.K_ESCAPE and not self.level_condition:
                    self.pause_index = 0
                    self.player.freeze = not self.player.freeze
                    self.pause = not self.pause

                # Navigate pause menu
                if every_key == pygame.K_w and not self.options_page and \
                        self.player.freeze and self.pause:
                    self.pause_index -= 1
                    self.pause_timer = pygame.time.get_ticks()
                elif every_key == pygame.K_s and not self.options_page and \
                        self.player.freeze and self.pause:
                    self.pause_index += 1
                    self.pause_timer = pygame.time.get_ticks()

                # Quick Restart counter (safe and default values)
                if every_key is pygame.K_r:
                    self.memory.qr_counter += 1

                # Choosing options from pause screen
                if self.player.freeze and self.pause and \
                        every_key == pygame.K_SPACE:
                    self.pause_options[self.pause_index]()
                    # Put this here to have it run only once
                    if self.options_page:
                        self.platforms = []
                        self.win_zones = []
                        self.death_zones = []
                        self.respawn_zones = []
                        self.memory.options_status = self.level_id
                        self.load_renders(OPTIONS_ID)

                # Change music tracks
                if every_key == pygame.K_n:
                    self.memory.music.next_track()
                elif every_key == pygame.K_b:
                    self.memory.music.previous_track()

        # Held controls for jumping
        if (held[pygame.K_SPACE] or held[pygame.K_w] or held[pygame.K_UP]) \
                and not self.player.enable_gravity and self.player.alive and \
                not self.player.freeze and not self.options_page and \
                150 <= pygame.time.get_ticks() - self.jump_timer:
            self.player.jump_ability = True  # Allow player to jump
            self.player.jump_boost = self.player.max_jump  # Setup jump
            self.player.jump_sound_1.play()  # Play jump sound
            self.player.jumps += 1  # Add to a jump counter
            self.jump_timer = pygame.time.get_ticks()  # Reset jump timer

            self.hold_jumps += ["J" + str(self.loop_counter)]

        # Held controls for choosing options
        if self.player.freeze and self.pause and held[pygame.K_s] and \
                not self.options_page and \
                200 < pygame.time.get_ticks() - self.pause_timer:
            self.pause_index += 1
            self.pause_timer = pygame.time.get_ticks()
        elif self.player.freeze and self.pause and held[pygame.K_w] and \
                not self.options_page and \
                200 < pygame.time.get_ticks() - self.pause_timer:
            self.pause_index -= 1
            self.pause_timer = pygame.time.get_ticks()

    def update(self):
        self.loop_counter += 1
        # Failsafe if player isn't rendered but level starts
        if self.player.square_render is None:
            return None  # Player is not rendered, skip function

        # Player is alive, not paused and haven't run, then check collision
        if self.player.alive and not self.player.freeze and \
                not self.level_condition and not self.pause:
            # Check if player collided with death zones (returns 1 or 0)
            self.deaths += self.player.death(self.death_zones)
            self.player.collision_plat(self.platforms)  # Top and bottom coll
            self.player.collision_wall(self.platforms)  # Side collision
            self.player.move()  # Player movement

        """Respawn for square players, reset spawn position, set direction
        to right by default, reset gravity"""
        if not self.player.alive and not self.player.freeze and \
                not self.level_condition and not self.pause:
            self.jump_timer = pygame.time.get_ticks()  # Reset jump timer
            self.player.jump_boost = -1 * (self.player.max_jump - 1)
            self.player.jump_ability = False
            self.player.xpos = self.x_spawn
            self.player.ypos = self.y_spawn
            self.player.direction = 1
            self.player.gravity_counter = self.player.max_gravity

        # If player is below the level, count as a death (out of bounds)
        if (576 * self.memory.res_height) + \
                self.player.height < self.player.ypos:
            self.player.alive = False
            self.deaths += 1

        # Check if the player restarted
        if self.memory.quick_restart <= self.memory.qr_counter:
            self.restart_death()

        # Check for win collision
        if self.player.alive and \
                self.player.square_render.collidelist(self.win_zones) != -1:
            self.level_condition = True
            self.player.alive = False

        # Respawn block collision
        if self.player.alive and \
                self.player.square_render.collidelist(self.respawn_zones) != -1:
            # Setup respawn block for readability
            respawn_block = self.player.square_render.collidelist(
                self.respawn_zones)
            # Set new x and y default spawns
            self.x_spawn = self.respawn_zones[respawn_block].x + \
                           (self.respawn_zones[respawn_block].width / 2) - 5
            self.y_spawn = self.respawn_zones[respawn_block].y + \
                           (self.respawn_zones[respawn_block].height / 2) - 5

        # Ensure pause index is within boundaries
        if self.pause_index < 0:
            self.pause_index = len(self.pause_options) - 1
        elif len(self.pause_options) - 1 < self.pause_index:
            self.pause_index = 0

    def restart_death(self):
        if 0 < len(self.resp_jumps):
            self.memory.update_temp(self.resp_jumps + self.hold_jumps)
            self.hold_jumps = []
            self.resp_jumps = []

        self.resp_jumps += [
            "R" + str(self.loop_counter)]

        self.player.alive = False
        self.player.freeze = False
        self.deaths += 1
        self.memory.qr_counter = 0

    def stop_level(self):
        self.run_scene = False

    def return_to_menu(self):
        self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0,
                                    0)
        self.change_scene(MenuScene(24, 303, self.memory))

    def access_options(self):
        self.options_page = not self.options_page

    def go_to_options(self):
        self.change_scene(OptionsPage(self.memory))

    def victory(self, screen):
        # Victory function played when win condition
        if 500 <= pygame.time.get_ticks() - self.victory_time and \
                self.victory_counter < 3:
            self.victory_time = pygame.time.get_ticks()  # Reset timer
            self.victory_counter += 1  # Increase index for victory_text
        for x in range(self.victory_counter):
            screen.blit(self.victory_text[x].text_img,
                        self.victory_text[x].text_rect)
            # Display victory text depending on index available (0-3)

    def render(self, screen):
        # Default rendering
        screen.fill(self.memory.background)

    def render_level(self, screen):
        """ This function will be altered in the child class"""
        pass

    def render_text(self, screen):
        """ Use this function to render important text for levels"""
        if not self.options_page:
            self.player.render(screen)

            if self.player.freeze and self.pause:
                pygame.draw.rect(screen, DARK_PURPLE, [330, 150, 420, 340])
                pygame.draw.rect(screen, GOLDELLOW, [340, 160, 400, 320])
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
                screen.blit(self.pause_text_6.text_img,
                            self.pause_text_6.text_rect)

                if 0 <= self.pause_index < len(self.pause_options):
                    selected_option = self.pause_list[
                        self.pause_index].text_rect
                    pygame.draw.rect(screen, DARK_PURPLE,
                                     [selected_option.x - 4,
                                      selected_option.y - 2,
                                      selected_option.width + 8,
                                      selected_option.height + 4], 2)

            # If player won, show the render of victory text
            if not self.memory.enable_replay:
                if self.level_condition:
                    self.victory(screen)
                # Otherwise, update amount of time total and in level
                else:
                    self.play_time = pygame.time.get_ticks()
                    self.victory_time = pygame.time.get_ticks()

            if pygame.time.get_ticks() - self.memory.music.text_timer < 3000:
                pygame.draw.rect(screen, YELLOW,
                                 self.memory.music.music_text.text_rect)
                screen.blit(self.memory.music.music_text.text_img,
                            self.memory.music.music_text.text_rect)

    def load_renders(self, level_id):
        self.element_names = list(self.level_elements[level_id].keys())
        self.collision_objects = {"self.platforms": self.platforms,
                                  "self.death_zones": self.death_zones,
                                  "self.win_zones": self.win_zones,
                                  "self.respawn_zones": self.respawn_zones}
        self.render_objects = []  # Initialize render objects

        for name in self.element_names:
            # Get DSNElement objects that aren't under Text
            if name != "Text" and name in self.level_elements[level_id]:
                # For each element in the level, get collision and render lists
                for element in self.level_elements[level_id][name]:
                    if name in self.collision_objects:
                        self.collision_objects[name] += [element.shape]
                        # Add rect objects for collision (collision, no render)
                    self.render_objects += [element]
                    # Load up render objects (only rendering, no collision)


class MenuScene(LevelScene):
    """
    Main Menu for Don't Stop Now game
    """

    def __init__(self, xspawn, yspawn, level_memory):
        # Use level_scene init, mainly to define the player and memory
        LevelScene.__init__(self, xspawn, yspawn, level_memory)
        self.level_id = 0  # Has a level id of 0 (defined to record jumps)
        self.option_count = 0  # Index counter to choose level
        self.options = [self.go_to_hub,
                        self.go_to_options,
                        self.go_to_stats, self.go_to_replay,
                        self.go_to_levelzero, self.go_to_instructions] + \
                       ([self.go_to_filler] * 2)    # filler options 2 times
        # Main menu options

        # Main menu text
        self.title_text = kogclass.Text("Press Space or W To Start", (530, 200),
                                        50, "impact",
                                        YELLOW, None)
        self.title_text.scale(self.memory.res_width, self.memory.res_height)
        self.title_text_2 = kogclass.Text("Press esc to pause", (530, 250), 30,
                                          "impact",
                                          YELLOW, None)
        self.title_text_2.scale(self.memory.res_width, self.memory.res_height)

        # Two types of text depending on game progress (new vs. continuing)
        self.title_text_s1_new = kogclass.Text("New Game", (216, 445), 30,
                                               "impact",
                                               YELLOW, None)
        self.title_text_s1_new.scale(self.memory.res_width,
                                     self.memory.res_height)
        self.title_text_s1_cont = kogclass.Text("Continue", (216, 445), 30,
                                                "impact",
                                                YELLOW, None)
        self.title_text_s1_cont.scale(self.memory.res_width,
                                      self.memory.res_height)

        self.title_text_s2 = kogclass.Text("Options", (432, 445), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s2.scale(self.memory.res_width, self.memory.res_height)
        self.title_text_s3 = kogclass.Text("Stats", (648, 445), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s3.scale(self.memory.res_width, self.memory.res_height)
        self.title_text_s4 = kogclass.Text("Replay", (864, 445), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s4.scale(self.memory.res_width, self.memory.res_height)

        self.title_text_s5 = kogclass.Text("Level Zero", (216, 535), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s5.scale(self.memory.res_width, self.memory.res_height)

        self.title_text_s6 = kogclass.Text("Instructions", (432, 535), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s6.scale(self.memory.res_width, self.memory.res_height)

        self.title_text_s7 = kogclass.Text("Filler", (648, 535), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s7.scale(self.memory.res_width, self.memory.res_height)

        self.title_text_s8 = kogclass.Text("Filler", (864, 535), 30,
                                           "impact",
                                           YELLOW, None)
        self.title_text_s8.scale(self.memory.res_width, self.memory.res_height)

        file_path = "assets/images/title"
        self.keep_image_text = pygame.image.load(
            file_path + "Keep.png").convert_alpha()  # ratio is 15:8
        self.on_image_text = pygame.image.load(file_path +
                                               "On.png").convert_alpha()
        self.going_image_text = pygame.image.load(file_path +
                                                  "Going.png").convert_alpha()

        self.keep_image_text = \
            pygame.transform.scale(self.keep_image_text,
                                   (self.keep_image_text.get_rect().width *
                                    self.memory.res_width * 0.2,
                                    self.keep_image_text.get_rect().height *
                                    self.memory.res_height * 0.225))
        self.on_image_text = \
            pygame.transform.scale(self.on_image_text,
                                   (self.on_image_text.get_rect().width *
                                    self.memory.res_width * 0.2,
                                    self.on_image_text.get_rect().height *
                                    self.memory.res_height * 0.225))
        self.going_image_text = \
            pygame.transform.scale(self.going_image_text,
                                   (self.going_image_text.get_rect().width *
                                    self.memory.res_width * 0.2,
                                    self.going_image_text.get_rect().height *
                                    self.memory.res_height * 0.225))

        # Highlight specific rect
        if len(self.memory.level_progress) < 2:
            add_rect = self.title_text_s1_new.text_rect
        else:
            add_rect = self.title_text_s1_cont.text_rect

        self.option_select = [add_rect,
                              self.title_text_s2.text_rect,
                              self.title_text_s3.text_rect,
                              self.title_text_s4.text_rect,
                              self.title_text_s5.text_rect,
                              self.title_text_s6.text_rect,
                              self.title_text_s7.text_rect,
                              self.title_text_s8.text_rect
                              ]

        self.load_renders(MENU_ID)

    def input(self, pressed, held):
        """Do not use LevelScene for input since we don't want to control
        the character on the menu"""
        for every_key in pressed:
            # If player chooses option, update menu statistics and change scene
            if every_key in [pygame.K_SPACE]:
                self.memory.music.switch_music()  # might need to change this
                self.memory.update_mem(self.level_id, self.deaths,
                                       self.player.jumps, self.start_time, 0)
                if self.option_count == 1:
                    self.memory.options_status = 0
                elif self.option_count == 0:
                    self.memory.music.set_music(self.memory.hub_index,
                                                self.memory.music.max_vol, -1,
                                                0, 0)
                self.options[self.option_count]()
            # Press right/d to move right of the selection
            if every_key is pygame.K_d:
                self.option_count += 1
            # Press left/a to move left of the selection
            if every_key is pygame.K_a:
                self.option_count -= 1

            if every_key is pygame.K_s:
                self.option_count += 4

            if every_key is pygame.K_w:
                self.option_count -= 4

    def update(self):
        # Use levelscene update for collision and player movement
        LevelScene.update(self)
        self.player.alive = True  # Player cannot die (might be problematic)

        # If options selected go past right boundary, set it to the left
        if len(self.options) - 1 < self.option_count:
            self.option_count = 0 + (self.option_count - len(self.options))
        # If options selected go past left boundary, set it to the right
        if self.option_count < 0:
            self.option_count = len(self.options) + self.option_count

        # Have player jump randomly occur rather than input
        if (random.randint(1, 2500) <= 15) and not self.player.enable_gravity:
            self.player.jumps += 1  # Add to jump counter
            self.player.jump_ability = True  # Allow player to jump
            self.player.jump_boost = self.player.max_jump  # Setup jump

        # Change if replays/second replay player should appear
        if self.option_count == 0:
            self.memory.replays_off()
        elif self.option_count == 3:
            self.memory.replays_on()  # Is a replay mode

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle

        # Render Settings Decor
        for element in self.render_objects:
            if element.type == "rect":  # rect drawings
                pygame.draw.rect(screen, element.color, element.shape)
            else:  # line drawings
                pygame.draw.line(screen, element.color,
                                 [element.shape[0], element.shape[1]],
                                 [element.shape[2], element.shape[3]],
                                 element.shape[4])

        # Text or Front-most
        screen.blit(self.keep_image_text,
                    (self.memory.res_width + 35, 10 * self.memory.res_height))
        screen.blit(self.on_image_text, (
            410 * self.memory.res_width - 5, 10 * self.memory.res_height))
        screen.blit(self.going_image_text, (
            720 * self.memory.res_width - 95, 10 * self.memory.res_height))

        if len(self.memory.level_progress) < 2:
            screen.blit(self.title_text_s1_new.text_img,
                        self.title_text_s1_new.text_rect)
        else:
            screen.blit(self.title_text_s1_cont.text_img,
                        self.title_text_s1_cont.text_rect)

        screen.blit(self.title_text_s2.text_img, self.title_text_s2.text_rect)
        screen.blit(self.title_text_s3.text_img, self.title_text_s3.text_rect)
        screen.blit(self.title_text_s4.text_img, self.title_text_s4.text_rect)
        screen.blit(self.title_text_s5.text_img, self.title_text_s5.text_rect)
        screen.blit(self.title_text_s6.text_img, self.title_text_s6.text_rect)
        screen.blit(self.title_text_s7.text_img, self.title_text_s7.text_rect)
        screen.blit(self.title_text_s8.text_img, self.title_text_s8.text_rect)

        LevelScene.render_text(self, screen)
        # self.title_guy.render(screen)

    def render_level(self, screen):
        for each_rect in self.platforms:
            pygame.draw.rect(screen, BLACK, each_rect)

        # Menu selector box highlight
        pygame.draw.rect(screen, DARK_RED,
                         [self.option_select[self.option_count].x - 5,
                          self.option_select[self.option_count].y - 5,
                          self.option_select[self.option_count].width + 10,
                          self.option_select[self.option_count].height + 10], 2)

    def go_to_hub(self):
        self.change_scene(Hubzones(300, 50, self.memory))

    def go_to_stats(self):
        self.change_scene((StatsPage(self.memory)))

    def go_to_replay(self):
        self.change_scene(ReplayIO(self.memory))

    def go_to_levelzero(self):
        self.change_scene(LevelZero(self.memory))

    def go_to_filler(self):
        self.change_scene(Filler(self.memory))

    def go_to_instructions(self):
        self.change_scene(Instructions(self.memory))


class HubzonePlayer(kogclass.SquareMe):
    def __init__(self, x_spawn, y_spawn, width, height, rgb, diff,
                 res_width, res_height, jump_vol):
        kogclass.SquareMe.__init__(self, x_spawn, y_spawn, width, height, rgb,
                                   diff,
                                   res_width, res_height, jump_vol)
        self.max_jump = 100

    def move(self):

        move_factor = (4 * self.direction) * self.diff_factor * self.res_width

        if self.left_x is not None and \
                self.xpos + move_factor <= self.left_x:
            self.xpos = self.left_x
        elif self.right_x is not None and \
                self.right_x <= self.xpos + move_factor + self.width:
            self.xpos = self.right_x - self.width
        else:
            self.xpos += move_factor

        self.gravity()
        self.jump()
        self.update_collision_detection()


class Hubzones(LevelScene):
    def __init__(self, x_spawn, y_spawn, level_memory):
        LevelScene.__init__(self, x_spawn, y_spawn, level_memory)
        self.player = HubzonePlayer(self.x_spawn, self.y_spawn, 20, 20, PURPLE,
                                    level_memory.diff_lookup[
                                        level_memory.diff_value],
                                    level_memory.res_width,
                                    level_memory.res_height,
                                    level_memory.sound_vol)
        # print(self.player)
        file_path = "assets/images/background/"
        self.npc = {
            0: pygame.image.load(file_path + "npc_0.png").convert_alpha(),
            # npc 1
            1: pygame.image.load(file_path + "npc_1.png").convert_alpha(),
            # npc 2
            2: pygame.image.load(file_path + "npc_2.png").convert_alpha(),
            # npc 3
        }
        self.pause_options = {
            0: self.restart_death, 1: self.go_to_options,
            2: self.return_to_menu, 3: self.stop_level
        }
        self.level_elements = level_memory.ls_elements
        self.backgrounds = {}
        background_index = 0
        try:
            file_path = "assets/images/background/"
            for file in os.listdir(file_path):
                if "background" in file:
                    self.backgrounds[background_index] = \
                        pygame.image.load(file_path + str(file)).convert_alpha()
                    background_index += 1
        except:
            # todo: Put log error here
            raise "No Backgrounds Found in Folrder"

        self.text_bubbles = [
            kogclass.Text("Text Bubbble", (310, 100), 25, "impact", GREY, None),
            kogclass.Text("I am not an NPC", (310, 150), 25, "impact", GREY,
                          None),
        ]

        self.text_bubbles[0].scale(level_memory.res_width,
                                   level_memory.res_height)
        self.text_bubbles[1].scale(level_memory.res_width,
                                   level_memory.res_height)
        self.options_page = False
        self.load_renders(-96)
        """ Hub non-level elements, add + self.memory.hub_index once all are
        added in non-levels.txt"""

        self.special_objects = [pygame.Rect(200, 500, 30, 30),
                                pygame.Rect(800, 500, 30, 30),
                                pygame.Rect(800, 300, 180,
                                            80)]  # this for the sign

        self.special_options = [self.return_to_menu, self.go_to_options,
                                self.go_to_hubselect]

        self.player.alive = True

    def input(self, pressed, held):
        # Don't do LevelScene.input(self, pressed, held)
        for every_key in pressed:
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive and not \
                    self.player.freeze and not self.pause and \
                    150 <= pygame.time.get_ticks() - self.jump_timer:
                self.player.jump_ability = True  # Allow player to jump
                self.player.jump_boost = self.player.max_jump  # Setup jump
                self.player.jump_sound_1.play()  # Play jump sound
                self.player.jumps += 1  # Add to a jump counter
                self.jump_timer = pygame.time.get_ticks()  # Reset jump timer

            # Pressing the jump key to stop player freezing and start level
            # This also updates the replay linked list
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] \
                    and not self.player.alive:
                if 0 < len(self.resp_jumps):
                    self.memory.update_temp(self.resp_jumps + self.hold_jumps)
                self.player.alive = True
                self.jump_timer = pygame.time.get_ticks()
            if every_key in [pygame.K_ESCAPE]:
                self.pause_index = 0
                self.player.freeze = not self.player.freeze
                self.pause = not self.pause
            # Navigate pause menu
            if every_key == pygame.K_w and not self.options_page and \
                    self.player.freeze and self.pause:
                self.pause_index -= 1
                self.pause_timer = pygame.time.get_ticks()
            elif every_key == pygame.K_s and not self.options_page and \
                    self.player.freeze and self.pause:
                self.pause_index += 1
                self.pause_timer = pygame.time.get_ticks()

            # Quick Restart counter (safe and default values)
            if every_key is pygame.K_r:
                self.memory.qr_counter += 1

            # Choosing options from pause screen
            if self.player.freeze and self.pause and \
                    every_key == pygame.K_SPACE:
                self.memory.options_status = -1
                # self.options_page = False
                # print(f"{self.options_page} - options page")
                self.pause_options[self.pause_index]()
                # Put this here to have it run only once
                if self.options_page:
                    self.platforms = []
                    self.win_zones = []
                    self.death_zones = []
                    self.respawn_zones = []
                    self.memory.options_status = self.level_id
                    self.load_renders(
                        OPTIONS_ID)  # options page during the game
            if every_key in [pygame.K_s]:
                if -1 < self.player.square_render.collidelist(
                        self.special_objects):
                    self.special_options[
                        self.player.square_render.collidelist(
                            self.special_objects)]()

            if every_key == pygame.K_d and \
                    1080 - self.player.width < self.player.xpos:
                self.change_scene(LevelSelect(self.memory))
            elif every_key == pygame.K_a and \
                    self.player.xpos < 0:
                self.change_scene(LevelSelect(self.memory))

        if held[pygame.K_a] and \
                0 <= self.player.xpos:
            self.player.direction = -1
        elif held[pygame.K_d] and \
                self.player.xpos + self.player.width <= 1080:
            self.player.direction = 1
        else:
            self.player.direction = 0

        # Held controls for choosing options
        if self.player.freeze and self.pause and held[pygame.K_s] and \
                not self.options_page and \
                200 < pygame.time.get_ticks() - self.pause_timer:
            self.pause_index += 1
            self.pause_timer = pygame.time.get_ticks()
        elif self.player.freeze and self.pause and held[pygame.K_w] and \
                not self.options_page and \
                200 < pygame.time.get_ticks() - self.pause_timer:
            self.pause_index -= 1
            self.pause_timer = pygame.time.get_ticks()

    def update(self):
        LevelScene.update(self)

    def go_to_hubselect(self):
        self.change_scene(HubSelect(self.memory))

    def render(self, screen):
        LevelScene.render(self, screen)  # <--
        if self.memory.hub_index in self.backgrounds:
            screen.blit(self.backgrounds[self.memory.hub_index], (0, 0))
        self.render_level(screen)

        for element in self.render_objects:
            if element.type == "rect":  # rect drawings
                pygame.draw.rect(screen, element.color, element.shape)
            else:  # line drawings
                pygame.draw.line(screen, element.color,
                                 [element.shape[0], element.shape[1]],
                                 [element.shape[2], element.shape[3]],
                                 element.shape[4])

        if not self.options_page:
            self.player.render(screen)

            if self.player.freeze and self.pause:
                pygame.draw.rect(screen, DARK_PURPLE, [330, 150, 420, 340])
                pygame.draw.rect(screen, GOLDELLOW, [340, 160, 400, 320])
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
                screen.blit(self.pause_text_6.text_img,
                            self.pause_text_6.text_rect)

                if 0 <= self.pause_index < len(self.pause_options):
                    selected_option = self.pause_list[
                        self.pause_index].text_rect
                    pygame.draw.rect(screen, DARK_PURPLE,
                                     [selected_option.x - 4,
                                      selected_option.y - 2,
                                      selected_option.width + 8,
                                      selected_option.height + 4], 2)

        self.player.render(screen)

    def render_level(self, screen):
        for each_rect in self.platforms:
            pygame.draw.rect(screen, BLACK, each_rect)

        for each_rect in self.special_objects:
            pygame.draw.rect(screen, GOLDELLOW, each_rect)


class Filler(kogclass.Scene):
    """Used as a placeholder for unfinished parts of the game"""

    def __init__(self, level_memory):
        kogclass.Scene.__init__(self)
        self.level_id = -1  # Invalid level id, don't record statistics
        self.filler_text = kogclass.Text(
            "THERE'S NOTHING HERE, PRESS R TO GO BACK",
            (540, 213), 50, "impact", DARK_RED, None)
        self.filler_text.scale(level_memory.res_width,
                               level_memory.res_height)
        self.memory = level_memory

    def input(self, pressed, held):
        for every_key in pressed:
            # Pressing R allows you to go back
            if every_key == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0,
                                            0)
                self.change_scene(MenuScene(24, 303, self.memory))

    def render(self, screen):
        # Render default white and the go back message
        screen.fill(WHITE)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)


class Instructions(kogclass.Scene):
    """Render an image of the instructions"""

    def __init__(self, level_memory):
        kogclass.Scene.__init__(self)
        self.level_id = -1  # Invalid level id, don't record statistics
        self.memory = level_memory

        file_path = "assets/images/instructions/"
        file_img = "InstructionsClass.png"

        if not os.path.isdir(file_path):
            print("No folder for instructions exists")
            self.close_game()
        if not os.path.isfile(file_path + file_img):
            print("Missing image for instructions")
            self.close_game()
        load_img = pygame.image.load(file_path +
                                     file_img).convert_alpha()
        self.instructions = pygame.transform.scale(load_img, (1080,
                                                   576))

    def input(self, pressed, held):
        for every_key in pressed:
            # Pressing R allows you to go back
            if every_key == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0,
                                            0)
                self.change_scene(MenuScene(24, 303, self.memory))

    def render(self, screen):
        # Render default white and the go back message
        screen.fill(WHITE)
        screen.blit(self.instructions, (0, 0))


class OptionsPage(LevelScene):
    """Class used to allow player to change game options"""

    def __init__(self, level_memory):
        LevelScene.__init__(self, -50, -50, level_memory)
        # Initialize LevelScene class objects (mainly for memory/rendering)

        # Used to define the bounds for certain settings
        self.setting_range = {
            0: [0, 2],
            1: [255, 235],
            2: [1, 2],
            3: [0, 100],
            4: [0, 100]
        }

        # Remember the last value for this setting
        self.setting_mem = {
            0: self.memory.diff_value,
            1: self.memory.bg_slider,
            2: self.memory.quick_restart,
            3: self.memory.music.perc_vol,
            4: self.memory.sound_vol
        }

        # Setup select options (so far, difficulty and music)

        self.num_to_diff = {0.6: "Easy", 0.8: "Medium", 1.0: "Hard"}
        # Difficulties available

        self.setting_words = {}

        self.setting_type = {
            0: ["Text", "Text", "Text"],
            1: ["Text", "Slider", "Text", "Text", "Text", "Text"],
            2: ["Text", "Text", "Text"],
            3: ["Text", "Slider", "Text", "Text", "Text", "Text"],
            4: ["Text", "Slider", "Text", "Text", "Text", "Text"]
        }  # What type of setting is it
        self.update_text()  # Add text to setting_words to render

        self.choose_setting = 0
        # Index for which setting to change (diff/music)
        self.change_setting = self.memory.diff_value
        # Variable for changing that selected setting (easy vs. hard)

        self.option_title = kogclass.Text("OPTIONS", ((1080 / 2), 50), 50,
                                          "impact", DARK_RED, None)
        self.option_title.scale(self.memory.res_width,
                                self.memory.res_height)
        self.return_text = kogclass.Text(
            "press R to go back", (1080 / 2, 100), 25,
            "impact", DARK_GREY, None)
        self.return_text.scale(self.memory.res_width,
                               self.memory.res_height)

        self.change_speed = 1
        # How fast holding the button will change the option
        self.change_time = pygame.time.get_ticks()
        # Time in between changing the selected option
        self.speed_inc = 1
        # How much time in changing the selected option has passed

        self.menu_buffer = pygame.time.get_ticks()
        # Time to transition between scenes and not change settings

        self.load_renders(OPTIONS_ID)

        self.hold_res = False  # Used to only apply res changes once

    def input(self, pressed, held):
        for action in pressed:
            # Go through the list of settings the player can change
            if action in [pygame.K_s, pygame.K_DOWN] and \
                    1200 < pygame.time.get_ticks() - self.menu_buffer:
                self.choose_setting += 1
            elif action in [pygame.K_w, pygame.K_UP] and \
                    1200 < pygame.time.get_ticks() - self.menu_buffer:
                self.choose_setting -= 1

            # Change that selected setting
            if action in [pygame.K_a, pygame.K_LEFT] and \
                    (200 / self.change_speed) < \
                    pygame.time.get_ticks() - self.change_time and \
                    1200 < pygame.time.get_ticks() - self.menu_buffer:
                self.setting_mem[self.choose_setting] -= 1
                self.change_time = pygame.time.get_ticks()
            elif action in [pygame.K_d, pygame.K_RIGHT] and \
                    (200 / self.change_speed) < \
                    pygame.time.get_ticks() - self.change_time and \
                    1200 < pygame.time.get_ticks() - self.menu_buffer:
                self.setting_mem[self.choose_setting] += 1
                self.change_time = pygame.time.get_ticks()

            # If press "R", return to main menu
            if action is pygame.K_r:
                if self.memory.options_status == -1:
                    self.change_scene(Hubzones(0, 0, self.memory))
                if self.memory.options_status == 0:
                    self.memory.music.set_music(0, self.memory.music.max_vol,
                                                -1, 0,
                                                0)
                    self.change_scene(MenuScene(24, 303, self.memory))
                elif 0 < self.memory.options_status:
                    self.platforms = []
                    self.win_zones = []
                    self.death_zones = []
                    self.respawn_zones = []
                    self.access_options()
                    self.load_renders(self.memory.options_status)

        if held[pygame.K_a] and (1000 / self.change_speed) < \
                pygame.time.get_ticks() - self.change_time and \
                1200 < pygame.time.get_ticks() - self.menu_buffer:
            self.setting_mem[self.choose_setting] -= 1
            self.change_time = pygame.time.get_ticks()

        elif held[pygame.K_d] and (1000 / self.change_speed) < \
                pygame.time.get_ticks() - self.change_time and \
                1200 < pygame.time.get_ticks() - self.menu_buffer:
            self.setting_mem[self.choose_setting] += 1
            self.change_time = pygame.time.get_ticks()

        if not (held[pygame.K_a] or held[pygame.K_d]):
            self.speed_inc = pygame.time.get_ticks()
            self.change_speed = 1

    def update(self):
        # Ensure bounds of choosing which select option is within bounds
        if self.choose_setting < 0:
            self.choose_setting = len(self.setting_mem) - 1
        elif len(self.setting_mem) - 1 < self.choose_setting:
            self.choose_setting = 0

        # Ensure bounds of how you want to change that setting is in bounds
        if self.setting_mem[self.choose_setting] < min(
                self.setting_range[self.choose_setting]):
            self.setting_mem[self.choose_setting] = max(
                self.setting_range[self.choose_setting])
        elif max(self.setting_range[self.choose_setting]) < \
                self.setting_mem[self.choose_setting]:
            self.setting_mem[self.choose_setting] = min(
                self.setting_range[self.choose_setting])

        # Apply those changes in memory
        self.memory.diff_value = self.setting_mem[0]
        self.memory.bg_slider = self.setting_mem[1]
        self.memory.background = [
            self.memory.bg_slider,
            self.memory.bg_slider,
            self.memory.bg_slider
        ]
        self.memory.quick_restart = self.setting_mem[2]
        self.memory.music.perc_vol = self.setting_mem[3]
        self.memory.sound_vol = self.setting_mem[4]

        # Increment how quick changing the settings go
        if 250 * self.change_speed < \
                pygame.time.get_ticks() - self.speed_inc and \
                self.change_speed < 21:
            self.change_speed += 1

        # Update the text with the respective changes
        self.update_text()

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle

        # Highlight and render the current option
        for count in range(len(self.setting_type[self.choose_setting])):
            render_type = self.setting_type[self.choose_setting][count]
            render_option = self.setting_words[self.choose_setting][count]
            if render_type == "Text":
                screen.blit(render_option.text_img,
                            render_option.text_rect)
            elif render_type == "Slider":
                pygame.draw.rect(screen, PURPLE,
                                 [render_option,
                                  255 * self.memory.res_height,
                                  10 * self.memory.res_height,
                                  10 * self.memory.res_width])
                pygame.draw.rect(screen, BLACK, [430 * self.memory.res_width,
                                                 265 * self.memory.res_height,
                                                 220 * self.memory.res_width,
                                                 3 * self.memory.res_height])
            elif render_type == "Rect":
                pass
            else:
                raise "Invalid Option Identifier Error"

        # Render option_titles and highlight selected option
        screen.blit(self.option_title.text_img, self.option_title.text_rect)
        screen.blit(self.return_text.text_img, self.return_text.text_rect)

        # Render Settings Decor
        for element in self.render_objects:
            if element.type == "rect":  # rect drawings
                pygame.draw.rect(screen, element.color, element.shape)
            else:  # line drawings
                pygame.draw.line(screen, element.color,
                                 [element.shape[0], element.shape[1]],
                                 [element.shape[2], element.shape[3]],
                                 element.shape[4])

        LevelScene.render_text(self, screen)

    def update_text(self):
        # Update or initialize self.setting_words with text
        self.setting_words = {
            0: [kogclass.Text("Difficulty: " +
                              str(self.num_to_diff[
                                      self.memory.diff_lookup[
                                          self.memory.diff_value]]),
                              (int(1080 / 2 * self.memory.res_width),
                               int(200 * self.memory.res_height)),
                              50 * max(self.memory.res_width,
                                       self.memory.res_height), "impact",
                              YELLOW, None),
                kogclass.Text("Choose the player movement speed with",
                              (int(1080 / 2 * self.memory.res_width),
                               int(315 * self.memory.res_height)),
                              25, "impact", YELLOW, None),
                kogclass.Text(
                    "easy (slow), medium (default) and hard (fastest)",
                    (int(1080 / 2 * self.memory.res_width),
                     int(340 * self.memory.res_height)),
                    25, "impact", YELLOW, None)],
            1: [kogclass.Text("Change Background", (
                int(1080 / 2 * self.memory.res_width),
                int(200 * self.memory.res_height)),
                              50 * max(self.memory.res_width,
                                       self.memory.res_height), "impact",
                              YELLOW, None),
                (40 + (11 * (
                        self.memory.bg_slider - 200))) * self.memory.res_width,
                kogclass.Text("LIGHT GREY", (345 * self.memory.res_width,
                                             265 * self.memory.res_height),
                              25 * max(self.memory.res_width,
                                       self.memory.res_height),
                              "impact", BLACK, None),
                kogclass.Text("WHITE", (715 * self.memory.res_width,
                                        265 * self.memory.res_height),
                              25 * max(self.memory.res_width,
                                       self.memory.res_height),
                              "impact", BLACK, None),
                kogclass.Text("Change the background ranging between",
                              (int(1080 / 2 * self.memory.res_width),
                               int(315 * self.memory.res_height)),
                              25, "impact", YELLOW, None),
                kogclass.Text("light grey and white",
                              (int(1080 / 2 * self.memory.res_width),
                               int(340 * self.memory.res_height)),
                              25, "impact", YELLOW, None)
                ],
            2: [kogclass.Text("Quick Restart: Press R " +
                              str(self.memory.quick_restart) + " Time(s)",
                              (int(1080 / 2 * self.memory.res_width),
                               int(200 * self.memory.res_height)),
                              50 * max(self.memory.res_width,
                                       self.memory.res_height), "impact",
                              YELLOW, None),
                kogclass.Text("Change how many times you'll need",
                              (int(1080 / 2 * self.memory.res_width),
                               int(315 * self.memory.res_height)),
                              25, "impact", YELLOW, None),
                kogclass.Text("press \"R\" to restart a level",
                              (int(1080 / 2 * self.memory.res_width),
                               int(340 * self.memory.res_height)),
                              25, "impact", YELLOW, None)
                ],
            3: [kogclass.Text("Set Music Volume", (
                int(1080 / 2 * self.memory.res_width),
                int(200 * self.memory.res_height)),
                              50 * max(self.memory.res_width,
                                       self.memory.res_height), "impact",
                              YELLOW, None),
                (430 - 5 +
                 (2.2 * self.memory.music.perc_vol)) * self.memory.res_width,
                kogclass.Text("MIN", (355 * self.memory.res_width,
                                      265 * self.memory.res_height),
                              25 * max(self.memory.res_width,
                                       self.memory.res_height),
                              "impact", BLACK, None),
                kogclass.Text("MAX", (715 * self.memory.res_width,
                                      265 * self.memory.res_height),
                              25 * max(self.memory.res_width,
                                       self.memory.res_height),
                              "impact", BLACK, None),
                kogclass.Text("Change the music volume on a scale",
                              (int(1080 / 2 * self.memory.res_width),
                               int(315 * self.memory.res_height)),
                              25, "impact", YELLOW, None),
                kogclass.Text("from 0 to 100",
                              (int(1080 / 2 * self.memory.res_width),
                               int(340 * self.memory.res_height)),
                              25, "impact", YELLOW, None)
                ],
            4: [kogclass.Text("Set Sound Volume", (
                int(1080 / 2 * self.memory.res_width),
                int(200 * self.memory.res_height)),
                              50 * max(self.memory.res_width,
                                       self.memory.res_height), "impact",
                              YELLOW, None),
                (430 - 5 + (
                        2.2 * self.memory.sound_vol)) * self.memory.res_width,
                kogclass.Text("MIN", (355 * self.memory.res_width,
                                      265 * self.memory.res_height),
                              25 * max(self.memory.res_width,
                                       self.memory.res_height),
                              "impact", BLACK, None),
                kogclass.Text("MAX", (715 * self.memory.res_width,
                                      265 * self.memory.res_height),
                              25 * max(self.memory.res_width,
                                       self.memory.res_height),
                              "impact", BLACK, None),
                kogclass.Text("Change the sound volume on a scale",
                              (int(1080 / 2 * self.memory.res_width),
                               int(315 * self.memory.res_height)),
                              25, "impact", YELLOW, None),
                kogclass.Text("from 0 to 100",
                              (int(1080 / 2 * self.memory.res_width),
                               int(340 * self.memory.res_height)),
                              25, "impact", YELLOW, None)
                ],
        }

        self.setting_type = {
            0: ["Text", "Text", "Text"],
            1: ["Text", "Slider", "Text", "Text", "Text", "Text"],
            2: ["Text", "Text", "Text"],
            3: ["Text", "Slider", "Text", "Text", "Text", "Text"],
            4: ["Text", "Slider", "Text", "Text", "Text", "Text"]
        }


class ReplayIO(LevelScene):
    """Class used to display UI for file/text input and output"""

    def __init__(self, level_memory):
        LevelScene.__init__(self, -50, -50, level_memory)
        self.file_in = kogclass.Text("File Input", (1080 / 3, 376 / 3),
                                     50, "impact", PURPLE, None)
        self.file_in.scale(self.memory.res_width,
                           self.memory.res_height)
        self.file_out = kogclass.Text("File Output", (1080 / 3, 376 / 3 * 2),
                                      50, "impact", PURPLE, None)
        self.file_out.scale(self.memory.res_width,
                            self.memory.res_height)

        self.text_in = kogclass.Text("Text Input", (1080 / 3 * 2, 376 / 3),
                                     50, "impact", PURPLE, None)
        self.text_in.scale(self.memory.res_width,
                           self.memory.res_height)
        self.text_out = kogclass.Text("Text Output", (1080 / 3 * 2,
                                                      376 / 3 * 2),
                                      50, "impact", PURPLE, None)
        self.text_out.scale(self.memory.res_width,
                            self.memory.res_height)
        self.return_text = kogclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", DARK_GREY, None)
        self.return_text.scale(self.memory.res_width,
                               self.memory.res_height)

        self.icon_list = [self.file_in, self.text_in,
                          self.file_out, self.text_out]
        """
        file/text layout:

                 file_in                    text_in


                 file_out                   text_out

        """

        self.choose_counter = 0

        self.help_text = [
            kogclass.Text("Press Space to Import Replays!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None),
            kogclass.Text("Press Space to Paste a Level!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None),
            kogclass.Text("Press Space to Export Replays!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None),
            kogclass.Text("Press Space to Select a Level to Copy!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None)
        ]
        self.help_text[0].scale(self.memory.res_width,
                                self.memory.res_height)
        self.help_text[1].scale(self.memory.res_width,
                                self.memory.res_height)
        self.help_text[2].scale(self.memory.res_width,
                                self.memory.res_height)
        self.help_text[3].scale(self.memory.res_width,
                                self.memory.res_height)

        self.extra_help = [
            kogclass.Text("Remember to paste replays_out into replays_in!",
                          (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None),
            kogclass.Text("", (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None),
            kogclass.Text("Go check and copy from replays_out!",
                          (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None),
            kogclass.Text("", (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None)
        ]
        self.extra_help[0].scale(self.memory.res_width,
                                 self.memory.res_height)
        self.extra_help[1].scale(self.memory.res_width,
                                 self.memory.res_height)
        self.extra_help[2].scale(self.memory.res_width,
                                 self.memory.res_height)
        self.extra_help[3].scale(self.memory.res_width,
                                 self.memory.res_height)

        self.invalid_text = kogclass.Text("INVALID Copy and Paste, Try Again!",
                                          (1080 / 2, 576 / 3), 75,
                                          "impact", RED, None)
        self.invalid_text.scale(self.memory.res_width,
                                self.memory.res_height)
        self.invalid_timer = pygame.time.get_ticks() - 3100

    def input(self, pressed, held):
        for action in pressed:
            if action is pygame.K_w:
                self.choose_counter -= 2
            elif action is pygame.K_a:
                self.choose_counter -= 1
            elif action is pygame.K_s:
                self.choose_counter += 2
            elif action is pygame.K_d:
                self.choose_counter += 1

            if action is pygame.K_r:
                self.change_scene(MenuScene(24, 303, self.memory))

            if action is pygame.K_SPACE:
                # File in
                if self.choose_counter == 0:
                    self.memory.read_replays()
                    self.change_scene(ReplaySelect(self.memory))

                # Text in
                elif self.choose_counter == 1:
                    if 0 < len(str(pygame.scrap.get(pygame.SCRAP_TEXT),
                                   "utf-8")) or \
                            str(pygame.scrap.get(pygame.SCRAP_TEXT),
                                "utf-8") is not None:
                        in_str = str(pygame.scrap.get(pygame.SCRAP_TEXT),
                                     "utf-8")
                    else:
                        in_str = ""
                    if 9 < len(in_str) and ", " in in_str and \
                            "[" in in_str and "]" in in_str:
                        in_list = in_str[1:-1].split(", ")
                        if in_list[0].isnumeric() and \
                                in_list[1].isnumeric():
                            valid_input = True
                        else:
                            valid_input = False
                            self.invalid_timer = pygame.time.get_ticks()
                    else:
                        in_list = []
                        valid_input = False
                        self.invalid_timer = pygame.time.get_ticks()

                    if valid_input:
                        ind_count = 2
                        out_list = []
                        while ind_count < len(in_list) and valid_input:
                            if in_list[ind_count][1].isalpha() and \
                                    in_list[ind_count][2:-2].isnumeric():
                                out_list += [in_list[ind_count]]
                                ind_count += 1
                            else:
                                valid_input = False
                        if valid_input:
                            self.memory.imp_diff[int(in_list[0])] = int(
                                in_list[1])
                            self.memory.replay_imp[int(in_list[0])] = out_list
                            self.change_scene(ReplaySelect(self.memory))
                        else:
                            self.invalid_timer = pygame.time.get_ticks()
                            # invalid here too
                    else:
                        self.invalid_timer = pygame.time.get_ticks()
                        # text invalid stuff

                # File out
                elif self.choose_counter == 2:
                    self.memory.write_replays()

                # Text out
                elif self.choose_counter == 3:
                    self.change_scene(ReplayOut(self.memory))
            # Add space bar to select option (once to select)

    def update(self):
        if self.choose_counter < 0:
            self.choose_counter = self.choose_counter + 4
        elif 3 < self.choose_counter:
            self.choose_counter = self.choose_counter - 4

    def render(self, screen):
        LevelScene.render(self, screen)

        screen.blit(self.file_in.text_img, self.file_in.text_rect)
        screen.blit(self.file_out.text_img, self.file_out.text_rect)
        screen.blit(self.text_in.text_img, self.text_in.text_rect)
        screen.blit(self.text_out.text_img, self.text_out.text_rect)
        screen.blit(self.return_text.text_img, self.return_text.text_rect)
        screen.blit(self.help_text[self.choose_counter].text_img,
                    self.help_text[self.choose_counter].text_rect)
        screen.blit(self.extra_help[self.choose_counter].text_img,
                    self.extra_help[self.choose_counter].text_rect)

        pygame.draw.rect(screen, YELLOW,
                         [self.icon_list[self.choose_counter].text_rect.x - 6,
                          self.icon_list[self.choose_counter].text_rect.y - 6,
                          self.icon_list[
                              self.choose_counter].text_rect.width + 12,
                          self.icon_list[
                              self.choose_counter].text_rect.height + 12], 2)

        if pygame.time.get_ticks() - self.invalid_timer < 3000:
            screen.blit(self.invalid_text.text_img,
                        self.invalid_text.text_rect)


class StatsPage(LevelScene):
    """ Class used to display the statistics for that game instance depending
    on the amount of levels that the player has completed
    """

    def __init__(self, level_memory):
        # For now, leave the player clone out of bounds
        LevelScene.__init__(self, -50, -50, level_memory)
        # Initialize LevelScene for it's memory/rendering
        self.memory.level_progress.sort()  # Sort level order
        self.level_id = -1  # Invalid level id, don't record statistics
        self.memory = level_memory  # Get memory

        # If statement used to detect if player has no levels recorded
        if len(self.memory.level_progress) == 0:
            self.select_level = None  # No levels available
            self.render_stats = []  # No statistics to render
            self.nothing_text = kogclass.Text(
                "GO COMPLETE SOME LEVELS FIRST!", (1080 / 2, (576 / 2)), 50,
                "impact", DARK_RED, None)
            self.nothing_text.scale(self.memory.res_width,
                                    self.memory.res_height)
        # Otherwise, set the counter to 0 (first displayed level) and display
        # the statistics
        else:
            self.select_level = 0  # set the counter to 0, first selection
            self.update_stats()  # Update text for the statistics shown

        self.return_text = kogclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", DARK_GREY, None)
        self.return_text.scale(self.memory.res_width,
                               self.memory.res_height)

    def input(self, pressed, held):
        # Check if there are level's completed
        if self.select_level is not None:
            for action in pressed:
                # Change displayed level (move to left)
                if action == pygame.K_a:
                    self.select_level -= 1
                # Change displayed level (move to right)
                elif action == pygame.K_d:
                    self.select_level += 1

        for action in pressed:
            # Always display the return message
            if action == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0,
                                            0)
                self.change_scene(MenuScene(24, 303, self.memory))

    def update(self):
        # Check if there are levels completed
        if self.select_level is not None:
            # Ensure level selection is in bounds
            if len(self.memory.level_progress) - 1 < self.select_level:
                self.select_level = 0
            elif self.select_level < 0:
                self.select_level = len(self.memory.level_progress) - 1

            # Update the text statistics with the level selected
            self.update_stats()

    def update_stats(self):
        # Get the time for that current level selected
        get_time = self.memory.level_times[
            self.memory.level_progress[self.select_level]]
        # Get total time for that game instance
        self.memory.total_time = pygame.time.get_ticks()
        total_time = kogclass.convert_time(self.memory.total_time)

        # Initialize text for the statistics for that selected level
        self.render_stats = [
            kogclass.Text(
                "LEVEL: " + str(self.memory.level_progress[self.select_level]),
                (1080 / 2, (576 / 2) - 25), 25, "impact", YELLOW, None),
            kogclass.Text("Deaths: " + str(self.memory.level_deaths[
                                               self.memory.level_progress[
                                                   self.select_level]]),
                          (1080 / 2, (576 / 2)), 25, "impact", YELLOW, None),
            kogclass.Text("Jumps: " + str(self.memory.level_jumps[
                                              self.memory.level_progress[
                                                  self.select_level]]),
                          (1080 / 2, (576 / 2) + 25), 25, "impact", YELLOW,
                          None),
            kogclass.Text("Total Deaths: " + str(self.memory.total_deaths),
                          ((1080 / 4), 50), 25, "impact", YELLOW, None),
            kogclass.Text("Total Jumps: " + str(self.memory.total_jumps),
                          ((1080 / 4 * 3), 50), 25, "impact", YELLOW, None),
            kogclass.Text("Total Time:",
                          ((1080 / 4 * 2), 50), 25, "impact", YELLOW, None),
            kogclass.Text(
                str(total_time[0]) + ":" + str(total_time[1]) + ":" + str(
                    total_time[2]),
                ((1080 / 4 * 2), 100), 25, "impact", YELLOW, None),
            kogclass.Text("Level Time: " + str(get_time[0]) + ":" + str(
                get_time[1]) + ":" + str(get_time[2]),
                          ((1080 / 4 * 2), (576 / 2) + 50), 25, "impact",
                          YELLOW, None),
            kogclass.Text("Total Stars Collected: " + \
                          str(self.memory.total_stars),
                          ((1080 / 4), 75), 25, "impact", YELLOW, None),
            kogclass.Text("Stars: " + \
                          str(self.memory.stars_collected[self.select_level]),
                          ((1080 / 4 * 2), (576 / 2) + 75), 25, "impact",
                          YELLOW, None)
        ]

    def render(self, screen):
        LevelScene.render(self, screen)  # Background Colors or Back-most
        self.render_level(screen)  # Level Elements or Middle

        # Render the selected levels statistics
        if self.select_level is not None:
            for stat_text in self.render_stats:
                screen.blit(stat_text.text_img, stat_text.text_rect)
        else:
            # If there's no levels completed, tell player to return
            screen.blit(self.nothing_text.text_img, self.nothing_text.text_rect)

        # Always render return text
        screen.blit(self.return_text.text_img, self.return_text.text_rect)

        # Render any LevelScene text, no use, just for formatting/consistency
        LevelScene.render_text(self, screen)


class UniversalSelect(LevelScene):
    """
    Level select class made as a transition between menu and levels. It also
    allows the player to choose a specific level (based on completion -
    to be implemented in the future)
    """

    def __init__(self, level_memory):
        LevelScene.__init__(self, (1080 / 2) - (10 / 2), 576 / 2, level_memory)
        self.player.width = 20
        self.player.height = 20
        """Initialize LevelScene with player parameters to the middle
        of the screen.
        """
        self.level_selector_text_0 = kogclass.Text("Choose a Level", (535, 100),
                                                   65,
                                                   "impact", YELLOW, None)
        self.level_selector_text_0.scale(self.memory.res_width,
                                         self.memory.res_height)

        self.level_selector_text_1 = kogclass.Text(
            "Tap/Hold A or D to navigate through the levels",
            (535, 450), 30, "impact", YELLOW, None)
        self.level_selector_text_1.scale(self.memory.res_width,
                                         self.memory.res_height)

        self.level_selector_text_2 = kogclass.Text(
            "Tap R to return to Main Menu", (545, 530), 25,
            "impact", DARK_GREY, None)
        self.level_selector_text_2.scale(self.memory.res_width,
                                         self.memory.res_height)

        self.level_selector_text_3 = kogclass.Text(
            "Press W or Space to start the level",
            (535, 490), 28, "impact", YELLOW, None)
        self.level_selector_text_3.scale(self.memory.res_width,
                                         self.memory.res_height)

        self.confirm_text = kogclass.Text("UNLOCKED ALL LEVELS",
                                          (1080 / 2, 576 / 2), 100, "impact",
                                          RED, None)
        self.confirm_text.scale(self.memory.res_width,
                                self.memory.res_height)

        self.blockmation_time = 0  # Time variable for moving level boxes
        self.text_x = 0  # Used to define the x position of level number text
        self.direction = 0  # Toggle determining direction level text moves
        self.choose_id = 0  # Rewrite in child class, int greater than 0

        self.memory = level_memory

        self.repjump_time = 0  # "Repeat jump" time, time until speed increases
        self.speed_jump = 1  # Determines selection speed
        self.allow_select = True  # If levels can be freely chosen

        self.level_set = []  # Rewrite in child class, should be list
        self.confirm_timer = pygame.time.get_ticks() - 3000

        self.level_offset = 0  # Visually offset numbers

    def input(self, pressed, held):
        for every_key in pressed:
            # Allow player to choose a level (based on ID) after 0.405 seconds
            if self.allow_select and \
                    every_key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w] and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                # Alter in child class if it's a hub or level set
                pass
            # Every 0.405 seconds, have the player jump
            if every_key in [pygame.K_a, pygame.K_d] and \
                    self.player.jump_ability and \
                    not self.player.enable_gravity and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.player.jump_boost = self.player.max_jump  # Setup jump
                self.player.jump_sound_1.play()  # Play jump sound
                self.player.jumps += 1  # Add to jump counter (useless)

                # Move the blocks to the right (illusion of player going left)
                if every_key == pygame.K_a and \
                        self.level_set[0] < self.choose_id:
                    self.blockmation_time = pygame.time.get_ticks()
                    # Reset timer for block animation
                    self.direction = 1  # Blocks going to the right
                # Move the blocks to the left (illusion of player going right)
                if every_key == pygame.K_d and \
                        self.choose_id < self.level_set[-1]:
                    self.blockmation_time = pygame.time.get_ticks()
                    # Reset timer for block animation
                    self.direction = -1  # Blocks going to the left

        """Make the player jump as well as move the blocks right (illusion of
        player going to the left).
        Else, make the player jump as well as move the blocks left (illusion of
        player going to the right).
        Both actions have to occur after at least 0.405 seconds from 
        the last action. Both have checks for boundaries
        """
        if held[pygame.K_a] and self.level_set[0] < self.choose_id and \
                self.player.jump_ability and \
                not self.player.enable_gravity and \
                (405 / self.speed_jump) < \
                pygame.time.get_ticks() - self.blockmation_time:
            self.player.jump_boost = self.player.max_jump  # Setup jump
            self.player.jump_sound_1.play()  # Play jump sound
            self.player.jumps += 1  # Add to jump counter (useless)

            self.blockmation_time = pygame.time.get_ticks()
            # Reset timer for block animation
            self.direction = 1  # Set block direction to the right
        elif held[pygame.K_d] and \
                self.choose_id < self.level_set[-1] and \
                self.player.jump_ability and \
                not self.player.enable_gravity and \
                (405 / self.speed_jump) < \
                pygame.time.get_ticks() - self.blockmation_time:
            self.player.jump_boost = self.player.max_jump  # Setup jump
            self.player.jump_sound_1.play()  # Play jump sound
            self.player.jumps += 1  # Add to jump counter (useless)

            self.blockmation_time = pygame.time.get_ticks()
            # Reset timer for block animation
            self.direction = -1  # Set block direction to the left

        # If nothing is held, reset the quick jump
        if not held[pygame.K_a] and not held[pygame.K_d]:
            self.repjump_time = pygame.time.get_ticks()

        # Secret :P
        if held[pygame.K_k] and held[pygame.K_o] and held[pygame.K_g] and \
                pygame.K_ESCAPE:
            for level_key in self.level_data:
                if 0 < level_key and level_key not in self.level_set:
                    self.level_set += [level_key]
            self.confirm_timer = pygame.time.get_ticks()

    def update(self):
        LevelScene.update(self)  # Have player collision and elements (useless)
        self.player.alive = True  # Player will always be alive
        self.player.xpos = self.x_spawn  # Set x position to spawn
        self.player.diff_factor = self.speed_jump  # Make sure jump constant

        # If statement ensures y position is always constant
        # If y position is below the y spawn (middle)
        if self.y_spawn <= self.player.ypos:
            self.player.ypos = self.y_spawn  # Set the y position to spawn again
            self.player.enable_gravity = False  # No gravity
            self.player.gravity_counter = self.player.max_gravity  # Reset grav
            self.player.jump_ability = True  # Allow jumps

        # After 3 seconds, speed up jumping
        if 3000 <= pygame.time.get_ticks() - self.repjump_time:
            self.speed_jump = 2  # The jump speed multiplier
        else:
            self.speed_jump = 1  # The jump speed multiplier

    def render(self, screen):
        LevelScene.render(self, screen)  # Basic rendering (screen.fill, etc.)

        LevelScene.render_text(self, screen)  # LevelScene text (useless)

        # Rendering the instructions of using the level-selector
        if not self.memory.enable_replay:
            screen.blit(self.level_selector_text_0.text_img,
                        self.level_selector_text_0.text_rect)
        screen.blit(self.level_selector_text_1.text_img,
                    self.level_selector_text_1.text_rect)
        screen.blit(self.level_selector_text_2.text_img,
                    self.level_selector_text_2.text_rect)
        screen.blit(self.level_selector_text_3.text_img,
                    self.level_selector_text_3.text_rect)

        # Text seen to the left side (current selection, -1)
        left_text = kogclass.Text(str(self.choose_id - 1 - self.level_offset),
                                  [(1080 / 2) - 200 + self.text_x,
                                   (576 / 2) + 39], 40, "impact", YELLOW,
                                  None)
        left_text.scale(self.memory.res_width,
                        self.memory.res_height)
        # Text seen in the middle/what the player is standing on (current sel)
        middle_text = kogclass.Text(str(self.choose_id - self.level_offset),
                                    [(1080 / 2) + self.text_x,
                                     (576 / 2) + 39],
                                    40, "impact", YELLOW, None)
        middle_text.scale(self.memory.res_width,
                          self.memory.res_height)
        # Text seen to the right side (current selection, +1)
        right_text = kogclass.Text(str(self.choose_id + 1 - self.level_offset),
                                   [(1080 / 2) + 200 + self.text_x,
                                    (576 / 2) + 39], 40, "impact", YELLOW,
                                   None)
        right_text.scale(self.memory.res_width,
                         self.memory.res_height)

        scroll_text = [left_text, middle_text, right_text]
        # Make a list to render it in a for loop

        for texts in scroll_text:
            """The if statement conditions around texts.text_rect.x allow
            the rects to be rendered until they go past the black bar. This
            gives the illusion that all the levels are rendered in a long line,
            but really we're loading/unloading them using these boundaries
            (between x of (1080 / 2) - 225 and (1080 / 2) + 195)
            """
            if ((1080 / 2) - 225) * self.memory.res_width < \
                    texts.text_rect.x < (
                    (1080 / 2) + 195) * self.memory.res_height and \
                    0 < int(texts.text) <= len(self.level_data):
                screen.blit(texts.text_img, texts.text_rect)
                pygame.draw.rect(screen,
                                 (0, 0, 0),  # Draw a black rect
                                 [texts.text_rect.x - 20,
                                  texts.text_rect.y - 5,
                                  texts.text_rect.width + 40,
                                  texts.text_rect.height + 10],
                                 4)
                """The rects x - 20 moves the text back 20, while the width of
                40 will move the rects x forward by 40, centering it 
                horizontally around the player 
                and be wide enough for the player to stand or jump on.
                The rects y - 5 but height of + 10 does the same and centers it
                vertically (slightly down for the player).
                """

        # If 0.4 seconds have passed (note that this is less than 0.405 as used
        # before), then move the text 4.4 by that direction
        if pygame.time.get_ticks() - self.blockmation_time < \
                400 / self.speed_jump:
            if self.direction == 1:
                self.text_x += 4.4 * self.speed_jump

            if self.direction == -1:
                self.text_x -= 4.4 * self.speed_jump
        # Otherwise, center the text position in the middle and make it the
        # current level selected
        else:
            if self.text_x != 0:
                # Change self.choose_id respectively
                self.choose_id += -1 * self.direction
            self.text_x = 0

        # 4 Sides surrounding level select to make a box
        pygame.draw.rect(screen, (0, 0, 0),
                         [int(((1080 / 2) - 250) * self.memory.res_width),
                          int(((576 / 2) - 100) * self.memory.res_height),
                          math.ceil(500 * self.memory.res_width),
                          math.ceil(10 * self.memory.res_height)])
        pygame.draw.rect(screen, (0, 0, 0),
                         [int(((1080 / 2) - 250) * self.memory.res_width),
                          int(((576 / 2) + 100) * self.memory.res_height),
                          math.ceil(500 * self.memory.res_width),
                          math.ceil(10 * self.memory.res_height)])
        pygame.draw.rect(screen, (0, 0, 0),
                         [int(((1080 / 2) - 250) * self.memory.res_width),
                          int(((576 / 2) - 100) * self.memory.res_height),
                          math.ceil(70 * self.memory.res_width),
                          math.ceil(200 * self.memory.res_height)])
        pygame.draw.rect(screen, (0, 0, 0),
                         [int(((1080 / 2) + 250 - 70) * self.memory.res_width),
                          int(((576 / 2) - 100) * self.memory.res_height),
                          math.ceil(70 * self.memory.res_width),
                          math.ceil(200 * self.memory.res_height)])

        if pygame.time.get_ticks() - self.confirm_timer < 3000:
            screen.blit(self.confirm_text.text_img,
                        self.confirm_text.text_rect)


class LevelSelect(UniversalSelect):
    def __init__(self, level_memory):
        UniversalSelect.__init__(self, level_memory)
        self.level_set = self.memory.id_range[self.memory.hub_index]
        self.choose_id = self.level_set[0]  # Level ID chosen
        self.level_offset = self.choose_id - 1

    def input(self, pressed, held):
        UniversalSelect.input(self, pressed, held)
        for every_key in pressed:
            # Return player to menu if pressing "R"
            if every_key == pygame.K_r:
                self.memory.music.set_music(self.memory.hub_index,
                                            self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(Hubzones(0, 0, self.memory))

            if self.allow_select and \
                    every_key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w] and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.change_scene(PlayLevel(self.level_data[self.choose_id][0],
                                            self.level_data[self.choose_id][1],
                                            self.memory, self.choose_id))
                # Load a level using memory and that level id

    def update(self):
        UniversalSelect.update(self)

    def render(self, screen):
        UniversalSelect.render(self, screen)


class HubSelect(LevelSelect):
    def __init__(self, level_memory):
        UniversalSelect.__init__(self, level_memory)
        self.level_set = [1, len(self.memory.id_range) - 1]
        self.choose_id = self.memory.hub_index + 1
        self.level_selector_text_0 = kogclass.Text("Choose a Hubzone",
                                                   (535, 100),
                                                   65,
                                                   "impact", YELLOW, None)
        self.level_selector_text_0.scale(self.memory.res_width,
                                         self.memory.res_height)

    def input(self, pressed, held):
        UniversalSelect.input(self, pressed, held)
        for every_key in pressed:
            # Return player to menu if pressing "R"
            if every_key == pygame.K_r:
                self.memory.music.set_music(self.memory.hub_index,
                                            self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(Hubzones(0, 0, self.memory))

            if self.allow_select and \
                    every_key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w] and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.memory.hub_index = self.choose_id - 1
                self.memory.music.set_music(self.memory.hub_index,
                                            self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(Hubzones(0, 0, self.memory))
                # Load a level using memory and that level id

    def update(self):
        UniversalSelect.update(self)

    def render(self, screen):
        UniversalSelect.render(self, screen)


class ReplaySelect(UniversalSelect):
    """Class that's similar to Level Select but has an extra filter
    for selecting levels with only valid replays"""

    def __init__(self, level_memory):
        UniversalSelect.__init__(self, level_memory)
        self.choose_id = 1
        self.allow_select = False  # Toggle off, cannot freely choose
        self.no_data = kogclass.Text("NO DATA", [1080 / 2, 576 / 2], 100,
                                     "impact", RED, None)
        self.no_data.scale(self.memory.res_width,
                           self.memory.res_height)
        self.replay_title = kogclass.Text("Choose A Replay Level",
                                          (1080 / 2, 160), 50, "impact",
                                          YELLOW, None)
        self.replay_title.scale(self.memory.res_width,
                                self.memory.res_height)
        self.level_set = [1, (len(self.memory.level_set) - 1)]

    def input(self, pressed, held):
        if self.choose_id in self.memory.replay_imp and \
                0 < len(self.memory.replay_imp[self.choose_id]):
            self.allow_select = True
        else:
            self.allow_select = False

        UniversalSelect.input(self, pressed, held)

        for action in pressed:
            # Return player to menu if pressing "R"
            if action == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0,
                                            0)
                self.change_scene(MenuScene(24, 303, self.memory))

            if self.allow_select and \
                    action in [pygame.K_UP, pygame.K_SPACE, pygame.K_w] and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.change_scene(PlayLevel(self.level_data[self.choose_id][0],
                                            self.level_data[self.choose_id][1],
                                            self.memory, self.choose_id))

    def update(self):
        UniversalSelect.update(self)

    def render(self, screen):
        UniversalSelect.render(self, screen)
        if self.choose_id in self.memory.replay_imp and \
                0 == len(self.memory.replay_imp[self.choose_id]):
            screen.blit(self.no_data.text_img, self.no_data.text_rect)

        screen.blit(self.replay_title.text_img,
                    self.replay_title.text_rect)


class ReplayOut(UniversalSelect):
    def __init__(self, level_memory):
        UniversalSelect.__init__(self, level_memory)
        self.level_set = [1, (len(self.memory.level_set) - 1)]
        self.choose_id = 1
        self.allow_select = False
        self.copy_text = kogclass.Text("Copied Level " + str(self.choose_id),
                                       (1080 / 2, 3 * 576 / 4),
                                       50, "impact", YELLOW, None)
        self.copy_text.scale(self.memory.res_width,
                             self.memory.res_height)
        self.copy_time = pygame.time.get_ticks() - 3100
        self.replayo_title = kogclass.Text("Choose a Level to Copy!",
                                           (1080 / 2, 160), 50, "impact",
                                           YELLOW, None)
        self.replayo_title.scale(self.memory.res_width,
                                 self.memory.res_height)

        self.no_data = kogclass.Text("NO DATA", [1080 / 2, 576 / 2], 100,
                                     "impact", RED, None)
        self.no_data.scale(self.memory.res_width,
                           self.memory.res_height)

    def input(self, pressed, held):
        UniversalSelect.input(self, pressed, held)
        for action in pressed:
            # Return player to menu if pressing "R"
            if action == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0,
                                            0)
                self.change_scene(MenuScene(24, 303, self.memory))

            if self.choose_id in self.memory.replay_exp and \
                    self.memory.replay_exp[self.choose_id] != [] and \
                    action == pygame.K_SPACE:
                self.copy_time = pygame.time.get_ticks()
                self.copy_text = kogclass.Text(
                    "Copied Level " + str(self.choose_id),
                    (1080 / 2, 3 * 576 / 4),
                    50, "impact", YELLOW, None)
                self.copy_text.scale(self.memory.res_width,
                                     self.memory.res_height)
                pygame.scrap.put(pygame.SCRAP_TEXT,
                                 bytes(str(
                                     self.memory.replay_exp[self.choose_id]),
                                     "utf-8"))

    def update(self):
        UniversalSelect.update(self)
        self.allow_select = False

    def render(self, screen):
        UniversalSelect.render(self, screen)
        if self.choose_id in self.memory.replay_exp and \
                0 == len(self.memory.replay_exp[self.choose_id]):
            screen.blit(self.no_data.text_img, self.no_data.text_rect)

        if pygame.time.get_ticks() - self.copy_time <= 3000:
            screen.blit(self.copy_text.text_img,
                        self.copy_text.text_rect)

        screen.blit(self.replayo_title.text_img,
                    self.replayo_title.text_rect)


class PlayLevel(LevelSelect, OptionsPage):
    """
    Class used to play levels defined in levels.txt. Levels are first
    loaded in kog_class with Memory into their dictionaries. Then the level
    id's selected in the LevelSelect determines what level is played here.
    On level completion, another PlayLevel instance is initialized but
    with level id + 1 (next level).
    """

    def __init__(self, x_spawn, y_spawn,
                 level_memory, play_id):
        OptionsPage.__init__(self, level_memory)
        LevelScene.__init__(self, x_spawn, y_spawn, level_memory)
        # Initialize __init__ for player, spawn and memory.
        self.level_id = play_id  # Set the level id
        self.element_names = list(self.level_elements[self.level_id].keys())
        # Get all the available level elements available
        self.collision_objects = {"self.platforms": self.platforms,
                                  "self.death_zones": self.death_zones,
                                  "self.win_zones": self.win_zones,
                                  "self.respawn_zones": self.respawn_zones}
        # Combine collision objects into a dict of lists

        self.render_objects = []  # Initialize render objects
        self.end_time = pygame.time.get_ticks()

        self.start_toggle = True  # By default, allow player to start anytime

        for name in self.element_names:
            # Get DSNElement objects that aren't under Text
            if name != "Text" and name in self.level_elements[self.level_id]:
                # For each element in the level, get collision and render lists
                for element in self.level_elements[self.level_id][name]:
                    if name in self.collision_objects:
                        self.collision_objects[name] += [element.shape]
                        # Add rect objects for collision (collision, no render)
                    self.render_objects += [element]
                    # Load up render objects (only rendering, no collision)
        self.display_left = kogclass.Text("Deaths: " + str(self.deaths) +
                                           ", Jumps: " + str(self.player.jumps),
                                           [90, 10], 20, "impact", YELLOW,
                                           None)

        time = kogclass.convert_time(pygame.time.get_ticks() - self.start_time)
        self.display_right = kogclass.Text(kogclass.format_time(time),
                                           [1080 - (6 * 8), 10], 20, "impact", YELLOW,
                                           None)
        """For time's x, I do 1080 - 8 times 8 since the length of the 
        time string is 8, and each char is about 8 pixels"""

        # Replay Option if enabled
        if self.memory.enable_replay:
            self.player.diff_factor = self.memory.diff_lookup[
                level_memory.imp_diff[self.level_id]]
            self.replayer_xspawn = self.x_spawn
            self.replayer_yspawn = self.y_spawn
            self.replayer = kogclass.SquareMe(self.replayer_xspawn,
                                              self.replayer_yspawn,
                                              10, 10, GREY,
                                              self.memory.diff_lookup[
                                                  level_memory.imp_diff[
                                                      self.level_id]],
                                              self.memory.res_width,
                                              self.memory.res_height,
                                              self.memory.sound_vol)
            self.replay_counter = 0
            self.replay_time = int(
                self.memory.replay_imp[self.level_id][0][2:-1])
            self.lose_condition = False
            self.win_text = kogclass.Text("WIN", [1080 / 2, 576 / 2], 250,
                                          "impact", YELLOW, None)
            self.win_text.scale(self.memory.res_width,
                                self.memory.res_height)
            self.lose_text = kogclass.Text("LOSE", [1080 / 2, 576 / 2], 250,
                                           "impact", YELLOW, None)
            self.lose_text.scale(self.memory.res_width,
                                 self.memory.res_height)
            self.count_down = 3
            self.count_change = pygame.time.get_ticks()
            self.count_time = pygame.time.get_ticks()  # Time spent counting
            self.start_toggle = False

            self.count_text = kogclass.Text(str(self.count_down), [1080 / 2,
                                                                   576 / 2],
                                            250,
                                            "impact", YELLOW, None)
            self.count_text.scale(self.memory.res_width,
                                  self.memory.res_height)

    def input(self, pressed, held):
        if not self.start_toggle:
            return None

        # Use the default player inputs in LevelScene.input (controls/options)
        if self.level_id in self.level_data:
            LevelScene.input(self, pressed, held)

        if self.options_page:
            OptionsPage.input(self, pressed, held)

        for action in pressed:
            if action == pygame.K_ESCAPE and not self.level_condition:
                if self.level_id in self.memory.star_data:
                    for star in self.memory.star_data[self.level_id]:
                        star.freeze = not star.freeze

    def update(self):
        if not self.start_toggle:
            if 1000 < pygame.time.get_ticks() - self.count_change and \
                    1 < self.count_down:
                self.count_down -= 1
                self.count_text = kogclass.Text(str(self.count_down), [1080 / 2,
                                                                       576 / 2],
                                                250,
                                                "impact", YELLOW, None)
                self.count_text.scale(self.memory.res_width,
                                      self.memory.res_height)
                self.count_change = pygame.time.get_ticks()

            if 3000 < pygame.time.get_ticks() - self.count_time:
                self.start_toggle = True
                self.player.alive = True
            else:
                # Change the time at the start of the level
                self.start_toggle = False
            return None

        # Use the default update features (collision, pausing, victory, etc.)
        if self.level_id in self.level_data:
            LevelScene.update(self)
            # Optimized Text updating
            self.display_left.text = "Deaths: " + \
                                               str(self.deaths) + \
                                               ", Jumps: " + \
                                               str(self.player.jumps)
            self.display_left.setup()
            self.display_left.render()
            time = kogclass.convert_time(pygame.time.get_ticks() -
                                         self.start_time)
            self.display_right.text = kogclass.format_time(time)
            self.display_right.setup()
            self.display_right.render()

        # Update star position and player detection
        if self.level_id in self.memory.star_data and not self.pause and \
                not self.player.freeze:
            for star in self.memory.star_data[self.level_id]:
                star.update(pygame.Rect(self.player.xpos,
                                        self.player.ypos,
                                        self.player.width,
                                        self.player.height))

        if self.options_page:
            OptionsPage.update(self)
            # Continously update the changes here
            # might have to put a toggle if it's causing lag
            self.player.diff_factor = \
                self.memory.diff_lookup[self.memory.diff_value]
            self.player.jump_sound_1.set_volume(0.1 *
                                                (self.memory.sound_vol / 100))
            pygame.mixer.music.set_volume(0.7 *
                                          (self.memory.music.perc_vol / 100))

        # If enabled replay, have the other player function
        if self.memory.enable_replay:

            if self.replay_counter < len(
                    self.memory.replay_imp[self.level_id]) and \
                    int(self.memory.replay_imp[self.level_id]
                        [self.replay_counter][2:-1]) - self.replay_time <= \
                    self.loop_counter and \
                    not (self.lose_condition or self.level_condition):
                if self.memory.replay_imp[self.level_id][self.replay_counter][
                   1:2] == "J":
                    self.replayer.gravity_counter = self.replayer.max_gravity
                    self.replayer.jump_ability = True  # Allow player to jump
                    self.replayer.jump_boost = self.player.max_jump
                    # Setup jump

                elif self.memory.replay_imp[self.level_id][self.replay_counter][
                     1:2] == "R":
                    self.replayer.xpos = self.replayer_xspawn
                    self.replayer.ypos = self.replayer_yspawn
                    self.replayer.alive = True
                    self.replayer.freeze = False
                    self.replayer.direction = 1

                self.replay_counter += 1

            self.replay_update()

            if self.level_condition or self.lose_condition:
                self.player.alive = False
                self.replayer.alive = False

        """After victory (and animations), update the memory with statistics
        for that level, change the level id, then pass it onto another
        PlayLevel class instance (next level)"""
        # Not replay mode
        if not self.memory.enable_replay:
            if 3 <= self.victory_counter and 500 <= pygame.time.get_ticks() - \
                    self.victory_time:
                # Get stars collected
                star_count = 0
                if self.level_id in self.memory.star_data:
                    for star in self.memory.star_data[self.level_id]:
                        if not star.alive:
                            star_count += 1
                # Update statistics with this level's data
                self.memory.update_mem(self.level_id, self.deaths,
                                       self.player.jumps, self.start_time,
                                       star_count)
                # Add this level's timed jumps/unfreezes
                self.memory.update_temp(self.resp_jumps + self.hold_jumps)
                self.memory.update_replays(
                    self.level_id,
                    [self.level_id] +
                    [self.memory.diff_value] +
                    self.memory.hold_replay.chain_to_list())
                # Reset temporary hold on chain of level's timed events
                self.memory.hold_replay = kogclass.ReplayChain()
                self.level_id += 1

                if self.level_id in self.level_data:
                    if self.memory.id_range[self.memory.hub_index][0] \
                            <= self.level_id <= \
                            self.memory.id_range[self.memory.hub_index][1]:
                        self.change_scene(
                            PlayLevel(self.level_data[self.level_id][0],
                                      self.level_data[self.level_id][1],
                                      self.memory,
                                      self.level_id))
                    else:
                        self.memory.hub_index += 1
                        self.change_scene(Hubzones(0, 0, self.memory))
                else:
                    # The very last level
                    # todo: Change this in the future for endings etc
                    self.change_scene(MenuScene(24, 303, self.memory))
        # Replay Mode
        else:

            if self.level_condition and \
                    3000 < pygame.time.get_ticks() - self.end_time:
                self.change_scene(ReplaySelect(self.memory))
            elif self.lose_condition and \
                    3000 < pygame.time.get_ticks() - self.end_time:
                self.change_scene(ReplaySelect(self.memory))

            if not (self.level_condition or self.lose_condition):
                self.end_time = pygame.time.get_ticks()

    def replay_update(self):
        if not self.start_toggle:
            return None

        if self.replayer is None or \
                self.replayer.square_render is None:
            return None

        # Replayer is alive, not paused and haven't run, then check collision
        if self.replayer.alive and not self.replayer.freeze and \
                not self.level_condition:
            # Check if replayer collided with death zones (returns 1 or 0)
            self.replayer.death(self.death_zones)
            self.replayer.collision_plat(self.platforms)  # Top and bottom coll
            self.replayer.collision_wall(self.platforms)  # Side collision
            self.replayer.move()  # replayer movement

        """Respawn for square players, reset spawn position, set direction
        to right by default, reset gravity"""
        if not self.replayer.alive and not self.replayer.freeze and \
                not self.level_condition:
            # No need for a jump timer
            self.replayer.jump_boost = -1 * (self.player.max_jump - 1)
            self.replayer.jump_ability = False
            self.replayer.xpos = self.replayer_xspawn
            self.replayer.ypos = self.replayer_yspawn
            self.replayer.direction = 1
            self.replayer.gravity_counter = self.replayer.max_gravity

        # If player is below the level, count as a death (out of bounds)
        if (576 * self.memory.res_height) + \
                self.replayer.height < self.replayer.ypos:
            self.replayer.alive = False

        # Check for win collision
        if self.replayer.alive and \
                self.replayer.square_render.collidelist(self.win_zones) != -1:
            self.lose_condition = True
            self.replayer.alive = False

        # Respawn block collision
        if self.replayer.alive and \
                self.replayer.square_render.collidelist(
                    self.respawn_zones) != -1:
            # Setup respawn block for readability
            respawn_block = self.replayer.square_render.collidelist(
                self.respawn_zones)
            # Set new x and y default spawns
            self.replayer_xspawn = \
                self.respawn_zones[respawn_block].x + \
                (self.respawn_zones[
                     respawn_block].width / 2) - 5
            self.replayer_yspawn = \
                self.respawn_zones[respawn_block].y + \
                (self.respawn_zones[
                     respawn_block].height / 2) - 5

    def render(self, screen):
        if self.level_id in self.level_data:
            if not self.options_page:
                # Default LevelScene rendering (screen)
                LevelScene.render(self, screen)

                if self.memory.enable_replay:
                    # Render the replayer ghost first
                    self.replayer.render(screen)

                # Render level rects/lines/draw
                self.render_level(screen)

                # Text Rendering for that level
                if "Text" in self.level_elements[self.level_id]:
                    for text in self.level_elements[self.level_id]["Text"]:
                        screen.blit(text.text_img, text.text_rect)

                # Render Stars
                if self.level_id in self.memory.star_data:
                    for star in self.memory.star_data[self.level_id]:
                        star.render(screen)

                # Lastly, render text
                LevelScene.render_text(self, screen)
                if self.memory.enable_replay:
                    if self.level_condition and \
                            1000 < pygame.time.get_ticks() - self.end_time:
                        screen.blit(self.win_text.text_img,
                                    self.win_text.text_rect)
                    elif self.lose_condition and \
                            1000 < pygame.time.get_ticks() - self.end_time:
                        screen.blit(self.lose_text.text_img,
                                    self.lose_text.text_rect)

                # Countdown for replays
                if not self.start_toggle and self.memory.enable_replay:
                    screen.blit(self.count_text.text_img,
                                self.count_text.text_rect)

                # Render special images/animations
                if self.level_id in self.memory.images:
                    for image in self.memory.images[self.level_id]:
                        image.render(screen)

                # Display statistics
                screen.blit(self.display_left.text_img,
                            self.display_left.text_rect)
                screen.blit(self.display_right.text_img,
                            self.display_right.text_rect)

            else:
                OptionsPage.render(self, screen)

    def render_level(self, screen):
        # Render all the rect/line objects for that level (visual)
        for element in self.render_objects:
            if element.type == "rect":  # rect drawings
                pygame.draw.rect(screen, element.color, element.shape)
            else:  # line drawings
                pygame.draw.line(screen, element.color,
                                 [element.shape[0], element.shape[1]],
                                 [element.shape[2], element.shape[3]],
                                 element.shape[4])


class Tutorial(PlayLevel):
    def __init__(self, x_spawn, y_spawn, level_memory, play_id):
        PlayLevel.__init__(self, x_spawn, y_spawn, level_memory, play_id)


class LevelZero(LevelScene):

    def __init__(self, level_memory):

        LevelScene.__init__(self, 45, 525, level_memory)
        # Initialize LevelScene for it's memory/rendering
        self.memory.level_progress.sort()  # Sort level order
        self.level_id = -1  # Invalid level id, don't record statistics
        self.memory = level_memory  # Get memory
        # self.timer = pygame.time.get_ticks()
        self.timer = 0
        self.fps = pygame.time.Clock()
        self.elasped = self.fps.tick(30)
        self.countdown = 45
        self.delete_everything_text = False

        # choosing level is set to None
        self.choose_level = None

        self.str_morse_code = ""  # morse code entries for short and long
        self.str_words = ""  # words to be displayed on screen as an entry for the user
        self.str_pass_word_check = ''  # checking if the word is correct
        self.morse_code_count = 0  # making sure you can't input more than 5 characters

        self.clear_code_morse_block = []  # box to clear text
        self.convert_code_morse_block = []  # box to convert morse_code into english aplhabets
        self.check_correct_morse_block = []  # checking if word exists in lock
        self.clear_all_text_morse_block = []  # clearing all texts

        self.short_dot = []  # short box entry
        self.long_dot = []  # long box entry

        ''''
        still trying to figure the timed text part
        '''

        self.level_text = [
            kogclass.Text(self.str_morse_code, (545, 413),
                          35, "impact", DARK_GREY, None),
            kogclass.Text(self.str_words, (545, 223),
                          105, "impact", BLACK, None),
            kogclass.Text("Check", (775, 453),
                          25, "impact", BLACK, None),
            kogclass.Text("Word", (775, 483),
                          25, "impact", BLACK, None),
            kogclass.Text("Clear", (270, 453),
                          25, "impact", BLACK, None),
            kogclass.Text("Code", (270, 483),
                          25, "impact", BLACK, None),
            kogclass.Text("Convert", (525, 453),
                          25, "impact", BLACK, None),
            kogclass.Text("Code", (525, 483),
                          25, "impact", BLACK, None),
            kogclass.Text("Everthing Has Been Reset", (525, 100),
                          55, "impact", DARK_RED, None)
        ]
        self.level_text[0].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[1].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[2].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[3].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[4].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[5].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[6].scale(level_memory.res_width,
                                 level_memory.res_height)
        self.level_text[7].scale(level_memory.res_width,
                                 level_memory.res_height)
        # self.level_text[2].scale(level_memory.res_width,
        #                            level_memory.res_height)

        self.collision_objects = {
            "self.platforms": self.platforms,
            "self.short_dot": self.short_dot,
            "self.long_dot": self.long_dot
        }

        self.render_objects = []

        self.action_timer = pygame.time.get_ticks()

    def input(self, pressed, held):
        LevelScene.input(self, pressed, held)

    def morse_decoder(self, morse_code_text, display):

        # keeping it in a string, redundant yes, can be removed and replaced
        morse_code = str(morse_code_text)

        # morse code dictionary
        morse_dict = {
            'short_long_': 'A', 'long_short_short_short_': 'B',
            'long_short_long_short_': 'C', 'long_short_short_': 'D',
            'short_': 'E',
            'short_short_long_short_': 'F', 'long_long_short_': 'G',
            'short_short_short_short_': 'H', 'short_short_': 'I',
            'short_long_long_long_': 'J',
            'long_short_long_': 'K', 'short_long_short_short_': 'L',
            'long_long_': 'M', 'long_short_': 'N', 'long_long_long_': 'O',
            'short_long_long_short_': 'P', 'long_long_short_long_': 'Q',
            'short_long_short_': 'R', 'short_short_short_': 'S', 'long_': 'T',
            'short_short_long_': 'U', 'short_short_short_long_': 'V',
            'short_long_long_': 'W', 'long_short_short_long_': 'X',
            'long_short_long_long_': 'Y',
            'long_long_short_short_': 'Z', 'long_long_long_long_long_': '0',
            'short_long_long_long_long_': '1',
            'short_short_long_long_long_': '2',
            'short_short_short_long_long_': '3',
            'short_short_short_short_long_': '4',
            'short_short_short_short_short_': '5',
            'long_short_short_short_short_': '6',
            'long_long_short_short_short_': '7',
            'long_long_long_short_short_': '8',
            'long_long_long_long_short_': '9'
        }

        # checking if morse code exists or not
        if morse_code_text in morse_dict:
            display = morse_dict[morse_code]
        else:
            print("No morse_code like that exists. "
                  "Please refer to the 'Internationl Morse Code'")

        return display  # appears to be missing an argument

    def clear_display_morse_code(self):
        self.str_morse_code = ''
        self.morse_code_count = 0
        # print("morse code text has been cleared!")
        # print(f"{self.str_morse_code} and
        # {self.morse_code_count} and {len(self.str_words)}")

    def clear_display_english_words(self):
        self.str_words = ''
        self.morse_code_count = 0
        # print("attempted answer has been cleared!")
        # print(f"{self.str_morse_code} and
        # {self.morse_code_count} and {self.str_words}")

    def pass_word_morse_code(self, f_string, display):
        adict = {
            'EE': '000000000000000000',
            'ET': '000000001111111100',
            'E': '1111111111111100000'
        }
        g_string = str(f_string)

        if f_string in adict:
            display = adict[g_string]
        else:
            display = 'what is going on here?'
        print(display)
        return display

    def update(self):
        LevelScene.update(self)

        # This is when you win

        if pygame.time.get_ticks() - self.timer < 1200:
            pass

        # if self.delete_everything_text == True:
        #         self.delete_everything_text_function()

        if self.morse_code_count < 5:
            if self.player.alive and \
                    self.player.square_render.collidelist(self.short_dot) != -1:
                self.str_morse_code = self.str_morse_code + "short_"
                self.morse_code_count += 1
                self.action_timer = pygame.time.get_ticks()
                # print(f"{self.str_morse_code} and {self.morse_code_count}")
            elif self.player.alive and \
                    self.player.square_render.collidelist(self.long_dot) != -1:
                self.str_morse_code = self.str_morse_code + "long_"
                self.morse_code_count += 1
                self.action_timer = pygame.time.get_ticks()
                # print(f"{self.str_morse_code} and {self.morse_code_count}")
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.clear_code_morse_block) != -1:
                self.clear_display_morse_code()
                self.action_timer = pygame.time.get_ticks()
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.convert_code_morse_block) != -1:
                self.str_words += self.morse_decoder(self.str_morse_code,
                                                     self.str_words)
                self.clear_display_morse_code()
                self.action_timer = pygame.time.get_ticks()
                # print(f"{self.str_morse_code} and {self.morse_code_count}")
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.check_correct_morse_block) != -1:
                self.pass_word_morse_code(self.str_words,
                                          self.str_pass_word_check)
                self.clear_display_morse_code()
                self.action_timer = pygame.time.get_ticks()
                self.clear_display_english_words()
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.clear_all_text_morse_block) != -1:
                # print("deleted everything")
                self.delete_everything_text = True
                self.delete_everything_text_function()
                self.action_timer = pygame.time.get_ticks()
        elif self.morse_code_count == 5:
            print("Maximum character amount reached! Clear or Convert Code.")
            if self.player.alive and \
                    self.player.square_render.collidelist(
                        self.clear_code_morse_block) != -1:
                self.clear_display_morse_code()
                self.action_timer = pygame.time.get_ticks()
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.convert_code_morse_block) != -1:
                self.str_words += self.morse_decoder(self.str_morse_code,
                                                     self.str_words)
                print(f"{self.str_words}")
                self.clear_display_morse_code()
                self.action_timer = pygame.time.get_ticks()
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.check_correct_morse_block) != -1:
                self.pass_word_morse_code(self.str_words,
                                          self.str_pass_word_check)
                self.clear_display_morse_code()
                self.clear_display_english_words()
                self.action_timer = pygame.time.get_ticks()
            elif self.player.alive and \
                    self.player.square_render.collidelist(
                        self.clear_all_text_morse_block) != -1:
                # print("deleted everything")
                self.delete_everything_text = True
                self.delete_everything_text_function()
                self.action_timer = pygame.time.get_ticks()

            # print(self.timer)

    '''couldn't get this to work as 
    I would like to in a function, with screen in there'''

    def delete_everything_text_function(self):
        # if self.delete_everything_text == True:
        self.clear_display_morse_code()
        self.clear_display_english_words()
        # self.timer = self.timer + self.elasped/30 #should be /1000
        # if self.timer > self.countdown:
        #     self.delete_everything_text = False
        #     self.timer = 0
        # print(self.timer)

    def render(self, screen):
        LevelScene.render(self, screen)
        self.render_level(screen)

        # drawing platforms
        self.platforms = [
            pygame.draw.rect(screen, BLACK, [1055, 0, 25, 576]),
            pygame.draw.rect(screen, BLACK, [0, 0, 25, 576]),
            pygame.draw.rect(screen, BLACK, [0, 0, 1080, 23]),
            pygame.draw.rect(screen, BLACK, [0, 480, 1080, 23]),
            pygame.draw.rect(screen, BLACK, [0, 553, 1080, 23])
        ]

        self.clear_code_morse_block = [
            pygame.draw.rect(screen, BLUE, [200, 433, 150, 71])]  # bottom 480
        self.convert_code_morse_block = [
            pygame.draw.rect(screen, YELLOW, [450, 433, 150, 71])]
        self.check_correct_morse_block = [
            pygame.draw.rect(screen, LIME_GREEN, [700, 433, 150, 71])]
        self.clear_all_text_morse_block = [
            pygame.draw.rect(screen, LIGHT_RED, [100, 433, 50, 71]),
            pygame.draw.rect(screen, LIGHT_RED, [900, 433, 50, 71])
        ]

        self.long_dot = [pygame.draw.rect(screen, CYAN, [1054, 444, 17, 85])]
        self.short_dot = [pygame.draw.rect(screen, CYAN, [9, 488, 17, 39])]

        # display texts as they appear
        self.level_text[0] = kogclass.Text(self.str_morse_code, (545, 413),
                                           35, "impact", DARK_GREY, None)
        screen.blit(self.level_text[0].text_img,
                    self.level_text[0].text_rect)  # draw text

        self.test_text_2 = kogclass.Text(self.str_words, (545, 223),
                                         105, "impact", BLACK, None)
        screen.blit(self.test_text_2.text_img,
                    self.test_text_2.text_rect)

        # self.level_text[2] = kogclass.Text("Check", (775, 453),
        #                                 25, "impact", BLACK, None)
        screen.blit(self.level_text[2].text_img,
                    self.level_text[2].text_rect)

        # self.level_text[3] = kogclass.Text("Word", (775, 483),
        #                                 25, "impact", BLACK, None)
        screen.blit(self.level_text[3].text_img,
                    self.level_text[3].text_rect)

        # self.level_text[4] = kogclass.Text("Clear", (270, 453),
        #                                 25, "impact", BLACK, None)
        screen.blit(self.level_text[4].text_img,
                    self.level_text[4].text_rect)

        # self.level_text[5] = kogclass.Text("Code", (270, 483),
        #                                 25, "impact", BLACK, None)
        screen.blit(self.level_text[5].text_img,
                    self.level_text[5].text_rect)

        # self.level_text[6] = kogclass.Text("Convert", (525, 453),
        #                                 25, "impact", BLACK, None)
        screen.blit(self.level_text[6].text_img,
                    self.level_text[6].text_rect)

        # self.level_text[7] = kogclass.Text("Code", (525, 483),
        #                                 25, "impact", BLACK, None)
        screen.blit(self.level_text[7].text_img,
                    self.level_text[7].text_rect)

        # display for delete text
        if self.delete_everything_text:
            self.test_text_9 = kogclass.Text("Everthing Has Been Reset",
                                             (525, 100),
                                             55, "impact", DARK_RED, None)
            screen.blit(self.level_text[8].text_img,
                        self.level_text[8].text_rect)
            self.timer = self.timer + self.elasped / 30  # should be /1000
            if self.timer > self.countdown:
                self.delete_everything_text = False
                self.timer = 0

        LevelScene.render_text(self, screen)

    def render_level(self, screen):
        # No death zones in this level!
        pass
