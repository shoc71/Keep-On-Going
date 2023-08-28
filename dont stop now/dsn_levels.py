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
DARK_GREEN = (1, 100, 32)
PURPLE = (181, 60, 177)
BROWN = (150, 75, 0)
DARK_GREY = (52, 52, 52)

# todo: move to main loop
file_path = "assets/images/"
dont_image_text = pygame.image.load(file_path + "dont (Custom).png")  # ratio is 15:8
stop_image_text = pygame.image.load(file_path + "stop (Custom).png")
now_image_text = pygame.image.load(file_path + "now (Custom).png")


class LevelScene(dsnclass.Scene):
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
        dsnclass.Scene.__init__(self)
        self.platforms = []     # All platforms for that level (collision)
        self.death_zones = []   # All deaths for that level (death condition)
        self.win_zones = []     # All win areas for that level (win condition)
        self.respawn_zones = []  # todo: add new respawn zones to levels

        self.x_spawn = x_spawn  # x spawning location for player
        self.y_spawn = y_spawn  # y spawning location for player
        self.player = dsnclass.SquareMe(self.x_spawn, self.y_spawn,
                                        10, 10, PURPLE,
                                        level_memory.diff_lookup[
                                            level_memory.diff_value])
        """Initialize player variable in the level using the x and y spawn,
        constant widths and heights of 10, the color PURPLE, and the difficulty
        defined by level_memory (settings dependent)
        """
        self.deaths = 0     # Recorded deaths for that level instance
        self.play_time = 0  # Time accumulated in that level
        self.level_condition = False    # Check if player has won (touch win)
        self.victory_time = 0   # Time variable for victory text display
        self.victory_counter = 0    # The index of victory_text list
        self.victory_text = [
            dsnclass.Text("DON'T", (310, 100), 100, "impact", YELLOW, None),
            dsnclass.Text("STOP", (570, 100), 100, "impact", YELLOW, None),
            dsnclass.Text("NOW", (820, 100), 100, "impact", YELLOW, None)
        ]
        # Text displayed when winning (touch the win_zones), uses time/counter

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
        # Text displayed when player pauses the game (ESC)

        self.memory = level_memory

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

    def input(self, pressed, held):
        for every_key in pressed:

            # Pressing/tapping and not holding jump key to jump
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] and not \
                    self.player.enable_gravity and self.player.alive and not \
                    self.player.freeze and 150 <= pygame.time.get_ticks() - self.jump_timer:
                self.player.jump_ability = True # Allow player to jump
                self.player.jump_boost = self.player.max_jump   # Setup jump
                self.player.jump_sound_1.play()     # Play jump sound
                self.player.jumps += 1  # Add to a jump counter
                self.jump_timer = pygame.time.get_ticks()   # Reset jump timer

                self.hold_jumps += ["J" + str(self.loop_counter)]

            # Pressing the jump key to stop player freezing and start level
            # This also updates the replay linked list
            if every_key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE] \
                    and not self.player.alive:
                if 0 < len(self.resp_jumps):
                    self.memory.update_temp(self.resp_jumps + self.hold_jumps)
                    self.hold_jumps = []
                    self.resp_jumps = []
                self.player.alive = True
                self.jump_timer = pygame.time.get_ticks()

                self.resp_jumps += ["R" + str(self.loop_counter)]

            # Pausing the game and stopping player movement/action
            if every_key == pygame.K_ESCAPE and not self.level_condition:
                self.player.freeze = not self.player.freeze

            # If paused, press q to quit
            if every_key == pygame.K_q and self.player.freeze:
                self.run_scene = False

            # Restart the level from pause menu, which counts as a death
            if self.player.freeze and every_key == pygame.K_r:
                if 0 < len(self.resp_jumps):
                    self.memory.update_temp(self.resp_jumps + self.hold_jumps)
                    self.hold_jumps = []
                    self.resp_jumps = []

                self.resp_jumps += [
                    "R" + str(self.loop_counter)]

                self.player.alive = False
                self.player.freeze = False
                self.deaths += 1

            # Press b to go back to main menu
            if self.player.freeze and every_key == pygame.K_b:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(MenuScene(40, 360, self.memory))

        # Held controls for jumping
        if (held[pygame.K_SPACE] or held[pygame.K_w] or held[pygame.K_UP]) \
                and not self.player.enable_gravity and self.player.alive and \
                not self.player.freeze and 150 <= pygame.time.get_ticks() - self.jump_timer:
            self.player.jump_ability = True # Allow player to jump
            self.player.jump_boost = self.player.max_jump   # Setup jump
            self.player.jump_sound_1.play()     # Play jump sound
            self.player.jumps += 1  # Add to a jump counter
            self.jump_timer = pygame.time.get_ticks()   # Reset jump timer

            self.hold_jumps += ["J" + str(self.loop_counter)]

    def update(self):
        self.loop_counter += 1
        # Failsafe if player isn't rendered but level starts
        if self.player.square_render is None:
            return None # Player is not rendered, skip function

        # Player is alive, not paused and haven't run, then check collision
        if self.player.alive and not self.player.freeze and \
                not self.level_condition:
            # Check if player collided with death zones (returns 1 or 0)
            self.deaths += self.player.death(self.death_zones)
            self.player.collision_plat(self.platforms)  # Top and bottom coll
            self.player.collision_wall(self.platforms)  # Side collision
            self.player.move()  # Player movement

        """Respawn for square players, reset spawn position, set direction
        to right by default, reset gravity"""
        if not self.player.alive and not self.player.freeze and \
                not self.level_condition:
            self.jump_timer = pygame.time.get_ticks()   # Reset jump timer
            self.player.jump_boost = -1 * (self.player.max_jump - 1)
            self.player.jump_ability = False
            self.player.xpos = self.x_spawn
            self.player.ypos = self.y_spawn
            self.player.direction = 1
            self.player.gravity_counter = self.player.max_gravity

        # If player is below the level, count as a death (out of bounds)
        if 580 + self.player.height < self.player.ypos:
            self.player.alive = False
            self.deaths += 1

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

    def victory(self, screen):
        # Victory function played when win condition
        if 500 <= pygame.time.get_ticks() - self.victory_time and \
                self.victory_counter < 3:
            self.victory_time = pygame.time.get_ticks() # Reset timer
            self.victory_counter += 1   # Increase index for victory_text
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


