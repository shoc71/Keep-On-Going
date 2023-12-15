import random
import os
import math

import pygame
import re

DARK_RED = (139, 0, 0)
YELLOW = (235, 195, 65)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (30, 144, 255)
CYAN = (47, 237, 237)
RED = (194, 57, 33)
LIME_GREEN = (50, 205, 50)
LIGHT_RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)
LIGHT_PINK = (255, 182, 193)
DARK_GREEN = (1, 100, 32)
PURPLE = (181, 60, 177)
BROWN = (150, 75, 0)
DARK_GREY = (52, 52, 52)


class Text:
    """
    Class used to simplify text creation for pygame
    """

    def __init__(self, text, text_pos, font_size, font_type,
                 font_color, text_other):
        self.text = text  # Text as a string
        self.position = text_pos  # Text position as a tuple or list (x and y)
        self.font_size = int(font_size)  # Int determining how big the text is
        self.font_type = font_type  # String used to indicate what font
        """Font selection is determined by your computer and it's preset fonts
        """
        self.color = font_color
        """A constant string for a tuple or a tuple using RGB values"""
        self.other = text_other
        """PLACEHOLDER for any other variables needed or desired in text"""
        self.font = None  # Initialized here, defined in setup()
        self.text_rect = None  # Initialized here, defined in render()
        self.text_img = None  # Initialized here, defined in render()

        self.setup()  # Called to set up the font
        self.render()
        """Called to continuously update the position, rect, color, and text
        """

    def setup(self):
        """
        Uses font type and size to translate into pygame text font
        to make self.font
        """
        self.font = pygame.font.SysFont(self.font_type, self.font_size)

    def render(self):
        """
        Creates self.text_img or the pygame image of the text using self.text,
            self.color.
        Creates self.text_rect, or a rect object using the size of the text.
        Then centers the rect around the text (or the defined position)
        """
        self.text_img = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_img.get_rect()
        self.text_rect.center = self.position

    def scale(self, width, height):
        self.position = list(self.position)
        self.position[0] = int(self.position[0] * width)
        self.position[1] = int(self.position[1] * height)
        self.position = tuple(self.position)
        self.font_size = int(self.font_size * max(width, height))

        # Apply those changes
        self.setup()
        self.render()


class Music:
    """
    Music class containing tracks available and the current music playing.
    Also responsible for music volume and music switching.
    """

    def __init__(self, perc_vol):
        self.music_tracks = []
        self.file_path = "assets/audio/soundtracks/"    # File path for audio
        try:
            for music in os.listdir(self.file_path):
                if "mp3" in music or "wav" in music:
                    self.music_tracks += [str(music)]
        except:
            # todo: ERROR LOG
            raise "Problem with Loading Music"

        self.hub_tracks = {}    # Hub number: [n,m] - song range for that hub
        self.level_tracks = {}  # Level number: [o,p] - song range for levels

        self.end = pygame.USEREVENT + 0  # Unique event, for when music ends
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 0)
        # Everytime music ends, return the event

        self.current_track_index = 0  # Everything but the main menu theme

        self.perc_vol = perc_vol  # Volume set by the player as a percentage
        self.music_vol = 0  # Adjustable music volume
        self.vol_time = pygame.time.get_ticks()  # Increment music with time
        self.max_vol = 0.7 * self.perc_vol / 100  # Max volume possible for music

        pygame.mixer.music.load(self.file_path + self.music_tracks[0])
        # Load the menu music

        pygame.mixer.music.set_volume(self.max_vol)  # Set to max for now
        pygame.mixer.music.play(-1)  # Start with main menu, play forever

        self.music_text = Text("PLAYING: " +
                               str(self.music_tracks[self.current_track_index]),
                               (1080 / 2, 556), 20, "impact", WHITE, None)
        self.text_timer = pygame.time.get_ticks()
        # Display what's currently playing

    def switch_music(self):
        # Reset music display timer
        self.text_timer = pygame.time.get_ticks()

        # Choose a random track index
        self.music_vol = 0
        self.current_track_index = random.randint(1, len(self.music_tracks) - 2)
        # Set the boundaries between 2nd/1 and 2nd last/len - 2 to avoid
        # main menu and credits

        # Update the music display text
        self.music_text = Text("PLAYING: " +
                               str(self.music_tracks[self.current_track_index]),
                               (1080 / 2, 556), 20, "impact", WHITE, None)

        # Load the selected track
        pygame.mixer.music.load(self.file_path +
                                (self.music_tracks[self.current_track_index]))

        # Set the volume
        pygame.mixer.music.set_volume(self.music_vol)

        pygame.mixer.music.play(0, 0, 0)  # Play the music once

    def next_track(self):
        if len(self.music_tracks) - 1 < self.current_track_index + 1:
            self.current_track_index = 0
        else:
            self.current_track_index += 1
        self.set_music(self.current_track_index, self.max_vol, -1, 0, 0)

    def previous_track(self):
        if self.current_track_index - 1 < 0:
            self.current_track_index = len(self.music_tracks) - 1
        else:
            self.current_track_index -= 1
        self.set_music(self.current_track_index, self.max_vol, -1, 0, 0)

    def set_music(self, track_num, vol, loops, start, fade_in):
        # Set the max volume
        self.max_vol = 0.7 * self.perc_vol / 100

        # Reset music display timer
        self.text_timer = pygame.time.get_ticks()

        # Update the current track index
        self.current_track_index = track_num

        # Update the music display text
        self.music_text = Text("PLAYING: " +
                               str(self.music_tracks[self.current_track_index]),
                               (1080 / 2, 556), 20, "impact", WHITE, None)

        # Load the selected track
        pygame.mixer.music.load(self.file_path +
                                (self.music_tracks[self.current_track_index]))

        # Set the volume
        self.music_vol = vol * self.perc_vol / 100
        pygame.mixer.music.set_volume(self.music_vol)

        pygame.mixer.music.play(loops, start, fade_in)  # Play the music

    def transition_music(self):
        # Slowly increase volume of music (0.01 every 0.075 seconds)
        # until volume reaches the max (0.7 or self.max_vol)
        # set the new self.max_vol if changed
        self.max_vol = 0.7 * self.perc_vol / 100
        while self.music_vol < self.max_vol and \
                75 < pygame.time.get_ticks() - self.vol_time:
            self.music_vol += 0.01  # Increase volume
            pygame.mixer.music.set_volume(self.music_vol)  # Update volume
            self.vol_time = pygame.time.get_ticks()  # Reset timer


