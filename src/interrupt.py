class GameExit(Exception):
    """
    ParaPac interrupt exception which would be raised upon a game exit.
    """


class GamePaused(Exception):
    """
    ParaPac interrupt exception which would be raised upon a game pause.
    """


class GameRetry(Exception):
    """
    ParaPac interrupt exception which would be raised when the player requests to retry the game.
    """


class GameOver(Exception):
    """
    ParaPac interrupt exception which would be raised if the player was killed, resulting a game over.
    """
