from __future__ import print_function
import os
import sys
import binascii

from lxml import etree
import requests
from needle.cases import NeedleTestCase


ENV = os.environ
SITEMAP = ENV.get('SITEMAP')
VERIFY_SSL = ENV.get('VERIFY_SSL', 'YES') == 'YES'
SIZES = ENV.get('SIZES', '1280x768 768x1024 360x640').split()


def _test(page_url):

    def test_wrapped(self):

        if not(VERIFY_SSL) and page_url.startswith('https://'):
            url = 'http://' + page_url[8:]
        else:
            url = page_url

        self.driver.get(url)
        self.assertScreenshot('html body',
                              '%dx%d_%s' % (self.viewport_width,
                                            self.viewport_height,
                                            binascii.hexlify(page_url)
                                            ),
                              0.1
                              )

    return test_wrapped


class _SiteMapNeedleTestCase(NeedleTestCase):
    """ """
    engine_class = 'needle.engines.perceptualdiff_engine.Engine'

    def setUp(self):
        super(NeedleTestCase, self).setUp()


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

    for size in SIZES:
        width, height = size.split('x')
        viewport_width, viewport_height = int(width), int(height)

        testcase = type('TestCase%s' % size, (_SiteMapNeedleTestCase,),
                        {'viewport_width': viewport_width,
                         'viewport_height': viewport_height,
                         })

        for url in urls:
            meth_name = 'test_%s' % binascii.hexlify(url)
            method = _test(url)
            method.__doc__ = 'test %s' % url

            setattr(testcase, meth_name, method)

        globals()['TestCase%s' % size] = testcase

loadTests()


if __name__ == '__main__':
    from nose.core import run_exit
    run_exit()
