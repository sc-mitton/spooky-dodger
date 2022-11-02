import time
from abc import ABC, abstractmethod

import pygame
from pygame.locals import MOUSEBUTTONDOWN

PYGWIDGETS_ANIMATION_PLAYING = 'playing'
PYGWIDGETS_ANIMATION_PAUSED = 'paused'
PYGWIDGETS_ANIMATION_STOPPED = 'stopped'


def _loadImageAndConvert(path):
    # Internal function to load an image and convert for putting on screen
    try:
        image = pygame.image.load(path)
    except FileNotFoundError:
        raise FileNotFoundError('Cannot load file: ' + path)

    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()

    return image


class PygWidget(ABC):
    """Base class for all other classes in the module
    |
    Methods:
        The majority of the methods in this class simply
        deal with getting and setting properties for
        instances such as visibility, enableing, and location
        |
        | move_x: move the widget a certain number of pixels in the
            x direction
        | move_y: move the widget a certain number of pixels in the
            y direction
        | move_xy: move the widget a certain number of pixels in the
            x and y directions
        | overlaps_rect: returns true or false if the widget overlaps
            with another rect
        | overlaps_object: returns true or false if the widget overlaps
            with another object
    """

    @abstractmethod
    def __init__(self):
        self.visible = True
        self.is_enabled = True
        self.dependents_list = []
        self.enable_dependents = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.loc = [0, 0]

    def __del__(self):
        self.dependents_list = []

    @property
    def visible(self):
        """Return the visible property"""
        return self._visible

    @visible.setter
    def visible(self, true_or_false):
        """Set the visible property"""
        self._visible = true_or_false

    @property
    def is_enabled(self):
        """Returns the enabled state."""
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, true_or_false):
        """Enables the current widget"""
        self._is_enabled = true_or_false

    def disable(self):
        """Disables the current widget."""
        self.is_enabled = False

    def getRect(self):
        """Returns the rect of this widget."""
        return self.rect

    @property
    def loc(self):
        """Returns the location of this widget as a tuple of values (X,Y) ."""
        return self._loc

    @loc.setter
    def loc(self, loc):   # loc must be a tuple or list of x,y coordinates
        """Sets a new location for this widget.  loc is a tuple of X and Y
            values (X, Y) It also changes the rect of the widget
        Parameter:
            |   loc - a tuple of X,Y coordinates
        """
        self._loc = loc
        self.rect[0] = self.loc[0]
        self.rect[1] = self.loc[1]

    def move_x(self, n_pixels):
        """Move some number of pixels in the X direction
        Parameter:

            |    n_pixels - the new x location
        """

        self.loc = (self.loc[0]+n_pixels, self.loc[1])

    def move_y(self, n_pixels):
        """Move some number of pixels in the Y direction
        Parameter:

            |    n_pixels - new new y location
        """

        self.loc = (self.loc[0], self.loc[1]+n_pixels)

    def move_xy(self, n_pixels_x, n_pixels_y):
        """Move some number of n pixels in the X and Y directions
        Parameter:

            |   n_pixels_x - number of pixels in the x direction
            |   n_pixels_y - number of pixels in the y direction

        """
        self.loc = (self.loc[0]+n_pixels_x, self.loc[1]+n_pixels_y)

    def overlaps_rect(self, otherRect):
        """Returns True if the rect object overlaps another rect
        Parameter:
            |
            |   otherRect - a second rectangle to compare to
        """

        overlaps = self.rect.colliderect(otherRect)
        return overlaps

    def overlaps_object(self, oOther):
        """Returns True if the rect of this object overlaps with rect of
        another pygwidgets object
        |
        Parameters:
            |
            |    oOther - a second object to compare to
        """

        other_rect = oOther.get_rect()
        overlaps = self.rect.colliderect(other_rect)
        return overlaps