class Memory:
    """
    Memory class used to load levels from a file (levels.txt), and record/update
    statistics
    """

    def __init__(self, width, height):
        self.total_deaths = 0  # Total deaths in one session
        self.total_jumps = 0  # Total jumps in one session
        self.total_time = 0  # Total time passed in one session
        self.total_stars = 0  # Total stars collected

        self.level_deaths = {}  # Deaths per level in one session
        self.level_jumps = {}  # Jumps per level in one session
        self.level_times = {}  # Times per level in one session
        self.stars_collected = {}  # Stars collected per level

        self.level_progress = []  # collection of level_id's for levels done

        self.level_set = {}
        """Loaded in level data containing player spawn (ADD MORE)
        """
        self.ls_elements = {}
        """Loaded in level data containing text, rects and lines for 
        platforms
        """
        self.level_id = 0  # Initialize level_id

        self.id_range = {}  # Ranges for different sets of levels
        self.range_index = 0

        self.diff_lookup = {
            0: 0.6,
            1: 0.8,
            2: 1.0
        }
        """The keys are integers referring to increasing difficulty.
        While their respective values are multipliers for player physics
        """

        self.diff_value = 1  # Normal/Default difficulty value

        """Background color and a slider to adjust it"""
        self.bg_slider = 255
        self.background = [self.bg_slider,
                           self.bg_slider,
                           self.bg_slider]

        """Variables related to write and read replay class functions
        """
        self.replay_imp = {}  # Imported replays from an external source
        self.imp_diff = {}  # Imported difficulties
        self.replay_exp = {}  # Replays from the player ready to export

        self.hold_replay = ReplayChain()  # Altered Queue for holding jump/unfreeze timings
        # hr_indexes is used to keep indexes for respawns/the latest 5 deaths

        # Toggle if replay mode is on or not (only accessed in Replays)
        self.enable_replay = False

        # Amount of times pressing R to have quick restart
        self.quick_restart = 1  # By default, it's 1 time
        self.qr_counter = 0

        # Volume setting for music
        self.total_music_per = 100

        # initialize music
        self.music = None

        # initialize sound volume
        self.sound_vol = 100

        # Initialize Width and Height of Screen, useful for changing resolutions
        self.res_width = width  # Ratio for width resolution, easily multiply
        self.res_height = height  # Ratio for height res, easily multiply

        self.res_index = 1

        self.res_set = {0: [900, 600],
                        1: [1080, 576],
                        2: [1280, 720],
                        3: [1920, 1080]}

        self.star_data = {}

        self.images = {}

        self.screen = None

        self.options_status = 0
        """Since there's different ways to access the options page,
        we denote:
            - 0 for coming from the menu
            - greater than 0 for coming from a level

        """

        self.hub_index = 1  # Keep track of current hub accessed

    def update_mem(self, level_id, death_count, jump_count, level_time,
                   stars):
        """
        Called in kog_levels PlayLevel to update or create statistics for
        that level using the parameters below.

        :param level_id: int referring to that specific level
        :param death_count: int for how many deaths on level completion
        :param jump_count: int for how many jumps on level completion
        :param level_time: int for how long it took to complete the level
        """
        self.total_deaths += death_count  # Add level deaths to total
        self.total_jumps += jump_count  # Add level jumps to total

        if level_id not in self.level_progress:
            self.level_progress += [level_id]
            # If the level has not yet been completed before, add it to progress

        if level_id in self.level_deaths:
            self.level_deaths[level_id] += death_count
            # Add to current amount of deaths for that level
        else:
            self.level_deaths[level_id] = death_count
            # first time completing that level, make a death count

        if level_id in self.level_jumps:
            self.level_jumps[level_id] += jump_count
            # add to current amount of jumps for that level
        else:
            self.level_jumps[level_id] = jump_count
            # first time completing that level, make a death count

        # Retrieve the time for that level
        current_time = convert_time(pygame.time.get_ticks() - level_time)

        # Overwrite an existing time if it's faster than the old time or
        # write a time if it doesn't exist yet
        if level_id not in self.level_times:
            # If there's no time, recorded, then add the time
            self.level_times[level_id] = current_time
        elif 1 <= level_id and self.level_times[level_id][0] * (60 ** 2) + \
                self.level_times[level_id][1] * 60 + \
                self.level_times[level_id][2] >= \
                current_time[0] * (60 ** 2) + \
                current_time[1] * 60 + \
                current_time[2]:
            """Check if the new time in seconds, minutes and hours is less than
            recorded seconds, minutes and hours. If so, then overwrite it
            """
            self.level_times[level_id] = current_time
        elif level_id == 0:
            # Update time for main menu
            self.level_times[level_id] = add_time(self.level_times[level_id],
                                                  current_time)

        # Update stars_collected
        if level_id not in self.stars_collected:
            self.stars_collected[level_id] = stars
            self.total_stars += stars
        elif level_id in self.stars_collected and \
                self.stars_collected[level_id] < stars:
            self.stars_collected[level_id] = stars
            self.total_stars += (stars - self.stars_collected[level_id])

    def load_all_levels(self):
        folder_path = "assets/levels/"

        self.level_set = {}
        """Loaded in level data containing player spawn (ADD MORE)
        """
        self.ls_elements = {}
        """Loaded in level data containing text, rects and lines for 
        platforms
        """
        self.level_id = 0  # Initialize level_id

        self.id_range = {}  # Ranges for different sets of levels
        self.range_index = 0

        try:
            file_list = os.listdir(folder_path)
        except:
            # LOG: Assets Folder Not Found
            raise "Assets Folder Not Found"
        else:
            # LOG: Assets Folder Found
            pass

        if len(os.listdir(folder_path)) == 0:
            raise "Assets Folder Empty"
        else:
            # LOG: Assets Folder Contains Levels
            pass

        for each_file in file_list:
            if each_file.split("_")[0].isdecimal():
                self.load_levels(folder_path + each_file)

        # Load non-level pygame objects, start at -6 + 1 for 4 instances
        self.level_id = -99
        self.load_levels(folder_path + "non_levels.txt")

        # Load stars
        self.load_stars(folder_path + "stars.txt")

        # Load images
        self.load_images(folder_path + "images.txt")


        """
        MenuScene ID = -5
        OptionsPage ID = -4
        """

    # load_levels is used to get level data from the levels folder

    def load_levels(self, in_file):
        color_lookup = {
            "DARK_RED": DARK_RED,
            "YELLOW": YELLOW,
            "BLACK": BLACK,
            "CYAN": CYAN,
            "RED": RED,
            "LIME_GREEN": LIME_GREEN,
            "LIGHT_RED": LIGHT_RED,
            "BROWN": BROWN,
            "WHITE": WHITE,
            "GREY": GREY,
            "LIGHT_PINK": LIGHT_PINK,
            "DARK_GREEN": DARK_GREEN,
            "PURPLE": PURPLE,
            "BLUE": BLUE,
            "ORANGE": ORANGE,
            "DARK_GREY": DARK_GREY
        }

        start = self.level_id + 1

        # Used to convert text file color names to static constant colors
        with open(in_file, "r") as open_file:
            identifier = ""

            for line in open_file.readlines():
                if re.search("self\..*", line):  # Distinguish level elements
                    """Will specifically look for lines with self. in them 
                    to get platforms, win, death, draw, etc. 
                    """
                    identifier = re.search("self\..* = ", line).group()[:-3]
                elif re.search(r"Text", line):  # Distinguish text
                    identifier = "Text"
                elif re.search(r"\(([0-9]+|-[0-9]+), ([0-9]+|-[0-9]+), "
                               r"([0-9]+|-[0-9]+)\)", line) and \
                        "pygame" not in line:
                    self.find_title(line)

                if re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+, "
                             r"[0-9]+, [0-9]+]\)", line):  # Add rect elements

                    # Get rect with color as a tuple or constant
                    in_rect = self.find_rect(line, color_lookup)

                    # add that rect to our element list for that level
                    if identifier not in self.ls_elements[self.level_id]:
                        # If there isn't any objects, make it the first
                        self.ls_elements[self.level_id][identifier] = [in_rect]
                    else:
                        # Add rect to the existing list for that level
                        self.ls_elements[self.level_id][identifier] += [in_rect]

                elif re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+], "
                               r"\[[0-9]+, [0-9]+], [0-9]\)", line):

                    # Get line with color as a tuple or constant
                    in_line = self.find_line(line, color_lookup)

                    # add that line to our element list for that level
                    if identifier not in self.ls_elements[self.level_id]:
                        # If there isn't any objects, make it the first
                        self.ls_elements[self.level_id][identifier] = [in_line]
                    else:
                        # Add line to the existing list for that level
                        self.ls_elements[self.level_id][identifier] += [in_line]

                # Search the line for the actual text
                if re.search(r"\(\".*\", \([0-9]+, [0-9]+\), [0-9]+, "
                             r"\"[a-zA-Z]+\", ([A-Z]+_[A-Z]+_[A-Z]+|"
                             r"[A-Z]+_[A-Z]+|"
                             r"[A-Z]+|"
                             r"\([0-9]+, [0-9]+, [0-9]+\)), None\)", line):

                    # Get text from file and assign it to text object
                    add_text = self.find_text(line, color_lookup)

                    # Add that text into our level_elements
                    if identifier not in self.ls_elements[self.level_id]:
                        # If there are no objects for Text, add it
                        self.ls_elements[self.level_id][identifier] = [add_text]
                    else:
                        # If there are objects, add onto it
                        self.ls_elements[self.level_id][identifier] += [
                            add_text]

        # Extra if statement for the case where there's only 1 thing in the file
        if start is None:
            start = self.level_id

        end = self.level_id  # Get the last level that was added in
        if start + end < 0:
            current_hub = -1
        else:
            current_hub = self.range_index

        self.id_range[current_hub] = [start, end]  # Put the range into mem
        self.range_index += 1  # Increment for the next set of ranges
        # self.print_levels is mainly used for debugging purposes only
        # self.print_levels()

    # The following methods are helpers for load_levels

    def find_title(self, line):
        """ Class helper method for load_levels
        This method finds and assigns the level title
        """
        # Search for the level title
        self.level_id += 1
        self.level_set[self.level_id] = []
        self.ls_elements[self.level_id] = {}

        # Finding level titles in the form ( , , )
        line_search = re.search(r"\(([0-9]+|-[0-9]+), "
                                r"([0-9]+|-[0-9]+), "
                                r"([0-9]+|-[0-9]+)\)",
                                line).group()
        format_search = line_search[1:-1].split(", ")

        self.level_set[self.level_id] = [int(format_search[0]),
                                         int(format_search[1]),
                                         int(format_search[2])]

        """Will then get the 3 numbers split by comma, then
        converts them into their ints - x, y and music
        """

    def find_rect(self, line, color_lookup):
        """ Class helper method for load_levels
        This method finds and assigns rects
        """

        """Rect elements are detected by this format:
        (screen, color, rect_properties ([x, y, width, height]))
        """
        rect_line = re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+, "
                              r"[0-9]+, [0-9]+]\)", line).group()
        """Obtain rect from the current line and assign to variable
        """
        rect_properties = re.search(r"\[[0-9]+, [0-9]+, "
                                    r"[0-9]+, [0-9]+]",
                                    rect_line).group()[1:-1].split(
            ", ")
        """Get a list of numbers as a string
        from .split, without the brackets ([1:-1]),
        from the rect_line variable
        """

        # If the color is in a tuple of string numbers (x, y, z)
        if re.search("\([0-9]+, [0-9]+, [0-9]+\)", rect_line):
            # Get the individual color values
            rect_color = re.search("\([0-9]+, [0-9]+, "
                                   "[0-9]+\)",
                                   rect_line).group().split(",")

            # Convert the rect into a KOGElement
            in_rect = KOGElement((int(rect_color[0][1:]),
                                  int(rect_color[1][1:]),
                                  int(rect_color[2][1:-1])),
                                 pygame.Rect(
                                     int(math.floor(int(
                                         rect_properties[0]) * self.res_width)),
                                     int(math.floor(int(
                                         rect_properties[
                                             1]) * self.res_height)),
                                     int(math.ceil(int(
                                         rect_properties[2]) * self.res_width)),
                                     int(math.floor(int(rect_properties[
                                                            3]) * self.res_height))),
                                 "rect")
        else:
            """Otherwise the color is defined in words:
                - X (BLUE)
                - X_Y (DARK_RED)
                - X_Y_Z (EDIT_DARK_GREEN)
            """
            # Get the color from the words
            rect_color = re.search("([A-Z]+_[A-Z]+_[A-Z]+|"
                                   "[A-Z]+_[A-Z]+|[A-Z]+)",
                                   rect_line).group()
            # Convert the rect into a KOGElement
            in_rect = KOGElement(color_lookup[rect_color],
                                 pygame.Rect(
                                     int(math.floor(int(
                                         rect_properties[0]) *
                                                    self.res_width)),
                                     int(math.floor(int(
                                         rect_properties[1]) *
                                                    self.res_height)),
                                     int(math.ceil(int(
                                         rect_properties[2]) *
                                                   self.res_width)),
                                     int(math.floor(int(rect_properties[3]) *
                                                    self.res_height))),
                                 "rect")

        return in_rect

    def find_line(self, line, color_lookup):
        """ Class helper method for load_levels
        This method finds and assigns line elements
        """

        """Line elements are detected by this format:
        (screen, color, [x, y], [width, height], thickness)
        """

        # Assign the line containing pygame.line elements
        line_info = re.search(r"\([a-z]+, .*, \[[0-9]+, [0-9]+], "
                              r"\[[0-9]+, [0-9]+], [0-9]\)",
                              line).group().split(", ")
        # Convert the line into an KOGElement
        in_line = KOGElement(line_info[1], [int(line_info[2][1:]),
                                            int(line_info[3][:-1]),
                                            int(int(line_info[4][1:]) * \
                                                self.res_width * self.res_height),
                                            int(int(line_info[5][:-1]) * \
                                                self.res_width * self.res_height),
                                            int(int(line_info[6][:-1]) * \
                                                max(self.res_width,
                                                    self.res_height))],
                             "line")
        return in_line

    def find_text(self, line, color_lookup):
        """ Class helper method for load_levels
        This method finds and assigns text objects
        """

        """(text, (x, y), color)
        Color is defined currently as:
            - X (BLUE)
            - X_Y (DARK_RED)
            - X_Y_Z (EDIT_DARK_GREEN)
        or as a tuple of numbers in the form of a string
        """
        # Split the parameters into their own separate strings
        format_search = re.search(r"\(\".*\", \([0-9]+, [0-9]+\), "
                                  r"[0-9]+, \"[a-zA-Z]+\", "
                                  r"([A-Z]+_[A-Z]+_[A-Z]+|"
                                  r"[A-Z]+_[A-Z]+|"
                                  r"[A-Z]+|"
                                  r"\([0-9]+, [0-9]+, [0-9]+\)), "
                                  r"None\)",
                                  line).group()[1:-1].split(", ")
        # Get color
        if format_search[5] in color_lookup:
            text_color = color_lookup[format_search[5]]
        else:
            text_color = (int(format_search[5][1:]),
                          int(format_search[6]),
                          int(format_search[7][:-1]))

        # Create Text class
        add_text = Text(format_search[0][1:-1],
                        (int(format_search[1][1:]),
                         int(format_search[2][0:-1])),
                        int(format_search[3]),
                        format_search[4][1:-1],
                        text_color,
                        None)
        add_text.scale(self.res_width, self.res_height)

        return add_text

    # load_stars will get star data/behavior in stars.txt

    def load_stars(self, in_file):
        with open(in_file, "r") as star_file:
            level_id = 0
            all_lines = star_file.readlines()

            for line in all_lines:
                if re.search("\\(.+\)", line):
                    level_id += 1
                    self.star_data[level_id] = []

                if re.search("\\[.+]", line):
                    get_data = line[1:-2].split(", ")
                    img_rect = pygame.Rect(int(get_data[1]),
                                           int(get_data[2]),
                                           int(get_data[3]),
                                           int(get_data[4]))
                    detect_rect = pygame.Rect((int(get_data[1]) +
                                               (int(get_data[3]) / 2)) -
                                              (int(get_data[5]) / 2),
                                              (int(get_data[2]) + (int(
                                                  get_data[4]) / 2)) -
                                              (int(get_data[6]) / 2),
                                              int(get_data[5]),
                                              int(get_data[6])
                                              )
                    roam_rect = pygame.Rect(int(get_data[7]),
                                            int(get_data[8]),
                                            int(get_data[9]),
                                            int(get_data[10]))
                    in_star = Collectable(int(get_data[0]),
                                          img_rect,
                                          detect_rect,
                                          roam_rect)
                    self.star_data[level_id] += [in_star]

    def load_images(self, in_file):
        # Defining a list of methods to make image classes
        # todo: In the future if these have special functions, use ani_type
        ani_type = []

        with open(in_file, "r") as img_file:
            all_lines = img_file.readlines()
            level_id = 0
            for line in all_lines:
                filter_line = line[0:-1]     # Remove "\n
                # Identified a level ID
                if filter_line.isnumeric():
                    level_id = int(filter_line)
                    if level_id not in self.images:
                        self.images[level_id] = []
                elif len(filter_line.split(", ")) == 6:
                    get = filter_line.split(", ")
                    self.images[level_id] += [Image(get[0],
                                                    int(get[1]),
                                                    int(get[2]),
                                                    int(get[3]),
                                                    int(get[4]),
                                                    int(get[5]))]
                else:
                    print("images.txt had a problem, quitting")

    # print_levels is used for debug purposes

    def print_levels(self):
        print("LEVEL TITLES:")
        print(self.level_set)
        print("=============")
        print("LEVEL ELEMENTS:")
        print(self.ls_elements)
        print("===============")
        print("LEVEL ID RANGES:")
        print(self.id_range)
        print("===============")
        print("STARS:")
        print(self.star_data)
        print("===============")
        print("IMAGES:")
        print(self.images)

    # The following methods are used for manipulating Replay class files/data

    def write_replays(self):
        with open("assets/replays_out.txt", "w") as write_file:
            for level_id in self.replay_exp:
                write_file.write(str(self.replay_exp[level_id]) + "\n" +
                                 "===" + "\n")

    def read_replays(self):
        level_counter = 1
        process_dict = {}
        with open("assets/replays_in.txt", "r") as read_file:
            for each_line in read_file.readlines():
                if each_line == "===\n":
                    level_counter += 1
                elif 0 < len(each_line) and each_line != "===\n" and \
                        each_line != "[]\n":
                    self.replay_imp[level_counter] = each_line[1:-2].split(
                        ", ")[2:]
                    self.imp_diff[level_counter] = int(
                        each_line[1:-1].split(", ")[1])

    def init_replays(self):
        level_counter = 1
        while level_counter < len(self.level_set):
            self.replay_exp[level_counter] = []
            self.replay_imp[level_counter] = []
            self.imp_diff[level_counter] = -1
            level_counter += 1

    def update_replays(self, level_id, replay_info):
        self.replay_exp[level_id] = replay_info

    def update_temp(self, replay_info):
        self.hold_replay.append(replay_info)  # replay_info must be a list

    def replays_on(self):
        self.enable_replay = True

    def replays_off(self):
        self.enable_replay = False

    def write_save(self):
        file_path = "assets/saves/save_file1.txt"
        with open(file_path, "w") as open_file:
            open_file.write(str(self.total_deaths) + "\n")
            open_file.write(str(self.total_jumps) + "\n")
            open_file.write(str(self.total_time +
                                pygame.time.get_ticks()) + "\n")
            open_file.write(str(self.total_stars) + "\n")
            open_file.write(str(self.level_deaths) + "\n")
            open_file.write(str(self.level_jumps) + "\n")
            open_file.write(str(self.level_times) + "\n")
            open_file.write(str(self.level_progress) + "\n")
            open_file.write(str(self.stars_collected) + "\n")

            open_file.write(str(self.diff_value) + "\n")
            open_file.write(str(self.bg_slider) + "\n")
            open_file.write(str(self.quick_restart) + "\n")
            open_file.write(str(self.music.perc_vol) + "\n")
            open_file.write(str(self.sound_vol) + "\n")
            open_file.write(str(self.hub_index))

    # load_save will load miscellaneous data from file

    def load_save(self):
        # todo: change this value to the desired file length
        check_len = 15
        file_path = "assets/saves/save_file1.txt"
        if os.path.isfile(file_path):
            with open(file_path, "r") as test_file:
                file_len = len(test_file.readlines())

        if os.path.isfile(file_path) and file_len == check_len:
            get_save = open(file_path, "r")
            self.total_deaths = int(get_save.readline())
            self.total_jumps = int(get_save.readline())
            self.total_time = int(get_save.readline())
            self.total_stars = int(get_save.readline())

            get_death = get_save.readline()[1:-2].split(", ")
            if 1 < len(get_death):
                for each_stat in get_death:
                    split_stat = each_stat.split(": ")
                    self.level_deaths[int(split_stat[0])] = int(split_stat[1])

            get_jumps = get_save.readline()[1:-2].split(", ")
            if 1 < len(get_jumps):
                for each_stat in get_jumps:
                    split_stat = each_stat.split(": ")
                    self.level_jumps[int(split_stat[0])] = int(split_stat[1])

            get_times = get_save.readline()[1:-2].split(", ")
            if 1 < len(get_times):
                for stat_ind in range(0, len(get_times), 3):
                    self.level_times[int(get_times[stat_ind].split(":")[0])] = [
                        int(get_times[stat_ind].split(": ")[1][1:]),
                        int(get_times[stat_ind + 1]),
                        int(get_times[stat_ind + 2][:-1])
                    ]

            get_prog = get_save.readline()[1:-2].split(", ")
            if 1 < len(get_prog):
                for each_stat in get_prog:
                    self.level_progress += [int(each_stat)]

            get_stars = get_save.readline()[1:-2].split(", ")
            if 1 < len(get_stars):
                for each_stat in get_jumps:
                    split_stat = each_stat.split(": ")
                    self.stars_collected[int(split_stat[0])] = \
                        int(split_stat[1])

            self.diff_value = int(get_save.readline())
            self.bg_slider = int(get_save.readline())
            self.background = [
                self.bg_slider,
                self.bg_slider,
                self.bg_slider
            ]
            self.quick_restart = int(get_save.readline())
            self.total_music_per = int(get_save.readline())
            pygame.mixer.music.set_volume(self.total_music_per)
            self.sound_vol = float(get_save.readline())
            self.hub_index = int(get_save.readline())
        elif os.path.isfile(file_path) and file_len == check_len:
            get_save = open(file_path, "w")
        else:
            # No previous save made
            get_save = open(file_path, "x")

        get_save.close()


