# Snake(X) - Enhanced Snake Game

Snake(X) is a feature-rich, polished version of the classic Snake game implemented in Python using Pygame. It offers multiple game modes, enhanced visuals, and a robust architecture designed for portability and fun.

## Key Features

- **Multiple Game Modes**: From the classic experience to high-stakes challenges.
- **Enhanced Graphics**: Dynamic food pulse animations, score-based snake color shifting, and screen shake effects for collisions.
- **Score Multiplier**: Rewards quick play! Eat food in quick succession to boost your score multiplier up to 5x.
- **Multiplayer Support**: Play with a friend on the same keyboard.
- **Cross-Platform**: Designed to run seamlessly on Windows, Linux, and macOS.

## Game Modes

1. **Normal Mode**: The classic Snake experience. Grow as long as you can!
2. **Survival Mode**: Avoid bombs that spawn randomly and disappear after a short time.
3. **Walls of Doom**: Navigate through a field of static obstacles. One wrong move and it's game over!
4. **Speed Run**: You have 60 seconds to get the highest score possible.
5. **Multiplayer**: Two snakes, one screen.
   - **Player 1**: Use Arrow Keys
   - **Player 2**: Use W, A, S, D Keys

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Steps
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd snake-game
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**:
   ```bash
   python main.py
   ```

## Technical Improvements

This project underwent a significant refactor to ensure high code quality:
- **Portability**: All hardcoded absolute paths were replaced with base-directory relative paths.
- **Grid Alignment**: Fixed a legacy issue where wrapping could cause the snake to misalign with the grid.
- **Session Management**: Introduced a unified GameSession state to allow for seamless "Resume" functionality.
- **CI/CD Ready**: Configured with a clean .pylintrc and .gitignore, maintaining a 10.0/10 rating on code quality.

## License

Free for all to use! Built by Ahmed Sajid and improved for the community.