class PygAnimation(PygWidget, pygame.sprite.Sprite):
    """Base class for all other animation classes, not meant to be used
    on its own.

    Parameters:
        | window: the main game window surface
        | loc: the location of the animation on the window surface
        | show_first_image_at_end: when the animation is done, the
            first image is shown
        | n_times: how many times the animation loops

    """
    def __init__(self, window, loc, show_first_image_at_end, loop, n_times):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)

        self.window = window
        self.loc = loc
        self.loop = loop
        self.show_first_image_at_end = show_first_image_at_end
        self.n_times = n_times

        self.image = None  # Current frame's image
        self.images_list = []
        self.end_times_list = []
        self.offsets_list = []
        self.index = 0  # Used to index into all three lists
        self.elapsed = 0  # Time that has elapsed in the current animation
        self.n_iterations_left = 0
        self.state = PYGWIDGETS_ANIMATION_STOPPED

    @property
    def loop(self):
        """Returns true or false baised on whether or not the animation is
        looping
        """

        return self._loop

    @loop.setter
    def loop(self, true_or_false):

        """Sets the animation to loop or stop looping"""
        self._loop = true_or_false

    def getRect(self):
        """Get the rectangle for the animation"""
        self.image = self.images_list[self.index]
        if self.image is None:
            return pygame.rect(0, 0, 0, 0)
        else:
            the_rect = self.image.get_rect()
            the_rect.topleft = self.loc
            return the_rect

    def start(self):
        """Starts an animation"""

        if self.state == PYGWIDGETS_ANIMATION_PLAYING:
            pass

        # Restart from beginning of animation
        elif self.state == PYGWIDGETS_ANIMATION_STOPPED:
            self.index = 0  # first image in list
            self.elapsed = 0
            self.playing_start_time = time.time()
            self.elapsed_stop_time = self.end_times_list[-1]
            self.next_elapsed_threshold = self.end_times_list[0]
            self.n_iterations_left = self.n_times  # typically 1

        # Restart where we left off
        elif self.state == PYGWIDGETS_ANIMATION_PAUSED:
            self.playing_start_time = time.time() - self.elapsed_at_paused
            self.elapsed = self.elapsed_at_pause
            self.elapsed_stop_time = self.end_times_list[-1]
            self.next_elapsed_threshold = self.end_times_list[self.index]

        self.state = PYGWIDGETS_ANIMATION_PLAYING
        # Set the current frame to the first image
        self.image = self.images_list[self.index]

    def pause(self):
        """Pauses an animation that is playing"""

        if self.state == PYGWIDGETS_ANIMATION_PLAYING:
            self.elapsed_at_paused = self.elapsed
            # only change state if it was playing
            self.state = PYGWIDGETS_ANIMATION_PAUSED

        elif self.state == PYGWIDGETS_ANIMATION_STOPPED:
            pass  # nothing to do

        elif self.state == PYGWIDGETS_ANIMATION_PAUSED:
            pass  # nothing to do

    def stop(self):
        """Stops an animation that is playing"""

        if self.state == PYGWIDGETS_ANIMATION_STOPPED:
            pass
        if self.state == PYGWIDGETS_ANIMATION_PAUSED:
            pass
        if self.state == PYGWIDGETS_ANIMATION_PLAYING:
            self.index = 0
            self.elapsed = 0

        self.state = PYGWIDGETS_ANIMATION_STOPPED

    def handle_event(self, event_obj):
        """Handles pygame events and changes the state of the animation.
        Returns True if the event is able to be handled.
        """

        if not self.is_enabled:
            return False
        if not self.visiblel:
            return

        if event_obj.type != MOUSEBUTTONDOWN:
            # The animation only cares about MOUSEBUTTONDOWN event
            return False

        event_point_in_animation_rect = self.rect.collidepoint(event_obj.pos)
        if not event_point_in_animation_rect:
            # This means the animation was clicked outside
            return False
        if self.state == PYGWIDGETS_ANIMATION_PLAYING:
            # If playing, ignore the click
            return False

        return True

    def update(self):
        """Update the currently running animation"""

        if self.state != PYGWIDGETS_ANIMATION_PLAYING:
            return False
        return_value = False  # typical return value

        self.elapsed = (time.time() - self.playing_start_time)

        # If we've come to the end of the animation
        if self.elapsed >= self.elapsed_stop_time:

            # Animation is looping
            if self.loop:  # restart the animation
                self.playing_start_time = time.time()
                self.next_elapsed_threshold = self.end_times_list[0]
                self.index = 0
                self.image = self.images_list[self.index]

            # Animation is not looping
            else:
                self.n_iterations_left += -1
                if self.n_iterations_left == 0:  # there are no loops left
                    self.state = PYGWIDGETS_ANIMATION_STOPPED
                    return_value = True  # animation has finished

                else:  # start another loop
                    self.playing_start_time = time.time()
                    self.next_elapsed_threshold = self.end_times_list[0]

            if self.show_first_image_at_end:
                self.index = 0  # show first image
                self.image = self.images_list[self.index]
            else:
                self.index = len(self.images_list) - 1
                self.image = self.images_list[self.index]

        if self.elapsed > self.next_elapsed_threshold:
            if self.index == 0 and self.elapsed >= self.elapsed_stop_time:
                pass
            else:
                self.index += 1
            self.image = self.images_list[self.index]
            self.next_elapsed_threshold = self.end_times_list[self.index]

        return return_value