class MenuScene(LevelScene):
    """
    Main Menu for Don't Stop Now game
    """
    def __init__(self, xspawn, yspawn, level_memory):
        # Use level_scene init, mainly to define the player and memory
        LevelScene.__init__(self, xspawn, yspawn, level_memory)
        self.level_id = 0   # Has a level id of 0 (defined to record jumps)
        self.option_count = 0   # Index counter to choose level
        self.options = [LevelSelect(level_memory), OptionsPage(level_memory),
                        StatsPage(level_memory), ReplayIO(level_memory)]
        # Main menu options

        # Main menu text
        self.title_splash = dsnclass.Text("DON'T STOP NOW", (540, 100), 100,
                                          "impact", YELLOW, None)
        self.title_text = dsnclass.Text("Press Space or W To Start", (530, 200),
                                        50, "impact",
                                        YELLOW, None)
        self.title_text_2 = dsnclass.Text("Press esc to pause", (530, 250), 30,
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
        self.title_text_s4 = dsnclass.Text("Replay", (864, 490), 30,
                                           "impact",
                                           YELLOW, None)

        # Text for displaying title select options organized in a lists
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
            # If player chooses option, update menu statistics and change scene
            if every_key in [pygame.K_SPACE, pygame.K_w]:
                self.memory.music.switch_music()
                self.memory.update_mem(self.level_id, self.deaths,
                                       self.player.jumps, self.start_time)
                self.change_scene(self.options[self.option_count])
            # Press right/d to move right of the selection
            if every_key is pygame.K_d:
                self.option_count += 1
            # Press left/a to move left of the selection
            if every_key is pygame.K_a:
                self.option_count -= 1

    def update(self):
        # Use levelscene update for collision and player movement
        LevelScene.update(self)
        self.player.alive = True    # Player cannot die (might be problematic)

        # If options selected go past right boundary, set it to the left
        if len(self.options) - 1 < self.option_count:
            self.option_count = 0
        # If options selected go past left boundary, set it to the right
        if self.option_count < 0:
            self.option_count = len(self.options) - 1

        # Have player jump randomly occur rather than input
        if (random.randint(1, 2500) <= 15) and not self.player.enable_gravity:
            self.player.jumps += 1  # Add to jump counter
            self.player.jump_ability = True # Allow player to jump
            self.player.jump_boost = self.player.max_jump   # Setup jump

        # Change if replays/second replay player should appear
        if self.option_count == 0:
            self.memory.replays_off()
        elif self.option_count == 3:
            self.memory.replays_on()  # Is a replay mode

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
    """Used as a placeholder for unfinished parts of the game"""
    def __init__(self, level_memory):
        dsnclass.Scene.__init__(self)
        self.level_id = -1  # Invalid level id, don't record statistics
        self.filler_text = dsnclass.Text(
            "THERE'S NOTHING HERE, PRESS R TO GO BACK",
            (540, 213), 50, "impact", DARK_RED, None)
        self.memory = level_memory

    def input(self, pressed, held):
        for every_key in pressed:
            # Pressing R allows you to go back
            if every_key == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(MenuScene(40, 360, self.memory))

    def render(self, screen):
        # Render default white and the go back message
        screen.fill(WHITE)
        screen.blit(self.filler_text.text_img, self.filler_text.text_rect)


class OptionsPage(LevelScene):
    # todo: add music/sound volume, need a memory variable to control all instances.
    """Class used to allow player to change game options"""
    def __init__(self, level_memory):
        LevelScene.__init__(self, -50, -50, level_memory)
        # Initialize LevelScene class objects (mainly for memory/rendering)

        # Used to define the bounds for certain settings
        self.setting_range = {
            0: [0, 2],
            1: [255, 200]
        }

        # Remember the last value for this setting
        self.setting_mem = {
            0: self.memory.diff_value,
            1: self.memory.bg_slider
        }

        # Setup select options (so far, difficulty and music)

        self.num_to_diff = {0.6: "Easy", 0.8: "Medium", 1.0: "Hard"}
        # Difficulties available
        self.setting_words = [] # Initialize list to hold current settings
        self.setting_type = []  # What type of setting is it
        self.update_text()  # Add text to setting_words to render

        self.choose_setting = 0 # Index for which setting to change (diff/music)
        self.change_setting = self.memory.diff_value
        # Variable for changing that selected setting (easy vs. hard)

        self.option_title = dsnclass.Text("OPTIONS", ((1080 / 2), 50), 50,
                                          "impact", DARK_RED, None)
        self.return_text = dsnclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", DARK_GREY, None)

        self.change_speed = 1
        # How fast holding the button will change the option
        self.change_time = pygame.time.get_ticks()
        # Time in between changing the selected option
        self.speed_inc = 1
        # How much time in changing the selected option has passed

    def input(self, pressed, held):
        for action in pressed:
            # Go through the list of settings the player can change
            if action in [pygame.K_s, pygame.K_DOWN]:
                self.choose_setting += 1
            elif action in [pygame.K_w, pygame.K_UP]:
                self.choose_setting -= 1

            # Change that selected setting
            if action in [pygame.K_a, pygame.K_LEFT] and \
                    (50 / self.change_speed) < \
                    pygame.time.get_ticks() - self.change_time:
                self.setting_mem[self.choose_setting] -= 1
                self.change_time = pygame.time.get_ticks()
            elif action in [pygame.K_d, pygame.K_RIGHT] and \
                    (50 / self.change_speed) < \
                    pygame.time.get_ticks() - self.change_time:
                self.setting_mem[self.choose_setting] += 1
                self.change_time = pygame.time.get_ticks()

            # If press "R", return to main menu
            if action is pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(MenuScene(40, 360, self.memory))

        if held[pygame.K_a] and (1000 / self.change_speed) < \
                pygame.time.get_ticks() - self.change_time:
            self.setting_mem[self.choose_setting] -= 1
            self.change_time = pygame.time.get_ticks()

        elif held[pygame.K_d] and (1000 / self.change_speed) < \
                pygame.time.get_ticks() - self.change_time:
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
        if self.setting_mem[self.choose_setting] < min(self.setting_range[self.choose_setting]):
            self.setting_mem[self.choose_setting] = max(self.setting_range[self.choose_setting])
        elif max(self.setting_range[self.choose_setting]) < self.setting_mem[self.choose_setting]:
            self.setting_mem[self.choose_setting] = min(self.setting_range[self.choose_setting])

        # Apply those changes
        self.memory.diff_value = self.setting_mem[0]
        self.memory.bg_slider = self.setting_mem[1]
        self.memory.background = [
            self.memory.bg_slider,
            self.memory.bg_slider,
            self.memory.bg_slider
        ]

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

        # Highlight the current option
        if self.setting_type[self.choose_setting] == "Text":
            hl_rect = self.setting_words[self.choose_setting].text_rect
        else:
            hl_rect = self.setting_words[self.choose_setting]

        pygame.draw.rect(screen, DARK_RED,
                         [hl_rect.x - 4, hl_rect.y - 1,
                          hl_rect.width + 8, hl_rect.height + 2], 2)

        # Write the current settings available on the screen
        screen.blit(self.setting_words[0].text_img,
                    self.setting_words[0].text_rect)    # Difficulty

        pygame.draw.rect(screen, BLACK, self.setting_words[1])
        pygame.draw.rect(screen, PURPLE,
                         [430 - 5 + (4 * (self.memory.bg_slider - 200)),
                          375, 10, 10])     # Background slider

        # Render option_titles and highlight selected option
        screen.blit(self.option_title.text_img, self.option_title.text_rect)
        screen.blit(self.return_text.text_img, self.return_text.text_rect)

        LevelScene.render_text(self, screen)

    def update_text(self):

        # Update or initialize self.setting_words with text
        self.setting_words = [
            dsnclass.Text("Difficulty: " +
                          str(self.num_to_diff[
                               self.memory.diff_lookup[
                                   self.memory.diff_value]]),
                          ((1080 / 2), 300), 50, "impact",
                          YELLOW, None),
            pygame.Rect([430, 385, 220, 3])
        ]

        self.setting_type = ["Text", "Rect"]


class ReplayIO(LevelScene):
    """Class used to display UI for file/text input and output"""
    def __init__(self, level_memory):
        LevelScene.__init__(self, -50, -50, level_memory)
        self.file_in = dsnclass.Text("File Input", (1080 / 3, 376 / 3),
                                     50, "impact", PURPLE, None)
        self.file_out = dsnclass.Text("File Output", (1080 / 3, 376 / 3 * 2),
                                      50, "impact", PURPLE, None)

        self.text_in = dsnclass.Text("Text Input", (1080 / 3 * 2, 376 / 3),
                                     50, "impact", PURPLE, None)
        self.text_out = dsnclass.Text("Text Output", (1080 / 3 * 2,
                                                      376 / 3 * 2),
                                      50, "impact", PURPLE, None)
        self.return_text = dsnclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", DARK_GREY, None)

        self.icon_list = [self.file_in, self.text_in,
                          self.file_out, self.text_out]
        """
        file/text layout:
        
                 file_in                    text_in
                 
                 
                 file_out                   text_out
        
        """

        self.choose_counter = 0

        self.help_text = [
            dsnclass.Text("Press Space to Import Replays!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None),
            dsnclass.Text("Press Space to Paste a Level!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None),
            dsnclass.Text("Press Space to Export Replays!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None),
            dsnclass.Text("Press Space to Select a Level to Copy!",
                          (1080 / 2, 576 - 150), 50,
                          "impact", YELLOW, None)
        ]

        self.extra_help = [
            dsnclass.Text("Remember to paste replays_out into replays_in!",
                          (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None),
            dsnclass.Text("", (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None),
            dsnclass.Text("Go check and copy from replays_out!",
                          (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None),
            dsnclass.Text("", (1080 / 2, 576 - 100), 50,
                          "impact", YELLOW, None)
        ]

        self.invalid_text = dsnclass.Text("INVALID Copy and Paste, Try Again!",
                                          (1080 / 2, 576 / 3), 75,
                                          "impact", RED, None)
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
                self.change_scene(MenuScene(40, 360, self.memory))

            if action is pygame.K_SPACE:
                # File in
                if self.choose_counter == 0:
                    self.memory.read_replays()
                    self.change_scene(ReplaySelect(self.memory))

                # Text in
                elif self.choose_counter == 1:
                    if 0 < len(str(pygame.scrap.get(pygame.SCRAP_TEXT), "utf-8")) or \
                            str(pygame.scrap.get(pygame.SCRAP_TEXT), "utf-8") is not None:
                        in_str = str(pygame.scrap.get(pygame.SCRAP_TEXT), "utf-8")
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
                          self.icon_list[self.choose_counter].text_rect.width + 12,
                          self.icon_list[self.choose_counter].text_rect.height + 12], 2)

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
        self.memory.level_progress.sort()   # Sort level order
        self.level_id = -1  # Invalid level id, don't record statistics
        self.memory = level_memory  # Get memory

        # If statement used to detect if player has no levels recorded
        if len(self.memory.level_progress) == 0:
            self.select_level = None    # No levels available
            self.render_stats = []  # No statistics to render
            self.nothing_text = dsnclass.Text(
                "GO COMPLETE SOME LEVELS FIRST!", (1080 / 2, (576 / 2)), 50,
                "impact", DARK_RED, None)
        # Otherwise, set the counter to 0 (first displayed level) and display
        # the statistics
        else:
            self.select_level = 0   # set the counter to 0, first selection
            self.update_stats() # Update text for the statistics shown

        self.return_text = dsnclass.Text(
            "press R to go back", (1080 / 2, (576 / 2) + 250), 25,
            "impact", DARK_GREY, None)

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
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(MenuScene(40, 360, self.memory))

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
        total_time = dsnclass.convert_time(pygame.time.get_ticks())

        # Initialize text for the statistics for that selected level
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


class LevelSelect(LevelScene):
    """
    Level select class made as a transition between menu and levels. It also
    allows the player to choose a specific level (based on completion -
    to be implemented in the future)
    """
    def __init__(self, level_memory):
        LevelScene.__init__(self, (1080 / 2) - (10 / 2), 576 / 2, level_memory)
        """Initialize LevelScene with player parameters to the middle
        of the screen.
        """
        self.filler_text = dsnclass.Text("Choose A Level",
                                         (540, 153), 50, "impact", YELLOW, None)
        
        self.level_selector_text_0 = dsnclass.Text("Choose a Level", (535, 100), 65,
                          "impact", YELLOW, None)
            
        self.level_selector_text_1 = dsnclass.Text("Tap/Hold A or D to navigate through the levels", 
                                                   (535, 450), 30, "impact", YELLOW, None)
        
        self.level_selector_text_2 = dsnclass.Text("Tap R to return to Main Menu", (545, 530), 25,
                          "impact", DARK_GREY, None)
        
        self.level_selector_text_3 = dsnclass.Text("Press W or Space to start the level", 
                                                   (535, 490), 28, "impact", YELLOW, None)
        

        self.blockmation_time = 0   # Time variable for moving level boxes
        self.text_x = 0 # Used to define the x position of level number text
        self.direction = 0  # Toggle determining direction level text moves
        self.choose_id = 1  # Level ID chosen

        self.memory = level_memory

        self.repjump_time = 0   # "Repeat jump" time, time until speed increases
        self.speed_jump = 1     # Determines selection speed
        self.allow_select = True    # If levels can be freely chosen

    def input(self, pressed, held):
        for every_key in pressed:
            # Return player to menu if pressing "R"
            if every_key == pygame.K_r:
                self.memory.music.set_music(0, self.memory.music.max_vol, -1, 0, 0)
                self.change_scene(MenuScene(40, 360,self.memory))

            # Allow player to choose a level (based on ID) after 0.405 seconds
            if self.allow_select and \
                    every_key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w] and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.change_scene(PlayLevel(self.level_data[self.choose_id][0],
                                            self.level_data[self.choose_id][1],
                                            self.memory, self.choose_id))
                # Load a level using memory and that level id
            # Every 0.405 seconds, have the player jump
            if every_key in [pygame.K_a, pygame.K_d] and \
                    self.player.jump_ability and \
                    not self.player.enable_gravity and \
                    405 < pygame.time.get_ticks() - self.blockmation_time:
                self.player.jump_boost = self.player.max_jump   # Setup jump
                self.player.jump_sound_1.play() # Play jump sound
                self.player.jumps += 1  # Add to jump counter (useless)

                # Move the blocks to the right (illusion of player going left)
                if every_key == pygame.K_a and 1 < self.choose_id:
                    self.blockmation_time = pygame.time.get_ticks()
                    # Reset timer for block animation
                    self.direction = 1  # Blocks going to the right
                # Move the blocks to the left (illusion of player going right)
                if every_key == pygame.K_d and self.choose_id < len(
                        self.level_data):
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
        # todo: (need to move checks to update)
        if held[pygame.K_a] and 1 < self.choose_id and \
                self.player.jump_ability and \
                not self.player.enable_gravity and \
                (405 / self.speed_jump) < \
                pygame.time.get_ticks() - self.blockmation_time:
            self.player.jump_boost = self.player.max_jump   # Setup jump
            self.player.jump_sound_1.play()  # Play jump sound
            self.player.jumps += 1  # Add to jump counter (useless)

            self.blockmation_time = pygame.time.get_ticks()
            # Reset timer for block animation
            self.direction = 1  # Set block direction to the right
        elif held[pygame.K_d] and self.choose_id < len(self.level_data) and \
                self.player.jump_ability and \
                not self.player.enable_gravity and \
                (405 / self.speed_jump) < \
                pygame.time.get_ticks() - self.blockmation_time:
            self.player.jump_boost = self.player.max_jump   # Setup jump
            self.player.jump_sound_1.play()  # Play jump sound
            self.player.jumps += 1  # Add to jump counter (useless)

            self.blockmation_time = pygame.time.get_ticks()
            # Reset timer for block animat
            self.direction = -1  # Set block direction to the left

        # If nothing is held, reset the quick jump
        if not held[pygame.K_a] and not held[pygame.K_d]:
            self.repjump_time = pygame.time.get_ticks()

    def update(self):
        LevelScene.update(self) # Have player collision and elements (useless)
        self.player.alive = True    # Player will always be alive
        self.player.xpos = self.x_spawn # Set x position to spawn
        self.player.diff_factor = self.speed_jump   # Make sure jump constant

        # If statement ensures y position is always constant
        # If y position is below the y spawn (middle)
        if self.y_spawn <= self.player.ypos:
            self.player.ypos = self.y_spawn  # Set the y position to spawn again
            self.player.enable_gravity = False  # No gravity
            self.player.gravity_counter = self.player.max_gravity   # Reset grav
            self.player.jump_ability = True # Allow jumps

        # After 3 seconds, speed up jumping
        if 3000 <= pygame.time.get_ticks() - self.repjump_time:
            self.speed_jump = 2  # Jump speed multiplier
        else:
            self.speed_jump = 1  # Jump speed multiplier

    def render(self, screen):
        LevelScene.render(self, screen)  # Basic rendering (screen.fill, etc.)

        LevelScene.render_text(self, screen)    # LevelScene text (useless)

        # Rendering the instructions of using the level-selector
        if self.memory.enable_replay == False:
            screen.blit(self.level_selector_text_0.text_img, self.level_selector_text_0.text_rect)
        screen.blit(self.level_selector_text_1.text_img, self.level_selector_text_1.text_rect)
        screen.blit(self.level_selector_text_2.text_img, self.level_selector_text_2.text_rect)
        screen.blit(self.level_selector_text_3.text_img, self.level_selector_text_3.text_rect)

        # Text seen to the left side (current selection, -1)
        left_text = dsnclass.Text(str(self.choose_id - 1),
                                  [(1080 / 2) - 200 + self.text_x,
                                   (576 / 2) + 39], 40, "impact", YELLOW,
                                  None)
        # Text seen in the middle/what the player is standing on (current sel)
        middle_text = dsnclass.Text(str(self.choose_id),
                                    [(1080 / 2) + self.text_x,
                                     (576 / 2) + 39],
                                    40, "impact", YELLOW, None)
        # Text seen to the right side (current selection, +1)
        right_text = dsnclass.Text(str(self.choose_id + 1),
                                   [(1080 / 2) + 200 + self.text_x,
                                    (576 / 2) + 39], 40, "impact", YELLOW,
                                   None)

        scroll_text = [left_text, middle_text, right_text]
        # Make a list to render it in a for loop

        for texts in scroll_text:
            """The if statement conditions around texts.text_rect.x allow
            the rects to be rendered until they go past the black bar. This
            gives the illusion that all the levels are rendered in a long line,
            but really we're loading/unloading them using these boundaries
            (between x of (1080 / 2) - 225 and (1080 / 2) + 195)
            """
            if (1080 / 2) - 225 < texts.text_rect.x < (1080 / 2) + 195 and \
                    0 < int(texts.text) <= len(self.level_data):
                screen.blit(texts.text_img, texts.text_rect)
                pygame.draw.rect(screen,
                                 (0, 0, 0),     # Draw a black rect
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
                         [(1080 / 2) - 250, (576 / 2) - 100, 500, 10])
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) - 250, (576 / 2) + 100, 500, 10])
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) - 250, (576 / 2) - 100, 70, 200])
        pygame.draw.rect(screen, (0, 0, 0),
                         [(1080 / 2) + 250 - 70, (576 / 2) - 100, 70, 200])


