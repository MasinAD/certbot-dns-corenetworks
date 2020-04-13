"""DNS Authenticator for Core Networks DNS."""
import logging

import zope.interface
from lexicon.providers import corenetworks

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon

logger = logging.getLogger(__name__)

ACCOUNT_URL = 'https://beta.api.core-networks.de/doc/#functon_auth_token'


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Core Networks

    This Authenticator uses the Core Networks beta API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Core Networks for DNS).'
    ttl = 60

    def __init__(self, *args, **kwargs):
#        l = open('corenetworks.log', 'a')
#        for arg in args:
#            l.write("Arg: %s\n" % arg)
#        for kwarg in kwargs:
#            l.write("KWarg: %s\n" % kwarg)
#        l.write(str(config))
#        l.write("Authenticator instantiated with args %s and kwargs %s" % (*args, **kwargs))
#        l.close()
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=30)
        add('credentials', help='Core Networks credentials INI file.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Core Networks beta API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Core Networks credentials INI file',
            {
                'login': 'API user name for Core Networks beta API. (See {0}.)'.format(ACCOUNT_URL),
                'password': 'Password for API user'
            }
        )
#        l = open('corenetworks.log', 'a')
#        l.write("_setup_credentials configured these credentials: %s\n" % str(self.credentials) )
#        l.close()

    def _perform(self, domain, validation_name, validation):
        self._get_corenetworks_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_corenetworks_client().del_txt_record(domain, validation_name, validation)

    def _get_corenetworks_client(self):
        return _CoreNetworksLexiconClient(self.credentials.conf('login'), self.credentials.conf('password'), self.ttl)


class _CoreNetworksLexiconClient(dns_common_lexicon.LexiconClient):
    """
    Encapsulates all communication with the Core Networks API via Lexicon.
    """

    def __init__(self, login, password, ttl):
        super(_CoreNetworksLexiconClient, self).__init__()
#        l = open('corenetworks.log', 'a')
#        l.write("_CoreNetworksLexiconClient instantiated with login {0} and password {1}".format(login, password))
#        l.close()
        config = dns_common_lexicon.build_lexicon_config('corenetworks', {
            'ttl': ttl,
        }, {
            'auth_username': login,
            'auth_password': password
        })

        self.provider = corenetworks.Provider(config)

    def _handle_http_error(self, e, domain_name):
        hint = None
        if str(e).startswith('401 Client Error: Unauthorized for url:'):
            hint = 'Is your API token value correct?'

        return errors.PluginError('Error determining zone identifier for {0}: {1}.{2}'
                                  .format(domain_name, e, ' ({0})'.format(hint) if hint else ''))
