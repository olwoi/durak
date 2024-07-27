## Durak Frontend Documentation

This documentation provides an overview of the functions available in the card game module.

- `get_suit_ordering`: Returns the ordering of the suits in the game based on a trump suit.

- `get_card_list`: Calculates the array of 32 cards in string representation based on the trump suit of the game.

- `convert_cards_to_strings`: Converts a boolean array of cards into a list of card strings.

- `convert_boolean_matrix`: Converts a boolean matrix of cards into a list of card strings.

Example Usage:

```python
trump = 0
card_ids = np.array([3, 6])

cards = np.zeros(32, dtype=bool)
cards[card_ids] = True

selected_cards = convert_cards_to_strings(cards, trump)
print(selected_cards)
```

