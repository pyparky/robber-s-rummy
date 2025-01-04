from typing import List
from .card import Card

class Player:
    def __init__(self, name: str, is_ai: bool = False):
        self.name = name
        self.hand: List[Card] = []
        self.is_ai = is_ai
        self.score = 0
    
    def __str__(self):
        return self.name
    
    def calculate_score(self) -> int:
        score = 0
        for card in self.hand:
            if card.value < 14:
                score += card.value
            else:
                score += 25 #joker
        return score