class ReplaySelect(LevelSelect):
    """Class that's similar to Level Select but has an extra filter
    for selecting levels with only valid replays"""
    def __init__(self, level_memory):
        LevelSelect.__init__(self, level_memory)
        self.allow_select = False   # Toggle off, cannot freely choose
        self.no_data = dsnclass.Text("NO DATA", [1080 / 2, 576 / 2], 100,
                                     "impact", RED, None)
        self.replay_title = dsnclass.Text("Choose A Replay Level",
                                          (1080 / 2, 160), 50, "impact",
                                          YELLOW, None)

    def input(self, pressed, held):
        if self.choose_id in self.memory.replay_imp and \
                0 < len(self.memory.replay_imp[self.choose_id]):
            self.allow_select = True
        else:
            self.allow_select = False

        LevelSelect.input(self, pressed, held)

    def update(self):
        LevelSelect.update(self)

    def render(self, screen):
        LevelSelect.render(self, screen)
        if self.choose_id in self.memory.replay_imp and \
                0 == len(self.memory.replay_imp[self.choose_id]):
            screen.blit(self.no_data.text_img, self.no_data.text_rect)

        screen.blit(self.replay_title.text_img,
                    self.replay_title.text_rect)


class ReplayOut(ReplaySelect):
    def __init__(self, level_memory):
        ReplaySelect.__init__(self, level_memory)
        self.allow_select = False
        self.copy_text = dsnclass.Text("Copied Level " + str(self.choose_id),
                                       (1080 / 2, 3 * 576 / 4),
                                       50, "impact", YELLOW, None)
        self.copy_time = pygame.time.get_ticks() - 3100
        self.replayo_title = dsnclass.Text("Choose a Level to Copy!",
                                           (1080 / 2, 160), 50, "impact",
                                           YELLOW, None)

    def input(self, pressed, held):
        LevelSelect.input(self, pressed, held)
        for action in pressed:
            if self.choose_id in self.memory.replay_exp and \
                    self.memory.replay_exp[self.choose_id] != [] and \
                    action == pygame.K_SPACE:
                self.copy_time = pygame.time.get_ticks()
                self.copy_text = dsnclass.Text("Copied Level " + str(self.choose_id),
                                       (1080 / 2, 3 * 576 / 4),
                                       50, "impact", YELLOW, None)
                pygame.scrap.put(pygame.SCRAP_TEXT,
                                 bytes(str(
                                     self.memory.replay_exp[self.choose_id]),
                                       "utf-8"))

    def update(self):
        LevelSelect.update(self)
        self.allow_select = False

    def render(self, screen):
        LevelSelect.render(self, screen)
        if self.choose_id in self.memory.replay_exp and \
                0 == len(self.memory.replay_exp[self.choose_id]):
            screen.blit(self.no_data.text_img, self.no_data.text_rect)

        if pygame.time.get_ticks() - self.copy_time <= 3000:
            screen.blit(self.copy_text.text_img,
                        self.copy_text.text_rect)

        screen.blit(self.replayo_title.text_img,
                    self.replayo_title.text_rect)


