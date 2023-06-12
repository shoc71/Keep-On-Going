import pygame

DARK_RED = (139, 0, 0)
YELLOW = (235, 195, 65)
BLACK = (0, 0, 0)
CYAN = (47, 237, 237)
RED = (194, 57, 33)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)


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
            "level-loop1_v2.wav",
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
        self.direction = "right"
        self.max_gravity = 95
        self.gravity_counter = self.max_gravity

        self.jump_sound_1 = pygame.mixer.Sound("jump_sfx.wav")
        self.jump_sound_1.set_volume(0.1)  # out of 1 = 100%

    def move(self):
        if self.direction == "right":
            self.xpos += 2
        elif self.direction == "left":
            self.xpos -= 2

        self.xpos = round(self.xpos)

        self.gravity()
        self.jump()

    def jump(self):
        if self.jump_ability and 0 <= self.jump_boost:
            self.ypos -= (self.jump_boost ** 2) * 0.001
            self.jump_boost -= 1
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
            # todo: bigggg bug fixes
            if collide_x + 2 < self.xpos + self.width < \
                    collide_x + collide_width + self.width - 2:
                self.enable_gravity = False
                self.jump_ability = True
                self.gravity_counter = self.max_gravity
                print("huh")

            print(collide_y, collide_height, self.height, self.ypos)
            # Bottom Platform Collision
            # Todo: separate into own function later: collision_bottom
            if collide_x - collide_width < self.xpos + 2 and \
                    self.xpos + self.width < \
                    collide_x + collide_width + 2 and \
                    collide_y + collide_height <= self.ypos + 2:
                print("Gravy")
                self.ypos += 0.5
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
                    (collide_y < self.ypos + self.height - 1.5) and \
                    (self.ypos < collide_y + collide_height - 1.5) and \
                    self.direction == "right" and \
                    self.xpos + self.width <= collide_x + 2:
                self.direction = "left"

            if collide_id != -1 and \
                    (collide_y < self.ypos + self.height - 1.5) and \
                    (self.ypos < collide_y + collide_height - 1.5) and \
                    self.direction == "left" and \
                    collide_x + collide_width - 2 <= self.xpos:
                self.direction = "right"

    def gravity(self):
        if self.enable_gravity and not self.jump_ability:
            self.ypos += (self.gravity_counter ** 2) * 0.00004

        if self.gravity_counter < 1100:
            self.gravity_counter += 2

        self.ypos = round(self.ypos)

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
