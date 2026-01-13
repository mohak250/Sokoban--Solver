A visual Sokoban game built with Python & Pygame that lets you play side-by-side with an AI and compare performance using different search algorithms.

 Features

 Human vs AI gameplay on the same level

 AI solvers: A*, BFS, DFS

 # Difficulty levels: Easy / Medium / Hard

 Smart AI with fallback strategy (never gets stuck)

 Smooth animations & modern UI

 Live stats: moves, pushes, score, time

# Tech Stack

Python 3

Pygame

AI Search Algorithms (A*, BFS, DFS)

# How to Run
pip install pygame
python frontend.py

# Controls

Arrow Keys / WASD → Move player

PLAY (YOU) → Start/Pause human play

PLAY AI → Watch AI solve the puzzle

RESET → Restart the level

Choose Difficulty and Algorithm from buttons

# AI Logic Overview

Uses search algorithms with time & node limits

Applies heuristics + deadlock detection

Falls back to a greedy strategy if search is incomplete

# Educational Value

This project demonstrates:

Search algorithms in real-world scenarios

Heuristic design

AI fallback strategies

Game state modeling

Python + Pygame integration
