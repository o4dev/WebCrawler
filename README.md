WebCrawler
==========

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
