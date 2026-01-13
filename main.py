"""
Sokoban: AI Performance Demo

Watch and compare different AI algorithms solving Sokoban puzzles!
See which algorithm is fastest and most efficient.

Features:
- Independent play buttons for YOU and AI
- Real-time performance metrics (time, moves, score)
- Three difficulty levels
- Three AI algorithms (A*, BFS, DFS)
- Visual side-by-side comparison

How to Use:
1. Select difficulty and algorithm from buttons
2. Click "PLAY (YOU)" to play manually with Arrow Keys/WASD
3. Click "PLAY AI" to watch AI solve the puzzle
4. Compare performance! Who's faster?
5. Click RESET to try again

Perfect for:
- Learning how AI algorithms work
- Comparing algorithm performance
- Understanding search strategies
- Educational demonstrations
"""

import sys
from frontend import SokobanFrontend


def main():
    """Launch the AI demo"""
    print("\n" + "="*70)
    print(" " * 10 + "🎮 SOKOBAN: AI PERFORMANCE DEMO 🤖")
    print("="*70)
    print()
    print("📊 FEATURES:")
    print("  • Watch AI algorithms solve puzzles in real-time")
    print("  • Compare your speed vs AI speed")
    print("  • See performance metrics: Time, Moves, Score")
    print("  • Test different algorithms: A*, BFS, DFS")
    print()
    print("🎮 HOW TO USE:")
    print("  1. Click difficulty & algorithm buttons to configure")
    print("  2. Click '▶ PLAY (YOU)' to play manually")
    print("  3. Click '▶ PLAY AI' to watch AI solve")
    print("  4. Click '🔄 RESET' to start over")
    print()
    print("⏱️  CHALLENGE:")
    print("  Can you beat the AI? Which algorithm is fastest?")
    print()
    print("="*70)
    print("\nLaunching game window...\n")
    
    try:
        game = SokobanFrontend()
        game.run()
        
        print("\n" + "="*70)
        print("👋 Thanks for watching the AI performance demo!")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()