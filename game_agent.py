"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""

import random

# ------------------------------------------------------------------------------


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


# ------------------------------------------------------------------------------


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    # This function acts as a dispatch mechanism so that different methods can
    # easily be tested against each other.
    return scoring_function_lecture(game, player)

# ------------------------------------------------------------------------------

def scoring_function_random(game, player):
    """ This scoring function returns a random value."""
    return random.random()

# ------------------------------------------------------------------------------

def scoring_function_naive(game, player):
    """ This function simply returns the number of legal moves for the given
    player"""
    return float(game.get_legal_moves(player).__len__())

# ------------------------------------------------------------------------------

def scoring_function_adaptive(game, player):
    """ This scoring function calculates the following score:

    This should ensure that an enemy move with more possibilities is not
    taken out of the consideration. In a hand full of manual experiments it
    seemed that situations where the number of own moves is 2 and the number
    of opponent moves is between 2 and 5 still include a good chance to win.
    As the moves are restricted to an L-Shape, the number of possible moves
    compared to each other is not necessarily significant."""

    ownMoves = game.get_legal_moves(player).__len__()
    opponentMoves = game.get_legal_moves(game.get_opponent(player)).__len__()
    numberOfMaxMoves = game.height * game.width
    numberOfMovesDone = game.move_count
    scalingFactor = 0.2 * numberOfMaxMoves

    return float(ownMoves - (scalingFactor / numberOfMovesDone) * opponentMoves)

# ------------------------------------------------------------------------------

def scoring_function_lecture(game, player):
    """ This scoring function calculates the following score:

        (1 * own moves) - (2 * opponent_moves)

    This should ensure that an enemy move with less movement options is
    weighted stronger than a move with less possible successor states."""

    ownMoves = game.get_legal_moves(player).__len__()
    opponentMoves = game.get_legal_moves(game.get_opponent(player)).__len__()

    return 1.3 * ownMoves - 1.75 * opponentMoves

# ------------------------------------------------------------------------------

def scoring_function_strategy(game, player):

    # If we are in the beginning of the game, ...
    if (game.move_count <= 0.2 * game.height * game.width):
        return scoring_function_naive(game, player)

    # If we are in the middle of the game, ...
    if (game.move_count <= 0.75 * game.height * game.width):
        return scoring_function_lecture(game, player)

    # If we are in end-game, ...
    return scoring_function_longest_path(game, player)

# ------------------------------------------------------------------------------

def scoring_function_longest_path(game, player):

    """This scoring function should prefer moves that have a longer path for
    the player than for the opponent. It should only be used in endgame as the
    performance impact is significant!"""

    own_longest_path = 0
    nme_longest_path = 0

    if not game.get_legal_moves(player):
        return 0

    for move in game.get_legal_moves(player):

        gamestate = game.forecast_move(move)

        score = scoring_function_longest_path(gamestate, player) + 1

        if score > own_longest_path:
            own_longest_path = score

    for move in game.get_legal_moves(game.get_opponent(player)):

        gamestate = game.forecast_move(move)

        score = scoring_function_longest_path(gamestate, game.get_opponent(player)) + 1

        if score > nme_longest_path:
            nme_longest_path = score

    return float(own_longest_path - nme_longest_path)
# ------------------------------------------------------------------------------


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        ----------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        if not legal_moves:
            return (-1, -1)

        # If the initial position was not set, set the player close to the
        # middle. The // operator means INTEGER DIVISION.
        if not game.move_count:
            row = game.height // 2
            col = game.width // 2
            return (row, col)

        # Ensure that a next move is always selected, even when the search
        # function is not returning any information. To ensure that there is
        # some dynamic involved the move is selected randomly.
        best_possible_move = random.choice(legal_moves)
        best_possible_score = float('-inf')

        try:

            # The first iteration level is set to 1 in case of `self.iterative`
            # being true, otherwise it is set to the search_depth which defines
            # the maximum level to be recursed to.
            if self.iterative:
                depth = 1
            else:
                depth = self.search_depth

            # Initialize an infinite loop to find the best possible value.
            while True:

                # Dispatch parameters to the method which was defined in the
                # game setup.
                score, possible_move = \
                    getattr(self, self.method)(game, depth)

                # update score and move if a better move was found
                if score > best_possible_score:
                    best_possible_score = score
                    best_possible_move = possible_move

                # in iterative mode, a new iteration should be triggered with
                # an additional level of depth. This is done until a Timeout
                # Exception is thrown or until all levels were discovered.
                if self.iterative:
                    depth += 1
                else:
                    break

        except Timeout as t:
            # When a Timeout Exception is catched, the last discovered best
            # move is returned.
            return best_possible_move

        # Return the best move found.
        return best_possible_move

