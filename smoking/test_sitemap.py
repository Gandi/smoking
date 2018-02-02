from __future__ import print_function
import logging
import os
import sys
import unittest

from lxml import etree
import requests


log = logging.getLogger(__name__)

ENV = os.environ
SITEMAP = ENV.get('SITEMAP')
VERIFY_SSL = ENV.get('VERIFY_SSL', 'YES') == 'YES'


TAG_SITEMAPINDEX = '{http://www.google.com/schemas/sitemap/0.9}sitemapindex'
TAG_URLSET = '{http://www.google.com/schemas/sitemap/0.9}urlset'


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


def load_sitemap(sitemap_url):
    log.info("Loading sitemap %s", sitemap_url)
    try:
        response = requests.get(sitemap_url, verify=VERIFY_SSL)
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
        print('The sitemap is not an XML valid document:',
              file=sys.stderr)
        print(sitemap, file=sys.stderr)
        sys.exit(1)
    return sitemap


def get_locations(sitemap_url):

    sitemap = load_sitemap(sitemap_url)

    if sitemap.tag == TAG_SITEMAPINDEX:
        for url in sitemap.getchildren():
            url = url[0].text
            for url in get_locations(url):
                yield url
    elif sitemap.tag == TAG_URLSET:
        for url in sitemap.getchildren():
            yield url[0].text
    else:
        print('The sitemap is valid', file=sys.stderr)
        print(sitemap, file=sys.stderr)
        sys.exit(1)


def loadTests():

    #
    if not SITEMAP:
        print('SITEMAP not set in the environ.',
              file=sys.stderr)
        sys.exit(1)

    urls = get_locations(SITEMAP)

    for idx, url in enumerate(urls):
        log.info('Adding test for url %s', url)
        meth_name = 'test_%s' % idx
        method = _test(url)
        method.__doc__ = 'test %s' % url
        setattr(SiteMapCrawl, meth_name, method)


loadTests()


if __name__ == '__main__':
    from nose.core import run_exit
    run_exit()
