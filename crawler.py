#!/usr/bin/env python
#
# Copyright (c) 2012, Luke Southam <luke@devthe.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# - Neither the name of the DEVTHE.COM LIMITED nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
A html Page() object with webcrawling capabilitys
"""

import urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
from pagerank import GetPageRank

__author__ = "Luke Southam <luke@devthe.com>"
__copyright__ = "Copyright 2012, DEVTHE.COM LIMITED"
__license__ = "The BSD 3-Clause License"
__status__ = "Development"


class Page(object):
    """
    A html Page() object with webcrawling capabilitys

    Args:
    url (str):          url to web page
    level=1 (int):   level of recursive web crawling.
                          0;just that page,
                          1;that page and its links
                          2;that page, its links and its link's links
                          etc

    Usage:

    >>> page = Page(url, level=1)

    >>> vars(page)
    {
        'url': "...",                             # url passed through __init__
        'source': "...",                          # urllib2.urlopen(url).read()
        'soup': < __name__.BeautifulSoup at ... > # BeautifulSoup(source)
        'title': "...",                           # title tag
        'description': "...",                     # meta tag description
        'rank': "...",                            # google's rank of url
        'keywords': ["...", ...],                 # meta tag keywords
        'urls': [...],                            # href of a tags
        'links': [...]                            # Page instances of urls with
                                                  # level - 1
    }

    # Each Page object creates links as Page(url, level-1)
    >>> page.links
    [< __name__.Page at ....>,
     < __name__.Page at ....>,
     < __name__.Page at ....>,
     ....]

    >>> page.links[0]
    < __name__.Page at ....>

    >>> page = page.links[0]
    >>> page.links
    [< __name__.Page at ....>,
     < __name__.Page at ....>,
     < __name__.Page at ....>,
     ....]

    """
    def __init__(self, url, level=1):
        self.url = url
        self.level = level
        self.get_page(url)

    def get_page(self, url):
        fp = urllib2.urlopen(url)
        if fp.getcode() != 200:
            raise self.HTTPError(fp.getcode(), url)
        self.source = fp.read()
        self.soup = BeautifulSoup(self.source)
        self.title = (self.soup.title.getText() if self.soup.title else None)
        self.description = (
            self.soup.findAll('meta',
                              attrs={"name": "description"})[0]['content']
            if self.soup.findAll('meta', attrs={"name": "description"})
            else None)
        self.keywords = (
            [kw.strip()
                for kw in self.soup.findAll('meta',
                                            attrs={"name": "keywords"}
                                            )[0]['content'].split(",")]
            if self.soup.findAll('meta', attrs={"name": "keywords"}) else None)
        self.get_urls()
        self.get_links()
        self.rank = GetPageRank(self.url)

    def get_urls(self):
        urls = []
        for url in self.soup.findAll('a', href=True):
            url = url['href']
            if url.startswith("#"):
                if url.startswith("#!"):
                    url = "?_escaped_fragment_=" + url[2:]
                    urls.append(url)
            else:
                if url.find("#!") != -1:
                    url = url.replace("#!", "?_escaped_fragment_=")
                urls.append(url)
        self.urls = urls
        self.fix_urls()

    def fix_urls(self):
        urls = self.urls
        url = self.url
        fixed_urls = []
        for link in urls:
            link = urljoin(url, link)
            fixed_urls.append(link)
        self.urls = rm_duplicate(fixed_urls)

    def get_links(self):
        if (self.level - 1) < 0:
            self.links = []
            return
        links = []
        for url in self.urls:
            try:
                link = self.__class__(url, level=self.level - 1)
                links.append(link)
            except:
                pass
        self.links = links
        self.total_urls = rm_duplicate(self.urls + [url
                                       for page in self.links
                                       for url in page.urls])


def rm_duplicate(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]
