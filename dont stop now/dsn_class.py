import pygame
import re

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


class Music:
    def __init__(self, set_track):
        self.music_tracks = [
            "main-menu.wav",
            "level-loop1.wav",
            "work_around_lead_edited.wav",
            "credits.wav"
        ]
        self.current_track_index = set_track

        pygame.mixer.music.load(self.music_tracks[self.current_track_index])
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)  # Play the background music on a loop

    def switch_music(self):
        # if level_complete
        self.current_track_index += 1 # Increment the track index

        # Check if all tracks have been played, then loop back to the first track
        if self.current_track_index >= len(self.music_tracks):
            self.current_track_index = 0

        # Load and play the new background music track
        pygame.mixer.music.load(self.music_tracks[self.current_track_index])
        if self.current_track_index == 2:
            pygame.mixer.music.set_volume(0.15)
        if self.current_track_index == 3:
            pygame.mixer.music.set_volume(1.5)
        pygame.mixer.music.play(-1)  # Play the background music on a loop


class Memory:
    def __init__(self):
        self.total_deaths = 0
        self.total_jumps = 0

        self.level_deaths = {}
        self.level_jumps = {}

        self.level_progress = []    # collection of level_id's

        self.level_set = {}
        self.ls_elements = {}

    def update_mem(self, level_id, death_count, jump_count):
        self.total_deaths += death_count
        self.total_jumps += jump_count

        if level_id not in self.level_progress:
            self.level_progress += [level_id]

        if level_id in self.level_deaths and \
                death_count < self.level_deaths[level_id]:
            self.level_deaths[level_id] += death_count
            # add to current amount of deaths for that level
        else:
            self.level_deaths[level_id] = death_count
            # first time completing that level, make a death count

        if level_id in self.level_jumps and \
                jump_count < self.level_jumps[level_id]:
            self.level_jumps[level_id] += jump_count
            # add to current amount of jumps for that level
        else:
            self.level_jumps[level_id] = jump_count
            # first time completing that level, make a death count

    def load_levels(self, in_file):
        self.level_set = {}
        self.ls_elements = {}

        color_lookup = {
            "DARK_RED": DARK_RED,
            "YELLOW": YELLOW,
            "BLACK": BLACK,
            "CYAN": CYAN,
            "RED": RED,
            "LIME_GREEN": LIME_GREEN,
            "LIGHT_RED": LIGHT_RED,
            "WHITE": WHITE,
            "GREY": GREY,
            "LIGHT_PINK": LIGHT_PINK,
            "EDIT_DARK_GREEN": EDIT_DARK_GREEN,
            "PURPLE": PURPLE
        }
        """
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
        """

        with open(in_file, "r") as open_file:
            identifier = ""
            level_id = 1

            for line in open_file.readlines():
                if re.search("self\..*", line):   # Distinguish level elements
                    identifier = re.search("self\..* = ", line).group()[:-3]
                elif re.search(r"Text", line):   # Distinguish text
                    identifier = "Text"
                elif re.search(r"\([0-9]+, [0-9]+, [0-9]+\)", line): # Finding level titles
                    line_search = re.search(r"\([0-9]+, [0-9]+, [0-9]+\)", line).group()
                    format_search = line_search[1:-1].split(", ")
                    self.level_set[level_id] = [int(format_search[0]),
                                                int(format_search[1]),
                                                int(format_search[2])]
                    self.ls_elements[level_id] = {}
                elif "=" in line.replace("\n", ""):
                    level_id += 1

                if re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+, [0-9]+, [0-9]+\]\)", line):  # Add rect elements
                    rect_line = re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+, [0-9]+, [0-9]+]\)", line).group()
                    rect_properties = re.search(r"\[[0-9]+, [0-9]+, [0-9]+, [0-9]+]", rect_line).group()[1:-1].split(", ")
                    if re.search("\([0-9]+, [0-9]+, [0-9]+\)", rect_line):
                        rect_color = re.search("\([0-9]+, [0-9]+, [0-9]+\)", rect_line).group()
                        in_rect = DSNElement(rect_color,
                                             pygame.Rect(
                                                 int(rect_properties[0]),
                                                 int(rect_properties[1]),
                                                 int(rect_properties[2]),
                                                 int(rect_properties[3])), "rect")
                    else:
                        rect_color = re.search("([A-Z]+_[A-Z]+|[A-Z]+)", rect_line).group()
                        in_rect = DSNElement(color_lookup[rect_color],
                                             pygame.Rect(int(rect_properties[0]),
                                                         int(rect_properties[1]),
                                                         int(rect_properties[2]),
                                                         int(rect_properties[3])), "rect")

                    # add that rect to our element list
                    if identifier not in self.ls_elements[level_id]:
                        self.ls_elements[level_id][identifier] = [in_rect]
                    else:
                        self.ls_elements[level_id][identifier] += [in_rect]

                elif re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+\], \[[0-9]+, [0-9]+\], [0-9]\)", line): # add line elements
                    line_info = re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+\], \[[0-9]+, [0-9]+\], [0-9]\)", line).group().split(", ")
                    in_line = DSNElement(line_info[1], [int(line_info[2][1:]),
                                         int(line_info[3][:-1]),
                                         int(line_info[4][1:]),
                                         int(line_info[5][:-1]),
                                         int(line_info[6][:-1])],
                                         "line")
                    # add that line to our element list
                    if identifier not in self.ls_elements[level_id]:
                        self.ls_elements[level_id][identifier] = [in_line]
                    else:
                        self.ls_elements[level_id][identifier] += [in_line]

                if re.search(r"\(\".*\", \([0-9]+, [0-9]+\), [0-9]+, \"[a-zA-Z]+\", [A-Z]+, None\)", line):
                    format_search = re.search(r"\(\".*\", \([0-9]+, [0-9]+\), [0-9]+, \"[a-zA-Z]+\", [A-Z]+, None\)", line).group()[1:-1].split(", ")
                    add_text = Text(format_search[0][1:-1], (int(format_search[1][1:]),
                                                             int(format_search[2][0:-1])),
                                    int(format_search[3]),
                                    format_search[4][1:],
                                    color_lookup[format_search[5]],
                                    None)

                    if identifier not in self.ls_elements[level_id]:
                        self.ls_elements[level_id][identifier] = [add_text]
                    else:
                        self.ls_elements[level_id][identifier] += [add_text]

        # self.print_levels is mainly used for debugging purposes only
        # self.print_levels()

    def print_levels(self):
        print(self.level_set)
        print()
        print(self.ls_elements)


