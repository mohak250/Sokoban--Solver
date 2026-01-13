from typing import List, Optional, Tuple
from queue import PriorityQueue, Queue
from collections import deque
import time
from game_engine import GameState, Direction

class AStarSearch:
    """A* search with improved heuristics and generous limits"""
    def search(self, initial_state: GameState, max_time: float, difficulty: str = "medium") -> Optional[List[Direction]]:
        start_time = time.time()
        # Much more generous node limits
        if difficulty == "easy":
            max_nodes = 30000
        elif difficulty == "medium":
            max_nodes = 50000
        else:  # hard
            max_nodes = 100000  # Very generous for hard puzzles

        pq = PriorityQueue()
        initial_h = self._heuristic(initial_state)
        counter = 0
        pq.put((initial_h, counter, initial_state, 0, []))
        visited = set()
        visited.add(initial_state._get_state_hash())
        nodes_explored = 0
        best_state = None
        best_heuristic = float('inf')
        best_path = []

        while not pq.empty():
            # More generous timeout
            if time.time() - start_time > max_time:
                # Return best partial solution found
                if best_path:
                    print(f"⏱️ A* timeout - using best path found ({len(best_path)} moves)")
                    return best_path
                print(f"⏱️ A* timeout after {nodes_explored} nodes")
                return None

            f_score, _, current_state, g_score, path = pq.get()
            nodes_explored += 1

            # Track best state for fallback
            current_h = self._heuristic(current_state)
            if current_h < best_heuristic and len(path) > 0:
                best_heuristic = current_h
                best_state = current_state
                best_path = path

            if current_state.is_solved():
                print(f"✅ A* solved: {len(path)} moves, {nodes_explored} nodes")
                return path

            # Explore all directions
            for direction in Direction:
                new_state = current_state.clone()
                if new_state.move(direction):
                    state_hash = new_state._get_state_hash()
                    if state_hash not in visited:
                        visited.add(state_hash)
                        new_g = g_score + 1
                        new_h = self._heuristic(new_state)
                        new_f = new_g + new_h
                        new_path = path + [direction]
                        counter += 1
                        pq.put((new_f, counter, new_state, new_g, new_path))

            if nodes_explored >= max_nodes:
                # Return best partial solution
                if best_path:
                    print(f"🔄 A* node limit - using best path ({len(best_path)} moves)")
                    return best_path
                print(f"🛑 A* node limit: {nodes_explored} nodes")
                break

        # Fallback: return best path found
        if best_path:
            print(f"💡 Returning best path found: {len(best_path)} moves")
            return best_path
        return None

    def _heuristic(self, state: GameState) -> float:
        """Improved heuristic that's never too optimistic"""
        if state.is_solved():
            return 0

        total = 0
        crates = list(state.crate_positions)
        targets = list(state.targets)
        unsolved = [c for c in crates if c not in state.targets]
        if not unsolved:
            return 0

        # Simple Manhattan distance sum
        for crate in unsolved:
            min_dist = min(
                abs(crate[0] - t[0]) + abs(crate[1] - t[1])
                for t in targets
            )
            total += min_dist

        # Heavy penalty for obvious deadlocks
        for crate in unsolved:
            if self._is_corner_deadlock(state, crate):
                total += 500

        return total

    def _is_corner_deadlock(self, state: GameState, pos: Tuple[int, int]) -> bool:
        """Simple corner deadlock check"""
        x, y = pos
        # Check if blocked horizontally and vertically
        left_wall = (x == 0 or state.grid[y][x-1].value == 1)
        right_wall = (x == state.width-1 or state.grid[y][x+1].value == 1)
        top_wall = (y == 0 or state.grid[y-1][x].value == 1)
        bottom_wall = (y == state.height-1 or state.grid[y+1][x].value == 1)

        # If in corner (walls on two adjacent sides), it's a deadlock
        if (left_wall or right_wall) and (top_wall or bottom_wall):
            return True
        return False

