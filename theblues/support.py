from email.utils import parseaddr
import requests
from requests.exceptions import RequestException

from theblues.errors import (
    log,
    ServerError,
)
from theblues.utils import (
    ensure_trailing_slash,
)


class Priority:
    L1 = "L1- Core functionality not available"
    L2 = "L2- Core functionality severely degraded"
    L3 = "L3- Standard support request"
    L4 = "L4- Non-urgent issue"
    L5 = "L5"
    Undecided = "Undecided"
    Wishlist = "Wishlist"
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"


class Support(object):

    # This represent the field name for business impact in SalesForce.
    BUSINESS_IMPACT = '00ND0000005lqBV'

    def __init__(self, url, orgId, recordType):
        """Initializer.

        @param url The url to the Support server.
        @param orgId the organization Id for SalesForce.
        @param recordType the record type.
        """
        self.url = ensure_trailing_slash(url)
        self.orgId = orgId
        self.recordType = recordType

    def create_case(self, name, email, subject, description, businessImpact,
                    priority, phone):
        """ Send a case creation to SalesForces to create a ticket.

        @param name of the person creating the case.
        @param email of the person creating the case.
        @param subject of the case.
        @param description of the case.
        @param businessImpact of the case.
        @param priority of the case.
        @param phone of the person creating the case.
        @return Nothing if this is ok.
        @raise ServerError when something goes wrong.
        @raise ValueError when data passed in are invalid
        """

        if not('@' in parseaddr(email)[1]):
            raise ValueError('invalid email: {}'.format(email))
        if '' == name or name is None:
            raise ValueError('empty name')
        if '' == subject or subject is None:
            raise ValueError('empty subject')
        if '' == description or description is None:
            raise ValueError('empty description')
        if '' == businessImpact or businessImpact is None:
            raise ValueError('empty business impact')
        if priority is None:
            raise ValueError('Ensure the priority is from the set of '
                             'known priorities')
        if '' == phone or phone is None:
            raise ValueError('empty phone')

        try:
            r = requests.post(self.url, data={
                'orgid': self.orgId,
                'recordType': self.recordType,
                'name': name,
                'email': email,
                'subject': subject,
                'description': description,
                self.BUSINESS_IMPACT: businessImpact,
                'priority': priority,
                'phone': phone,
                'external': 1
                }, timeout=10)
            r.raise_for_status()
        except RequestException as err:
            log.info('cannot create case: {}'.format(err))
            raise ServerError(
                'cannot create case: {}'.format(err))
