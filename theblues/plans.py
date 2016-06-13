from collections import namedtuple
import datetime

from theblues.errors import (
    log,
    ServerError,
)
from theblues.utils import (
    ensure_trailing_slash,
    make_request,
)

Plan = namedtuple('Plan',
                  ['url', 'plan', 'created_on', 'description', 'price'])
PLAN_VERSION = 'v2'


class Plans(object):

    def __init__(self, url):
        """Initializer.

        @param url The url to the Plan API.
        """
        self.url = ensure_trailing_slash(url) + PLAN_VERSION + '/'

    def get_plans(self, reference):
        """Get the plans for a given charm.

        @param the Reference to a charm.
        @return a tuple of plans or an empty tuple if no plans.
        @raise ServerError
        """
        json = make_request(
            '{}charm?charm-url={}'.format(self.url,
                                          'cs:' + reference.path()))
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
                'cannot process terms: invalid JSON response: {!r}'.format(
                    json))
            raise ServerError(
                'unable to get list of plans for {}: {}'.format(
                    reference.path(), err))