# The following classes are for recording player movement while playing a level

class ReplayBlock:
    """A more convenient way to hold replay info, the info in each node"""

    def __init__(self, times, in_type):
        self.times = times  # Time for that action
        self.type = in_type  # Type of action


class ReplayNode:
    """Acts as a node for the chain, only to be used with ReplayChain"""

    def __init__(self, item):
        self.item = item
        self.next = None


class ReplayChain:
    """
    This is similar to kog_editor's linked list, except we have pointers
    on both ends now. Similarly, it's crucial that we are able to move
    elements from the beginning and end of the chain. That's why, this linked
    list adapts the structure of a queue adapting pointers to the head and tail
    of a chain
    This linked list is only usable with the replay idea in mind, as it only
    holds up to 5 items. Furthermore, it also uses a count when adding which
    corresponds with amount of deaths in the KOG game.
    """

    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, item):
        if self.head is None and self.tail is None and self.check_len() == 0:
            # Empty, get first node
            self.head = ReplayNode(item)
            self.tail = self.head
        elif 0 < self.check_len() < 5 and self.tail is not None:
            # More than one node, not at limit of 5 yet
            new_node = ReplayNode(item)
            self.tail.next = new_node
            self.tail = self.tail.next
        elif 5 <= self.check_len() < 6 and self.head is not None and \
                self.tail is not None:
            # Chain going to go past the length limit
            self.head = self.head.next
            new_node = ReplayNode(item)
            self.tail.next = new_node
            self.tail = self.tail.next
        else:
            print("ERROR: LINKED LIST TOO LONG, report this!")

    def check_len(self):
        focus_node = self.head
        counter = 0
        while focus_node is not None:
            counter += 1
            focus_node = focus_node.next

        return counter

    def chain_to_list(self):
        focus_node = self.head
        out_list = []
        while focus_node is not None:
            out_list += focus_node.item
            focus_node = focus_node.next

        return out_list


