import collections
import requests
import os
import tempfile

from collections import namedtuple
from urllib.parse import quote, urlencode, urljoin
from django.utils.translation import ugettext_lazy as _
from requests.exceptions import HTTPError

CredentialPlugin = namedtuple('CredentialPlugin', ['name', 'inputs', 'backend'])


def raise_for_status(resp):
    resp.raise_for_status()
    if resp.status_code >= 300:
        exc = HTTPError()
        setattr(exc, 'response', resp)
        raise exc

class CertFiles():
    """
    A context manager used for writing a certificate and (optional) key
    to $TMPDIR, and cleaning up afterwards.
    This is particularly useful as a shared resource for credential plugins
    that want to pull cert/key data out of the database and persist it
    temporarily to the file system so that it can loaded into the openssl
    certificate chain (generally, for HTTPS requests plugins make via the
    Python requests library)
    with CertFiles(cert_data, key_data) as cert:
        # cert is string representing a path to the cert or pemfile
        # temporarily written to disk
        requests.post(..., cert=cert)
    """

    certfile = None

    def __init__(self, cert, key=None):
        self.cert = cert
        self.key = key

    def __enter__(self):
        if not self.cert:
            return None
        self.certfile = tempfile.NamedTemporaryFile('wb', delete=False)
        self.certfile.write(self.cert.encode())
        if self.key:
            self.certfile.write(b'\n')
            self.certfile.write(self.key.encode())
        self.certfile.flush()
        return str(self.certfile.name)

    def __exit__(self, *args):
        if self.certfile and os.path.exists(self.certfile.name):
            os.remove(self.certfile.name)

            
aim_inputs = {
    'fields': [{
        'id': 'url',
        'label': _('CyberArk AIM URL'),
        'type': 'string',
        'format': 'url',
    }, {
        'id': 'app_id',
        'label': _('Application ID'),
        'type': 'string',
        'secret': True,
    }, {
        'id': 'client_key',
        'label': _('Client Key'),
        'type': 'string',
        'secret': True,
        'multiline': True,
    }, {
        'id': 'client_cert',
        'label': _('Client Certificate'),
        'type': 'string',
        'secret': True,
        'multiline': True,
    }, {
        'id': 'verify',
        'label': _('Verify SSL Certificates'),
        'type': 'boolean',
        'default': True,
    }],
    'metadata': [{
        'id': 'object_query',
        'label': _('Object Query'),
        'type': 'string',
        'help_text': _('Lookup query for the object. Ex: Safe=TestSafe;Object=testAccountName123'),
    }, {
        'id': 'object_query_format',
        'label': _('Object Query Format'),
        'type': 'string',
        'default': 'Exact',
        'choices': ['Exact', 'Regexp']
    }, {
        'id': 'reason',
        'label': _('Reason'),
        'type': 'string',
        'help_text': _('Object request reason. This is only needed if it is required by the object\'s policy.')
    }],
    'required': ['url', 'app_id', 'object_query'],
}


def aim_backend(**kwargs):
    url = kwargs['url']
    client_cert = kwargs.get('client_cert', None)
    client_key = kwargs.get('client_key', None)
    verify = kwargs['verify']
    app_id = kwargs['app_id']
    object_query = kwargs['object_query']
    object_query_format = kwargs['object_query_format']
    reason = kwargs.get('reason', None)

    query_params = {
        'AppId': app_id,
        'Query': object_query,
        'QueryFormat': object_query_format,
    }
    if reason:
        query_params['reason'] = reason

    request_qs = '?' + urlencode(query_params, quote_via=quote)
    request_url = urljoin(url, '/'.join(['AIMWebService', 'api', 'Accounts']))

    with CertFiles(client_cert, client_key) as cert:
        res = requests.get(
            request_url + request_qs,
            timeout=30,
            cert=cert,
            verify=verify,
            allow_redirects=False,
        )
    raise_for_status(res)
    return res.json()['AWSAccessKeyID']


aim_plugin = CredentialPlugin(
    'CyberArk AIM Central Credential Provider Lookup (AWS Access Key ID)',
    inputs=aim_inputs,
    backend=aim_backend
)
