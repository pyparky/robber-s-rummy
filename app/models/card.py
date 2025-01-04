from .suit import Suit

suit_colors = {
    'P': 'red',
    'F': 'green',
    'N': 'yellow',
    'K': 'blue'
}

class Card:
    def __init__(self, suit: Suit, value: int, id: int):
        self.suit = suit
        self.value = value
        self.id = id
    
    def __str__(self):
        return f"{self.value}" #_{self.id}_{self.suit.value}
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.value == other.value and self.id == self.id
    
    def __repr__(self) -> str:
        color = suit_colors.get(self.suit.value, 'pink')
        return f"[{color}]{self.value}[/{color}]" #_{self.id}