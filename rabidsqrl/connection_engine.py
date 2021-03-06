import logging
import urllib.request
import urllib.parse
from html.parser import HTMLParser

log = logging.getLogger(__name__)

class CEHTMLParser(HTMLParser):
    '''
    Take an HTML document with divs w/attributes 'query' and 'injection-result'
    and print the div data to stdout. If the divs/attributes aren't there, nothing
    is printed.
    '''
    def __init__(self):
        super(CEHTMLParser, self).__init__(strict=False)
        self._show_data = False
        self._ids = ['query', 'injection-result']

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs:
                if 'id' == attr[0] and attr[1] in self._ids:
                    print('{}: '.format(attr[1]))
                    self._show_data = True
                    break

    def handle_data(self, data):
        if self._show_data:
            print('\t{}'.format(data))

    def handle_endtag(self, tag):
        if tag == 'div':
            if self._show_data:
                self._show_data = False

class ConnectionEngineException(Exception):
    '''Exception class for ConnectionEngine. NOOP.'''
    pass

class ConnectionEngine(object):
    '''Take a list of URLs and run them, optionally showing
    crafted results if asked.'''
    def __init__(self, attacks, show_results, blind):
        self.attacks = attacks
        self.show_results = show_results
        self.blind = blind

    def do_attacks(self):
        for attack in self.attacks:
            for url in attack.next_url():
                if self.blind:
                    url += '&blind=1'
                log.info('Sending request: {}'.format(url))
                with urllib.request.urlopen(url) as fd:
                    resp = fd.read()
                    log.info('Read {} bytes in response.'.format(len(resp)))

                    if self.show_results:
                        self._show_results(resp)
                    
                    errcode, errmess = attack.handle_response(str(resp), url)
                    if errcode:
                        print ('Error in attack: {}'.format(errmess))
                        return 1

        return 0

    def _show_results(self, resp):
        p = CEHTMLParser()
        p.feed(resp.decode())
