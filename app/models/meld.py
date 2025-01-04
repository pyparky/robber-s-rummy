from dataclasses import dataclass
from typing import List
from .card import Card

@dataclass
class Meld:
    cards: List[Card]
    type: str  # 'run' or 'set'
    
    def can_be_robbed(self, card: Card) -> bool:
        if self.type == 'run':
            # Can add to either end of the run
            sorted_cards = sorted(self.cards, key=lambda x: x.value)
            if (card.suit == sorted_cards[0].suit and 
                card.value == sorted_cards[0].value - 1):
                return True
            if (card.suit == sorted_cards[-1].suit and 
                card.value == sorted_cards[-1].value + 1):
                return True
        elif self.type == 'set':
            # Can add same value, different suit
            return (card.value == self.cards[0].value and 
                   card.suit not in [c.suit for c in self.cards])
        return False