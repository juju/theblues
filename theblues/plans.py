from collections import namedtuple
import datetime

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
PLAN_VERSION = 'v3'


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

        @return an object containing a list of wallets, a total, and available
            credit.
        @raise ServerError
        """
        response = make_request(
            '{}wallet'.format(self.url),
            timeout=self.timeout,
            client=self._client)
        try:
            response['wallets'] = tuple(map(
                lambda wallet: Wallet(
                    owner=wallet['owner'],
                    wallet=wallet['wallet'],
                    limit=wallet['limit'],
                    budgeted=wallet['budgeted'],
                    unallocated=wallet['unallocated'],
                    available=wallet['available'],
                    consumed=wallet['consumed'],
                    default='default' in wallet), response['wallets']))
            total = response['total']
            response['total'] = WalletTotal(
                limit=total['limit'],
                budgeted=total['budgeted'],
                available=total['available'],
                unallocated=total['unallocated'],
                usage=total['usage'],
                consumed=total['consumed'])
            return response
        except Exception as err:
            log.info(
                'cannot process wallets: invalid JSON response: {!r}'.format(
                    response))
            raise ServerError(
                'unable to get list of wallets: {}'.format(err))

    def get_wallet(self, wallet_name):
        """Get a single wallet.

        @param the name of the wallet.
        @return the wallet's total.
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
        except (KeyError, TypeError, ValueError) as err:
            log.info(
                'cannot process wallet: invalid JSON response: {!r}'.format(
                    response))
            raise ServerError(
                'unable to get list of wallets: {}'.format(err))
        except Exception as exc:
            log.info(
                'cannot get wallet from server: {!r}'.format(exc))
        raise ServerError(
            'unable to get list of wallets: {}'.format(exc))

    def update_wallet(self, wallet_name, value):
        """Update a wallet with a new limit.

        @param the name of the wallet.
        @param the new value of the limit.
        @return the result form the server.
        @raise ServerError via make_request.
        """
        request = {
            'update': {
                'limit': str(value),
            }
        }
        return make_request(
            '{}wallet/{}'.format(self.url, wallet_name),
            method='PATCH',
            body=request,
            timeout=self.timeout,
            client=self._client)

    def create_wallet(self, wallet_name, value):
        """Create a new wallet.

        @param the name of the wallet.
        @param the value of the limit.
        @return the result form the server.
        @raise ServerError via make_request.
        """
        request = {
            'wallet': wallet_name,
            'limit': str(value),
        }
        return make_request(
            '{}wallet'.format(self.url),
            method='POST',
            body=request,
            timeout=self.timeout,
            client=self._client)

    def delete_wallet(self, wallet_name):
        """Delete a wallet.

        @param the name of the wallet.
        @return the result form the server.
        @raise ServerError via make_request.
        """
        return make_request(
            '{}wallet/{}'.format(self.url, wallet_name),
            method='DELETE',
            timeout=self.timeout,
            client=self._client)

    def create_budget(self, wallet_name, model_uuid, value):
        """Create a new budget for a model and wallet.

        @param the name of the wallet.
        @param the model UUID.
        @param the new value of the limit.
        @return the result form the server.
        @raise ServerError via make_request.
        """
        request = {
            'model': model_uuid,
            'limit': value,
        }
        return make_request(
            '{}wallet/{}/budget'.format(self.url, wallet_name),
            method='POST',
            body=request,
            timeout=self.timeout,
            client=self._client)

    def update_budget(self, wallet_name, model_uuid, value):
        """Update a budget limit.

        @param the name of the wallet.
        @param the model UUID.
        @param the new value of the limit.
        @return the result form the server.
        @raise ServerError via make_request.
        """
        request = {
            'update': {
                'wallet': wallet_name,
                'limit': value,
            }
        }
        return make_request(
            '{}model/{}/budget'.format(self.url, model_uuid),
            method='PATCH',
            body=request,
            timeout=self.timeout,
            client=self._client)

    def delete_budget(self, model_uuid):
        """Delete a budget.

        @param the name of the wallet.
        @param the model UUID.
        @raise ServerError via make_request.
        """
        return make_request(
            '{}model/{}/budget'.format(self.url, model_uuid),
            method='DELETE',
            timeout=self.timeout,
            client=self._client)
