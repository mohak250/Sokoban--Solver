"""
Sokoban Frontend - Fixed with proper AI move execution
"""

import pygame
from typing import Tuple, Optional
from game_engine import SokobanGame, Direction, Tile, get_level
from ai_agent import AIController


# Color scheme
COLORS = {
    'background': (25, 30, 40),
    'wall': (60, 70, 85),
    'wall_highlight': (80, 90, 105),
    'wall_shadow': (40, 50, 65),
    'floor': (245, 245, 240),
    'floor_alt': (235, 235, 230),
    'target': (255, 200, 50),
    'target_glow': (255, 220, 100),
    'crate': (160, 82, 45),
    'crate_highlight': (200, 120, 80),
    'crate_shadow': (100, 50, 25),
    'crate_on_target': (50, 150, 50),
    'human': (52, 152, 219),
    'human_outline': (30, 100, 180),
    'ai': (231, 76, 60),
    'ai_outline': (180, 40, 30),
    'text': (255, 255, 255),
    'panel': (35, 40, 50),
    'button': (70, 130, 180),
    'button_hover': (100, 160, 210),
    'button_active': (50, 180, 100),
    'play_button': (50, 200, 100),
    'play_hover': (70, 220, 120),
    'stop_button': (200, 50, 50),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192)
}

TILE_SIZE = 60
FPS = 60
ANIMATION_SPEED = 10