class PlayLevel(LevelSelect):
    """
    Class used to play levels defined in levels.txt. Levels are first
    loaded in dsn_class with Memory into their dictionaries. Then the level
    id's selected in the LevelSelect determines what level is played here.
    On level completion, another PlayLevel instance is initialized but
    with level id + 1 (next level).
    """
    def __init__(self, x_spawn, y_spawn,
                 level_memory, play_id):
        LevelScene.__init__(self, x_spawn, y_spawn, level_memory)
        # Initialize __init__ for player, spawn and memory.
        self.level_id = play_id # Set the level id
        self.element_names = list(self.level_elements[self.level_id].keys())
        # Get all the available level elements available
        self.collision_objects = {"self.platforms": self.platforms,
                                  "self.death_zones": self.death_zones,
                                  "self.win_zones": self.win_zones,
                                  "self.respawn_zones": self.respawn_zones}
        # Combine collision objects into a dict of lists

        self.render_objects = []    # Initialize render objects
        self.end_time = pygame.time.get_ticks()

        self.start_toggle = True    # By default, allow player to start anytime

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

        # Replay Option if enabled
        if self.memory.enable_replay:
            self.player.diff_factor = self.memory.diff_lookup[level_memory.imp_diff[self.level_id]]
            self.replayer_xspawn = self.x_spawn
            self.replayer_yspawn = self.y_spawn
            self.replayer = dsnclass.SquareMe(self.replayer_xspawn, self.replayer_yspawn,
                                                   10, 10, GREY,
                                                   self.memory.diff_lookup[level_memory.imp_diff[self.level_id]])
            self.replay_counter = 0
            self.replay_time = int(self.memory.replay_imp[self.level_id][0][2:-1])
            self.lose_condition = False
            self.win_text = dsnclass.Text("WIN", [1080 / 2, 576 / 2], 250,
                                          "impact", YELLOW, None)
            self.lose_text = dsnclass.Text("LOSE", [1080 / 2, 576 / 2], 250,
                                           "impact", YELLOW, None)
            self.count_down = 3
            self.count_change = pygame.time.get_ticks()
            self.count_time = pygame.time.get_ticks()   # Time spent counting
            self.start_toggle = False

            self.count_text = dsnclass.Text(str(self.count_down), [1080 / 2,
                                                              576 / 2], 250,
                                            "impact", YELLOW, None)

    def input(self, pressed, held):
        if not self.start_toggle:
            return None

        # Use the default player inputs in LevelScene.input (controls/options)
        if self.level_id in self.level_data:
            LevelScene.input(self, pressed, held)

    def update(self):
        if not self.start_toggle:
            if 1000 < pygame.time.get_ticks() - self.count_change and \
                    1 < self.count_down:
                self.count_down -= 1
                self.count_text = dsnclass.Text(str(self.count_down), [1080 / 2,
                                                     576 / 2], 250,
                              "impact", YELLOW, None)
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

        # If enabled replay, have the other player function
        if self.memory.enable_replay:

            if self.replay_counter < len(self.memory.replay_imp[self.level_id]) and \
                    int(self.memory.replay_imp[self.level_id]
                        [self.replay_counter][2:-1]) - self.replay_time <= \
                    self.loop_counter and \
                    not (self.lose_condition or self.level_condition):
                if self.memory.replay_imp[self.level_id][self.replay_counter][1:2] == "J":
                    self.replayer.gravity_counter = self.replayer.max_gravity
                    self.replayer.jump_ability = True  # Allow player to jump
                    self.replayer.jump_boost = self.player.max_jump  # Setup jump

                elif self.memory.replay_imp[self.level_id][self.replay_counter][1:2] == "R":
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
                # Update statistics with this level's data
                self.memory.update_mem(self.level_id, self.deaths,
                                       self.player.jumps, self.start_time)
                # Add this level's timed jumps/unfreezes
                self.memory.update_temp(self.resp_jumps + self.hold_jumps)
                self.memory.update_replays(self.level_id,
                                           [self.level_id] +
                                           [self.memory.diff_value] +
                                           self.memory.hold_replay.chain_to_list())
                # Reset temporary hold on chain of level's timed events
                self.memory.hold_replay = dsnclass.ReplayChain()
                self.level_id += 1

                if self.level_id in self.level_data:
                    self.change_scene(PlayLevel(self.level_data[self.level_id][0],
                                                self.level_data[self.level_id][1],
                                                self.memory,
                                                self.level_id))
                else:
                    self.change_scene(MenuScene(40, 360, self.memory))
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
        if 580 + self.replayer.height < self.replayer.ypos:
            self.replayer.alive = False

        # Check for win collision
        if self.replayer.alive and \
                self.replayer.square_render.collidelist(self.win_zones) != -1:
            self.lose_condition = True
            self.replayer.alive = False

        # Respawn block collision
        if self.replayer.alive and \
                self.replayer.square_render.collidelist(self.respawn_zones) != -1:
            # Setup respawn block for readability
            respawn_block = self.replayer.square_render.collidelist(
                self.respawn_zones)
            # Set new x and y default spawns
            self.replayer_xspawn = self.respawn_zones[respawn_block].x + \
                (self.respawn_zones[respawn_block].width / 2) - 5
            self.replayer_yspawn = self.respawn_zones[respawn_block].y + \
                (self.respawn_zones[respawn_block].height / 2) - 5

    def render(self, screen):
        if self.level_id in self.level_data:
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

            # Lastly, render text
            LevelScene.render_text(self, screen)
            if self.memory.enable_replay:
                if self.level_condition and \
                        1000 < pygame.time.get_ticks() - self.end_time:
                    screen.blit(self.win_text.text_img, self.win_text.text_rect)
                elif self.lose_condition and \
                        1000 < pygame.time.get_ticks() - self.end_time:
                    screen.blit(self.lose_text.text_img, self.lose_text.text_rect)

            if not self.start_toggle and self.memory.enable_replay:
                screen.blit(self.count_text.text_img, self.count_text.text_rect)

    def render_level(self, screen):
        # Render all the rect/line objects for that level (visual)
        for element in self.render_objects:
            if element.type == "rect":  # rect drawings
                pygame.draw.rect(screen, element.color, element.shape)
            else:   # line drawings
                pygame.draw.line(screen, element.color,
                                 [element.shape[0], element.shape[1]],
                                 [element.shape[2], element.shape[3]],
                                 element.shape[4])
