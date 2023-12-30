import pygame
import kog_levels as koglevels
import kog_class as kogclass


class Program:
    """
    Class responsible for how the game runs
    """
    def __init__(self, width, height) -> None:
        self.running = True     # Determines if the game is running
        self.memory = kogclass.Memory(width / 1080, height / 576)     # Initialize game memory
        self.memory.load_all_levels()   # Load all levels from different files
        self.memory.init_replays()
        self.memory.load_save()
        self.memory.music = kogclass.Music(self.memory.total_music_per)

    def run(self, width, height, current_scene):
        """
        Where the actual game loop is running.
        Everything game related is defined in scene.
        Scene is initialized by running Program (in main
        which is outer scope) with the screen size and scene.
        At this point in time, scene is run as MenuScene.

        Everything relating to calling the scene is called here, such as
        input, update, and render while the game is running.

        If the game isn't running, then in the final loop (or the loop when
        the game is told to close by various means), self.running is set to
        false and the scene is changed to nothing. Then the game is safe to
        close.

        This is also where inputs are collected before they are sent to
        the inputs for scene.

        Finally, this is where FPS is set and where the display is updated.
        """
        self.memory.screen = pygame.display.set_mode([width, height])   # Set screen size

        pygame.scrap.init()
        if not pygame.scrap.get_init():
            raise Exception("pygame.scrap is no longer supported :(")

        # Put the resolution ratio into memory, where 1080 and 576 are the min

        scene = current_scene   # Set scene currently shown through a parameter
        # Start game loop
        while self.running:
            keys_pressed = []   # Keys pressed/tapped (key press)
            keys_held = pygame.key.get_pressed()    # Keys held collected
            for event in pygame.event.get():    # Collect all key presses
                # Quit condition if you press the X on the top right
                if event.type == pygame.QUIT:
                    self.memory.write_save()
                    self.running = False    # Stop running this loop
                    pygame.mixer.music.stop()   # Stop the music
                    scene.run_scene = False     # Tell scene to stop running
                # If player does a keypress, append to our list for key presses
                if event.type == pygame.KEYDOWN:
                    keys_pressed.append(event.key)

                if event.type == self.memory.music.end:
                    self.memory.music.switch_music()

            # Stop the game using other conditions (running, but scene says off)
            if self.running and not scene.run_scene:
                self.memory.write_save()
                self.running = False    # Stop running this loop
                pygame.mixer.music.stop()   # Stop the music
                scene.close_game()      # Tell scene to shut off
            else:
                # Functional game loop

                scene.input(keys_pressed, keys_held)    # Call to use keys in
                scene.update()  # Call to dynamically use/update/check changes
                scene.render(self.memory.screen)    # Visually render desired graphics
                scene = scene.this_scene
                """This line is important to allow changing scenes (if 
                this_scene is different like using 
                scene.change_scene(next_scene). Otherwise, scene will not be 
                changed and will continue being this scene (same memory
                address, no change)."""

                if 0 != scene.level_id:
                    self.memory.music.transition_music()

            fps.tick(120)   # 120 frames per second
            pygame.display.update()     # Update the visual output dynamically


if __name__ == "__main__":
    pygame.init()   # Initialize pygame
    pygame.mixer.init()  # Initialize pygame's sound

    fps = pygame.time.Clock()   # Initialize the frame rate

    # Alter these values to change the resolution
    game_width = 1080
    game_height = 576

    file_path = "assets/images/window_icon"
    pygame.display.set_caption("Keep On Going") # game window caption
    icon = pygame.image.load(file_path + "rect10.png") # loading image
    default_icon_image_size = (32, 32) # reducing size of image
    icon = pygame.transform.scale(icon, default_icon_image_size)
    # scaling image correctly
    pygame.display.set_icon(icon) # game window icon

    start_game = Program(game_width, game_height)
    # Initialize running the game with Program

    # Start game in Menu if continuing, else go to first tutorial level
    if 0 < len(start_game.memory.level_progress):
        start_scene = koglevels.MenuScene(24, 303, start_game.memory)
    else:
        start_game.memory.hub_index = 0
        start_scene = koglevels.PlayLevel(start_game.memory.level_set[1][0],
                                          start_game.memory.level_set[1][1],
                                          start_game.memory, 1)
    # Initialize the first scene/starting scene shown to the player
    start_game.run(game_width, game_height, start_scene)  # Run the game loop
    """The game loop will be stuck at this line (start_game.run) until the
    while loop (while self.running:) is no longer true. When self.running is
    False, the program will move onto the next line to quit"""

    pygame.quit()   # Quit the game/pygame instance