class KOGElement:
    """A more convenient way to hold level element info"""

    def __init__(self, color, shape, in_type):
        self.color = color  # Block color
        self.shape = shape  # Block shape
        self.type = in_type  # Distinguish line vs rect types


class Image:
    def __init__(self, in_file, xpos, ypos, width, height, frame_delay):
        """
        :param in_file: A single image file
        :param xpos: x position relative to the 1080 scale
        :param ypos: y position relative to the 576 scale
        :param frame_delay: time inbetween each  (in seconds)
        """
        self.img_rect = pygame.Rect(xpos, ypos, width, height)
        self.frame_delay = frame_delay * 1000
        # Frame delay is in seconds

        self.animate_index = 0
        self.animate_time = pygame.time.get_ticks()
        pygame.display.set_mode([1080, 576])

        if ".png" in in_file or ".jpg" in in_file:
            load_image = pygame.image.load(in_file).convert_alpha()
            scale_image = pygame.transform.scale(load_image,
                                                 (self.img_rect.width,
                                                  self.img_rect.height))
            self.image = scale_image
        else:
            self.image = None

    def validate(self):
        if self.image is None:
            return "File's Provided Not Put In A List"
        elif self.img_rect is None or \
                self.img_rect.x < 0 or 1080 < self.img_rect.x:
            return "Invalid x position out of bounds or not given"
        elif self.img_rect is None or \
                self.img_rect.y < 0 or 576 < self.img_rect.y:
            return "Invalid y position out of bounds or not given"
        elif self.frame_delay is None or type(self.frame_delay) is not int or \
                type(self.frame_delay) is not float:
            return "Frame delay is invalid (not int or float)"

    def update_pos(self, x, y):
        self.img_rect.x = x
        self.img_rect.y = y

    def render(self, screen):
        screen.blit(self.image, self.img_rect)