class BFSSearch:
    """BFS with much more generous limits"""
    def search(self, initial_state: GameState, max_time: float, difficulty: str = "medium") -> Optional[List[Direction]]:
        start_time = time.time()
        # More generous limits
        if difficulty == "easy":
            max_nodes = 20000
        elif difficulty == "medium":
            max_nodes = 40000
        else:
            max_nodes = 80000

        queue = Queue()
        queue.put((initial_state, []))
        visited = set()
        visited.add(initial_state._get_state_hash())
        nodes_explored = 0
        best_path = []

        while not queue.empty():
            if time.time() - start_time > max_time:
                if best_path:
                    print(f"⏱️ BFS timeout - using best path ({len(best_path)} moves)")
                    return best_path
                print(f"⏱️ BFS timeout after {nodes_explored} nodes")
                return None

            current_state, path = queue.get()
            nodes_explored += 1

            # Keep track of any progress
            if len(path) > len(best_path) and len(path) < 100:
                best_path = path

            if current_state.is_solved():
                print(f"✅ BFS solved: {len(path)} moves, {nodes_explored} nodes")
                return path

            for direction in Direction:
                new_state = current_state.clone()
                if new_state.move(direction):
                    state_hash = new_state._get_state_hash()
                    if state_hash not in visited:
                        visited.add(state_hash)
                        new_path = path + [direction]
                        queue.put((new_state, new_path))

            if nodes_explored >= max_nodes:
                if best_path:
                    print(f"🔄 BFS node limit - using progress made")
                    return best_path
                print(f"🛑 BFS node limit: {nodes_explored} nodes")
                break

        return None

class DFSSearch:
    """DFS with iterative deepening"""
    def search(self, initial_state: GameState, max_time: float, difficulty: str = "medium") -> Optional[List[Direction]]:
        start_time = time.time()
        # Depth limits by difficulty
        if difficulty == "easy":
            max_depth = 50
            max_nodes = 20000
        elif difficulty == "medium":
            max_depth = 80
            max_nodes = 40000
        else:
            max_depth = 120
            max_nodes = 80000

        stack = deque()
        stack.append((initial_state, [], 0))
        visited = set()
        visited.add(initial_state._get_state_hash())
        nodes_explored = 0
        best_path = []

        while stack:
            if time.time() - start_time > max_time:
                if best_path:
                    print(f"⏱️ DFS timeout - using best path ({len(best_path)} moves)")
                    return best_path
                print(f"⏱️ DFS timeout after {nodes_explored} nodes")
                return None

            current_state, path, depth = stack.pop()
            nodes_explored += 1

            if len(path) > len(best_path) and len(path) < 100:
                best_path = path

            if current_state.is_solved():
                print(f"✅ DFS solved: {len(path)} moves, {nodes_explored} nodes")
                return path

            if depth >= max_depth:
                continue

            for direction in Direction:
                new_state = current_state.clone()
                if new_state.move(direction):
                    state_hash = new_state._get_state_hash()
                    if state_hash not in visited:
                        visited.add(state_hash)
                        new_path = path + [direction]
                        stack.append((new_state, new_path, depth + 1))

            if nodes_explored >= max_nodes:
                if best_path:
                    print(f"🔄 DFS node limit - using progress made")
                    return best_path
                print(f"🛑 DFS node limit: {nodes_explored} nodes")
                break

        return None

