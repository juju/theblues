import logging


log = logging.getLogger(__name__)


class EntityNotFound(Exception):
    pass


class InvalidMacaroon(Exception):
    pass


class ServerError(Exception):
    pass


def timeout_error(url, timeout):
    """Raise a server error indicating a request timeout to the given URL."""
    msg = 'Request timed out: {} timeout: {}s'.format(url, timeout)
    log.warning(msg)
    return ServerError(msg)
