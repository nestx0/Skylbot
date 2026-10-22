# ppt_game.py
import random

class PPTGame:
    OPTIONS = {
        "Rock": "🪨",
        "Paper": "📄",
        "Scissors": "✂️"
    }

    WIN_CONDITIONS = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper"
    }

    @classmethod
    def get_bot_choice(cls):
        return random.choice(list(cls.OPTIONS.keys()))

    @classmethod
    def determine_winner(cls, player_choice, bot_choice):
        if player_choice == bot_choice:
            return "draw"
        if cls.WIN_CONDITIONS[player_choice] == bot_choice:
            return "player"
        return "bot"