class Animate:

    def __init__(self, in_files, xpos, ypos, width, height, frame_delay):
        """
        :param in_files: List of file_paths to all of this objects frames
        :param xpos: x position relative to the 1080 scale
        :param ypos: y position relative to the 576 scale
        :param frame_delay: time inbetween each  (in seconds)
        """
        self.file_frames = []
        self.img_rect = pygame.Rect(xpos, ypos, width, height)
        self.frame_delay = frame_delay * 1000
        # Frame delay is in seconds

        self.animate_index = 0
        self.animate_time = pygame.time.get_ticks()
        pygame.display.set_mode([1080, 576])

        for file in os.listdir(in_files):
            if ".png" in file or ".jpg" in file:
                load_image = pygame.image.load(in_files + file).convert_alpha()
                scale_image = pygame.transform.scale(load_image,
                                                     (self.img_rect.width,
                                                      self.img_rect.height))
                self.file_frames += [scale_image]

    def validate(self):
        if self.file_frames is None:
            return "File's Provided Not Put In A List"
        elif self.img_rect is None or \
                self.img_rect.x < 0 or 1080 < self.img_rect.x:
            return "Invalid x position out of bounds or not given"
        elif self.img_rect is None or \
                self.img_rect.y < 0 or 576 < self.img_rect.y:
            return "Invalid y position out of bounds or not given"
        elif self.frame_delay is None or type(self.frame_delay) is not int or \
                type(self.frame_delay) is not float:
            return "Frame delay is invalid (not int or float)"

    def animate(self, screen):
        self.update()
        self.render(screen)

    def update(self):
        # Check if it's time to change the frame
        if self.frame_delay < pygame.time.get_ticks() - self.animate_time:
            self.animate_index += 1
            self.animate_time = pygame.time.get_ticks()

        # Check if the animate_index is out of bounds and ready to loop
        if self.animate_index < 0:
            self.animate_index = len(self.file_frames)
        elif len(self.file_frames) - 1 < self.animate_index:
            self.animate_index = 0

    def update_pos(self, x, y):
        self.img_rect.x = x
        self.img_rect.y = y

    def render(self, screen):
        frame = self.file_frames[self.animate_index]
        screen.blit(frame, self.img_rect)


class AnimateRect:
    def __init__(self, in_rect, color, transparency, frame_delay):
        self.rect = in_rect
        self.frame_delay = frame_delay * 1000
        # Amount of time before this Rect does an action (in seconds)

        self.animate_time = pygame.time.get_ticks()

        self.rect_surface = pygame.Surface((in_rect.width, in_rect.height))

        self.rect_surface.set_alpha(transparency)
        self.transparency = transparency

        self.color = color

    def more_clear(self):
        if 0 < self.transparency:
            self.transparency -= 5

        if self.transparency < 0:
            self.rect_surface.set_alpha(0)
        else:
            self.rect_surface.set_alpha(self.transparency)

    def more_opaque(self):
        if self.transparency < 255:
            self.transparency += 5

        if 255 <= self.transparency:
            self.rect_surface.set_alpha(255)
        else:
            self.rect_surface.set_alpha(self.transparency)

    def update_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def render(self, screen):
        self.rect_surface.fill(self.color)
        screen.blit(self.rect_surface, [self.rect.x, self.rect.y])


