"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # checking who's turn it is based on the number of X and O
    # Since X starts first, the first player should be X
    # (done)
    count_x = 0
    count_o = 0
    for row in board:
        for cell in row:
            if cell == X:
                count_x += 1
            elif cell == O:
                count_o += 1
    if count_x <= count_o:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    i refers to the row in the cell, j refers to the cell in the row
    """
    # (done)
    actions = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # (done)
    copied_board = copy.deepcopy(board)
    if copied_board[action[0]][action[1]] != EMPTY:
        raise ValueError
    else:
        copied_board[action[0]][action[1]] = player(copied_board)
        return copied_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # define possibilities of winning for each cell
    # all cells can score horizontally or vertically, but only
    # the corner and center cells can score diagonally
    # winner is executed before a player turn (ie after a winning
    # move is made, it will only know at the start of the next turn
    # AFTER the action is done)
    # (done)
    def check_nwse_diagonal(cell):
        player = board[cell[0]][cell[1]]
        # determine for center tile
        if (cell[0] == 1) and (cell[1] == 1):
            if board[cell[0] - 1][cell[1] - 1] == player and board[cell[0] + 1][cell[1] + 1] == player:
                return player
            else:
                return False
        else:
            # cehcking if cell is on top left corner
            try:
                if board[cell[0] + 1][cell[1] + 1] == player and board[cell[0] + 2][cell[1] + 2] == player:
                    return player
                else:
                    return False
            # must mean the cell is on bottom right corner
            except IndexError:
                if board[cell[0] - 1][cell[1] - 1] == player and board[cell[0] - 2][cell[1] - 2] == player:
                    return player
                else:
                    return False

    def check_swne_diagonal(cell):
        player = board[cell[0]][cell[1]]
        # determine for center tile
        if (cell[0] == 1) and (cell[1] == 1):
            if board[cell[0] - 1][cell[1] + 1] == player and board[cell[0] + 1][cell[1] - 1] == player:
                return player
            else:
                return False
        else:
            # checking if cell is on bottom left corner
            try:
                if board[cell[0] + 1][cell[1] - 1] == player and board[cell[0] + 2][cell[1] - 2] == player:
                    return player
                else:
                    return False
            # must mean the cell is on top right corner
            except IndexError:
                if board[cell[0] - 1][cell[1] + 1] == player and board[cell[0] - 2][cell[1] + 2] == player:
                    return player
                else:
                    return False

    def check_horizontal(cell):
        player = board[cell[0]][cell[1]]
        # determine for center column
        if (cell[0] == 1) and (cell[1] == 1):
            if board[cell[0]][cell[1] - 1] == player and board[cell[0]][cell[1] + 1] == player:
                return player
            else:
                return False
        else:
            # checking if cell is to the left
            try:
                if board[cell[0]][cell[1] + 1] == player and board[cell[0]][cell[1] + 2] == player:
                    return player
                else:
                    return False
            # must mean cell is to the right
            except IndexError:
                if board[cell[0]][cell[1] - 1] == player and board[cell[0]][cell[1] - 2] == player:
                    return player
                else:
                    return False

    def check_vertical(cell):
        player = board[cell[0]][cell[1]]
        # determine for center column
        if (cell[0] == 1) and (cell[1] == 1):
            if board[cell[0] - 1][cell[1]] == player and board[cell[0] + 1][cell[1]] == player:
                return player
            else:
                return False
        else:
            # checking if cell is on top
            try:
                if board[cell[0] + 1][cell[1]] == player and board[cell[0] + 2][cell[1]] == player:
                    return player
                else:
                    return False
            # must mean cell is at the bottom
            except IndexError:
                if board[cell[0] - 1][cell[1]] == player and board[cell[0] - 2][cell[1]] == player:
                    return player
                else:
                    return False

    winner = None
    for i in range(len(board)):
        for j in range(len(board[i])):
            if winner == None:
                nwse_diagonal = False
                swne_diagonal = False
                if (i == 0 and j == 0) or (i == 2 and j == 2):
                    nwse_diagonal = True
                elif (i == 0 and j == 2) or (i == 2 and j == 0):
                    swne_diagonal = True
                if nwse_diagonal:
                    diagonal = check_nwse_diagonal((i, j))
                elif swne_diagonal:
                    diagonal = check_swne_diagonal((i, j))
                horizontal = check_horizontal((i, j))
                vertical = check_vertical((i, j))
                if diagonal:
                    winner = diagonal
                elif horizontal:
                    winner = horizontal
                elif vertical:
                    winner = vertical
    return winner


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #(done)
    if (winner(board)):
        return True
    else:
        blanks = 0
        for row in board:
            for cell in row:
                if cell != EMPTY:
                    blanks += 1
        if blanks == 9:
            return True
        else:
            return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # (done)
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    turn = player(board)
    # in checking for X or O, the checker recurses until a terminal
    # condition is met and choosing the first optimal solution (1
    # or -1)
    # a list of actions is returned as a tuple (action, score) and
    # is then appropriately sorted, with the action leading to
    # the highest/lowest score returned
    def max_check(board, recurse=0):
        if terminal(board):
            score = utility(board)
            # divide score based on how deep the recursion went by
            for i in range(recurse):
                score /= 2
            return score
        else:
            values_list = []
            for action in actions(board):
                values_list.append(min_check(result(board, action), recurse + 1))
            values_list.sort(reverse=True)
            return (values_list[0])

    def min_check(board, recurse=0):
        if terminal(board):
            score = utility(board)
            # divide score based on how deep the recursion went by
            for i in range(recurse):
                score /= 2
            return score
        else:
            values_list = []
            for action in actions(board):
                values_list.append(max_check(result(board, action), recurse + 1))
            values_list.sort()
            return (values_list[0])
                
    action_list = []
    for action in actions(board):
        if turn == X:
            action_list.append((action, min_check(result(board, action))))
        elif turn == O:
            action_list.append((action, max_check(result(board, action))))
    if turn == X:
        action_list.sort(key=lambda tup: tup[1], reverse=True)
    elif turn == O:
        action_list.sort(key=lambda tup: tup[1])
    return action_list[0][0]
