"""Tests for certbot_dns_corenetworks.dns_corenetworks."""

import os
import unittest

import mock
from requests.exceptions import HTTPError

from certbot.plugins import dns_test_common
from certbot.plugins import dns_test_common_lexicon
from certbot.tests import util as test_util

LOGIN = 'foo'
PASSWORD = 'bar'

class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common_lexicon.BaseLexiconAuthenticatorTest):

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_corenetworks.dns_corenetworks import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        dns_test_common.write({"corenetworks_login": LOGIN, "corenetworks_password": PASSWORD }, path)

        self.config = mock.MagicMock(corenetworks_credentials=path,
                                     corenetworks_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "corenetworks")

        self.mock_client = mock.MagicMock()
        # _get_corenetworks_client | pylint: disable=protected-access
        self.auth._get_corenetworks_client = mock.MagicMock(return_value=self.mock_client)


class CoreNetworksLexiconClientTest(unittest.TestCase, dns_test_common_lexicon.BaseLexiconClientTest):

    LOGIN_ERROR = HTTPError('401 Client Error: Unauthorized for url: ...')

    def setUp(self):
        from certbot_dns_corenetworks.dns_corenetworks import _CoreNetworksLexiconClient

        self.client = _CoreNetworksLexiconClient(LOGIN, PASSWORD, 0)

        self.provider_mock = mock.MagicMock()
        self.client.provider = self.provider_mock


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