# ------------------------------------------------------------------------------

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """

        # When the defined time is exhausted, a Timeout Exception is raised to
        # end the search process.
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # If a win or lose of my player was found, the relating utility() value
        # and the relating move are returned.
        if game.is_winner(self) or game.is_loser(self):
            return game.utility(self), game.get_player_location(self)

        # When depth has reached 0, the nodes must be evaluted by calling the
        # scoring function. The score of the relating move and the relating
        # move are returned.
        if depth == 0:
            return self.score(game, self), game.get_player_location(self)

        # Best score and move are initialized, with regard to the
        # maximizing_player bool value.
        best_score = float('-inf') if maximizing_player else float('+inf')
        best_move = (-1, -1)

        # Iterate over all possible children.
        for move in game.get_legal_moves():

            # A copy of the current game is created that reflects the current
            # move. This is important to ensure progress in the search.
            gamestate = game.forecast_move(move)

            # Execute recursive minimax calls with depth reduced by one and
            # maximizing_player flipped to the opposite.
            score, _ = self.minimax(gamestate, depth-1, not maximizing_player)

            # If the last iteration found a move with a better score, best_score
            # and best_move are updated.
            if self.score_is_better(score, best_score, maximizing_player):
                best_score = score
                best_move = move

        return best_score, best_move

# ------------------------------------------------------------------------------

    def score_is_better(self, score, best_score, maximizing_player):
        """This helper function evaluates two scores against each other and
        evaluates if the new score is better than the latest best_score, with
        respect to the maximizing_player bool value.

        Parameters
        ----------
        score : float
            Score that was found in the last search

        best_score : float
            Best score found so far

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        bool
            True if score is better than the best_score
            False otherwise
        """
        if maximizing_player and score > best_score:
            return True

        if not maximizing_player and score < best_score:
            return True

# ------------------------------------------------------------------------------

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # If a win or lose of my player was found, the relating utility() value
        # and the relating move are returned.
        if game.is_winner(self) or game.is_loser(self):
            return game.utility(self), game.get_player_location(self)

        # When depth has reached 0, the nodes must be evaluted by calling the
        # scoring function. The score of the relating move and the relating
        # move are returned.
        if depth == 0:
            return self.score(game, self), game.get_player_location(self)

        # Best score and move are initialized, with regard to the
        # maximizing_player bool value.
        best_score = float('-inf') if maximizing_player else float('+inf')
        best_move = (-1, -1)

        # Iterate over all possible children.
        for move in game.get_legal_moves():

            # A copy of the current game is created that reflects the current
            # move. This is important to ensure progress in the search.
            gamestate = game.forecast_move(move)

            # Execute recursive minimax calls with depth reduced by one and
            # maximizing_player flipped to the opposite.
            score, _ = self.alphabeta(gamestate, depth-1, alpha, beta, not maximizing_player)

            # If the last iteration found a move with a better score, best_score
            # and best_move are updated.
            if self.score_is_better(score, best_score, maximizing_player):
                best_score = score
                best_move = move

            # Alpha-Beta addition
            if maximizing_player:
                if best_score >= beta:
                    break
                alpha = max(alpha, best_score)

            if not maximizing_player:
                if best_score <= alpha:
                    break
                beta = min(beta, best_score)

        return best_score, best_move