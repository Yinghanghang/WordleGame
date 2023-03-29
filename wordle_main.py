import pygame
import random
import sys
from words_list import *

pygame.init()

# Constants
CORRECT_WORD = "hello"
MARKER_ALPHABET = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
GREY = "#787c7e"
YELLOW = "#c9b458"
GREEN = "#6aaa64"
EMPTY_OUTLINE = "#d3d6da"  # rect outline for empty letter
FILLED_OUTLINE = "#878a8c"  # rect outline for typed letter
LETTER_LENGTH = 5

# Set up fonts
GUESSED_LETTER_FONT = pygame.font.Font("images/FreeSansBold.otf", 52)
MARKER_LETTER_FONT = pygame.font.Font("images/FreeSansBold.otf", 26)

# Set up screen and images
WIDTH, HEIGHT = 635, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
TILES = pygame.image.load("images/grids.png")
# Get a rectangle that encloses the TILES image
TILES_RECT = TILES.get_rect(center=(WIDTH // 2, HEIGHT // 3))

# Set up window caption
pygame.display.set_caption("WORDLE")

# Fill the screen with white and blit the TILE image onto the
# screen at position TILES_RECT
SCREEN.fill("white")
SCREEN.blit(TILES, TILES_RECT)
# updates the screen display
pygame.display.update()

# Set up letter box properties
LETTER_X_SPACING = 85
LETTER_Y_SPACING = 12
BOX_SIZE = 75

# Initialize global variables
current_guess_list = []  # store the letter box object
current_guess_string = ""
guesses_attempts = 0
current_letter_x_pos = 110  # the x position of the letter
guess_markers = []  # letters at the bottom
game_outcome = ""


class GuessMarker:
    def __init__(self, box_x_pos, box_y_pos, letter):
        """
        Initializes properties of the indicator
        """
        self.box_x_pos = box_x_pos
        self.box_y_pos = box_y_pos
        self.box_color = EMPTY_OUTLINE
        self.box_rect = pygame.Rect(self.box_x_pos, self.box_y_pos, 57, 55)
        self.letter = letter
        self.letter_surface = MARKER_LETTER_FONT.render(
            self.letter, True, "white")
        self.letter_rect = self.letter_surface.get_rect(
            center=(self.box_rect.centerx, self.box_rect.centery))

    def draw(self):
        """
        Draws the indicator and its text on the screen.
        """
        pygame.draw.rect(SCREEN, self.box_color, self.box_rect)
        SCREEN.blit(self.letter_surface, self.letter_rect)
        pygame.display.update()


def initiate_guess_markers():
    # initial position of guess marker on the screen
    guess_marker_x, guess_marker_y = 20, 620

    # Drawing the markers on the screen.
    for i in range(len(MARKER_ALPHABET)):
        for letter in MARKER_ALPHABET[i]:
            new_guess_marker = GuessMarker(guess_marker_x, guess_marker_y,
                                           letter)
            new_guess_marker.draw()
            guess_markers.append(new_guess_marker)
            guess_marker_x += 60
        guess_marker_y += 70
        if i == 0:
            guess_marker_x = 50  # start of second row
        elif i == 1:
            guess_marker_x = 110  # start of third row


initiate_guess_markers()


class LetterBOX:
    def __init__(self, letter, box_x_pos, box_y_pos):
        """
        Initializes a letter object with its background color, text color,
        position,
        and other attributes needed for display.
        """
        self.box_color = "white"  # background color of letter box
        self.box_x_pos = box_x_pos
        self.box_y_pos = box_y_pos
        self.box_rect = pygame.Rect(self.box_x_pos, self.box_y_pos,
                                    BOX_SIZE, BOX_SIZE)
        self.letter_color = "black"  # color of the letter text
        self.letter = letter

        #  create a text surface object in which text is drawn on it
        self.letter_surface = GUESSED_LETTER_FONT.render(
            self.letter, True, self.letter_color)
        # creates a new rect object for the letter_surface and set the
        # position of the rect object
        self.letter_rect = self.letter_surface.get_rect(
            center=(self.box_rect.centerx, self.box_rect.centery))

    def draw(self):
        """
        Draws the letter on the screen with its
        background color, text, and outline.
        """
        pygame.draw.rect(SCREEN, self.box_color, self.box_rect)

        # draw a rect with outline if the color is white; don't draw the
        # rect outline if the background color is yellow, grey or green
        if self.box_color == "white":
            # 3 controls the thickness of the outline
            pygame.draw.rect(SCREEN, FILLED_OUTLINE, self.box_rect, 3)

        # render the text again if the color of text changed
        self.letter_surface = GUESSED_LETTER_FONT.render(
            self.letter, True, self.letter_color)

        # put the letter_surface object to the displaying object SCREEN at
        # the position of text_rect using blit
        SCREEN.blit(self.letter_surface, self.letter_rect)

        # show the display SCREEN
        pygame.display.update()

    def delete(self):
        """
        Deletes the letter from the screen by restoring its background
        color and redrawing the outline.
        """
        pygame.draw.rect(SCREEN, "white", self.box_rect)
        pygame.draw.rect(SCREEN, EMPTY_OUTLINE, self.box_rect, 3)
        pygame.display.update()


def create_new_letter(current_letter):
    """
    Create a new letter and add it to the current guess.
    """
    global current_guess_string, current_letter_x_pos
    current_guess_string

    # Append the new letter to the current guess string
    current_guess_string += current_letter

    # Calculate the position of the new letter
    x_pos = current_letter_x_pos
    y_pos = guesses_attempts * 100 + LETTER_Y_SPACING

    # Create a new Letter object and add it to the current guess list
    new_letter = LetterBOX(current_letter, x_pos, y_pos)
    current_guess_list.append(new_letter)

    # Update the x position for the next letter
    current_letter_x_pos += LETTER_X_SPACING

    # Draw all the letters on the screen
    for letter in current_guess_list:
        letter.draw()


def delete_letter():
    """
    Deletes the last letter from the current guess.
    """
    global current_guess_string, current_letter_x_pos

    # string slicing from index 0 to -2
    current_guess_string = current_guess_string[:-1]

    # call function delete() to redraw the rectangle
    current_guess_list[-1].delete()

    # remove letter from current list
    current_guess_list.pop()
    current_letter_x_pos -= LETTER_X_SPACING
    pygame.display.update()


def evaluate_guess(current_guess):
    """
    Check the current guess and decide its colors.
    """
    global current_guess_list, current_guess_string, guesses_attempts, \
        current_letter_x_pos, game_outcome

    marker_color = GREY

    # local variable indicating the status of the current round
    current_round_decided = False

    for i in range(LETTER_LENGTH):
        current_letter = current_guess[i].letter.lower()

        if current_letter in CORRECT_WORD:
            # Correct letter in correct position
            if current_letter == CORRECT_WORD[i]:
                current_guess[i].box_color = GREEN
                marker_color = GREEN
                if not current_round_decided:  # if game has not decided yet
                    game_outcome = "W"
            else:  # Correct letter in wrong position
                current_guess[i].box_color = YELLOW
                marker_color = YELLOW
                # Lost the game already at this point
                current_round_decided = True
                game_outcome = ""

        else:  # Incorrect letter
            current_guess[i].box_color = GREY
            current_round_decided = True
            game_outcome = ""

        for marker in guess_markers:
            if marker.letter == current_letter.upper():
                marker.box_color = marker_color
                marker.draw()
                break

        # reset the marker color to grey
        marker_color = GREY

        # change the text color to better match with the background color
        current_guess[i].letter_color = "white"
        current_guess[i].draw()
        pygame.display.update()

    # Update global variables for next guess
    guesses_attempts += 1
    current_guess_list = []
    current_guess_string = ""
    current_letter_x_pos = 110

    # Check if game is lost
    if guesses_attempts == 6 and game_outcome == "":
        game_outcome = "L"


def feedback(attempt):
    """
    Print the feedback corresponding to the number of attempts
    it took to guess the wordle.
    """
    match attempt:
        case 1:
            return 'Genius!'
        case 2:
            return 'Magnificent!'
        case 3:
            return 'Impressive!'
        case 4:
            return 'Splendid!'
        case 5:
            return 'Great!'
        case 6:
            return 'Phew!'


def show_result():
    """
    Display the game result and play again message on the screen.
    """
    # Draw a white rectangle on the screen to display the message.
    pygame.draw.rect(SCREEN, "white", (10, 600, 1000, 600))

    # Render the game result message.
    feedback_font = pygame.font.Font("images/FreeSansBold.otf", 25)
    feedback_text = feedback_font.render(f" {feedback(guesses_attempts)}",
                                         True, "black")
    feedback_rect = feedback_text.get_rect(center=(WIDTH / 2, 650))
    play_again_font = pygame.font.Font("images/FreeSansBold.otf", 25)
    word_text = play_again_font.render(f"The word was {CORRECT_WORD}.",
                                       True, "black")
    word_rect = word_text.get_rect(center=(WIDTH / 2, 700))
    SCREEN.blit(feedback_text, feedback_rect)
    SCREEN.blit(word_text, word_rect)

    # Render the play again message.
    play_again_text = play_again_font.render(
        "Press ENTER to Play Again", True, "black")
    play_again_rect = play_again_text.get_rect(center=(WIDTH / 2, 750))
    SCREEN.blit(play_again_text, play_again_rect)

    pygame.display.update()


def reset_state():
    """
    Resets all global variables to their default states.
    """
    global guesses_attempts, CORRECT_WORD, current_guess_list, \
        current_guess_string, game_outcome

    # Fill the screen with white color and blit the tiles.
    SCREEN.fill("white")
    SCREEN.blit(TILES, TILES_RECT)

    guesses_attempts = 0
    game_outcome = ""
    CORRECT_WORD = random.choice(WORDS_LIST)
    current_guess_list = []
    current_guess_string = ""
    pygame.display.update()

    # Reset the guess markers
    for marker in guess_markers:
        marker.box_color = EMPTY_OUTLINE
        marker.draw()


while True:
    if game_outcome:  # 'W' or 'L'
        show_result()
    # Handle events
    for event in pygame.event.get():
        # Quit the game if the user closes the window
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # If a key is pressed
        if event.type == pygame.KEYDOWN:
            # If Backspace is pressed, delete the last letter from the guess
            if event.key == pygame.K_BACKSPACE:
                if len(current_guess_string) > 0:
                    delete_letter()
            # If Enter is pressed
            elif event.key == pygame.K_RETURN:
                if game_outcome:  # if the game has ended: lose or win
                    reset_state()
                else:  # If a valid guess was made, check it
                    if len(current_guess_string) == LETTER_LENGTH \
                      and current_guess_string.lower() in WORDS_LIST:
                        evaluate_guess(current_guess_list)
            else:  # If a letter key is pressed, create a new letter
                # and add it to the guess
                key_pressed = event.unicode.upper()
                if key_pressed.isalpha():
                    # print(key_pressed)
                    if len(current_guess_string) < 5:
                        create_new_letter(key_pressed)
