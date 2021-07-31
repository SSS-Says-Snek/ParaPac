class GameExit(Exception):
    """
    ParaPac interrupt exception which would be raised upon a game exit.
    """


class GameRetry(Exception):
    """
    ParaPac interrupt exception which would be raised when the player requests to retry the game.
    """


class GameOver(Exception):
    """
    ParaPac interrupt exception which would be raised if the player was killed, resulting a game over.
    """


class GameFinish(Exception):
    """
    ParaPac interrupt exception which would be raised when the player wins the game.
    """
