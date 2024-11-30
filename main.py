 # main.py
from PySide6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QDialog,
    QHBoxLayout, QMessageBox, QGridLayout, QListWidget, QListWidgetItem
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QPixmap, QIcon, QPainter, QFont
from PySide6.QtCore import Qt, QUrl, QThread
import sys, os
from UnoGame import UnoGame

class StartMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Menu")
        self.setFixedSize(300, 200)

        # Layout for buttons
        layout = QVBoxLayout()

        # Title label
        title = QLabel("Welcome to Uno Game!")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Play button
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.start_game)
        layout.addWidget(play_button)

        # Info button
        info_button = QPushButton("Info")
        info_button.clicked.connect(self.show_info)
        layout.addWidget(info_button)

        # Quit button
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close_game)
        layout.addWidget(quit_button)

        self.setLayout(layout)

    def start_game(self):
        self.hide()  # Hide menu when game starts
        self.game_window = UnoGameWindow()
        self.game_window.show()

    def show_info(self):
        self.info_window = InfoWindow()
        self.info_window.show()

    def close_game(self):
        QApplication.instance().quit()

class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Info")
        self.setFixedSize(300, 200)

        #Info Menu Option
        layout = QVBoxLayout()
        info_label = QLabel("Welcome to my adaptation of the classic game Uno!\n\nGameplay persists as normal, with the twist of Super \nCards added to the game. These Super Cards can\n be played at any time, like wild cards, and may have\n drastic effects on the game. Enjoy!")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        self.setLayout(layout)

class ColorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose a Color")
        self.selected_color = None

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Buttons for each color
        colors = ['red', 'blue', 'green', 'yellow']
        for color in colors:
            button = QPushButton(color.capitalize())
            button.setStyleSheet(f'background-color: {color}')
            button.clicked.connect(lambda _, c=color: self.set_color(c))
            button_layout.addWidget(button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_color(self, color):
        self.selected_color = color
        self.accept()

class UnoGameWindow(QWidget):
    def __init__(self, num_players=4):
        super().__init__()
        self.uno_game = UnoGame(num_players)
        self.num_players = num_players

        # Set up background and music
        self.background_image = QPixmap("assets/backgrounds/Background12.png")

        self.background_music_player = QMediaPlayer()
        self.background_audio_output = QAudioOutput()
        self.background_music_player.setAudioOutput(self.background_audio_output)
        self.background_audio_output.setVolume(0.05)
        self.setup_background_music()

        self.sfx_player = QMediaPlayer()
        self.sfx_audio_output = QAudioOutput()
        self.sfx_player.setAudioOutput(self.sfx_audio_output)

        self.init_ui()

    def setup_background_music(self):
        music_file_path = os.path.join(os.getcwd(), "sounds", "backgroundMusic.wav")
        self.background_music_player.setSource(QUrl.fromLocalFile(music_file_path))
        self.background_music_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.background_music_player.play()

    def play_sound_effect(self, sound_file):
        file_path = os.path.join(os.getcwd(), "sounds", sound_file)
        self.sfx_player.setSource(QUrl.fromLocalFile(file_path))
        self.sfx_player.play()

    def init_ui(self):
        self.setWindowTitle("Uno Game")
        self.setGeometry(100, 100, 1000, 600)  # Width x Height

        # Main layout
        main_layout = QVBoxLayout()

        # Top layout: Deck and Discard Pile
        top_layout = QHBoxLayout()

        # Deck
        self.deck_label = QLabel(self)
        deck_pixmap = QPixmap('assets/cards/back.png').scaled(100, 150, Qt.KeepAspectRatio)
        self.deck_label.setPixmap(deck_pixmap)
        self.deck_label.setAlignment(Qt.AlignCenter)
        self.deck_label.setCursor(Qt.PointingHandCursor)  # Change cursor to pointer
        self.deck_label.mousePressEvent = self.on_deck_clicked  # Connect click event
        top_layout.addWidget(self.deck_label)

        self.super_deck_label = QLabel(self)
        super_deck_pixmap = QPixmap('assets/cards/super_card_back.png').scaled(100, 150, Qt.KeepAspectRatio)
        self.super_deck_label.setPixmap(super_deck_pixmap)
        self.super_deck_label.setAlignment(Qt.AlignCenter)
        self.super_deck_label.setCursor(Qt.PointingHandCursor)  # Change cursor to pointer
        self.super_deck_label.mousePressEvent = self.on_super_deck_clicked  # Connect click event
        top_layout.addWidget(self.super_deck_label)

        # Discard Pile
        self.discard_label = QLabel(self)
        top_card = self.uno_game.top_card
        discard_image_path = f'assets/cards/{top_card.color}_{top_card.type}.png'
        discard_pixmap = QPixmap(discard_image_path).scaled(100, 150, Qt.KeepAspectRatio)
        self.discard_label.setPixmap(discard_pixmap)
        self.discard_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.discard_label)

        main_layout.addLayout(top_layout)

        # Middle layout: Current Player and Instructions
        middle_layout = QHBoxLayout()

        # Current Player Info
        self.current_player_label = QLabel(self)
        self.update_current_player_label()
        middle_layout.addWidget(self.current_player_label)

        # Game Status
        self.status_label = QLabel(" ") #Game Started!
        middle_layout.addWidget(self.status_label)

        main_layout.addLayout(middle_layout)

        # Player's Hand
        self.hand_layout = QHBoxLayout()
        self.update_player_hand()
        main_layout.addLayout(self.hand_layout)

        # Action Buttons
        action_layout = QHBoxLayout()

        # Play Selected Card
        self.play_button = QPushButton('Play Selected Card', self)
        self.play_button.clicked.connect(self.play_selected_card)
        action_layout.addWidget(self.play_button)

        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    # Draws background image in
    def paintEvent(self, event):
            """
            Override the paint event to draw the background image.
            """
            painter = QPainter(self)

            painter.drawPixmap(self.rect(), self.background_image)

    def set_background_image(self, image_path):
        self.setStyleSheet(f"""
            QWidget {{
                background-image: url({image_path});
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
            }}
        """)

    # Draw a card
    def on_deck_clicked(self, event):
        self.draw_card()

    # Draw a super card
    def on_super_deck_clicked(self, event):
        if self.uno_game.super_deck:
            super_card = self.uno_game.super_deck.pop()  # Draw from the super deck
            self.uno_game.players[self.uno_game.current_player].append(super_card)
            self.play_sound_effect("DrawCard.wav")
            #self.status_label.setText("Super card drawn!")
            self.update_player_hand()  # Update hand to show the new super card
            self.uno_game.current_player = (self.uno_game.current_player + self.uno_game.direction) % self.num_players
            self.update_current_player_label()  # Update the label to show the next player's turn
            self.update_player_hand()  # Update the hand to show the next player's cards
        else:
            QMessageBox.warning(self, "Super Deck Empty", "No super cards left to draw.")

    # Draw a normal card
    def draw_card(self):
        self.play_sound_effect("DrawCard.wav")
        success, message = self.uno_game.draw_card(self.uno_game.current_player)
        if success:
            self.status_label.setText(message)
            self.update_player_hand()  # Update the current player's hand after drawing
            # Switch to the next player
            self.uno_game.current_player = (self.uno_game.current_player + self.uno_game.direction) % self.num_players
            self.update_current_player_label()  # Update the label to show the next player's turn
            self.update_player_hand()  # Update the hand to show the next player's cards
        else:
            QMessageBox.warning(self, "Draw Failed", message)

    # Displays which player's turn it is
    def update_current_player_label(self):
        current_player = self.uno_game.current_player + 1

        self.current_player_label.setText(f"    Player {current_player}'s Turn")

        # Set the font: make it larger, and choose a fun font
        font = QFont("Comic Sans MS", 20, QFont.Bold)  # You can change "Comic Sans MS" to any other font
        self.current_player_label.setFont(font)

        # Set the color of the text
        self.current_player_label.setStyleSheet("QLabel { color: #10123a; }")

    def update_player_hand(self):
        for i in reversed(range(self.hand_layout.count())):
            widget = self.hand_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Get current player's hand
        current_player = self.uno_game.current_player
        player_hand = self.uno_game.players[current_player]

        self.card_buttons = []
        for idx, card in enumerate(player_hand):
            button = QPushButton(self)
            card_image_path = f'assets/cards/{card.color}_{card.type}.png'
            pixmap = QPixmap(card_image_path).scaled(80, 120, Qt.KeepAspectRatio)
            icon = QIcon(pixmap)
            button.setIcon(icon)
            button.setIconSize(pixmap.size())
            button.setCheckable(True)
            button.setFixedSize(90, 130)
            button.card_index = idx
            self.hand_layout.addWidget(button)
            self.card_buttons.append(button)

    # Discard pile manager
    def update_discard_pile(self):
        top_card = self.uno_game.top_card
        if top_card.type == "chiefskip" or top_card.type == "doubleplay" or top_card.type == "extplayall" or top_card.type == "intplayall":
            discard_image_path = f'assets/cards/super_{top_card.type}.png'  # Super card image
        else:
            discard_image_path = f'assets/cards/{top_card.color}_{top_card.type}.png'
        pixmap = QPixmap(discard_image_path).scaled(100, 150, Qt.KeepAspectRatio)
        self.discard_label.setPixmap(pixmap)

    # Button to play a selected card
    def play_selected_card(self):

        selected_buttons = [btn for btn in self.card_buttons if btn.isChecked()]
        if not selected_buttons:
            QMessageBox.warning(self, "No Selection", "Please select a card to play.")
            return
        if len(selected_buttons) > 1:
            QMessageBox.warning(self, "Multiple Selections", "Please select only one card to play.")
            return

        selected_button = selected_buttons[0]
        card_index = selected_button.card_index
        success, message = self.uno_game.play_card(self.uno_game.current_player, card_index)

        if success:
            self.status_label.setText(message)
            if "Color selection needed" in message:
                self.prompt_color_selection()  # Wild/Plus4 card played, choose a new color
            else:
                self.update_discard_pile()
                self.next_turn()

        else:
            QMessageBox.warning(self, "Invalid Move", message)

        self.play_sound_effect("PlayCard.wav")


    # Color selection when a wild card is played
    def prompt_color_selection(self):
        dialog = ColorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_color = dialog.selected_color
            self.uno_game.choose_new_color(selected_color)  # Set new color in game logic
            special_image_path = f'assets/cards/card_selected_{selected_color}.png'
            pixmap = QPixmap(special_image_path).scaled(100, 150, Qt.KeepAspectRatio)
            self.discard_label.setPixmap(pixmap)

            self.next_turn()

    def next_turn(self):
        # Proceed to the next player's turn
        self.uno_game.current_player = (self.uno_game.current_player + self.uno_game.direction) % self.num_players
        winner = self.uno_game.check_winner()
        if winner != -1:
            QMessageBox.information(self, "Game Over", f"Player {winner + 1} wins!")
            self.play_button.setEnabled(False)
            #self.draw_button.setEnabled(False)
            QApplication.quit()
        else:
            self.update_current_player_label()
            self.update_player_hand()

    def animate_color_selection(self, selected_color):
        """Animates the selected color card landing on the discard pile."""
        # Update the discard pile to show the selected color
        discard_image_path = f'assets/cards/{selected_color}_wild.png'  # Use wild card of selected color
        pixmap = QPixmap(discard_image_path).scaled(100, 150, Qt.KeepAspectRatio)

        # Set the new color image on the discard pile
        self.discard_label.setPixmap(pixmap)

        # Update the game's top card color to the selected color
        self.uno_game.top_card.color = selected_color

    def on_color_selected(self, color):
        self.uno_game.select_color(color)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = StartMenu()
    menu.show()
    #window = UnoGameWindow(num_players=4)
    #window.show()
    sys.exit(app.exec())
