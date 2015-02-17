from __future__ import print_function
import os
import sys
import binascii
import unittest

from lxml import etree
import requests

ENV = os.environ
SITEMAP = ENV.get('SITEMAP')
VERIFY_SSL = ENV.get('VERIFY_SSL', 'YES') == 'YES'


def _test(page_url):
    def test_wrapped(self):
        try:
            response = requests.get(page_url, verify=VERIFY_SSL)
            response.raise_for_status()
        except requests.ConnectionError:
            self.fail('Connection failed on %s' % page_url)
        except requests.HTTPError:
            self.fail('HTTP STATUS %s on %s' % (response.status_code,
                                                page_url))
    return test_wrapped


class SiteMapCrawl(unittest.TestCase):
    """ """


def loadTests():

    #
    if not SITEMAP:
        print('SITEMAP not set in the environ.',
              file=sys.stderr)
        sys.exit(1)

    try:
        response = requests.get(SITEMAP, verify=VERIFY_SSL)
        response.raise_for_status()
    except requests.ConnectionError:
        print('Cannot download the sitemap, host is down.',
              file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError:
        print('Cannot download the sitemap, host is in trouble.',
              file=sys.stderr)
        sys.exit(1)

    try:
        sitemap = response.text.encode(response.encoding)
    except UnicodeDecodeError:
        print('The sitemap as an invalid encoding',
              file=sys.stderr)
        sys.exit(1)

    try:
        sitemap = etree.fromstring(sitemap)
    except etree.XMLSyntaxError:
        print('The sitemap is not an XML valid document',
              file=sys.stderr)
        sys.exit(1)

    urls = [loc[0].text for loc in sitemap]

    if not urls:
        print('The sitemap does not contain any url',
              file=sys.stderr)
        sys.exit(1)

    for url in urls:
        meth_name = 'test_%s' % binascii.hexlify(url)
        method = _test(url)
        method.__doc__ = 'test %s' % url
        setattr(SiteMapCrawl, meth_name, method)


loadTests()


if __name__ == '__main__':
    from nose.core import run_exit
    run_exit()
