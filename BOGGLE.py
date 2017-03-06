import random
import os
import time
from collections import defaultdict
from nltk.corpus import words
import urllib.request
import json

def clear_console():
    """Clears the console (need this to ensure turns are private).
    """
    os.system('cls' if os.name=='nt' else 'clear')

def launch_game():
    """ Elicits user input for game parameters; checks validity of input.
    Returns list of game parameters: [player_names, num_players, seconds_per_turn].
    E.g. [["Jacob", "Casey"], 2, 180]
    """

    clear_console()

    print("\n\tWELCOME!", "PLEASE REVIEW RULES: http://www.wikihow.com/Play-Boggle",
              "PLEASE SET UP GAME PARAMETERS:", sep="\n\n\t")

    # get number of players
    num_players = 0
    while num_players < 2:
        try: num_players = int(input("\n\t  How many players? "))
        except: print("\t\t Integer input required.")

    # get list of player names
    list_players = []
    while len(list_players) != num_players:
        try:
            list_players = str(input("\t  Player names, separated by commas: ")).split(",")
            list_players = [player.strip() for player in list_players]
        except: print("\t\t String input required.")

    # get duration of turns (in seconds)
    len_turns = 0
    while len_turns < 30 or len_turns > 180:
        try: len_turns = int(input("\t  How many seconds per turn? (max: 180, min: 30) "))
        except: print("\t\t Integer input required.")

    return list_players, num_players, len_turns

def create_board():
    """Creates a 4x4 'board' of random letters.
    Returns 'board' of 16 letters as flat list for calculations.
    Use show_board(create_board()) to display 16 letters as 4x4 table for players.
    """
    alph = ['a ','a ','a ','b ','b ','c ','c ','d ','d ','e ','e ','e ',
                'f ','g ','h ','i ','i ','i ','j ','k ','l ','l ','m ','m ',
                'n ','n ','o ','o ','o ','p ','q ','r ','r ','s ','s ',
                't ','t ','u ','u ','v ','w ','x ','y ','y ','y ','z ']
    boggle_board = random.sample(alph, 16)
    return boggle_board

def show_board(boggle_board):
    """Prints 4x4 Boggle board for players to examine.
    Argument: List of 16 letters from create_board().
    """
    print('\t  '+' '.join(boggle_board[0:4]))
    print('\t  '+' '.join(boggle_board[4:8]))
    print('\t  '+' '.join(boggle_board[8:12]))
    print('\t  '+' '.join(boggle_board[12:16])+'\n')

def track_plays(player_list, len_turns, boggle_board):
    """Gives each player a time-limited turn to record the words they see on the board.

    Arguments:
    player_list is a list of player names, e.g. ["Casey","Jacob"]
    len_turns is the integer duration of a turn in seconds.
    boggle_board is a list of 16 letters from create_board().

    Returns a list of tuples; each tuple is (player_name, word_played)
    E.g. [('Jacob', 'two'), ('Jacob', 'malice'), ('Casey','toss')]
    """

    play_tracker = list()
    for name in player_list:

        clear_console()
        print("\n\tOK, " + name + ", it's your turn.\n")
        show_board(boggle_board)
        print("\tEnter a legal word and hit return:\n")

        elapsed_time = 0
        while elapsed_time < len_turns:
            start_time = time.time()
            word_played = input("\t  >> ")
            play_tracker.append((name, word_played))
            end_time = time.time()
            time_delta = end_time - start_time
            elapsed_time += time_delta

    return play_tracker

def validate_plays(play_tracker, boggle_board):
    """Eliminates plays that violate game rules.

    Arguments:
    play_tracker is a list of tuples: [(player_name, word_played), (player_name, word_played), ...]
    boggle_board is a list of 16 letters from create_board().

    Returns:
    play_tracker, as above but removed all tuples representing illegal plays.
    """

    # since play_tracker is player_name-to-word mapping,
    # create dictionary: word-to-player_name mapping
    word_to_players = defaultdict(list)
    for name, word_played in play_tracker:
        word_to_players[word_played].append(name)

    for word in word_to_players.keys():
        # remove reduntant player names
        word_to_players[word] = set(word_to_players[word])
        # validate plays against 'unique word' rule
        if len(word_to_players[word]) > 1:
            play_tracker = [(name, word_played) for name, word_played in play_tracker if word_played != word]

    # validate plays against 'longer than 2 letters' rule
    play_tracker = [(name, word_played) for name, word_played in play_tracker if len(word_played) > 2]

    # validate plays against 'English language' rule
    play_tracker = [(name, word_played) for name, word_played in play_tracker if word_played in words.words()]

    # validate plays against online Boggle solver
    board_as_str = ''.join([i.strip() for i in boggle_board])
    my_url = "http://fuzzylogicinc.net/boggle/Solver.svc?BoardID="+board_as_str+"&Length=3"
    with urllib.request.urlopen(my_url) as response:
        my_web_page = response.read()
    my_page_as_json = json.loads(my_web_page.decode('utf-8'))
    solver_results = list()
    for dict in my_page_as_json['Solutions']:
        solver_results.append(dict['Word'])
    play_tracker = [(name, word_played) for name, word_played in play_tracker if word_played in solver_results]

    return play_tracker


def score_plays(player_list, play_tracker, boggle_board):
    """Assign scores to players, and display scores.

    Arguments:
    player_list is a list of player names, e.g. ["Casey","Jacob"]
    play_tracker is a list of tuples: [(player_name, word_played), (player_name, word_played), ...]
    boggle_board is a list of 16 letters from create_board().
    """

    clear_console()

    # go word for word, assign points based on length
    player_to_scores = defaultdict(int)
    for name, word_played in play_tracker:
        score = 0
        word_length = len(word_played)
        if word_length < 5: score = 1
        elif word_length < 6: score = 2
        elif word_length < 7: score = 3
        elif word_length < 8: score = 5
        else: score = 11
        player_to_scores[name] += score

    # invert word_to_players
    player_to_words = defaultdict(list)
    for name, word_played in play_tracker:
        player_to_words[name].append(word_played)

    # show board
    print()
    show_board(boggle_board)
    for i in range(len(player_list)):
        player = player_list[i]
        total_points = player_to_scores[player]
        words_played = player_to_words[player]
        print("\t {} scored {} points for {}".format(player, total_points, words_played))
    print()

def play_game():
    my_game = launch_game()
    my_board = create_board()
    my_plays = track_plays(my_game[0], my_game[2], my_board)
    my_validated_plays = validate_plays(my_plays, my_board)
    my_results = score_plays(my_game[0], my_validated_plays, my_board)

play_game()