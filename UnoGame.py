# UnoGame.py
import random
import os
import time
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QPropertyAnimation, QPoint
from PySide6.QtWidgets import QWidget, QLabel

class Card:
    def __init__(self, color, card_type):
        self.color = color
        self.type = card_type

    def __str__(self):
        return f"{self.color} {self.type}"

    def is_playable(self, top_card, allPlay):
        #print(f"intplay is : {isIntPlay}")
        return (
            self.color == top_card.color or
            self.type == top_card.type or
            self.color == "all" or
            self.color == "super" or
            allPlay == True
        )

class UnoGame:
    def __init__(self, num_players):
        # Initialize variables for the game
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
        self.previous_card = self.top_card

        self.cheering_player = QMediaPlayer()
        self.cheering_audio_output = QAudioOutput()
        self.cheering_player.setAudioOutput(self.cheering_audio_output)

        self.doublePlayed = False
        self.dpPlayer = None
        self.chiefPlayed = False
        self.playerToSkip = None;
        self.canAllPlay = False
        self.intplayer = None
        self.extplayer = None

    # Winner cheering audio
    def play_cheering_sound(self):
        cheering_sound_path = os.path.join(os.getcwd(), "Sounds", "Winner.wav")
        self.cheering_player.setSource(QUrl.fromLocalFile(cheering_sound_path))
        self.cheering_player.setAudioOutput(self.cheering_audio_output)
        self.cheering_player.play()

    # Checks if any player has won (they have 0 cards in hand)
    def check_winner(self):
        for i, player in enumerate(self.players):
            if len(player) == 0:
                self.play_cheering_sound()  # Play the cheering sound when a winner is found
                return i  # Player index who won
        return -1  # No winner yet

    # Create the normal deck
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

    # Create the super deck
    def initialize_super_deck(self):
        super_card_types = ["extplayall", "intplayall", "doubleplay", "chiefskip"]  # Super card types
        for card_type in super_card_types:
            for _ in range(3):
                self.super_deck.append(Card("super", card_type))
        random.shuffle(self.super_deck)

    # Deal 7 cards to each player to start the game
    def deal_cards(self):
        for player in self.players:
            for _ in range(7):
                if self.deck:
                    player.append(self.deck.pop())

    # Start the discard pile with non-wild cards
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

    # If the deck is empty, discard pile is reshuffled into the deck
    def replenish_deck(self):
        # Move all but the top card to the deck and shuffle
        top = self.discard.pop()
        self.deck = self.discard
        self.discard = [top]
        random.shuffle(self.deck)

    # Checks if a card is playable
    def can_player_play(self, player_index, card):
        top_card = self.top_card
        return card.is_playable(top_card, self.canAllPlay)

    # Playing a card
    def play_card(self, player_index, card_index):
        player_hand = self.players[player_index]
        selected_card = player_hand[card_index]

        # Check if the card can be played
        if (not selected_card.is_playable(self.top_card, self.canAllPlay)):
            return False, "Invalid move. You can't play this card."

        self.previous_card = self.top_card;

        # Conditions if a super card is played
        if selected_card.color == "super":

            selected_card.color = self.previous_card.color

            self.discard.append(selected_card)
            self.top_card = selected_card
            player_hand.pop(card_index)
            self.apply_super_card_effects(selected_card)  # Call a method for super card logic

            #Super Card ExtPlayAll Effect
            if self.extplayer != self.who_next_player() and self.extplayer != None:
                self.canAllPlay = True

            return True, "" # "Super card played!"

        # Super card DoublePlay Effect
        if(self.doublePlayed and self.dpPlayer == self.current_player):
            self.back_a_player()
            self.doublePlayed = False;

        # Play the card
        self.discard.append(selected_card)
        self.top_card = selected_card
        player_hand.pop(card_index)

        # Handle special card actions
        if selected_card.type in ['wild', 'plus4']:
            if selected_card.type == 'plus4':
                self.apply_card_effects(selected_card)  # Ensure the effects are applied
            return True, "Color selection needed."  # Signal that a special image is needed

        # Apply any effects from the card
        self.apply_card_effects(selected_card)

        #Super Card Chief Skip Effect
        if self.chiefPlayed == True and self.who_next_player() == self.playerToSkip:
            self.next_player()
            self.playerToSkip = None
            self.chiefPlayed = False

        #Super Card IntPlayAll Effect
        if self.intplayer == self.who_next_player():
            self.canAllPlay = True
        if self.intplayer == self.current_player and self.canAllPlay == True:
            self.canAllPlay = False
            self.intplayer = None

        #Super Card ExtPlayAll Effect
        if self.extplayer == self.who_next_player():
            self.canAllPlay = False
            self.extplayer = None

        # Checks if any player has won
        winner = self.check_winner()
        if winner != -1:
            self.play_cheering_sound()

        return True, "" #"Card played successfully."

    # Drawing cards
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

            #Super Card Chief Skip Effect if Player Before Skipee Draws
            if self.chiefPlayed == True and self.who_next_player() == self.playerToSkip:
                self.next_player()
                self.playerToSkip = None
                self.chiefPlayed = False

            return True, "" #"Card drawn."
        else:
            return False, "No cards to draw."

    # Moves to the next player based on the current direction
    def next_player(self):
        self.current_player = (self.current_player + self.direction) % self.num_players

    # Stays with the same player based on the current direction (for double play super card)
    def back_a_player(self):
        self.current_player = (self.current_player - (self.direction)) % self.num_players

    def on_color_selected(self, selected_color):
        self.apply_card_effects(self.current_card, selected_color)

    # Uno Action Card Effects
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

    # Super Card Effects
    def apply_super_card_effects(self, card):
        if card.type == "extplayall":
            self.extplayer = self.current_player
        elif card.type == "intplayall":
            self.intplayer = self.current_player
        elif card.type == "doubleplay":
            self.doublePlayed = True;
            self.dpPlayer = self.current_player
        elif card.type == "chiefskip":
            cardsNum = 10
            self.playerToSkip = None
            for i in range (0, self.num_players):
                player_hand = len(self.players[i])

                if player_hand < cardsNum:
                    cardsNum = player_hand
                    self.playerToSkip = i
            self.chiefPlayed = True

    def choose_new_color(self, new_color):
        self.top_card.color = new_color  # Update top card color

    def select_color(self, color):
        self.display_selected_color_image(color)

    def display_selected_color_image(self, color):
        image_name = f"card_select_{color}.png"
        self.show_image_on_discard_pile(image_name)

    # Returns the index of the next player
    def who_next_player(self):
        return (self.current_player + self.direction) % self.num_players
