import pygame
import os

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60

IMAGES = {}
SOUNDS = {}
FONTS = {}

def load_image(file, name, alpha=False, colorkey=None):
    """
    Loads an image, prepares it for play, and stores it in the IMAGES dictionary.
    :param file: Path to the image file.
    :param name: Name/key to store the image in the IMAGES dictionary.
    :param alpha: Boolean to indicate if alpha transparency should be used.
    :param colorkey: Color key for transparency. If None, no colorkey is applied. 
                     If -1, the color of the top-left pixel is used.
    """
    try:
        image = pygame.image.load(file)
        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        
        # Store the image in the global IMAGES dictionary
        IMAGES[name] = image
        return image
    except pygame.error as message:
        print('Cannot load image:', file)
        raise SystemExit(message)

def load_sound(file, name):
    """
    Loads a sound file and stores it in the SOUNDS dictionary.
    :param file: Path to the sound file.
    :param name: Name/key to store the sound in the SOUNDS dictionary.
    """
    try:
        sound = pygame.mixer.Sound(file)
        # Store the sound in the global SOUNDS dictionary
        SOUNDS[name] = sound
    except pygame.error as message:
        print('Cannot load sound:', file)
        raise SystemExit(message)
        
def load_font(name, size, is_system_font=False):
    """
    Loads a font and stores it in the FONTS dictionary.
    :param name: Name of the font file or system font.
    :param size: Size of the font.
    :param is_system_font: Boolean, True if loading a system font.
    """
    try:
        if is_system_font:
            font = pygame.font.SysFont(name, size)
        else:
            font = pygame.font.Font(name, size)
        
        if not is_system_font:
            # Use only the base name of the file (without path and extension) for the key
            base_name = os.path.splitext(os.path.basename(name))[0]
            font_key = f"{base_name.lower()}_{size}"
        else:
            # For system fonts, use the name directly
            font_key = f"{name.replace(' ', '_').lower()}_{size}"
    
        FONTS[font_key] = font
    except IOError as e:
        print(f"Cannot load font: {name}, {e}")
        raise SystemExit(e)