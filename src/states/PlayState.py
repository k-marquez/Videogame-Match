"""
ISPPJ1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

Author: Kevin Márquez
marquezberriosk@gmail.com

Author: Lewis Ochoa
lewis8a@gmail.com

This file contains the class PlayState.
"""
from typing import Dict, Any, List, Set, NoReturn, Tuple
from copy import deepcopy

import pygame

from gale.input_handler import InputHandler, InputData
from gale.state_machine import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Tile import Tile
from src.Board import Board

class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> NoReturn:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1

        self.highlighted_tile = False

        self.active = True

        self.timer = settings.CUSTOM_SETTINGS["level-time"]
        self.hint_timer = settings.HINT_TIME
        self.hint_tiles = []

        self.goal_score = self.level * 1.25 * settings.CUSTOM_SETTINGS["goal-score"]

        self.tiles_in_match = []

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to hits tiles
        self.hint_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.hint_alpha_surface,
            (0, 0, 0, 150),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        while not self.can_play():
            delattr(self, "board")
            self.board = Board(settings.VIRTUAL_WIDTH - 272, 16)

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()
        
        Timer.every(1, decrement_timer)
        
        def increment_hint_timer():
            self.hint_timer += 1

        Timer.every(1, increment_hint_timer)

        InputHandler.register_listener(self)

    def exit(self) -> NoReturn:
        InputHandler.unregister_listener(self)

    def update(self, _: float) -> NoReturn:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> NoReturn:
        self.board.render(surface)

        if self.highlighted_tile:
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))

        if self.hint_timer > 10:
            for pos_tile in self.hint_tiles:
                x = pos_tile['x'] + self.board.x
                y = pos_tile['y'] + self.board.y
                if self.timer % 2 == 0:
                    surface.blit(self.hint_alpha_surface, (x, y))
                else:
                    surface.blit(self.tile_alpha_surface, (x, y))

        
        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> NoReturn:
        if not self.active:
            return
        
        if input_id == "click":
            
            pos_x, pos_y = self.__to_virtual_pos(input_data)
            i, j = self.__to_index(pos_x, pos_y)

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j <= settings.BOARD_WIDTH:
                if input_data.pressed and not self.highlighted_tile:
                    self.highlighted_tile = True
                    self.highlighted_i1 = i
                    self.highlighted_j1 = j
               
                elif input_data.released and self.highlighted_tile:
                    tile1 = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
                    
                    # Valid movement
                    self.active = False
                    tile2 = self.board.tiles[i][j]
                    self.__swap_tiles(tile1, tile2)
                    matches = self.__get_matches([tile1, tile2])
                    
                    def before_matched():
                        self.tiles_in_match = []
                        self.tiles_in_match.append(tile1)
                        self.tiles_in_match.append(tile2)
                        self.__solve_matches(matches)
                    
                    # Swap tiles
                    if matches is not None:
                        self.hint_tiles = []
                        self.hint_timer = 0
                        Timer.tween(
                            0.25,
                            [
                                (tile1, {"x": tile2.x, "y": tile2.y}),
                                (tile2, {"x": self.highlighted_j1 * settings.TILE_SIZE,
                                        "y": self.highlighted_i1 * settings.TILE_SIZE}),
                            ],
                            on_finish=before_matched,
                        )
                    # Get back highlighted tile (No match)
                    else:
                        self.__swap_tiles(tile2, tile1)
                        Timer.tween(
                            0.15,
                            [
                                (tile1, {"x": self.highlighted_j1 * settings.TILE_SIZE,
                                         "y": self.highlighted_i1 * settings.TILE_SIZE,}
                                ),
                            ],
                        )
                    # Reset on input for acepting entries
                    self.__reset_input()                         
                
        # Draggin tile selected
        elif input_id == "mouse_motion" and self.highlighted_tile:
            pos_x, pos_y = self.__to_virtual_pos(input_data)
            i, j = self.__to_index(pos_x, pos_y)
            di , dj = self.__get_index_delta(i,j, self.highlighted_i1, self.highlighted_j1) 
            
            # Valid movement
            if (di < 2 and dj == 0) or (dj < 2 and di == 0):
                self.board.tiles[self.highlighted_i1][self.highlighted_j1].x = pos_x - settings.TILE_SIZE / 2
                self.board.tiles[self.highlighted_i1][self.highlighted_j1].y =  pos_y - settings.TILE_SIZE / 2

            # Invalid movement
            else:
                self.__reset_input()
                tile1 = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
                Timer.tween(
                    0.15,
                    [
                        (tile1, {"x": self.highlighted_j1 * settings.TILE_SIZE,
                                 "y": self.highlighted_i1 * settings.TILE_SIZE,}
                        ),
                    ],
                )
        if input_id == "click3":
            pos_x, pos_y = self.__to_virtual_pos(input_data)
            i, j = self.__to_index(pos_x, pos_y)
            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j <= settings.BOARD_WIDTH and input_data.released:
                if self.board.tiles[i][j].powerup == True:
                    self.hint_tiles = []
                    self.board.tiles[i][j].active = True
                    settings.SOUNDS["explosion"].stop()
                    settings.SOUNDS["explosion"].play()
                    self.board.matches.append([self.board.tiles[i][j]])
                    self.score += self.board.remove_matches() * 50
                    falling_tiles = self.board.get_falling_tiles()

                    def recal_matches():
                        matches = self.__get_matches([item[0] for item in falling_tiles])
                        if matches is not None:
                            self.__solve_matches(matches)
                        
                        # Check if exits almost one move
                        while not self.can_play():
                            delattr(self, "board")
                            # New board if not exits movements
                            self.board = Board(settings.VIRTUAL_WIDTH - 272, 16)
                            # Reboot hint timer
                            self.hint_timer = 0
                            settings.SOUNDS["board"].stop()
                            settings.SOUNDS["board"].play()
                    
                    Timer.tween(
                        0.25,
                        falling_tiles,
                        on_finish=recal_matches,
                    )
    
    def __get_index_delta(self, i1: int, j1: int, i2:int, j2:int) -> Tuple[int, int]:
        di = abs(i1 - i2)
        dj = abs(j1 - j2)
        return di, dj
    
    def __reset_input(self) -> NoReturn:
        self.active = True
        self.highlighted_tile = False
    
    def __swap_tiles(self, tile1: Tile, tile2: Tile) -> NoReturn:
        (self.board.tiles[tile1.i][tile1.j], self.board.tiles[tile2.i][tile2.j],) = (
            self.board.tiles[tile2.i][tile2.j],
            self.board.tiles[tile1.i][tile1.j],
        )
        tile1.i, tile1.j, tile2.i, tile2.j = ( tile2.i, tile2.j, tile1.i, tile1.j,)
    
    def __to_virtual_pos(self, input_data: InputData) -> Tuple[int, int]:
        pos_x, pos_y = input_data.position
        pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH - self.board.x
        pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT - self.board.y
        
        return pos_x, pos_y

    def __to_index(self, x: int, y: int)-> Tuple[int, int]:
        i = y // settings.TILE_SIZE
        j = x // settings.TILE_SIZE

        return i, j

    def __get_matches(self, tiles: List) -> Set[Tile]:
        return self.board.calculate_matches_for(tiles)
    
    def __solve_matches(self, matches: Set[Tile]) -> NoReturn:
        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            size_m = len(match)
            for tile in match:
                if tile.powerup:
                    tile.active = True
            if size_m == 4 and tile.powerup == False:
                if tile == self.tiles_in_match[0]:
                    self.tiles_in_match[0].powerup = True
                    self.tiles_in_match[0].variety = self.tiles_in_match[0].variety + 5
                    self.tiles_in_match[0].type = 1
                    settings.SOUNDS["powerup1"].stop()
                    settings.SOUNDS["powerup1"].play()

                if tile == self.tiles_in_match[1]:
                    self.tiles_in_match[1].powerup = True
                    self.tiles_in_match[1].variety = self.tiles_in_match[1].variety + 5
                    self.tiles_in_match[1].type = 1
                    settings.SOUNDS["powerup1"].stop()
                    settings.SOUNDS["powerup1"].play()

            if size_m >= 5:
                if tile == self.tiles_in_match[0]:
                    self.tiles_in_match[0].powerup = True
                    self.tiles_in_match[0].variety = self.tiles_in_match[0].variety + 1
                    self.tiles_in_match[0].type = 2
                    settings.SOUNDS["powerup2"].stop()
                    settings.SOUNDS["powerup2"].play()

                if tile == self.tiles_in_match[1]:
                    self.tiles_in_match[1].powerup = True
                    self.tiles_in_match[1].variety = self.tiles_in_match[1].variety + 1
                    self.tiles_in_match[1].type = 2
                    settings.SOUNDS["powerup2"].stop()
                    settings.SOUNDS["powerup2"].play()

        self.score += self.board.remove_matches() * 50
        falling_tiles = self.board.get_falling_tiles()

        def recal_matches():
            matches = self.__get_matches([item[0] for item in falling_tiles])
            if matches is not None:
                self.__solve_matches(matches)
            
            # Check if exits almost one move
            while not self.can_play():
                delattr(self, "board")
                # New board if not exits movements
                self.board = Board(settings.VIRTUAL_WIDTH - 272, 16)
                # Reboot hint timer
                self.hint_timer = 0
                settings.SOUNDS["board"].stop()
                settings.SOUNDS["board"].play()
        
        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=recal_matches,
        )

    def can_play(self) -> bool:
        if len(self.hint_tiles) > 0:
            return True
        
        for j in range(settings.BOARD_WIDTH - 1):
            for i in range(settings.BOARD_HEIGHT - 1):
                if self.is_there_movement(i,j):
                    return True

        return False
    
    def is_there_movement(self, i: int, j: int) -> bool:
        return self.__is_there_movement(i,j,1,0) or self.__is_there_movement(i,j,0,1)
    
    def __is_there_movement(self, i: int, j: int, left: int, down: int) -> bool:
        tile1 = self.board.tiles[i][j]
        tile2 = self.board.tiles[i + down][j + left]
        if tile1.powerup:
            self.hint_tiles = [{"x": tile1.x, "y": tile1.y}]
            self.hint_tiles = deepcopy(self.hint_tiles)
            return True
        elif tile2.powerup:
            self.hint_tiles = [{"x": tile2.x, "y": tile2.y}]
            self.hint_tiles = deepcopy(self.hint_tiles)
            return True
            
        self.__swap_tiles(tile1, tile2)
        matches = self.__get_matches([tile1, tile2])
        self.__swap_tiles(tile1, tile2)
        if matches is not None: 
            self.hint_tiles = [{"x": tiles.x, "y": tiles.y} for row in matches for tiles in row]
            self.hint_tiles = deepcopy(self.hint_tiles)
            self.board.matches = []
            return True
        
        return False