class DSNElement:

    def __init__(self, color, shape, type):
        self.color = color
        self.shape = shape
        self.type = type


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

        self.jumps = 0
        self.jump_ability = False
        self.enable_gravity = True
        self.max_jump = 50
        self.jump_boost = -1 * (self.max_jump - 1)
        self.direction = 1
        self.max_gravity = 95
        self.gravity_counter = self.max_gravity

        self.jump_sound_1 = pygame.mixer.Sound("jump_sfx.wav")
        self.jump_sound_1.set_volume(0.1)  # out of 1 = 100%

        # Update collision logic position
        self.left_col = pygame.Rect(self.xpos - 20, self.ypos + 3, 20 + 1, self.height - 4)
        self.right_col = pygame.Rect(self.xpos + self.width - 1, self.ypos + 3, 20 + 1, self.height - 4)
        self.top_col = pygame.Rect(self.xpos + 1, self.ypos - 20, self.width - 2, 20 + 1)
        self.bot_col = pygame.Rect(self.xpos + 1, self.ypos + self.height - 1, self.width - 2, 20 + 1)

    def move(self):
        # Move horizontally depending on the direction
        self.xpos += 4 * self.direction

        # Gravity and jump functions
        self.gravity()
        self.jump()

        # Update collision logic position
        self.left_col = pygame.Rect(self.xpos - 20, self.ypos + 1, 20 + 1,
                                    self.height - 2)
        self.right_col = pygame.Rect(self.xpos + self.width - 1, self.ypos + 1,
                                     20 + 1, self.height - 2)
        self.top_col = pygame.Rect(self.xpos + 1, self.ypos - 20,
                                   self.width - 2, 20 + 1)
        self.bot_col = pygame.Rect(self.xpos + 1, self.ypos + self.height - 1,
                                   self.width - 2, 20 + 1)

    def jump(self):
        if self.jump_ability and 0 <= self.jump_boost:
            self.ypos -= (self.jump_boost ** 2) * 0.002
            self.jump_boost -= 2
        else:
            self.jump_ability = False

    def render(self, screen):
        self.square_render = pygame.draw.rect(screen, self.color, [self.xpos,
                                                                   self.ypos,
                                                                   self.width,
                                                                   self.height])

        # Visualize collision, uncomment to see
        """pygame.draw.rect(screen, (55, 230, 50), self.left_col)
        pygame.draw.rect(screen, (55, 230, 50), self.right_col)
        pygame.draw.rect(screen, (55, 230, 50), self.top_col)
        pygame.draw.rect(screen, (55, 230, 50), self.bot_col)"""

    def collision_plat(self, object_list: [pygame.Rect]):
        bot_collisions = self.bot_col.collidelistall(object_list)
        self.enable_gravity = True

        for bcollide_id in bot_collisions:
            collide_x = object_list[bcollide_id].x
            collide_y = object_list[bcollide_id].y
            collide_width = object_list[bcollide_id].width
            collide_height = object_list[bcollide_id].height

            if bcollide_id != -1 and object_list[bcollide_id].y <= self.ypos + self.height and \
                    collide_x + 4 < self.xpos + self.width and self.xpos < collide_x + collide_width - 4:
                self.enable_gravity = False
                self.jump_ability = True
                self.gravity_counter = self.max_gravity

            """New addition to the collision that ensures 
            the player isn't inside the platform"""
            if 0 < len(bot_collisions) and object_list[bot_collisions[0]].y < self.ypos + self.height < \
                object_list[bot_collisions[0]].y + self.height and \
                    collide_x + 6 < self.xpos + self.width and self.xpos < collide_x + collide_width - 6:
                self.ypos = object_list[bcollide_id].y - self.height

        # Top ceiling collision
        top_collisions = self.top_col.collidelistall(object_list)
        for tcollide_id in top_collisions:
            collide_x = object_list[tcollide_id].x
            collide_y = object_list[tcollide_id].y
            collide_width = object_list[tcollide_id].width
            collide_height = object_list[tcollide_id].height

            if tcollide_id != -1 and self.square_render.colliderect(object_list[tcollide_id]) and \
                    collide_x + 8 < self.xpos + self.width and \
                    self.xpos < collide_x + collide_width - 8:
                self.jump_ability = False
                self.jump_boost = -1
                self.enable_gravity = True

    def collision_wall(self, object_list: [pygame.Rect]):
        # New collision logic:
        left_collision = self.left_col.collidelistall(object_list)
        right_collision = self.right_col.collidelistall(object_list)

        # Left side collision, going left to turn right
        for lcollide_id in left_collision:
            collide_x = object_list[lcollide_id].x
            collide_y = object_list[lcollide_id].y
            collide_width = object_list[lcollide_id].width
            collide_height = object_list[lcollide_id].height
            if lcollide_id != -1 and self.square_render.colliderect(object_list[lcollide_id]) and \
                    collide_y < self.ypos + self.height and \
                    self.ypos < collide_y + collide_height and \
                object_list[lcollide_id].x + object_list[lcollide_id].width <= self.xpos + 4:
                self.enable_gravity = True
                self.direction = 1

        # Right side collision, going right to turn left
        for rcollide_id in right_collision:
            collide_x = object_list[rcollide_id].x
            collide_y = object_list[rcollide_id].y
            collide_width = object_list[rcollide_id].width
            collide_height = object_list[rcollide_id].height
            if rcollide_id != -1 and self.square_render.colliderect(object_list[rcollide_id]) and \
                    collide_y < self.ypos + self.height and \
                    self.ypos < collide_y + collide_height and \
                self.xpos + self.width - 4 <= object_list[rcollide_id].x:
                self.enable_gravity = True
                self.direction = -1

    def gravity(self):
        if self.enable_gravity and not self.jump_ability:
            gravity_y = (self.gravity_counter ** 2) * 0.00015
            self.ypos += gravity_y

        if self.gravity_counter < 1100:
            self.gravity_counter += 2

    def death(self, death_list: [pygame.Rect]):
        collide_id = self.square_render.collidelist(death_list)
        if collide_id != -1:
            self.alive = False
            return 1
        else:
            return 0


class Scene:
    def __init__(self):
        """
        self.this_scene will tell the current scene it's on at that moment.
        Currently, it's set to itself, which means the
        current scene is this one.
        """
        self.this_scene = self
        self.run_scene = True
        self.level_id = -1

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
