"""
ISPPJ1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

Author: Kevin Márquez
marquezberriosk@gmail.com

Author: Lewis Ochoa
lewis8a@gmail.com

This file contains the class NewBoardState.
"""
from typing import Dict, Any

import pygame

from gale.state_machine import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Board import Board

class NewBoardState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        settings.SOUNDS["board"].stop()
        settings.SOUNDS["board"].play()

        self.transition_alpha = 255
        self.level_label_y = -100
        self.level = enter_params["level"]
        self.score = enter_params["score"]
        
        self.timer = enter_params["timer"]

        # New Board
        self.board = Board(settings.VIRTUAL_WIDTH - 272, 16)
        
        # A surface that supports alpha for the screen
        self.screen_alpha_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

        # first, over a period of 1 second, transition out alpha to 0
        # (fade-in).
        Timer.tween(
            1,
            [(self, {"transition_alpha": 0})],
            # once that is finished, start a transition of our text label to
            # center of the screen over 0.25 seconds
            on_finish=lambda: Timer.tween(
                0.25,
                [(self, {"level_label_y": settings.VIRTUAL_HEIGHT // 2 - 30})],
                # after that, pause for 1.5 second with Timer.after
                on_finish=lambda: Timer.after(
                    1.5,
                    # Then, animate the label going down past the bottom edge
                    lambda: Timer.tween(
                        0.25,
                        [(self, {"level_label_y": settings.VIRTUAL_HEIGHT + 30})],
                        # We are ready to play
                        on_finish=lambda: self.state_machine.change(
                            "play",
                            level=self.level,
                            board=self.board,
                            score=self.score,
                            timer=self.timer,
                        ),
                    ),
                ),
            ),
        )

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        render_text(
            surface,
            "Ups!",
            settings.FONTS["large"],
            8,
            self.level_label_y,
            (255, 255, 255),
            shadowed=True,
        )
    
        render_text(
            surface,
            "There isn't moves",
            settings.FONTS["small-medium"],
            8,
            self.level_label_y + 45,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            surface,
            "Generating a new board",
            settings.FONTS["small-medium"],
            8,
            self.level_label_y + 70,
            (255, 255, 255),
            shadowed=True,
        )

        # our transition foregorund rectangle
        pygame.draw.rect(
            self.screen_alpha_surface,
            (255, 255, 255, self.transition_alpha),
            pygame.Rect(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT),
        )
        surface.blit(self.screen_alpha_surface, (0, 0))