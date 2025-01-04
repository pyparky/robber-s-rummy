import random
from typing import List, Tuple, Dict
from rich.console import Console
from rich.table import Table
from rich import print
from .models.suit import Suit
from .models.card import Card, suit_colors
from .models.meld import Meld
from .models.player import Player

console = Console()

class RobbersRummy:
    def __init__(self, num_players: int, num_ai_players: int):
        if not 1 <= num_players <= 3:
            raise ValueError("Number of players must be between 1 and 3")
        if not num_ai_players == 1:
            raise ValueError("Number of AI player must be 1")
        
        self.all_cards: List[Card] = []
        self.original_deck = []
        self.players: List[Player] = []
        self.game_over = False
        
        # Create human players
        for i in range(num_players):
            self.players.append(Player(f"Player {i+1}"))
        
        # Create AI players
        for i in range(num_ai_players):
            self.players.append(Player(f"AI {i+1}", is_ai=True))
        
        self.current_player_idx = -1
        self.all_melds: List[Meld] = []  # Track all melds in play
        
    def create_deck(self) -> List[Card]:
        deck = []
        uid = 0
        for suit in Suit:
            for value in range(1, 14):
                deck.append(Card(suit, value, uid))
                uid += 1
                deck.append(Card(suit, value, uid)) #two cards of each
                uid += 1
        random.shuffle(deck)
        return deck

    def deal_initial_hand(self):
        # Deal 14 cards to each player
        for _ in range(14):
            for player in self.players:
                if self.all_cards:
                    player.hand.append(self.all_cards.pop())        

    def _is_valid_run(self, cards: List[Card]) -> bool:
        if len(cards) < 3:
            return False
        
        # Sort cards by value
        sorted_cards = sorted(cards, key=lambda x: x.value)
        
        # Check if all cards are same suit and consecutive values
        suit = sorted_cards[0].suit
        prev_value = sorted_cards[0].value
        
        for card in sorted_cards[1:]:
            if card.suit != suit or card.value != prev_value + 1:
                return False
            prev_value = card.value
            
        return True
    
    def _is_valid_set(self, cards: List[Card]) -> bool:
        if len(cards) < 3:
            return False
        
        # Check if all cards have same value
        value = cards[0].value
        suits = set()
        
        for card in cards:
            if card.value != value:
                return False
            suits.add(card.suit)
            
        # Check no duplicate suits
        return len(suits) == len(cards)

    def find_robbable_melds(self, card: Card) -> List[Meld]:
        robbable = []
        for meld in self.all_melds:
            if meld.can_be_robbed(card):
                robbable.append(meld)
                break # Only rob one meld
        return robbable

    def _human_play_turn(self, player: Player):
        while True:
            
            self.is_game_over()

            self._display_game_state(player)
            print("\nActions:")
            print("1. Draw from deck")
            print("2. Form new meld")
            print("3. Rob existing meld")
            print("4. End turn")
            print("5. Quit game")
            
            try:
                user_input = input("Choose an action: ")
                print(f"User input: {user_input}")
                choice = int(user_input)
                
                if choice == 1:
                    if self.all_cards:
                        if len(self.all_cards) == 0:
                            print("Has no more moves!")
                            return
                        card_drawn = self.all_cards.pop()
                        player.hand.append(card_drawn)
                        print(f"Card drawn from deck: {self._color_card(card_drawn)}")
                        return
                    else:
                        print("Deck is empty!")
                        continue
                
                elif choice == 2:
                    self._handle_new_meld(player)
                
                elif choice == 3:
                    self._handle_robbing(player)
                
                elif choice == 4:
                    return

                elif choice == 5:
                    self.game_over = True
                    print("Quitting game...")
                    break
                
            except ValueError:
                print("Invalid input! Please enter a number.")

    def _handle_new_meld(self, player: Player):
        print("\nSelect cards for new meld (comma-separated indices, e.g.: <1,2,3> Or from-to, e.g.: <1-3> ):")
        print("Your hand:")
        player.hand = sorted(player.hand, key=lambda x: (x.suit.value, x.value))
        for i, card in enumerate(player.hand):
            print(f"{i+1}: {self._color_card(card)}")
        
        try:
            user_input = input("Choose cards: ")
            if "-" in user_input:
                start, end = [int(i)-1 for i in user_input.split("-")]
                indices = list(range(start, end+1))
            else:
                indices = [int(i)-1 for i in user_input.split(",")]

            if not all(0 <= i < len(player.hand) for i in indices):
                print("Invalid indices!")
                return
            
            selected_cards = [player.hand[i] for i in indices]
            
            if self._is_valid_run(selected_cards):
                meld = Meld(selected_cards, 'run')
                self.all_melds.append(meld)
                for card in selected_cards:
                    player.hand.remove(card)
                print("Run meld created!")
                
            elif self._is_valid_set(selected_cards):
                meld = Meld(selected_cards, 'set')
                self.all_melds.append(meld)
                for card in selected_cards:
                    player.hand.remove(card)
                print("Set meld created!")
                
            else:
                print("Invalid meld!")
                
        except ValueError:
            print("Invalid input!")

    def _handle_robbing(self, player: Player):
        print("\nSelect meld to rob:")
        for i, meld in enumerate(self.all_melds):
            cards_str = " ".join(self._color_card(c) for c in sorted(meld.cards, key=lambda x: (x.value)))
            print(f"{i+1}: {meld.type} ({cards_str})")
        
        try:
            meld_idx = int(input("Choose meld to rob (0 to cancel): ")) - 1
            if 0 <= meld_idx < len(self.all_melds):
                target_meld = self.all_melds[meld_idx]
                
                # Remove meld from all_melds
                self.all_melds.remove(target_meld)
                
                # target_meld.cards to player's hand
                player.hand.extend(target_meld.cards)

                print("Meld successfully robbed and added to Player's hand!")
            
        except ValueError:
            print("Invalid input!")

    def _ai_play_turn(self, player: Player):
        header = (
            f"|Cards in deck: {len(self.all_cards)}|"
            f"Player sum of cards: {len(player.hand)}|"
            f"Current player's name: {player.name}|"
        )
        print("\n" + "="*150)
        print(header)
        print("="*150)
        print()

        self._show_cards_in_hand(player)

        tried_rob = False
        for card in player.hand:
            robbable = self.find_robbable_melds(card)
            if robbable:
                tried_rob = True
                print(f"{player.name} is robbing a meld!")
                target_meld = robbable[0]
                
                # Perform robbery
                self.all_melds.remove(target_meld)                
                new_cards = target_meld.cards + [card]
                self.all_melds.append(Meld(new_cards, target_meld.type))
                player.hand.remove(card)

        value_groups, suit_groups = self.try_form_melds(player)
        set_arranged = self.ai_arrange_set(player, value_groups)                
        run_arranged = self.ai_arrange_run(player, suit_groups)
        
        if not set_arranged and not run_arranged and not tried_rob:
            if len(self.all_cards) == 0:
                print(f"{player.name} has no more moves, because deck is empty!")
                return
            # No robbing and no meld. Let's draw a card
            drawn_card = self.all_cards.pop()
            print(f"{player.name} drew a card: {self._color_card(drawn_card)}")            
            player.hand.append(drawn_card)

        return

    def _show_cards_in_hand(self, player):
        v, s = self.try_form_melds(player, clear=False)        
        # Create a table for value groups and suit groups
        table = Table(box=None, show_header=True)
        table.add_column("Value Groups", width=30)
        table.add_column("Suit Groups", width=30)        
        # Add rows to the table
        max_length = max(len(v), len(s))
        value_keys = sorted(v.keys())
        suit_keys = sorted(s.keys(), key=lambda x: x.value)        
        for i in range(max_length):
            value_str = ""
            suit_str = ""
            if i < len(value_keys):
                value = value_keys[i]
                value_str = f"{value}: {' '.join(self._color_card(card) for card in v[value])}"
            if i < len(suit_keys):
                suit = suit_keys[i]
                suit_str = f"{self._color_suit(suit.value)}: {' '.join(self._color_value_based_on_suit(str(card.value), suit.value) for card in sorted(s[suit], key=lambda x: x.value))}"
            table.add_row(value_str, suit_str)        
        console.print(table)

    def ai_arrange_set(self, player: Player, value_groups: Dict[int, List[Card]]) -> bool:
        arranged = False

        for cards in value_groups.values():
            if self._is_valid_set(cards):
                arranged = True
                meld = Meld(cards, 'set')
                self.all_melds.append(meld)
                print(f"AI arranged a set")
                for card in cards:
                    player.hand.remove(card)

        return arranged

    def ai_arrange_run(self, player: Player, suit_groups: Dict[Suit, List[Card]]) -> bool:
        arranged = False

        for cards in suit_groups.values():
            cards.sort(key=lambda x: x.value)
            longest_subarray = self._find_longest_consecutive_subarray(cards)
            if len(longest_subarray) < 3:
                continue
            arranged = True
            meld = Meld(longest_subarray, 'run')
            self.all_melds.append(meld)
            print(f"AI arranged a run")
            for card in longest_subarray:
                player.hand.remove(card)

        return arranged
    
    def _find_longest_consecutive_subarray(self, cards: List[Card]) -> List[Card]:
        """
        Sliding window approach to find the longest consecutive subarray 
        """
        longest_subarray = []
        current_subarray = []
        
        # Start with the first card
        current_subarray = [cards[0]]
        
        for i in range(1, len(cards)):
            current_card = cards[i]
            previous_card = cards[i-1]
            
            # Check if the current card continues the sequence
            if current_card.value == previous_card.value + 1:
                current_subarray.append(current_card)
            else:
                # Sequence broken, check if current subarray is valid and longest
                if len(current_subarray) >= 3 and len(current_subarray) > len(longest_subarray):
                    longest_subarray = current_subarray.copy()
                # Start a new subarray with current card
                current_subarray = [current_card]
        
        # Check the last subarray
        if len(current_subarray) >= 3 and len(current_subarray) > len(longest_subarray):
            longest_subarray = current_subarray
        
        return longest_subarray

    def _ai_rearrange_melds(self, player: Player, cards: List[Card]):
        # AI logic to rearrange melds
        value_groups, suit_groups = self.try_form_melds(player)
        
        found = False
        # Try to form sets first
        for _, group in value_groups.items():
            if self._is_valid_set(group):
                found = True
                meld = Meld(group, 'set')
                self.all_melds.append(meld)

                # remove group from hand
                for card in group:
                    if card in player.hand:
                        player.hand.remove(card)

                for card in group:
                    if card in cards:
                        cards.remove(card)

        # Try to form run
        for _, group in suit_groups.items():
            group.sort(key=lambda x: x.value)
            for i in range(len(group)-2):
                for j in range(i+2, len(group)):
                    potential_run = group[i:j+1]
                    if self._is_valid_run(potential_run):
                        found = True
                        meld = Meld(potential_run, 'run')
                        self.all_melds.append(meld)

                        # remove potential_run from hand
                        for card in potential_run:
                            if card in player.hand:
                                player.hand.remove(card)

                        for card in potential_run:
                            if card in cards:
                                cards.remove(card)
        
        # If there are remaining cards, form the last meld
        if cards:
            if self._is_valid_run(cards):
                meld = Meld(cards, 'run')
                self.all_melds.append(meld)

                # remove group from hand, but check if card is still in hand
                for card in cards:
                    if card in player.hand:
                        player.hand.remove(card)                
                
            elif self._is_valid_set(cards):
                meld = Meld(cards, 'set')
                self.all_melds.append(meld)

                # remove group from hand, but check if card is still in hand
                for card in cards:
                    if card in player.hand:
                        player.hand.remove(card)                

        if found:
            print("AI successfully rearranged melds!")
        else:
            print("AI failed to rearrange melds!")

    def try_form_melds(self, player: Player, clear: bool = True) -> Tuple[Dict[int, List[Card]], Dict[Suit, List[Card]]]:
        # Try sets first (they're usually more valuable)
        value_groups = {}
        for card in player.hand:
            if card.value not in value_groups:
                value_groups[card.value] = []
            value_groups[card.value].append(card)
        
        # Try run
        suit_groups = {}
        for card in player.hand:
            if card.suit not in suit_groups:
                suit_groups[card.suit] = []
            suit_groups[card.suit].append(card)        

        if clear:                    
            for value, cards in list(value_groups.items()):
                if len(cards) < 3:
                    del value_groups[value]
            for suit, cards in list(suit_groups.items()):
                if len(cards) < 3:
                    del suit_groups[suit]

        return value_groups, suit_groups

    def play_turn(self):
        while self.is_game_over() == False:
            self.check_game_integrity()

            if self.current_player_idx == -1: # First turn when no player has played yet
                self.current_player_idx = 0
            else:
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

            player = self.players[self.current_player_idx]
            
            if player.is_ai:
                self._ai_play_turn(player)
            else:
                self._human_play_turn(player)        
    
    def _display_game_state(self, current_player: Player):
        players_names = ", ".join(player.name for player in self.players)
        players_cards_count = ", ".join(str(len(player.hand)) for player in self.players)
        header = (
            f"|Cards in deck: {len(self.all_cards)}|"
            f"Players' names: {players_names}|"
            f"Players' sum of cards: {players_cards_count}|"
            f"Current player's name: {current_player.name}|"
        )
        print("\n" + "="*150)
        print(header)
        print("="*150)
        
        self._show_cards_in_hand(current_player)

        print("\nMelds:")
        for meld in self.all_melds:
            meld_str = " ".join(self._color_card(card) for card in sorted(meld.cards, key=lambda x: (x.value)))
            print(f"  {meld.type}: {meld_str}")
        print("="*50)

    def _color_value_based_on_suit(self, value, suit) -> str:
        color = suit_colors.get(suit, 'pink')
        return f"[{color}]{value}[/{color}]"
    
    def _color_suit(self, value) -> str:
        color = suit_colors.get(value, 'pink')
        return f"[{color}]{value}[/{color}]"

    def _color_card(self, card: Card) -> str:
        color = suit_colors.get(card.suit.value, 'pink')
        return f"[{color}]{card}[/{color}]"

    def is_game_over(self) -> bool:
        if self.game_over:
            return True
        result = any(len(player.hand) == 0 for player in self.players)
        self.game_over = result
        return result

    def check_game_integrity(self) -> bool:
        current_cards = self.all_cards.copy()
        for player in self.players:
            current_cards.extend(player.hand)
        for meld in self.all_melds:
            current_cards.extend(meld.cards)
        
        original_card_counts = self._count_cards(self.original_deck)
        current_card_counts = self._count_cards(current_cards)
        
        if original_card_counts != current_card_counts:
            print("Original cards counts:")
            for card, count in original_card_counts.items():
                print(f"{card}: {count}")
            print("Current cards counts:")
            for card, count in current_card_counts.items():
                print(f"{card}: {count}")
            raise ValueError("Game integrity check failed!")
        
        return True

    def _count_cards(self, cards: List[Card]) -> Dict[Tuple[Suit, int], int]:
        card_counts = {}
        for card in cards:
            key = (card.suit, card.value)
            if key in card_counts:
                card_counts[key] += 1
            else:
                card_counts[key] = 1
        return card_counts