class Collectable:
    """
    Render, move, and give mechanics to collectables
    This can otherwise be known as the star pets (starmets)
    """

    def __init__(self, object_id, collect_rect, detect_rect, roam_rect):
        self.alive = True
        self.freeze = False  # Determine if star should move

        self.id = object_id
        self.rect = collect_rect
        self.detect_rect = detect_rect
        self.roam_rect = roam_rect
        self.fldr_id = [
            "stars/"
        ]  # object id to which folder they should use
        """
        an id of 0 is unspecific and uses all files in the stars folder
        """

        self.animate_star = Animate("assets/images/" +
                                    self.fldr_id[object_id],
                                    self.rect.x, self.rect.y,
                                    self.rect.width, self.rect.height, 2)

        if not self.animate_star.validate():
            raise "UNABLE TO LOAD STAR DATA"

        self.behaviour = 0  # 3 behaviours, max index of 2

        self.move_x = 0
        self.move_y = 0

        self.random_direction = [-1, 0, 1]
        self.random_time = pygame.time.get_ticks()
        # Time before next random movement change
        self.move_delay = pygame.time.get_ticks()
        # Time used to move away from the zone

        self.movement_time = pygame.time.get_ticks()
        # Control the movement speed of the stars with time

    def render_test(self, screen):
        # Render unrendered rects for debugging
        pygame.draw.rect(screen, RED, self.roam_rect)  # Roam rect
        pygame.draw.rect(screen, BLUE, self.detect_rect)  # Detection rect
        pygame.draw.rect(screen, YELLOW, self.rect)  # Image rect

    def update(self, player_rect):
        """Move delay used in self.detect_bounds(): if enough time
        has passed in moving away from the border, resume usual movement.
        Usual movement is usually either avoiding the player or random
        movement"""
        if 500 <= pygame.time.get_ticks() - self.move_delay and \
                not self.freeze:
            # If the player is within the star's vision zone
            if self.detect_rect.colliderect(player_rect):
                # move accordingly away from the player
                self.detect_player(player_rect)
            else:
                # do random movement
                self.random_movement()
        # Prioritize moving away from the border over avoiding/random movement
        self.detect_bounds()

        # every 0.025 seconds, apply the movement
        if not self.freeze and \
                25 <= pygame.time.get_ticks() - self.movement_time:
            self.rect.x += self.move_x
            self.rect.y += self.move_y

            self.detect_rect.x = (self.rect.x + (self.rect.width / 2)) - \
                                 (self.detect_rect.width / 2)
            self.detect_rect.y = (self.rect.y + (self.rect.height / 2)) - \
                                 (self.detect_rect.height / 2)

            self.movement_time = pygame.time.get_ticks()

        self.animate_star.update_pos(self.rect.x, self.rect.y)

    def render(self, screen):
        if not self.alive:
            return None
        # Test render only renders the collision rects
        # self.render_test(screen)
        self.animate_star.animate(screen)

    def detect_player(self, player_rect):
        if self.freeze:
            return None

        # If the player is to the left of the star
        if player_rect.x < self.rect.x:
            self.move_x = 1  # move right
        # If the player is to the right of the star
        elif self.rect.x + self.rect.width < player_rect.x:
            self.move_x = -1  # move left

        # If the player is above the star
        if player_rect.y < self.rect.y:
            self.move_y = 1  # move down
        # If the player is below the star
        elif self.rect.y + self.rect.height < player_rect.y:
            self.move_y = -1  # move up

        # Detect if player is touching, if so, get removed
        if player_rect.colliderect(self.rect):
            self.alive = False

    def detect_bounds(self):
        # If the star is out to the right of the barrier
        if self.roam_rect.x + self.roam_rect.width <= \
                self.rect.x + self.rect.width:
            self.move_x = -1  # move back to the left
            self.move_delay = pygame.time.get_ticks()  # move for x seconds
        # If the star is out to the left of the barrier
        elif self.rect.x <= self.roam_rect.x:
            self.move_x = 1  # move back to the right
            self.move_delay = pygame.time.get_ticks()  # move for x seconds

        # If the star is below the barrier
        if self.roam_rect.y + self.roam_rect.height <= \
                self.rect.y + self.rect.height:
            self.move_y = -1  # move back up into the barrier
            self.move_delay = pygame.time.get_ticks()  # move for x seconds
        # If the star is above the barrier
        elif self.rect.y <= self.roam_rect.y:
            self.move_y = 1  # move back down into the barrier
            self.move_delay = pygame.time.get_ticks()  # move for x seconds

    def random_movement(self):
        # randomly set the direction of x and y from -1, 0, then 1
        # Don't do another random movement for another 0.5 seconds at least
        if 500 <= pygame.time.get_ticks() - self.random_time:
            self.move_x = self.random_direction[random.randint(0, 2)]
            self.move_y = self.random_direction[random.randint(0, 2)]
            self.random_time = pygame.time.get_ticks()
            # Reset the timer


