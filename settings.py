"""
ISPPJ1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

Author: Kevin Márquez
marquezberriosk@gmail.com

Author: Lewis Ochoa
lewis8a@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, sounds,
textures, frames, and fonts.
"""
from pathlib import Path

import pygame

from gale import input_handler

from src.frames_utility import generate_tile_frames

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "down")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "click")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_3, "click3")
input_handler.InputHandler.set_mouse_motion_action(input_handler.MOUSE_MOTION_UP, "mouse_motion")
input_handler.InputHandler.set_mouse_motion_action(input_handler.MOUSE_MOTION_LEFT, "mouse_motion")
input_handler.InputHandler.set_mouse_motion_action(input_handler.MOUSE_MOTION_RIGHT, "mouse_motion")
input_handler.InputHandler.set_mouse_motion_action(input_handler.MOUSE_MOTION_DOWN, "mouse_motion")

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 570

VIRTUAL_WIDTH = 512
VIRTUAL_HEIGHT = 288

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

TILE_SIZE = 32

NUM_VARIETIES = 1
NUM_COLORS = 18

BACKGROUND_SCROLL_SPEED = 40
BACKGROUND_LOOPING_POINT = -1024 + VIRTUAL_WIDTH - 4 + 51

LEVEL_TIME = 60
HINT_TIME = 5

GOAL_SCORE = 1000

BASE_DIR = Path(__file__).parent

TEXTURES = {
    "background": pygame.image.load(BASE_DIR / "graphics" / "background.png"),
    "tiles": pygame.image.load(BASE_DIR / "graphics" / "match3.png"),
}

FRAMES = {"tiles": generate_tile_frames(TEXTURES["tiles"])}

pygame.mixer.init()

SOUNDS = {
    "clock": pygame.mixer.Sound(BASE_DIR / "sounds" / "clock.wav"),
    "error": pygame.mixer.Sound(BASE_DIR / "sounds" / "error.wav"),
    "game-over": pygame.mixer.Sound(BASE_DIR / "sounds" / "game-over.wav"),
    "match": pygame.mixer.Sound(BASE_DIR / "sounds" / "match.wav"),
    "next-level": pygame.mixer.Sound(BASE_DIR / "sounds" / "next-level.wav"),
    "select": pygame.mixer.Sound(BASE_DIR / "sounds" / "select.wav"),
    "powerup1": pygame.mixer.Sound(BASE_DIR / "sounds" / "powerup1.wav"),
    "powerup2": pygame.mixer.Sound(BASE_DIR / "sounds" / "powerup2.wav"),
    "explosion": pygame.mixer.Sound(BASE_DIR / "sounds" / "explosion.wav"),
    "board": pygame.mixer.Sound(BASE_DIR / "sounds" / "board.wav"),
}

pygame.mixer.music.load(BASE_DIR / "sounds" / "music.mp3")

pygame.font.init()

FONTS = {
    "small": pygame.font.Font(BASE_DIR / "fonts" / "font.ttf", 12),
    "medium": pygame.font.Font(BASE_DIR / "fonts" / "font.ttf", 24),
    "large": pygame.font.Font(BASE_DIR / "fonts" / "font.ttf", 48),
    "huge": pygame.font.Font(BASE_DIR / "fonts" / "font.ttf", 64),
}

CUSTOM_SETTINGS = {
    "goal-score": GOAL_SCORE,
    "level-time": LEVEL_TIME,
    "num-colors": NUM_COLORS
}