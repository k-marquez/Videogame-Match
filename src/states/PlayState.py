"""
ISPPJ1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""
from typing import Dict, Any, List, Set

import pygame

from gale.input_handler import InputHandler, InputData
from gale.state_machine import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Tile import Tile


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1

        self.highlighted_tile = False

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

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

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

        InputHandler.register_listener(self)

    def exit(self) -> None:
        InputHandler.unregister_listener(self)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.highlighted_tile:
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
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

    def on_input(self, input_id: str, input_data: InputData) -> None:
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
                    di, dj = self.__get_index_delta(i, j, self.highlighted_i1, self.highlighted_j1)
                    tile1 = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
                    
                    # Valid movement
                    if di != dj:
                        self.active = False
                        tile2 = self.board.tiles[i][j]

                        self.__swap_tiles(tile1, tile2)

                        matches = self.__get_matches([tile1, tile2])

                        # Swap tiles
                        if matches is not None:                            
                            Timer.tween(
                                0.25,
                                [
                                    (tile1, {"x": tile2.x, "y": tile2.y}),
                                    (tile2, {"x": self.highlighted_j1 * settings.TILE_SIZE,
                                            "y": self.highlighted_i1 * settings.TILE_SIZE}),
                                ],
                                on_finish=lambda: self.__solve_matches(matches),
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
                    # Invalid movement
                    else:
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
            if  (di != dj) or (di == 0 and dj == 0):
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
    def __get_index_delta(self, i1: int, j1: int, i2:int, j2:int) -> tuple[int, int]:
        di = abs(i1 - i2)
        dj = abs(j1 - j2)
        return di, dj
    
    def __reset_input(self) -> None:
        self.active = True
        self.highlighted_tile = False
    
    def __swap_tiles(self, tile1: Tile, tile2: Tile) -> None:
        (self.board.tiles[tile1.i][tile1.j], self.board.tiles[tile2.i][tile2.j],) = (
            self.board.tiles[tile2.i][tile2.j],
            self.board.tiles[tile1.i][tile1.j],
        )
        tile1.i, tile1.j, tile2.i, tile2.j = ( tile2.i, tile2.j, tile1.i, tile1.j,)
    
    def __to_virtual_pos(self, input_data: InputData) -> tuple[int, int]:
        pos_x, pos_y = input_data.position
        pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH - self.board.x
        pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT - self.board.y
        
        return pos_x, pos_y

    def __to_index(self, x: int, y: int)-> tuple[int, int]:
        i = y // settings.TILE_SIZE
        j = x // settings.TILE_SIZE

        return i, j

    def __get_matches(self, tiles: List) -> Set[Tile]:
        return self.board.calculate_matches_for(tiles)
    
    def __solve_matches(self, matches: Set[Tile]) -> None:
        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()
        
        def recal_matches():
            matches = self.__get_matches([item[0] for item in falling_tiles])
            if matches is not None:
                self.__solve_matches(matches)

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=recal_matches,
        )