class AnimatedSprite:
    """Smooth sprite animation"""
    
    def __init__(self, x: int, y: int, tile_size: int):
        self.grid_x = x
        self.grid_y = y
        self.tile_size = tile_size
        self.screen_x = x * tile_size
        self.screen_y = y * tile_size
        self.target_x = self.screen_x
        self.target_y = self.screen_y
        self.is_animating = False
    
    def set_target_position(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.target_x = grid_x * self.tile_size
        self.target_y = grid_y * self.tile_size
        self.is_animating = True
    
    def update(self):
        if not self.is_animating:
            return
        
        dx = self.target_x - self.screen_x
        dy = self.target_y - self.screen_y
        
        if abs(dx) > 0:
            move = min(ANIMATION_SPEED, abs(dx)) * (1 if dx > 0 else -1)
            self.screen_x += move
        
        if abs(dy) > 0:
            move = min(ANIMATION_SPEED, abs(dy)) * (1 if dy > 0 else -1)
            self.screen_y += move
        
        if abs(dx) < ANIMATION_SPEED and abs(dy) < ANIMATION_SPEED:
            self.screen_x = self.target_x
            self.screen_y = self.target_y
            self.is_animating = False
    
    def get_screen_pos(self) -> Tuple[int, int]:
        return (int(self.screen_x), int(self.screen_y))


class Button:
    """Interactive button"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font, color_key: str = 'button'):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        self.is_active = False
        self.color_key = color_key
    
    def draw(self, screen: pygame.Surface):
        if self.is_active:
            color = COLORS['button_active']
        elif self.is_hovered:
            color = COLORS.get(f'{self.color_key}_hover', COLORS['button_hover'])
        else:
            color = COLORS[self.color_key]
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['text'], self.rect, 2, border_radius=8)
        
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class GameRenderer:
    """Renders the game boards"""
    
    def __init__(self, screen: pygame.Surface, game: SokobanGame):
        self.screen = screen
        self.game = game
        self.tile_size = TILE_SIZE
        
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 56)
        self.text_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 22)
        
        self._init_sprites()
    
    def _init_sprites(self):
        try:
            human_state = self.game.get_human_state()
            self.human_player = AnimatedSprite(
                human_state.player_pos[0], human_state.player_pos[1], self.tile_size
            )
            self.human_crates = {}
            for crate_pos in human_state.crate_positions:
                self.human_crates[crate_pos] = AnimatedSprite(
                    crate_pos[0], crate_pos[1], self.tile_size
                )
            
            ai_state = self.game.get_ai_state()
            self.ai_player = AnimatedSprite(
                ai_state.player_pos[0], ai_state.player_pos[1], self.tile_size
            )
            self.ai_crates = {}
            for crate_pos in ai_state.crate_positions:
                self.ai_crates[crate_pos] = AnimatedSprite(
                    crate_pos[0], crate_pos[1], self.tile_size
                )
        except Exception as e:
            print(f"❌ Error initializing sprites: {e}")
            raise
    
    def update_sprites(self):
        try:
            human_state = self.game.get_human_state()
            self.human_player.set_target_position(
                human_state.player_pos[0], human_state.player_pos[1]
            )
            
            new_crates = {}
            for crate_pos in human_state.crate_positions:
                if crate_pos in self.human_crates:
                    sprite = self.human_crates[crate_pos]
                    sprite.set_target_position(crate_pos[0], crate_pos[1])
                    new_crates[crate_pos] = sprite
                else:
                    new_crates[crate_pos] = AnimatedSprite(
                        crate_pos[0], crate_pos[1], self.tile_size
                    )
            self.human_crates = new_crates
            
            ai_state = self.game.get_ai_state()
            self.ai_player.set_target_position(
                ai_state.player_pos[0], ai_state.player_pos[1]
            )
            
            new_crates = {}
            for crate_pos in ai_state.crate_positions:
                if crate_pos in self.ai_crates:
                    sprite = self.ai_crates[crate_pos]
                    sprite.set_target_position(crate_pos[0], crate_pos[1])
                    new_crates[crate_pos] = sprite
                else:
                    new_crates[crate_pos] = AnimatedSprite(
                        crate_pos[0], crate_pos[1], self.tile_size
                    )
            self.ai_crates = new_crates
        except Exception as e:
            print(f"❌ Error updating sprites: {e}")
    
    def update_animations(self):
        self.human_player.update()
        for sprite in self.human_crates.values():
            sprite.update()
        
        self.ai_player.update()
        for sprite in self.ai_crates.values():
            sprite.update()
    
    def render(self):
        self.screen.fill(COLORS['background'])
        
        human_state = self.game.get_human_state()
        board_width = human_state.width * self.tile_size
        board_height = human_state.height * self.tile_size
        
        human_offset_x = 50
        ai_offset_x = human_offset_x + board_width + 100
        board_offset_y = 150
        
        self._render_player_label("YOU", human_offset_x + board_width // 2, 100, COLORS['human'])
        self._render_player_label("AI", ai_offset_x + board_width // 2, 100, COLORS['ai'])
        
        self._render_board(human_state, human_offset_x, board_offset_y, 
                          self.human_player, self.human_crates, COLORS['human'])
        self._render_board(self.game.get_ai_state(), ai_offset_x, board_offset_y, 
                          self.ai_player, self.ai_crates, COLORS['ai'])
        
        self._render_stats(human_state, human_offset_x, board_offset_y + board_height + 20)
        self._render_stats(self.game.get_ai_state(), ai_offset_x, board_offset_y + board_height + 20)
    
    def _render_board(self, state, offset_x, offset_y, player_sprite, crate_sprites, player_color):
        for y in range(state.height):
            for x in range(state.width):
                rect = pygame.Rect(
                    offset_x + x * self.tile_size,
                    offset_y + y * self.tile_size,
                    self.tile_size, self.tile_size
                )
                
                tile = state.grid[y][x]
                
                if tile == Tile.WALL:
                    pygame.draw.rect(self.screen, COLORS['wall_shadow'], rect)
                    inner = rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, COLORS['wall'], inner)
                    highlight = pygame.Rect(inner.x, inner.y, inner.width, 8)
                    pygame.draw.rect(self.screen, COLORS['wall_highlight'], highlight)
                    pygame.draw.rect(self.screen, COLORS['wall_shadow'], inner, 2)
                elif tile == Tile.TARGET:
                    floor_color = COLORS['floor'] if (x + y) % 2 == 0 else COLORS['floor_alt']
                    pygame.draw.rect(self.screen, floor_color, rect)
                    pygame.draw.circle(self.screen, COLORS['target_glow'], 
                                     rect.center, self.tile_size // 3 + 3)
                    pygame.draw.circle(self.screen, COLORS['target'], 
                                     rect.center, self.tile_size // 3)
                else:
                    floor_color = COLORS['floor'] if (x + y) % 2 == 0 else COLORS['floor_alt']
                    pygame.draw.rect(self.screen, floor_color, rect)
                
                pygame.draw.rect(self.screen, COLORS['background'], rect, 1)
        
        for crate_pos, sprite in crate_sprites.items():
            screen_x, screen_y = sprite.get_screen_pos()
            crate_rect = pygame.Rect(
                offset_x + screen_x + 8, offset_y + screen_y + 8,
                self.tile_size - 16, self.tile_size - 16
            )
            
            if crate_pos in state.targets:
                color = COLORS['crate_on_target']
                shadow = (30, 100, 30)
                highlight = (80, 200, 80)
            else:
                color = COLORS['crate']
                shadow = COLORS['crate_shadow']
                highlight = COLORS['crate_highlight']
            
            shadow_rect = crate_rect.copy()
            shadow_rect.y += 4
            pygame.draw.rect(self.screen, shadow, shadow_rect, border_radius=6)
            pygame.draw.rect(self.screen, color, crate_rect, border_radius=6)
            
            highlight_rect = pygame.Rect(crate_rect.x + 4, crate_rect.y + 4, 
                                        crate_rect.width - 8, 8)
            pygame.draw.rect(self.screen, highlight, highlight_rect, border_radius=3)
            pygame.draw.rect(self.screen, shadow, crate_rect, 3, border_radius=6)
        
        screen_x, screen_y = player_sprite.get_screen_pos()
        center = (offset_x + screen_x + self.tile_size // 2,
                 offset_y + screen_y + self.tile_size // 2)
        
        shadow_center = (center[0] + 2, center[1] + 3)
        pygame.draw.circle(self.screen, (0, 0, 0), shadow_center, self.tile_size // 3 + 2)
        
        outline_color = COLORS[f'{state.player_id}_outline']
        pygame.draw.circle(self.screen, outline_color, center, self.tile_size // 3 + 3)
        pygame.draw.circle(self.screen, player_color, center, self.tile_size // 3)
        
        highlight_pos = (center[0] - 4, center[1] - 4)
        pygame.draw.circle(self.screen, (255, 255, 255), highlight_pos, self.tile_size // 6)
    
    def _render_player_label(self, text, center_x, y, color):
        surface = self.title_font.render(text, True, color)
        rect = surface.get_rect(center=(center_x, y))
        self.screen.blit(surface, rect)
    
    def _render_stats(self, state, x, y):
        stats = [
            f"Moves: {state.moves}",
            f"Pushes: {state.pushes}",
            f"Score: {state.get_score()}",
            f"Time: {state.get_time_elapsed():.1f}s"
        ]
        
        if state.is_solved():
            stats.append("✅ SOLVED!")
        
        for i, text in enumerate(stats):
            color = COLORS['gold'] if "SOLVED" in text else COLORS['text']
            surface = self.small_font.render(text, True, color)
            self.screen.blit(surface, (x, y + i * 28))


class SokobanFrontend:
    """Main game frontend - FIXED AI EXECUTION"""
    
    def __init__(self):
        try:
            pygame.init()
            
            self.difficulty = "medium"
            self.algorithm = "astar"
            self.level_index = 0
            
            level_data = get_level(self.difficulty, self.level_index)
            board_width = max(len(row) for row in level_data) * TILE_SIZE
            board_height = len(level_data) * TILE_SIZE
            
            self.window_width = board_width * 2 + 200
            self.window_height = board_height + 400
            
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption("Sokoban: AI Performance Demo")
            
            self.clock = pygame.time.Clock()
            self.running = True
            
            self.ui_font = pygame.font.Font(None, 24)
            self.button_font = pygame.font.Font(None, 22)
            self.big_button_font = pygame.font.Font(None, 28)
            
            self._create_ui_buttons()
            self._init_game()
            
            self.human_playing = False
            self.ai_playing = False
            self.ai_move_delay = 0.15  # Seconds between AI moves
            self.ai_last_move_time = 0
            
        except Exception as e:
            print(f"❌ Error initializing frontend: {e}")
            raise
    
    def _create_ui_buttons(self):
        top_y = self.window_height - 180
        button_w = 90
        button_h = 35
        spacing = 100
        start_x = 50
        
        self.diff_easy = Button(start_x, top_y, button_w, button_h, "EASY", self.button_font)
        self.diff_medium = Button(start_x + spacing, top_y, button_w, button_h, "MEDIUM", self.button_font)
        self.diff_hard = Button(start_x + spacing * 2, top_y, button_w, button_h, "HARD", self.button_font)
        
        algo_start_x = start_x + spacing * 3 + 50
        
        self.algo_astar = Button(algo_start_x, top_y, button_w, button_h, "A*", self.button_font)
        self.algo_bfs = Button(algo_start_x + spacing, top_y, button_w, button_h, "BFS", self.button_font)
        self.algo_dfs = Button(algo_start_x + spacing * 2, top_y, button_w, button_h, "DFS", self.button_font)
        
        bottom_y = self.window_height - 120
        play_button_w = 200
        play_button_h = 50
        
        center_x = self.window_width // 2
        button_spacing = 220
        
        self.human_play_button = Button(
            center_x - button_spacing - play_button_w // 2, bottom_y,
            play_button_w, play_button_h, "▶ PLAY (YOU)", self.big_button_font, 'play_button'
        )
        
        self.ai_play_button = Button(
            center_x + button_spacing - play_button_w // 2, bottom_y,
            play_button_w, play_button_h, "▶ PLAY AI", self.big_button_font, 'play_button'
        )
        
        reset_w = 150
        self.reset_button = Button(
            center_x - reset_w // 2, bottom_y,
            reset_w, play_button_h, "🔄 RESET", self.big_button_font, 'stop_button'
        )
        
        self.difficulty_buttons = {
            'easy': self.diff_easy,
            'medium': self.diff_medium,
            'hard': self.diff_hard
        }
        
        self.algorithm_buttons = {
            'astar': self.algo_astar,
            'bfs': self.algo_bfs,
            'dfs': self.algo_dfs
        }
        
        self._update_button_states()
    
    def _update_button_states(self):
        for name, btn in self.difficulty_buttons.items():
            btn.is_active = (name == self.difficulty)
        
        for name, btn in self.algorithm_buttons.items():
            btn.is_active = (name == self.algorithm)
    
    def _init_game(self):
        try:
            level_data = get_level(self.difficulty, self.level_index)
            self.game = SokobanGame(level_data)
            self.renderer = GameRenderer(self.screen, self.game)
            
            self.ai_controller = AIController(self.algorithm, self.difficulty)
            self.ai_solution_computed = False
            
            self.human_playing = False
            self.ai_playing = False
            
            print(f"✅ Game ready: {self.difficulty.upper()}, {self.algorithm.upper()}\n")
            
        except Exception as e:
            print(f"❌ Error initializing game: {e}")
            raise
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            for name, btn in self.difficulty_buttons.items():
                if btn.handle_event(event):
                    if self.difficulty != name:
                        self.difficulty = name
                        self._update_button_states()
                        self._init_game()
            
            for name, btn in self.algorithm_buttons.items():
                if btn.handle_event(event):
                    if self.algorithm != name:
                        self.algorithm = name
                        self._update_button_states()
                        self._init_game()
            
            if self.human_play_button.handle_event(event):
                self.human_playing = not self.human_playing
                self.human_play_button.text = "⏸ PAUSE (YOU)" if self.human_playing else "▶ PLAY (YOU)"
                print(f"{'▶' if self.human_playing else '⏸'} Human: {'PLAYING' if self.human_playing else 'PAUSED'}")
            
            if self.ai_play_button.handle_event(event):
                if not self.ai_playing:
                    self.ai_playing = True
                    self.ai_play_button.text = "⏸ PAUSE AI"
                    print(f"▶ AI: STARTING")
                    # Compute solution immediately
                    if not self.ai_solution_computed:
                        self.ai_controller.compute_solution(self.game.get_ai_state())
                        self.ai_solution_computed = True
                else:
                    self.ai_playing = False
                    self.ai_play_button.text = "▶ PLAY AI"
                    print(f"⏸ AI: PAUSED")
            
            if self.reset_button.handle_event(event):
                print("\n🔄 RESET\n")
                self._init_game()
                self.human_play_button.text = "▶ PLAY (YOU)"
                self.ai_play_button.text = "▶ PLAY AI"
            
            if event.type == pygame.KEYDOWN and self.human_playing:
                moved = False
                if event.key in [pygame.K_UP, pygame.K_w]:
                    moved = self.game.move_human(Direction.UP)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    moved = self.game.move_human(Direction.DOWN)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    moved = self.game.move_human(Direction.LEFT)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    moved = self.game.move_human(Direction.RIGHT)
                
                if moved:
                    self.renderer.update_sprites()
    
    def update(self):
        try:
            self.renderer.update_animations()
            
            # FIXED AI LOGIC
            if self.ai_playing and not self.game.get_ai_state().is_solved():
                # Wait for animation to finish
                if not self.renderer.ai_player.is_animating:
                    current_time = pygame.time.get_ticks() / 1000.0
                    
                    if current_time - self.ai_last_move_time >= self.ai_move_delay:
                        # Get next move with game state for fallback
                        next_move = self.ai_controller.get_next_move(self.game.get_ai_state())
                        
                        if next_move:
                            if self.game.move_ai(next_move):
                                self.renderer.update_sprites()
                                self.ai_last_move_time = current_time
                        else:
                            # No more moves available
                            self.ai_playing = False
                            self.ai_play_button.text = "▶ PLAY AI"
                            if not self.game.get_ai_state().is_solved():
                                print("⚠️  AI has no more moves (may be stuck)")
            
            elif self.ai_playing and self.game.get_ai_state().is_solved():
                # AI finished!
                self.ai_playing = False
                self.ai_play_button.text = "▶ PLAY AI"
                print("🎉 AI SOLVED THE PUZZLE!")
                
        except Exception as e:
            print(f"❌ Error in update: {e}")
    
    def render(self):
        self.renderer.render()
        
        panel_y = self.window_height - 210
        panel_rect = pygame.Rect(0, panel_y, self.window_width, 210)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.line(self.screen, COLORS['text'], (0, panel_y), (self.window_width, panel_y), 2)
        
        diff_label = self.ui_font.render("DIFFICULTY:", True, COLORS['text'])
        self.screen.blit(diff_label, (50, panel_y + 15))
        
        algo_label = self.ui_font.render("ALGORITHM:", True, COLORS['text'])
        self.screen.blit(algo_label, (400, panel_y + 15))
        
        for btn in self.difficulty_buttons.values():
            btn.draw(self.screen)
        for btn in self.algorithm_buttons.values():
            btn.draw(self.screen)
        
        self.human_play_button.draw(self.screen)
        self.ai_play_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        
        inst_y = self.window_height - 25
        inst = "Click PLAY buttons to start | Use Arrow Keys/WASD when playing | Compare speeds!"
        inst_surface = pygame.font.Font(None, 20).render(inst, True, COLORS['text'])
        inst_rect = inst_surface.get_rect(center=(self.window_width // 2, inst_y))
        self.screen.blit(inst_surface, inst_rect)
        
        pygame.display.flip()
    
    def run(self):
        print("\n" + "="*70)
        print("🎮 SOKOBAN: AI PERFORMANCE DEMO")
        print("="*70)
        print("📖 Click 'PLAY (YOU)' and use Arrow Keys/WASD")
        print("🤖 Click 'PLAY AI' to watch AI solve")
        print("⏱️  Compare your speed vs AI!")
        print("="*70 + "\n")
        
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
        
        pygame.quit()
        print("\n👋 Thanks for playing!\n")