class SquareMe:  # lil purple dude

    def __init__(self, x_spawn, y_spawn, width, height, rgb, diff,
                 res_width, res_height, jump_vol):
        """
        self.square parameters: [
        [x_spawn, y_spawn],
        [width, height]
        [RGB value],
        difficuty_value
        ]
        """
        self.xpos = x_spawn  # Current x_position, initialized as spawn
        self.ypos = y_spawn  # Current y_position, initialized as spawn
        self.width = math.ceil(width * res_width)  # Current width, always 10
        self.height = math.ceil(height * res_height)
        # Current height, always 10
        self.color = rgb  # Color of player as static constant or tuple
        self.square_render = None  # Pygame.draw rect of the player
        self.alive = False  # If the player is alive (able to move)
        self.freeze = False  # If the player is forced to pause

        self.jumps = 0  # Amount of jumps the player had done (remove)
        self.jump_ability = False  # If the player is able to jump
        self.enable_gravity = True  # If gravity is acting on the player
        self.max_jump = 50  # Limit for the jump loop to iterate
        self.jump_boost = -1 * (self.max_jump - 1)  # Counter for jump loop
        self.direction = 1  # Move direction: 1 for right, -1 for left
        self.max_gravity = 95  # Limit for the gravity loop to iterate
        self.gravity_counter = self.max_gravity  # Counter for gravity loop
        self.diff_factor = diff * res_width
        # Movement multiplier based on difficulty and resolution sclaing

        file_path = "assets/audio/sfx/"
        self.jump_sound_1 = pygame.mixer.Sound(file_path + "jump_sfx.wav")
        # Jump sound for player
        self.jump_sound_1.set_volume(0.1 * (jump_vol / 100))  # out of 1 or 100%
        # Jump volume for the player, set at 0.1 out of 1, or 10%

        # Get location and info of surrounding blocks
        self.collide_rect = pygame.Rect(self.xpos - (30 * res_width),
                                        self.ypos - (30 * res_height),
                                        self.width + (60 * res_width),
                                        self.height + (80 * res_height))
        # Top, bottom, left and right collision
        self.left_col = pygame.Rect(self.xpos - self.width - (10 * res_width),
                                    self.ypos + (res_height * 1),
                                    self.width + (res_width * 10),
                                    8 * res_height)
        self.right_col = pygame.Rect(self.xpos + self.width,
                                     self.ypos + (res_height * 1),
                                     self.width + (10 * res_width),
                                     8 * res_height)
        self.top_col = pygame.Rect(self.xpos,
                                   self.ypos - self.height - (10 * res_height),
                                   10 * res_width,
                                   self.height + (10 * res_height))
        self.bot_col = pygame.Rect(self.xpos, self.ypos + self.height,
                                   10 * res_width, self.height * 4)

        self.res_width = res_width
        self.res_height = res_height

        """One single larger rect for collision detection
        """
        self.grav_y = None
        self.jump_y = None
        self.left_x = None
        self.right_x = None

        # Decor rects/player visuals
        self.afterimages = []
        # Amount of time before the next after image is made
        self.afterimg_delay = pygame.time.get_ticks()

    def move(self):
        """
        Move the player by 4 units in the specific direction, multiplied
        by the difficulty factor (max of 1 usually)
        """
        # Move horizontally depending on the direction
        move_factor = (4 * self.direction) * self.diff_factor * self.res_width
        if self.left_x is not None and \
                self.xpos + move_factor <= self.left_x:
            self.direction = 1
            self.xpos = self.left_x
        elif self.right_x is not None and \
                self.right_x <= self.xpos + move_factor + self.width:
            self.direction = -1
            self.xpos = self.right_x - self.width
        else:
            self.xpos += move_factor

        # Gravity and jump functions
        self.gravity()
        self.jump()

        self.update_collision_detection()

    def update_afterimages(self):
        # How frequently after_img is animated according to player speed
        # INT's: 40, 60, 80 - 80 is default
        effect_factor = 40 / self.diff_factor

        # Change transparency if it's too solid/opaque initially, default is 125
        transp = 100

        # Have 3 afterimages at most
        # After 0.5 seconds, make the after_image
        if len(self.afterimages) < 3 and \
                effect_factor < pygame.time.get_ticks() - self.afterimg_delay:
            # Transparency goes from 0 (transparent) to 255 (opaque)
            self.afterimages += [AnimateRect(pygame.Rect(self.xpos,
                                                         self.ypos,
                                                         self.width,
                                                         self.height),
                                             self.color,
                                             transp, effect_factor / 10000)]
            self.afterimg_delay = pygame.time.get_ticks()

        # Loop through afterimages and update their transparency
        for rect in self.afterimages:
            # Check if their transparency is at 0, if so reset
            if rect.transparency <= 0 and \
                    effect_factor < pygame.time.get_ticks() - self.afterimg_delay:
                rect.update_pos(self.xpos, self.ypos)
                rect.transparency = 125
                self.afterimg_delay = pygame.time.get_ticks()
            elif rect.frame_delay < pygame.time.get_ticks() - rect.animate_time:
                # Else change transparency
                rect.more_clear()
                rect.animate_time = pygame.time.get_ticks()

    def update_collision_detection(self):
        # Update collision logic position in real time with the player position
        self.collide_rect.x = self.xpos - (30 * self.res_width)
        self.collide_rect.y = self.ypos - (30 * self.res_height)
        self.left_col.x = self.xpos - self.width - (10 * self.res_width)
        self.left_col.y = self.ypos + (self.res_height * 1)
        self.right_col.x = self.xpos + self.width
        self.right_col.y = self.ypos + (self.res_height * 1)
        self.top_col.x = self.xpos
        self.top_col.y = self.ypos - self.height - (10 * self.res_height)
        self.bot_col.x = self.xpos
        self.bot_col.y = self.ypos + self.height

    def jump(self):
        # Jump that will change the player's y position in the game loop
        if self.jump_ability and 0 <= self.jump_boost:
            jump_factor = ((self.jump_boost ** 2) * 0.002) * self.diff_factor
            if self.jump_y is not None and \
                    self.ypos - self.jump_y < jump_factor:
                self.ypos = self.jump_y
                self.jump_ability = False
                self.jump_boost = -1
                self.enable_gravity = True
            else:
                self.ypos -= jump_factor * self.res_height
                """Change the y position based on the counter and difficulty. This
                Creates a parabolic relationship from being squared."""
                self.jump_boost -= 2 * self.diff_factor
                """Decrease the counter until it reaches 0
                This is used to create the first arc of the jump"""
        else:
            """Crucial for the second half of the jump, 
            allowing the player to fall"""
            self.jump_ability = False

    def render(self, screen):
        # Visualize collision rect, uncomment to see
        """pygame.draw.rect(screen, (55, 230, 50), self.collide_rect)  # big square
        pygame.draw.rect(screen, BLUE, self.left_col)  # left
        pygame.draw.rect(screen, BLUE, self.right_col)  # right
        pygame.draw.rect(screen, BLUE, self.top_col)  # top
        pygame.draw.rect(screen, BLUE, self.bot_col)  # bottom"""

        # Update the square render/rect with the position (x and y)
        self.square_render = pygame.draw.rect(screen, self.color, [self.xpos,
                                                                   self.ypos,
                                                                   self.width,
                                                                   self.height])

        # TODO: Test player outline:
        """ pygame.draw.rect(screen, YELLOW, [self.xpos, self.ypos,
                                          self.width, self.height], 1)"""

        # Update player afterimages
        self.update_afterimages()
        # I put this update here since it's only updating the renders

        # Render afterimages
        for rect in self.afterimages:
            rect.render(screen)

    def collision_plat(self, object_list: [pygame.Rect]):
        # Get all the colliding rects with the bottom rect
        bot_collisions = self.collide_rect.collidelistall(object_list)

        # Bottom platform collision
        self.bottom_collision(object_list, bot_collisions)

        # Top ceiling collision
        top_collisions = self.collide_rect.collidelistall(object_list)
        self.top_collision(object_list, top_collisions)

    def collision_wall(self, object_list: [pygame.Rect]):
        # New collision logic:
        left_collision = self.collide_rect.collidelistall(object_list)
        right_collision = self.collide_rect.collidelistall(object_list)

        self.left_collision(object_list, left_collision)
        self.right_collision(object_list, right_collision)

    def top_collision(self, object_list, top_collisions):
        all_yheight = []
        for tcollide_id in top_collisions:
            collide_x = object_list[tcollide_id].x
            collide_y = object_list[tcollide_id].y
            collide_width = object_list[tcollide_id].width
            collide_height = object_list[tcollide_id].height

            """
            This if statement checks for if the player's top touches the ceiling
                or the bottom of a platform:
                - If there's any rect that collided (id != -1)
                - 
            """
            if self.top_col.colliderect(object_list[tcollide_id]) and not \
                    self.left_col.colliderect(object_list[tcollide_id]) and not \
                    self.right_col.colliderect(object_list[tcollide_id]) and \
                    collide_y + collide_height < self.ypos:
                all_yheight += [collide_y + collide_height]

            if (self.square_render.colliderect(object_list[tcollide_id]) or
                self.ypos == collide_y + collide_height) and \
                    self.top_col.colliderect(object_list[tcollide_id]) and \
                    not self.left_col.colliderect(object_list[tcollide_id]) and \
                    not self.right_col.colliderect(object_list[tcollide_id]):
                self.jump_ability = False
                self.jump_boost = -1
                self.enable_gravity = True

                if self.ypos < collide_y + collide_height and \
                        self.xpos < collide_x + collide_width and \
                        collide_x < self.xpos + self.width:
                    self.ypos = collide_y + collide_height

        if 0 < len(all_yheight):
            self.jump_y = max(all_yheight)
        else:
            self.jump_y = None

    def bottom_collision(self, object_list, bot_collisions):
        """By default, set gravity to be true (we don't know if the player is on
        the ground or in the air)
        """
        all_y = []
        self.enable_gravity = True
        for bcollide_id in bot_collisions:
            """
            The if statement checks for if the player is on top of a platform
            and does so by checking:
            - If there's any rect that collided (id != -1)
            - If the player's bottom (self.ypos + self.height) is touching
                the bottom platform (collide_y <=) or a bit inside the platform
                (<= collide_y + self.height)
            - and If the player is within the bounds of the platform.

                The left boundary is collide_x < self.xpos + self.width, or if
                the right side of the player (self.xpos + self.width) is within 
                the left side of the platform (collide_x).

                The right boundary is self.xpos < collide_x + collide_width, or
                if the left side of the player (self. xpos) is within the
                right side of the platform (collide_x + collide_width)
            """
            collide_y = object_list[bcollide_id].y
            if self.ypos < collide_y and \
                    self.bot_col.colliderect(object_list[bcollide_id]) and not \
                    self.left_col.colliderect(object_list[bcollide_id]) and not \
                    self.right_col.colliderect(object_list[bcollide_id]):
                all_y += [collide_y]

            if (self.ypos + self.height == collide_y or
                self.square_render.colliderect(object_list[bcollide_id])) and \
                    self.bot_col.colliderect(object_list[bcollide_id]) and \
                    not self.left_col.colliderect(object_list[bcollide_id]) and \
                    not self.right_col.colliderect(object_list[bcollide_id]):
                # If true, disable/reset gravity, enable jump
                self.enable_gravity = False
                self.jump_ability = True
                self.gravity_counter = self.max_gravity

                if collide_y < self.ypos + self.height:
                    self.ypos = collide_y - self.height

        if 0 < len(all_y):
            self.grav_y = min(all_y)
        else:
            self.grav_y = None

    def left_collision(self, object_list, left_collision):
        all_xl = []
        # Left side collision, going left to turn right
        for lcollide_id in left_collision:
            collide_x = object_list[lcollide_id].x
            collide_y = object_list[lcollide_id].y
            collide_width = object_list[lcollide_id].width
            collide_height = object_list[lcollide_id].height

            if self.left_col.colliderect(object_list[lcollide_id]) and \
                    not self.top_col.colliderect(object_list[lcollide_id]) and \
                    not self.bot_col.colliderect(object_list[lcollide_id]) and \
                    collide_x + collide_width < self.xpos:
                all_xl += [collide_x + collide_width]

            if lcollide_id != -1 and self.square_render.colliderect(
                    object_list[lcollide_id]) and \
                    self.left_col.colliderect(object_list[lcollide_id]) and \
                    collide_y < self.ypos + self.height and \
                    self.ypos < collide_y + collide_height:
                self.direction = 1
                self.enable_gravity = True

                if self.xpos < collide_x + collide_width and \
                        not self.top_col.colliderect(object_list[lcollide_id]):
                    self.xpos = collide_x + collide_width

        if 0 < len(all_xl):
            self.left_x = max(all_xl)
        else:
            self.left_x = None

    def right_collision(self, object_list, right_collision):
        all_xr = []
        # Right side collision, going right to turn left
        for rcollide_id in right_collision:
            collide_x = object_list[rcollide_id].x
            collide_y = object_list[rcollide_id].y
            collide_width = object_list[rcollide_id].width
            collide_height = object_list[rcollide_id].height

            if self.right_col.colliderect(object_list[rcollide_id]) and \
                    not self.top_col.colliderect(object_list[rcollide_id]) and \
                    not self.bot_col.colliderect(object_list[rcollide_id]) and \
                    self.xpos + self.width < collide_x:
                all_xr += [collide_x]

            if rcollide_id != -1 and self.square_render.colliderect(
                    object_list[rcollide_id]) and \
                    self.right_col.colliderect(object_list[rcollide_id]) and \
                    collide_y < self.ypos + self.height and \
                    self.ypos < collide_y + collide_height:
                self.direction = -1
                self.enable_gravity = True

                if collide_x < self.xpos + self.width and \
                        not self.top_col.colliderect(object_list[rcollide_id]):
                    self.xpos = collide_x - self.width

        if 0 < len(all_xr):
            self.right_x = min(all_xr)
        else:
            self.right_x = None

    def gravity(self):
        # fix turning off gravity
        if self.enable_gravity and not self.jump_ability:
            gravity_y = ((self.gravity_counter ** 2) * 0.00015) * \
                        self.diff_factor * self.res_height
        else:
            gravity_y = 0

        if self.enable_gravity and not self.jump_ability:
            if self.grav_y is not None and \
                    self.grav_y < gravity_y + self.ypos + self.height:
                self.ypos = self.grav_y - self.height
                self.enable_gravity = False
                self.jump_ability = True
                self.gravity_counter = self.max_gravity
            else:
                self.ypos += gravity_y

        if self.gravity_counter < 1100:
            self.gravity_counter += 2 * self.diff_factor

    def death(self, death_list: [pygame.Rect]):
        collide_id = self.square_render.collidelist(death_list)
        if collide_id != -1:
            self.alive = False
            return 1
        else:
            return 0


