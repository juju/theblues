from collections import namedtuple
import datetime
import json

from macaroonbakery import httpbakery

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
Wallet = namedtuple('Wallet',
                    ['owner', 'wallet', 'limit', 'budgeted', 'unallocated',
                     'available', 'consumed', 'default'])
WalletTotal = namedtuple(
    'WalletTotal',
    ['limit', 'budgeted', 'unallocated', 'available', 'consumed', 'usage'])
PLAN_VERSION = 'v2'


class Plans(object):

    def __init__(self, url, timeout=DEFAULT_TIMEOUT, client=None):
        """Initializer.

        @param url The url to the Plan API.
        @param timeout How long to wait before timing out a request in seconds;
            a value of None means no timeout.
        @param client (httpbakery.Client) holds a context for making http
        requests with macaroons.
        """
        self.url = ensure_trailing_slash(url) + PLAN_VERSION + '/'
        self.timeout = timeout
        if client is None:
            client = httpbakery.Client()
        self._client = client

    def get_plans(self, reference):
        """Get the plans for a given charm.

        @param the Reference to a charm.
        @return a tuple of plans or an empty tuple if no plans.
        @raise ServerError
        """
        response = make_request(
            '{}charm?charm-url={}'.format(self.url,
                                          'cs:' + reference.path()),
            timeout=self.timeout, client=self._client)
        try:
            return tuple(map(lambda plan: Plan(
                url=plan['url'], plan=plan['plan'],
                created_on=datetime.datetime.strptime(
                    plan['created-on'],
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                description=plan.get('description'),
                price=plan.get('price')), response))
        except (KeyError, TypeError, ValueError) as err:
            log.info(
                'cannot process plans: invalid JSON response: {!r}'.format(
                    response))
            raise ServerError(
                'unable to get list of plans for {}: {}'.format(
                    reference.path(), err))
        except Exception as exc:
            log.info(
                'cannot process plans: invalid JSON response: {!r}'.format(
                    response))
            raise ServerError(
                'unable to get list of plans for {}: {}'.format(
                    reference.path(), exc))

    def list_wallets(self):
        """Get the list of wallets

        @return an object of wallets, a total, and available credit.
        @raise ServerError
        """
        response = make_request(
            '{}wallet'.format(self.url),
            timeout=self.timeout,
            client=self._client)
        try:
            response['wallets'] = map(
                lambda wallet: Wallet(
                    owner=wallet['owner'],
                    wallet=wallet['wallet'],
                    limit=wallet['limit'],
                    budgeted=wallet['budgeted'],
                    unallocated=wallet['unallocated'],
                    available=wallet['available'],
                    consumed=wallet['consumed'],
                    default=wallet['default']), response['wallets'])
            total = response['total']
            response['total'] = WalletTotal(
                limit=total['limit'],
                budgeted=total['budgeted'],
                available=total['available'],
                unallocated=total['unallocated'],
                usage=total['usage'],
                consumed=total['consumed'])
            return response
        except (KeyError, TypeError, ValueError, Exception) as err:
            log.info(
                'cannot process wallets: invalid JSON response: {!r}'.format(
                    response))
            raise ServerError(
                'unable to get list of wallets: {}'.format(err))

    def get_wallet(self, wallet_name):
        """Get a single wallet.

        @param the name of the wallet.
        @return an object of wallets, a total, and available credit.
        @raise ServerError
        """
        response = make_request(
            '{}wallet/{}'.format(self.url, wallet_name),
            timeout=self.timeout,
            client=self._client)
        try:
            total = response['total']
            response['total'] = WalletTotal(
                limit=total['limit'],
                budgeted=total['budgeted'],
                available=total['available'],
                unallocated=total['unallocated'],
                usage=total['usage'],
                consumed=total['consumed'])
            return response
        except (KeyError, TypeError, ValueError, Exception) as err:
            log.info(
                'cannot process wallet: invalid JSON response: {!r}'.format(
                    response))
            raise ServerError(
                'unable to get list of wallet: {}'.format(err))

    # def update_wallet(self, wallet_name, value):
    #     # Patch to /wallet/{wallet}
    #     request = {
    #         'update': {
    #             'limit': value,
    #         }
    #     }
    #     response = make_request(
    #         '{}wallet/{}'.format(wallet_name),
    #         method='PATCH',
    #         body=json.dumps(request),
    #         timeout=self.timeout,
    #         client=self._client)
    #     pass
    #
    # def create_wallet(self, wallet_name, value):
    #     # Post to /wallet
    #     request = {
    #         'wallet': wallet_name,
    #         'limit': value,
    #     }
    #     response = make_request(
    #         '{}wallet'.format(wallet_name),
    #         method='POST',
    #         body=json.dumps(request),
    #         timeout=self.timeout,
    #         client=self._client)
    #     pass
    #
    # def delete_wallet(self, wallet_name):
    #     pass
    #
    # def create_budget(self, wallet_name, budget):
    #     pass
    #
    # def update_budget(self, model_uuid, wallet_name, value):
    #     pass
    #
    # def delete_budget(self, model_uuid):
    #     pass