class SimpleGreedyFallback:
    """Simple greedy strategy as last resort"""
    def get_next_move(self, state: GameState) -> Optional[Direction]:
        """Get a single greedy move toward nearest unsolved crate"""
        unsolved_crates = [c for c in state.crate_positions if c not in state.targets]
        if not unsolved_crates:
            return None

        # Find nearest unsolved crate
        player_pos = state.player_pos
        nearest_crate = min(
            unsolved_crates,
            key=lambda c: abs(c[0] - player_pos[0]) + abs(c[1] - player_pos[1])
        )

        # Try to move toward it
        dx = nearest_crate[0] - player_pos[0]
        dy = nearest_crate[1] - player_pos[1]

        # Try moves in order of preference
        moves_to_try = []
        if abs(dy) > abs(dx):  # Vertical distance larger
            if dy > 0:
                moves_to_try.append(Direction.DOWN)
            else:
                moves_to_try.append(Direction.UP)
            if dx > 0:
                moves_to_try.append(Direction.RIGHT)
            elif dx < 0:
                moves_to_try.append(Direction.LEFT)
        else:  # Horizontal distance larger
            if dx > 0:
                moves_to_try.append(Direction.RIGHT)
            else:
                moves_to_try.append(Direction.LEFT)
            if dy > 0:
                moves_to_try.append(Direction.DOWN)
            elif dy < 0:
                moves_to_try.append(Direction.UP)

        # Add remaining directions
        for d in Direction:
            if d not in moves_to_try:
                moves_to_try.append(d)

        # Try each move
        for direction in moves_to_try:
            test_state = state.clone()
            if test_state.move(direction):
                return direction

        return None

class AIController:
    """Enhanced AI controller with fallback strategies"""
    def __init__(self, algorithm: str = "astar", difficulty: str = "medium"):
        self.algorithm_name = algorithm.lower()
        self.difficulty = difficulty.lower()

        # Create algorithm instance
        if self.algorithm_name == "astar":
            self.search_algorithm = AStarSearch()
        elif self.algorithm_name == "bfs":
            self.search_algorithm = BFSSearch()
        elif self.algorithm_name == "dfs":
            self.search_algorithm = DFSSearch()
        else:
            self.search_algorithm = AStarSearch()
            self.algorithm_name = "astar"

        # Greedy fallback
        self.greedy_fallback = SimpleGreedyFallback()

        # Much more generous search times
        self.search_times = {
            "easy": 5.0,  # 5 seconds
            "medium": 8.0,  # 8 seconds
            "hard": 12.0  # 12 seconds (very generous)
        }

        self.solution_path = []
        self.current_step = 0
        self.is_thinking = False
        self.using_fallback = False
        print(f"🤖 AI ready: {self.algorithm_name.upper()}, {self.difficulty.upper()}")

    def compute_solution(self, game_state: GameState) -> bool:
        """Compute solution - ALWAYS returns True (never fails)"""
        if self.is_thinking:
            return True

        self.is_thinking = True
        self.using_fallback = False
        print(f"🤔 AI computing solution ({self.algorithm_name.upper()})...")

        max_time = self.search_times.get(self.difficulty, 8.0)
        solution = self.search_algorithm.search(game_state, max_time, self.difficulty)

        self.is_thinking = False

        if solution and len(solution) > 0:
            self.solution_path = solution
            self.current_step = 0
            print(f"💡 AI found path with {len(solution)} moves")
            return True
        else:
            # FALLBACK: Use greedy strategy
            print(f"⚠️ Search incomplete - using greedy fallback")
            self.using_fallback = True
            self.solution_path = []
            self.current_step = 0
            return True  # Never fail!

    def get_next_move(self, game_state: GameState) -> Optional[Direction]:
        """Get next move - uses fallback if needed"""
        if self.using_fallback:
            # Recompute greedy move each time
            return self.greedy_fallback.get_next_move(game_state)

        if self.current_step < len(self.solution_path):
            move = self.solution_path[self.current_step]
            self.current_step += 1
            return move

        return None

    def has_solution(self) -> bool:
        """Check if AI has moves ready"""
        if self.using_fallback:
            return True  # Always has greedy moves
        return len(self.solution_path) > 0 and self.current_step < len(self.solution_path)

    def reset(self):
        """Reset AI state"""
        self.solution_path = []
        self.current_step = 0
        self.is_thinking = False
        self.using_fallback = False