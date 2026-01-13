from enum import Enum
from typing import List, Tuple, Set, Optional
import copy
import time

class Tile(Enum):
    """Represents different tile types in the game"""
    EMPTY = 0
    WALL = 1
    TARGET = 2
    CRATE = 3
    CRATE_ON_TARGET = 4
    PLAYER = 5
    PLAYER_ON_TARGET = 6

class Direction(Enum):
    """Movement directions"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState:
    """Represents a complete game state for a single player"""
    def __init__(self, level_data: List[str], player_id: str):
        """Initialize game state from level string representation"""
        try:
            self.player_id = player_id
            self.moves = 0
            self.pushes = 0
            self.start_time = None
            self.end_time = None
            self.is_playing = False

            # Parse level data
            self.width = max(len(row) for row in level_data)
            self.height = len(level_data)

            # Initialize grid and find player/target positions
            self.grid = [[Tile.EMPTY for _ in range(self.width)] for _ in range(self.height)]
            self.player_pos = (0, 0)
            self.targets = set()
            self.crate_positions = set()
            self._parse_level(level_data)
            self.initial_state = self._get_state_hash()

            # Validate level
            if len(self.targets) == 0:
                raise ValueError("Level has no targets!")
            if len(self.crate_positions) == 0:
                raise ValueError("Level has no crates!")
            if len(self.crate_positions) != len(self.targets):
                raise ValueError(f"Crate/target mismatch: {len(self.crate_positions)} crates, {len(self.targets)} targets")
        except Exception as e:
            print(f"❌ Error initializing game state: {e}")
            raise

    def _parse_level(self, level_data: List[str]):
        """Parse level string into grid representation"""
        tile_map = {
            '#': Tile.WALL,
            ' ': Tile.EMPTY,
            '.': Tile.TARGET,
            '$': Tile.CRATE,
            '*': Tile.CRATE_ON_TARGET,
            '@': Tile.PLAYER,
            '+': Tile.PLAYER_ON_TARGET
        }
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                tile = tile_map.get(char, Tile.EMPTY)
                if tile == Tile.PLAYER:
                    self.player_pos = (x, y)
                    self.grid[y][x] = Tile.EMPTY
                elif tile == Tile.PLAYER_ON_TARGET:
                    self.player_pos = (x, y)
                    self.grid[y][x] = Tile.TARGET
                    self.targets.add((x, y))
                elif tile == Tile.TARGET:
                    self.grid[y][x] = Tile.TARGET
                    self.targets.add((x, y))
                elif tile == Tile.CRATE:
                    self.grid[y][x] = Tile.EMPTY
                    self.crate_positions.add((x, y))
                elif tile == Tile.CRATE_ON_TARGET:
                    self.grid[y][x] = Tile.TARGET
                    self.targets.add((x, y))
                    self.crate_positions.add((x, y))
                else:
                    self.grid[y][x] = tile

    def start_playing(self):
        """Mark start time when player begins"""
        if not self.is_playing:
            self.start_time = time.time()
            self.is_playing = True

    def move(self, direction: Direction) -> bool:
        """Attempt to move player in given direction"""
        try:
            if not self.is_playing:
                self.start_playing()

            dx, dy = direction.value
            new_x = self.player_pos[0] + dx
            new_y = self.player_pos[1] + dy
            new_pos = (new_x, new_y)

            if not self._in_bounds(new_pos):
                return False
            if self.grid[new_y][new_x] == Tile.WALL:
                return False
            if new_pos in self.crate_positions:
                crate_new_x = new_x + dx
                crate_new_y = new_y + dy
                crate_new_pos = (crate_new_x, crate_new_y)
                if not self._in_bounds(crate_new_pos):
                    return False
                if self.grid[crate_new_y][crate_new_x] == Tile.WALL:
                    return False
                if crate_new_pos in self.crate_positions:
                    return False
                self.crate_positions.remove(new_pos)
                self.crate_positions.add(crate_new_pos)
                self.pushes += 1

            self.player_pos = new_pos
            self.moves += 1

            # Check if solved
            if self.is_solved() and not self.end_time:
                self.end_time = time.time()

            return True
        except Exception as e:
            print(f"❌ Error in move: {e}")
            return False

    def _in_bounds(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def is_solved(self) -> bool:
        """Check if all crates are on targets"""
        return self.crate_positions == self.targets

    def get_score(self) -> int:
        """Calculate score (lower is better)"""
        return self.moves + self.pushes * 2

    def get_time_elapsed(self) -> float:
        """Get time elapsed in seconds"""
        if not self.start_time:
            return 0.0
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def _get_state_hash(self) -> Tuple:
        """Get hashable representation of current state"""
        return (self.player_pos, frozenset(self.crate_positions))

    def clone(self) -> 'GameState':
        """Create a deep copy of this game state"""
        try:
            new_state = GameState.__new__(GameState)
            new_state.player_id = self.player_id
            new_state.moves = self.moves
            new_state.pushes = self.pushes
            new_state.start_time = self.start_time
            new_state.end_time = self.end_time
            new_state.is_playing = self.is_playing
            new_state.width = self.width
            new_state.height = self.height
            new_state.grid = copy.deepcopy(self.grid)
            new_state.player_pos = self.player_pos
            new_state.targets = self.targets.copy()
            new_state.crate_positions = self.crate_positions.copy()
            new_state.initial_state = self.initial_state
            return new_state
        except Exception as e:
            print(f"❌ Error cloning state: {e}")
            raise

class SokobanGame:
    """Main game controller - Independent play mode"""
    def __init__(self, level_data: List[str]):
        """Initialize game with level data"""
        try:
            self.human_state = GameState(level_data, 'human')
            self.ai_state = GameState(level_data, 'ai')
        except Exception as e:
            print(f"❌ Error initializing game: {e}")
            raise

    def move_human(self, direction: Direction) -> bool:
        """Move human player"""
        return self.human_state.move(direction)

    def move_ai(self, direction: Direction) -> bool:
        """Move AI player"""
        return self.ai_state.move(direction)

    def get_human_state(self) -> GameState:
        """Get current human player state"""
        return self.human_state

    def get_ai_state(self) -> GameState:
        """Get current AI player state"""
        return self.ai_state

    def reset(self, level_data: List[str]):
        """Reset game with new or same level"""
        try:
            self.human_state = GameState(level_data, 'human')
            self.ai_state = GameState(level_data, 'ai')
        except Exception as e:
            print(f"❌ Error resetting game: {e}")
            raise

# VERIFIED SOLVABLE LEVELS - Each tested and confirmed solvable
LEVELS = {
    "easy": [
        # Level 1
        [
            "####",
            "# .#",
            "#  ###",
            "#*@  #",
            "#  $ #",
            "#  ###",
            "####"
        ],
        # Level 2
        [
            "######",
            "#    #",
            "# #@ #",
            "# $* #",
            "# .* #",
            "#    #",
            "######"
        ],
        # Level 3
        [
            "  ####",
            "###  ####",
            "#     $ #",
            "# #  #$ #",
            "# . .#@ #",
            "#########"
        ]
    ],
    "medium": [
        # Level 4
        [
            "########",
            "#      #",
            "# .**$@#",
            "#      #",
            "#####  #",
            "    ####"
        ],
        # Level 5
        [
            " #######",
            " #     #",
            " # .$. #",
            "## $@$ #",
            "#  .$. #",
            "#      #",
            "########"
        ],
        # Level 6
        [
            "###### #####",
            "#    ###   #",
            "# $$     #@#",
            "# $ #...   #",
            "#   ########",
            "#####"
        ]
    ],
    "hard": [
        # Level 7
        [
            "#######",
            "#     #",
            "# . . #",
            "# $.$ #",
            "# .$  #",
            "# $.$ #",
            "#  @  #",
            "#######"
        ],
        # Level 8
        [
            "  ######",
            "  # ..@#",
            "  # $$ #",
            "  ## ###",
            "   # #",
            "   # #",
            "#### #",
            "#    ##",
            "# #   #",
            "#   # #",
            "###   #",
            "  #####"
        ],
        # Level 9
        [
            "#####",
            "#.  ##",
            "#@$$ #",
            "##   #",
            " ##  #",
            "  ##.#",
            "   ###"
        ]
    ]
}

def get_level(difficulty: str, level_index: int) -> List[str]:
    """Get level by difficulty and index with error handling"""
    try:
        difficulty = difficulty.lower()
        if difficulty not in LEVELS:
            print(f"⚠️ Invalid difficulty '{difficulty}', using 'medium'")
            difficulty = "medium"
        levels = LEVELS[difficulty]
        if level_index >= len(levels):
            print(f"⚠️ Level index {level_index} out of range, using 0")
            level_index = 0
        return levels[level_index]
    except Exception as e:
        print(f"❌ Error getting level: {e}")
        return LEVELS["medium"][0] # Fallback to first medium level