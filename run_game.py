from datetime import datetime
from rich.console import Console
from app.rummy import RobbersRummy
from tests.test_rummy import TestRummyGame

console = Console()

if __name__ == "__main__":
    console.clear()
    
    print()
    print("*"*53)
    print(f"***** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} *****")
    print("*"*53)
    print()
    
    # Run tests
    test_game = TestRummyGame()
    test_game.test_initialization()
    test_game.test_initial_deal()
    test_game.test_valid_run()
    test_game.test_valid_set()
    test_game.test_find_robbable_melds_run_happy_postfix()
    test_game.test_find_robbable_melds_run_happy_prefix()
    test_game.test_find_robbable_melds_run_same_number()
    test_game.test_find_robbable_melds_run_wrong_color()
    test_game.test_find_robbable_melds_run_wrong_number()
    test_game.test_find_robbable_melds_set_happy()
    test_game.test_find_robbable_melds_set_same_color()
    test_game.test_find_robbable_melds_set_wrong_number()
    test_game.test_find_robbable_melds_set_same_number()
    test_game.test_try_form_melds_suit_group_happy()
    test_game.test_try_form_melds_value_group_happy()
    test_game.test_ai_arrange_set_happy()
    test_game.test_ai_arrange_2_set_happy()
    test_game.test_ai_arrange_run_happy()
    test_game.test_ai_arrange_2_run_happy()
    test_game.test_ai_arrange_2_overlapped_run_happy()

    # Run game
    game = RobbersRummy(num_players=1, num_ai_players=1)
    game.all_cards = game.create_deck()
    game.original_deck = game.all_cards.copy()
    game.deal_initial_hand()
    game.play_turn()
    print("Game over!")
    game.check_game_integrity()
