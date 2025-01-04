from collections import defaultdict
from app.models.suit import Suit
from app.models.card import Card
from app.models.meld import Meld
from app.rummy import RobbersRummy

class TestRummyGame:
    def test_initialization(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_cards = game.create_deck()
        game.original_deck = game.all_cards.copy()
        assert len(game.all_cards) == 104
        assert len(game.original_deck) == 104

        # Count cards of each color
        suit_counts = defaultdict(int)
        for card in game.all_cards:
            suit_counts[card.suit] += 1
                
        assert suit_counts[Suit.HEARTS] == 26  # (13 numbers * 2) + 1 special
        assert suit_counts[Suit.DIAMONDS] == 26  # (13 numbers * 2) + 1 special
        assert suit_counts[Suit.CLUBS] == 26  # 13 numbers * 2
        assert suit_counts[Suit.SPADES] == 26  # 13 numbers * 2

        assert len(game.players) == 2
        assert len(game.all_melds) == 0
        assert game.current_player_idx == -1

    def test_initial_deal(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_cards = game.create_deck()
        game.original_deck = game.all_cards.copy()
        game.deal_initial_hand()
        assert len(game.players[0].hand) == 14
        assert len(game.players[1].hand) == 14
        assert game.players[0].is_ai == False
        assert game.players[1].is_ai == True
        assert len(game.all_cards) == 76
        assert len(game.original_deck) == 104

    def test_valid_run(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.HEARTS, 2, 1),
            Card(Suit.HEARTS, 3, 2),
            Card(Suit.HEARTS, 4, 3),
            Card(Suit.HEARTS, 5, 4),
        ]
        assert game._is_valid_run(cards) == True

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.HEARTS, 2, 1),
            Card(Suit.HEARTS, 3, 2),
            Card(Suit.HEARTS, 5, 3),
            Card(Suit.HEARTS, 6, 4),
        ]
        assert game._is_valid_run(cards) == False

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.HEARTS, 2, 1)            
        ]
        assert game._is_valid_run(cards) == False

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.HEARTS, 1, 1),
            Card(Suit.HEARTS, 2, 2)
        ]
        assert game._is_valid_run(cards) == False

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.HEARTS, 2, 1),
            Card(Suit.DIAMONDS, 3, 2),
            Card(Suit.HEARTS, 4, 3),
        ]
        assert game._is_valid_run(cards) == False

    def test_valid_set(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.DIAMONDS, 1, 1),
            Card(Suit.CLUBS, 1, 2),
        ]
        assert game._is_valid_set(cards) == True

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.HEARTS, 1, 1),
            Card(Suit.CLUBS, 1, 2),
        ]
        assert game._is_valid_set(cards) == False

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.DIAMONDS, 1, 1),
            Card(Suit.CLUBS, 2, 2),
        ]
        assert game._is_valid_set(cards) == False

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.DIAMONDS, 1, 1),
        ]
        assert game._is_valid_set(cards) == False

        cards = [
            Card(Suit.HEARTS, 1, 0),
            Card(Suit.DIAMONDS, 2, 1),
            Card(Suit.CLUBS, 3, 2),
        ]
        assert game._is_valid_set(cards) == False

    def test_find_robbable_melds_run_happy_postfix(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3)], 'run'),
                          Meld([Card(Suit.HEARTS, 5, 5),Card(Suit.HEARTS, 6, 6),Card(Suit.HEARTS, 7, 7)], 'run') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.HEARTS, 4, 4))        
        assert len(melds) == 1
        assert len(melds[0].cards) == 3

    def test_find_robbable_melds_run_happy_prefix(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 2, 1),Card(Suit.HEARTS, 3, 2),Card(Suit.HEARTS, 4, 3)], 'run') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.HEARTS, 1, 0))        
        assert len(melds) == 1
        assert len(melds[0].cards) == 3

    def test_find_robbable_melds_run_same_number(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3)], 'run') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.HEARTS, 3, 4))        
        assert len(melds) == 0

    def test_find_robbable_melds_run_wrong_color(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3)], 'run') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.DIAMONDS, 4, 4))        
        assert len(melds) == 0

    def test_find_robbable_melds_run_wrong_number(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3)], 'run') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.HEARTS, 5, 5))        
        assert len(melds) == 0

    def test_find_robbable_melds_set_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 2, 1),Card(Suit.DIAMONDS, 2, 2),Card(Suit.CLUBS, 2, 3)], 'set'),
                          Meld([Card(Suit.HEARTS, 2, 10),Card(Suit.DIAMONDS, 2, 11),Card(Suit.CLUBS, 2, 12)], 'set') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.SPADES, 2, 4))        
        assert len(melds) == 1
        assert len(melds[0].cards) == 3

    def test_find_robbable_melds_set_same_color(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 2, 1),Card(Suit.DIAMONDS, 2, 2),Card(Suit.CLUBS, 2, 3)], 'set') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.CLUBS, 2, 4))        
        assert len(melds) == 0

    def test_find_robbable_melds_set_wrong_number(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 2, 1),Card(Suit.DIAMONDS, 2, 2),Card(Suit.CLUBS, 2, 3)], 'set') ]
        assert len(game.all_melds[0].cards) == 3
        melds = game.find_robbable_melds(Card(Suit.SPADES, 3, 4))        
        assert len(melds) == 0

    def test_find_robbable_melds_set_same_number(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.all_melds = [ Meld([Card(Suit.HEARTS, 2, 1),Card(Suit.DIAMONDS, 2, 2),Card(Suit.CLUBS, 2, 3),Card(Suit.SPADES, 2, 4)], 'set') ]
        assert len(game.all_melds[0].cards) == 4
        melds = game.find_robbable_melds(Card(Suit.SPADES, 2, 5))        
        assert len(melds) == 0

    def test_try_form_melds_suit_group_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3),Card(Suit.CLUBS, 4, 4),Card(Suit.CLUBS, 5, 5)]
        value_groups, suit_groups = game.try_form_melds(game.players[1], clear=False)
        assert len(suit_groups) == 2
        assert len(value_groups) == 5
        assert len(suit_groups[Suit.HEARTS]) == 3
        assert len(suit_groups[Suit.CLUBS]) == 2

        value_groups, suit_groups = game.try_form_melds(game.players[1], clear=True)
        assert len(suit_groups) == 1
        assert len(value_groups) == 0
        assert len(suit_groups[Suit.HEARTS]) == 3
        assert Suit.CLUBS not in suit_groups.keys()

    def test_try_form_melds_value_group_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 1, 1),Card(Suit.CLUBS, 1, 2),Card(Suit.DIAMONDS, 1, 3),Card(Suit.CLUBS, 4, 4),Card(Suit.CLUBS, 5, 5)]
        value_groups, suit_groups = game.try_form_melds(game.players[1], clear=False)
        assert len(suit_groups) == 3
        assert len(value_groups) == 3
        assert len(value_groups[1]) == 3
        assert len(value_groups[4]) == 1
        assert len(value_groups[5]) == 1
        assert len(suit_groups[Suit.HEARTS]) == 1
        assert len(suit_groups[Suit.DIAMONDS]) == 1
        assert len(suit_groups[Suit.CLUBS]) == 3

        value_groups, suit_groups = game.try_form_melds(game.players[1], clear=True)
        assert len(suit_groups) == 1
        assert len(value_groups) == 1
        assert len(value_groups[1]) == 3
        assert 4 not in value_groups.keys()
        assert 5 not in value_groups.keys()
        assert Suit.CLUBS in suit_groups.keys()

    def test_ai_arrange_set_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 1, 1),Card(Suit.CLUBS, 1, 2),Card(Suit.DIAMONDS, 1, 3),Card(Suit.CLUBS, 4, 4),Card(Suit.CLUBS, 5, 5)]
        value_groups, _ = game.try_form_melds(game.players[1], clear=False)
        assert len(game.players[1].hand) == 5
        arranged = game.ai_arrange_set(game.players[1], value_groups)
        assert arranged == True
        assert len(game.players[1].hand) == 2
        assert game.players[1].hand[0].value == 4
        assert game.players[1].hand[1].value == 5
        assert len(game.all_melds) == 1

    def test_ai_arrange_2_set_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 1, 1),Card(Suit.CLUBS, 1, 2),Card(Suit.DIAMONDS, 1, 3),Card(Suit.CLUBS, 4, 4),Card(Suit.DIAMONDS, 5, 5),Card(Suit.HEARTS, 5, 6),Card(Suit.SPADES, 5, 7)]
        value_groups, _ = game.try_form_melds(game.players[1], clear=False)
        assert len(game.players[1].hand) == 7
        arranged = game.ai_arrange_set(game.players[1], value_groups)
        assert arranged == True
        assert len(game.players[1].hand) == 1
        assert game.players[1].hand[0].value == 4
        assert game.players[1].hand[0].suit == Suit.CLUBS
        assert len(game.all_melds) == 2

    def test_ai_arrange_run_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3),Card(Suit.CLUBS, 4, 4),Card(Suit.CLUBS, 5, 5)]
        _, suit_groups = game.try_form_melds(game.players[1], clear=False)
        assert len(game.players[1].hand) == 5
        arranged = game.ai_arrange_run(game.players[1], suit_groups)
        assert arranged == True
        assert len(game.players[1].hand) == 2
        assert game.players[1].hand[0].value == 4
        assert game.players[1].hand[1].value == 5
        assert game.players[1].hand[0].suit == Suit.CLUBS
        assert len(game.all_melds) == 1

    def test_ai_arrange_2_run_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 1, 1),Card(Suit.HEARTS, 2, 2),Card(Suit.HEARTS, 3, 3),Card(Suit.CLUBS, 4, 4),Card(Suit.CLUBS, 5, 5),Card(Suit.CLUBS, 6, 6),Card(Suit.DIAMONDS, 7, 7)]
        _, suit_groups = game.try_form_melds(game.players[1], clear=False)
        assert len(game.players[1].hand) == 7
        arranged = game.ai_arrange_run(game.players[1], suit_groups)
        assert arranged == True
        assert len(game.players[1].hand) == 1
        assert game.players[1].hand[0].value == 7
        assert game.players[1].hand[0].suit == Suit.DIAMONDS
        assert len(game.all_melds) == 2

    def test_ai_arrange_2_overlapped_run_happy(self):
        game = RobbersRummy(num_players=1, num_ai_players=1)
        game.players[1].hand = [Card(Suit.HEARTS, 4, 4),Card(Suit.HEARTS, 5, 5),Card(Suit.HEARTS, 6, 6),Card(Suit.HEARTS, 7, 7),Card(Suit.HEARTS, 12, 12)]
        _, suit_groups = game.try_form_melds(game.players[1], clear=False)
        assert len(game.players[1].hand) == 5
        arranged = game.ai_arrange_run(game.players[1], suit_groups)
        assert arranged == True
        assert len(game.players[1].hand) == 1
        assert game.players[1].hand[0].value == 12
        assert game.players[1].hand[0].suit == Suit.HEARTS
        assert len(game.all_melds) == 1