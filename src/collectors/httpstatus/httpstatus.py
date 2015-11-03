# coding=utf-8

import os
import sys
from collections import namedtuple
from importlib import import_module

import requests
from diamond.collector import Collector


class HttpStatusCollector(Collector):
    def __init__(self, **kwargs):
        super(HttpStatusCollector, self).__init__(**kwargs)
        nicks = self.config.get('health_check_nicks')
        urls = self.config.get('health_check_urls')

        if nicks and urls:
            nicks = self.config['health_check_nicks']
            urls = self.config['health_check_urls']
            if not isinstance(nicks, list):
                if ',' in nicks:
                    nicks = [nick.strip() for nick in nicks.split(',')]
                    urls = [url.strip() for url in urls.split(',')]
                    self.urls = dict(zip(nicks, urls))
                else:
                    self.urls = {nicks: urls}
            else:
                self.urls = dict(zip(nicks, urls))

    def get_default_config_help(self):
        config_help = super(HttpStatusCollector, self).get_default_config_help()
        config_help.update({
            'health_check_nicks':
                'comma separated list of nicks for health check URLs',
            'health_check_urls':
                'comma separated list of URLs  of which to test health'
        })
        return config_help

    def get_default_config(self):
        default_config = super(HttpStatusCollector, self).get_default_config()
        default_config['path'] = 'httpstatus'
        default_config['health_check_nicks'] = 'google, googlecoza'
        default_config['health_check_urls'] = 'http://www.google.com, http://www.google.co.za'

        default_config['headers'] = {'User-Agent': 'Diamond HTTP collector', }
        return default_config

    def collect(self):
        for nickname, url in self.urls.iteritems():
            self.log.debug("collecting %s", str(url))
            try:
                response = requests.get(url)

                self.publish_gauge(
                    '{0}.is_alive'.format(nickname), response.ok)

            except Exception, e:
                self.log.error("Unknown error opening url: %s", e)