class Scene:
    """
    Class template for creating scene based games
    """

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
        """
        This function should contain the pressed for loop and other held
        buttons. Pressing or holding these buttons should cause something
        to change such as a class variable (+= 1, True/False, change str.. etc.)
        or call another function.

        :param pressed: Detect buttons that are pressed (like if held, it will
        only be updated with the initial press)
        :param held: Detect buttons that are held down
        :return:
        """
        pass

    def update(self):
        # this will be overridden in subclasses
        """
        This function should check for variables that need to be updated
        continuously. A good way to distinguish this from input is that this
        update function doesn't directly respond from a button press. For
        example, let's have input add to self.x by 1, or self.x += 1. Then, if
        we wanted to keep self.x within the bounds of 0 to 10, we check for that
        in update. In update, we'd use if self.x < 0 and 10 < self.x to check
        whenever self.x goes out of these bounds to then reset self.x.

        :return:
        """
        pass

    def render(self, screen):
        # this will be overridden in subclasses
        """
        This function is solely used for rendering purposes such as
        screen.blit or pygame.draw
        :param screen:
        :return:
        """
        pass

    def change_scene(self, next_scene):
        """
        This function is used in the main pygame loop. This function is
        responsible for formally changing the scene
        """
        self.this_scene = next_scene

    def close_game(self):
        """
        Set the current scene to nothing and is used to stop the game.
        This function is responsible for ending the game loop (or scene)
        formally.
        """
        self.change_scene(None)


class KOGLog:
    """Class used to manage and hold game logs"""

    def __init__(self):
        pass


"""
!! NOTICE !!
BELOW ARE A SET OF HELPER FUNCTIONS (STATIC) - Not restricted to classes
"""


def convert_time(in_time):
    """Converts input time of seconds into seconds, minutes and hours"""
    seconds, minutes, hours = 0, 0, 0
    if in_time > 1000:
        seconds = round(in_time / 1000)
    if seconds >= 60:
        minutes = seconds // 60
        seconds = seconds % 60
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60

    return [hours, minutes, seconds]


def add_time(old_times, new_times):
    """
    Function that returns the combined time
    :param old_times: Time present in memory
    :param new_times: New time accumulated
    :return:
    """
    seconds = old_times[2] + new_times[2]
    minutes_to_s = (old_times[1] + new_times[1]) * 60
    hours_to_s = (old_times[0] + new_times[0]) * (60 ** 2)
    # print(old_times, new_times)
    # print(seconds, minutes_to_s, hours_to_s)

    return convert_time((seconds + minutes_to_s + hours_to_s) * 1000)


def format_time(time_list):
    """ Convert list of times into a formatted string of 00:00:00"""
    out_time = ""
    for time in time_list:
        if len(str(time)) < 2:   # Time of 1 char, single digit
            out_time += "0" + str(time)
        else:   # Double digits
            out_time += str(time)
        out_time += ":"

    return out_time[:-1]

