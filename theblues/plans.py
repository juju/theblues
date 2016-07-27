from collections import namedtuple
import datetime

from theblues.errors import (
    log,
    ServerError,
)
from theblues.utils import (
    ensure_trailing_slash,
    make_request,
    DEFAULT_TIMEOUT,
)

Plan = namedtuple('Plan',
                  ['url', 'plan', 'created_on', 'description', 'price'])
PLAN_VERSION = 'v2'


class Plans(object):

    def __init__(self, url, timeout=DEFAULT_TIMEOUT):
        """Initializer.

        @param url The url to the Plan API.
        @param timeout How long to wait before timing out a request in seconds;
            a value of None means no timeout.
        """
        self.url = ensure_trailing_slash(url) + PLAN_VERSION + '/'
        self.timeout = timeout

    def get_plans(self, reference):
        """Get the plans for a given charm.

        @param the Reference to a charm.
        @return a tuple of plans or an empty tuple if no plans.
        @raise ServerError
        """
        json = make_request(
            '{}charm?charm-url={}'.format(self.url,
                                          'cs:' + reference.path()),
            timeout=self.timeout)
        try:
            return tuple(map(lambda plan: Plan(
                url=plan['url'], plan=plan['plan'],
                created_on=datetime.datetime.strptime(
                    plan['created-on'],
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                description=plan.get('description'),
                price=plan.get('price')), json))
        except (KeyError, TypeError, ValueError) as err:
            log.info(
                'cannot process plans: invalid JSON response: {!r}'.format(
                    json))
            raise ServerError(
                'unable to get list of plans for {}: {}'.format(
                    reference.path(), err))
        except Exception as exc:
            log.info(
                'cannot process plans: invalid JSON response: {!r}'.format(
                    json))
            raise ServerError(
                'unable to get list of plans for {}: {}'.format(
                    reference.path(), exc))
