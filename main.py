#!/usr/bin/env python3
"""
Farming Simulation Game - Main Entry Point
A 2D grid-based farming simulation with educational agricultural management.
"""

import sys
import pygame
from scripts.core.game_manager import GameManager


def main():
    """Main game entry point"""
    try:
        # Initialize Pygame
        pygame.init()
        
        # Create and run game manager
        game = GameManager()
        game.run()
        
    except Exception as e:
        print(f"Game crashed with error: {e}")
        sys.exit(1)
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()