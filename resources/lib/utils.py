import logging
import urllib2
import cookielib


SUB_EXT = ["srt", "sub", "txt", "smi", "ssa", "ass"]
LOGGER = logging.getLogger('BSPlayer')
logging.basicConfig(
    format='%(asctime)s T:%(thread)d  %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)


def python_logger(module, msg):
    LOGGER.debug((u"### [%s] - %s" % (module, msg)))


def check_connectivity(url, timeout=5):
    try:
        urllib2.urlopen(url, timeout=timeout)
    except urllib2.URLError:
        return False
    return True


def get_session():
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; Synapse)')]
    return opener

