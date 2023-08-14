import pygame
import dsn_levels as dsnlevel
import dsn_class as dsnclass


class Program:
    """
    Class responsible for how the game runs
    """
    def __init__(self) -> None:
        self.running = True     # Determines if the game is running
        self.memory = dsnclass.Memory()     # Initialize game memory
        self.memory.load_levels("levels.txt")   # Load levels into memory

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
        screen = pygame.display.set_mode([width, height])   # Set screen size
        scene = current_scene   # Set scene currently shown through a parameter
        while self.running:
            keys_pressed = []   # Keys pressed/tapped (key press)
            keys_held = pygame.key.get_pressed()    # Keys held collected
            for event in pygame.event.get():    # Collect all key presses
                # Quit condition if you press the X on the top right
                if event.type == pygame.QUIT:
                    self.running = False    # Stop running this loop
                    scene.run_scene = False     # Tell scene to stop running
                # If player does a keypress, append to our list for key presses
                if event.type == pygame.KEYDOWN:
                    keys_pressed.append(event.key)

            # Stop the game using other conditions (running, but scene says off)
            if self.running and not scene.run_scene:
                self.running = False    # Stop running this loop
                scene.close_game()      # Tell scene to shut off
            else:
                scene.input(keys_pressed, keys_held)    # Call to use keys in
                scene.update()  # Call to dynamically use/update/check changes
                scene.render(screen)    # Visually render desired graphics
                scene = scene.this_scene
                """This line is important to allow changing scenes (if 
                this_scene is different like using 
                scene.change_scene(next_scene). Otherwise, scene will not be 
                changed and will continue being this scene (same memory
                address, no change)."""

            fps.tick(120)   # 120 frames per second
            pygame.display.update()     # Update the visual output dynamically


if __name__ == "__main__":
    pygame.init()   # Initialize pygame
    pygame.mixer.init() # Initialize pygame's sound
    pygame.display.set_caption("Dont Stop Now")
    # for image import - commented out cuz image doesn't exist yet
    # pygame.display.set_icon("player.png")
    fps = pygame.time.Clock()   # Initialize the frame rate
    start_game = Program()      # Initialize running the game with Program
    start_scene = dsnlevel.MenuScene(40, 360, start_game.memory)
    # Initialize the first scene/starting scene shown to the player
    start_game.run(1080, 576, start_scene)  # Run the game loop
    """The game loop will be stuck at this line (start_game.run) until the
    while loop (while self.running:) is no longer true. When self.running is
    False, the program will move onto the next line to quit"""

    pygame.quit()   # Quit the game/pygame instance
