# UnoGame.py
import random
import os
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl

class Card:
    def __init__(self, color, card_type):
        self.color = color
        self.type = card_type

    def __str__(self):
        return f"{self.color} {self.type}"

    def is_playable(self, top_card):
        return (
            self.color == top_card.color or
            self.type == top_card.type or
            self.color == "all" or
            self.color == "super"
        )

class UnoGame:
    def __init__(self, num_players):
        self.deck = []
        self.super_deck = []
        self.players = [[] for _ in range(num_players)]
        self.discard = []
        self.top_card = None
        self.active_color = None
        self.direction = 1
        self.current_player = 0
        self.num_players = num_players
        self.initialize_deck()
        self.initialize_super_deck()
        self.deal_cards()
        self.initialize_top_card()

        self.cheering_player = QMediaPlayer()
        self.cheering_audio_output = QAudioOutput()
        self.cheering_player.setAudioOutput(self.cheering_audio_output)

    def play_cheering_sound(self):
        cheering_sound_path = os.path.join(os.getcwd(), "Sounds", "Winner.wav")
        self.cheering_player.setSource(QUrl.fromLocalFile(cheering_sound_path))
        self.cheering_player.setAudioOutput(self.cheering_audio_output)
        self.cheering_player.play()

    def check_winner(self):
        for i, player in enumerate(self.players):
            if len(player) == 0:
                self.play_cheering_sound()  # Play the cheering sound when a winner is found
                return i  # Player index who won
        return -1  # No winner yet

    def initialize_deck(self):

        types = ["zero", "one", "two", "three", "four", "five", "six", "seven",
                 "eight", "nine", "skip", "reverse", "plus2"]
        colors = ["red", "blue", "yellow", "green"]
        for color in colors:
            for card_type in types:
                self.deck.append(Card(color, card_type))
                if card_type != "zero":  # Add a second set of non-zero cards
                    self.deck.append(Card(color, card_type))
        # Add wild and special cards
        for _ in range(4):
            self.deck.append(Card("all", "plus4"))
            self.deck.append(Card("all", "wild"))
        random.shuffle(self.deck)

    def initialize_super_deck(self):
        super_card_types = ["extplayall", "intplayall", "doubleplay", "chiefskip"]  # Super card types
        for card_type in super_card_types:
            for _ in range(2):
                self.super_deck.append(Card("super", card_type))
        random.shuffle(self.super_deck)

    def deal_cards(self):
        for player in self.players:
            for _ in range(7):
                if self.deck:
                    player.append(self.deck.pop())

    def initialize_top_card(self):
        while True:
            if not self.deck:
                self.replenish_deck()
            card = self.deck.pop()
            if card.type not in ["plus4", "wild"]:  # Avoid starting with a wild card
                self.discard.append(card)
                self.top_card = card
                break
            else:
                self.deck.insert(0, card)  # Put back the wild card at the bottom

    def replenish_deck(self):
        # Move all but the top card to the deck and shuffle
        top = self.discard.pop()
        self.deck = self.discard
        self.discard = [top]
        random.shuffle(self.deck)

    def can_player_play(self, player_index, card):
        top_card = self.top_card
        return card.is_playable(top_card)

    def play_card(self, player_index, card_index):
        player_hand = self.players[player_index]
        selected_card = player_hand[card_index]

        if selected_card.color == "super": #STILL DEBUGGING
            #previous_color = self.top_card.color
            previous_color = self.active_color

            self.discard.append(selected_card)
            self.top_card = selected_card  # Super card on top of the discard pile
            self.active_color = previous_color #DIDNT WORK
            #print(self.active_color)
            #self.top_card.color = previous_color
            player_hand.pop(card_index)
            #self.apply_super_card_effects(selected_card)  # Call a method for super card logic
            return True, "Super card played!"

        # Check if the card can be played
        if not selected_card.is_playable(self.top_card):
            return False, "Invalid move. You can't play this card."

        # Play the card
        self.discard.append(selected_card)
        self.top_card = selected_card
        #self.active_color = selected_card.color
        player_hand.pop(card_index)

        # Handle special card actions
        if selected_card.type in ['wild', 'plus4']:
            if selected_card.type == 'plus4':
                self.apply_card_effects(selected_card)  # Ensure the effects are applied
            return True, "Color selection needed."  # Signal that a special image is needed

        # Apply any effects from the card
        self.apply_card_effects(selected_card)

        winner = self.check_winner()
        if winner != -1:
            self.play_cheering_sound()

        return True, "Card played successfully."

    def draw_cards(self, player_index, number):
        for _ in range(number):
            if not self.deck:
                self.replenish_deck()
            if self.deck:
                self.players[player_index].append(self.deck.pop())

    def draw_card(self, player_index):

        if not self.deck:
            self.replenish_deck()
        if self.deck:
            self.players[player_index].append(self.deck.pop())

            return True, "Card drawn."
        else:
            return False, "No cards to draw."

    def next_player(self):
        #Moves to the next player based on the current direction
        self.current_player = (self.current_player + self.direction) % self.num_players

    def on_color_selected(self, selected_color):
        self.apply_card_effects(self.current_card, selected_color)

    def apply_card_effects(self, card, selected_color=None):
        if card.type == "skip":
            self.next_player()
        elif card.type == "reverse":
            self.direction *= -1
            if self.num_players == 2:
                self.next_player()
        elif card.type == "plus2":
            self.draw_cards((self.current_player + self.direction) % self.num_players, 2)
            self.next_player()
        elif card.type == "plus4":
            # The next player draws 4 cards and loses their turn

            self.draw_cards((self.current_player + self.direction) % self.num_players, 4)
            self.next_player()
            return True, "Color selection needed."
        elif card.type == "wild":
            return True, "Color selection needed."  # Flag for UI to trigger color selection
        if selected_color:
                self.display_selected_color_image(selected_color)
        return False, "No special effects."

    def apply_super_card_effects(self, card):
        if card.type == "extplayall":
            # Allow all players to play an extra card
            pass
        elif card.type == "intplayall":
            # Internal player effect logic
            pass
        elif card.type == "doubleplay":
            # Allow the current player to play another card immediately
            pass
        elif card.type == "chiefSkip":
            # Allow the current player to play another card immediately
            pass

    def choose_new_color(self, new_color):
        self.top_card.color = new_color  # Update top card color

    def select_color(self, color):
        self.display_selected_color_image(color)

    def display_selected_color_image(self, color):
        image_name = f"card_select_{color}.png"
        self.show_image_on_discard_pile(image_name)
