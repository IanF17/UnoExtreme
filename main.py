# main.py
from PySide6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QDialog,
    QHBoxLayout, QMessageBox, QGridLayout, QListWidget, QListWidgetItem
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
import sys
from UnoGame import UnoGame

class ColorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose a Color")
        self.selected_color = None

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Create buttons for each color
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
        self.accept()  # Close the dialog with an accepted status

class UnoGameWindow(QWidget):
    def __init__(self, num_players=3):
        super().__init__()
        self.uno_game = UnoGame(num_players)  # Initialize the game
        self.num_players = num_players
        self.init_ui()
        self.set_background_image("assets/backgrounds/Background2.png")


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
        self.super_deck_label.mousePressEvent = self.on_deck_clicked  # Connect click event
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
        self.status_label = QLabel("Game started!")
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

        # Draw Card Button at Bottom of Screen
        # self.draw_button = QPushButton('Draw Card', self)
        # self.draw_button.clicked.connect(self.draw_card)
        # action_layout.addWidget(self.draw_button)

        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def set_background_image(self, image_path):
        self.setStyleSheet(f"""
            QWidget {{
                background-image: url({image_path});
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
            }}
        """)

    def on_deck_clicked(self, event):
        self.draw_card()

    def update_current_player_label(self):
        current_player = self.uno_game.current_player + 1
        self.current_player_label.setText(f"Player {current_player}'s Turn")

    def update_player_hand(self):
        # Clear existing hand layout
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
            button.card_index = idx  # Custom attribute to track card index
            self.hand_layout.addWidget(button)
            self.card_buttons.append(button)

    def draw_card(self):
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

    def update_discard_pile(self):
        top_card = self.uno_game.top_card
        discard_image_path = f'assets/cards/{top_card.color}_{top_card.type}.png'
        pixmap = QPixmap(discard_image_path).scaled(100, 150, Qt.KeepAspectRatio)
        self.discard_label.setPixmap(pixmap)

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
                # After color is selected, update the discard pile with the special image
                # selected_color = self.uno_game.top_card.color  # Retrieve the selected color
                # special_image_path = f'assets/cards/card_selected_{selected_color}.png'
                # self.discard_label.setPixmap(QPixmap(special_image_path).scaled(100, 150, Qt.KeepAspectRatio))
            else:
                self.update_discard_pile()
                self.next_turn()

        else:
            QMessageBox.warning(self, "Invalid Move", message)

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
    window = UnoGameWindow(num_players=4)
    window.show()
    sys.exit(app.exec())
