# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 20:19:25 2017

@author: Kirill
"""

import requests
from lxml import html
import urllib


sitemap_url = 'https://besplatka.ua/sitemap.xml'
controls = ['/electronika-i-bitovaya-tehnika/smartfone-telefone']
controls_1 = '-categories-'
controls_2 = '/sitemap-besplatka'


def get_url_sitemap(sitemap_url):
    res = requests.get(sitemap_url)
    sub_res = html.fromstring(res.content).xpath('//sitemap/loc/text()')
    return sub_res


def get_url_final(sitemap_url):
    res = requests.get(sitemap_url)
    sub_res = html.fromstring(res.content).xpath('//url/loc/text()')
    return sub_res


def url_list_in_sitemap(sitemap_url):
    res_sitemap = set()
    for url_sm in get_url_sitemap(sitemap_url):
        if controls_1 in url_sm:
            for url_final in get_url_final(url_sm):
                for item in controls:
                    if item in url_final:
                        res_sitemap.add(
                                urllib.parse.unquote(urllib.parse.unquote(url_final))
                                )
        elif controls_2 in url_sm:
            for url_final in get_url_final(url_sm):
                for item in controls:
                    if item in url_final:
                        res_sitemap.add(
                                urllib.parse.unquote(urllib.parse.unquote(url_final))
                                )          
    return res_sitemap

if __name__ == '__main__':
#    sitemap = get_url_sitemap(sitemap_url)
    url_set = url_list_in_sitemap(sitemap_url)