class SpriteSheetAnimation(PygAnimation):
    """Creates an animation from a sprite sheet

    Parameters:
        | window: the surface to draw the animation on
        | loc: the starting location of the animation
        | sprite_sheet_path: the system path to the sprite sheet
        | n_images: total number of images in the sprite sheet
        | width: the width of the sprite
        | height: the height of the sprite
        | n_times: the number of times to play the animation if
            it isn't looping
        | frame_duration: a list or tuple of duraitons for each frame,
            or an integer specifying the length of all frames
        | loop: set the animation to loop indefinitely
        | show_first_image_at_end: when the animation is done,
            show the first image of the animation
        | flip: a tuple or list that indicates the animation should be flipped
            in the horizontal or verticle direction, or both
        | frame_order = list of the final order of the frames that should
            appear in the animation
        | auto_start: immediately start the animation without
            having to click on it to start the animation
    """

    def __init__(
                self, window, loc, sprite_sheet_path, n_images, width,
                height, frame_duration, frame_order=None, flip=None,
                bak_color=None, loop=False, n_times=1,
                show_first_image_at_end=True, auto_start=True
                ):

        super().__init__(window, loc, show_first_image_at_end, loop, n_times)

        self.sprite_sheet = _loadImageAndConvert(sprite_sheet_path)
        self.rect.width = width
        self.rect.height = height

        # If a durations list is given, then check the length to make sure
        # it matches the number of images in the sprite sheet. If an integer
        # is given for the duration, then the duration for each frame is the
        # same
        if isinstance(frame_duration, tuple) or \
           isinstance(frame_duration, list):
            use_same_duration = False  # this is a list of durations
            if n_images != len(frame_duration):
                raise ValueError('Number of images ' + str(n_images) +
                                 ' and number of duration times ' +
                                 str(len(frame_duration)) +
                                 ' do not match.')
        else:
            use_same_duration = True

        # Split up the sprite sheet into the different images and load them
        # into self.images_list
        row = 0
        col = 0
        end_time = 0
        n_cols = self.sprite_sheet.get_width() // width
        for i in range(n_images):
            x = col*width
            y = row*height

            # Create sub_surface rect
            sub_surface_rect = pygame.Rect(x, y, width, height)
            image = self.sprite_sheet.subsurface(sub_surface_rect)
            if flip:
                image = pygame.transform.flip(image, flip[0], flip[1])
            if bak_color:
                image.set_colorkey(bak_color)

            self.images_list.append(image)
            self.offsets_list.append((0, 0))

            # Add either the set frame duration, or the next frame duration
            # from the passed perameter
            if use_same_duration:
                end_time += round(frame_duration, 3)
                self.end_times_list.append(end_time)
            else:
                end_time += round(frame_duration[i], 3)
                self.end_times_list.append(end_time)

            # Incremenet the column, and go to the next row if needed
            col += 1
            if col == n_cols:
                row += 1
                col = 0

        # Extract the subset of the sprite sheet that should be the final
        # animation
        if frame_order:
            self._extract_frames(frame_order)

        # The animation shouldn't start automatically unless the setting is
        # selected
        self.state = PYGWIDGETS_ANIMATION_STOPPED
        if auto_start:
            self.start()

    def _extract_frames(self, frame_order):
        """Extract the frames of interest from the larger list of images
        extracted from the sprite sheet and trim the end_times_list to same
        size of the list subset
        """

        images_list = []
        end_times_list = []
        offsets_list = []
        for i in frame_order:
            images_list.append(self.images_list[i])
            offsets_list.append(self.offsets_list[i])
        end_times_list = self.end_times_list[:len(frame_order)-1]

        self.images_list = images_list
        self.end_times_list = end_times_list
        self.offsets_list = offsets_list
