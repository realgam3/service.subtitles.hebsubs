import re
import time
import urllib
import zipfile
from os import path
from math import floor
from random import random
from urlparse import urljoin
from StringIO import StringIO

from utils import SUB_EXT, python_logger, get_session

BASE_URL = 'http://www.torec.net'


class Torec(object):
    def __init__(self, search_url=BASE_URL, log=python_logger):
        self.session = get_session()
        self.search_url = search_url
        self.log = log
        self.sub_dict = {
            'sub_id': -1,
            's': 1920,
            'code': None,
            'sh': 'yes',
            'guest': None,
            'timewaited': int(floor(random() * 7 + 12))
        }

    def __enter__(self):
        self.get_guest_code()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def get_guest_code(self):
        res = self.session.open(
            urljoin(self.search_url, '/ajax/sub/guest_time.asp'),
            data=urllib.urlencode({
                'sub_id': self.sub_dict['sub_id'],
                's': self.sub_dict['s']
            })
        )
        self.sub_dict['guest'] = res.read()
        if self.sub_dict['guest'] != 'error':
            return True
        return False

    def get_subtitle_id(self, subtitle_release):
        res = self.session.open(
            "{url}?{params}".format(
                url=urljoin(self.search_url, 'ssearch.asp'),
                params=urllib.urlencode({'search': subtitle_release})
            )
        )

        r = re.compile('<td class="newd_table_titleLeft_BG"><div><a href="/sub\.asp\?sub_id=(.*?)">.*?</a></div></td>')
        regex_res = r.search(res.read())
        if regex_res:
            return regex_res.group(1)

    def search_subtitles(self, subtitle_release, **params):
        subtitle_release = path.splitext(path.basename(subtitle_release))[0]
        self.sub_dict['sub_id'] = self.get_subtitle_id(subtitle_release)

        res = self.session.open(
            "{url}?{params}".format(
                url=urljoin(self.search_url, 'sub.asp'),
                params=urllib.urlencode({'sub_id': self.sub_dict['sub_id']})
            )
        )

        options = re.compile('<option value="(?P<code>.*?)" style=".*?">(?P<version>.*?)</option>')
        for option in options.finditer(res.read()):
            sub_options = option.groupdict()
            self.sub_dict['code'] = sub_options['code']
            yield dict(
                download_link=self.search_url,
                data_encoded=urllib.urlencode(self.sub_dict),
                subtitle_name=sub_options['version'].replace(' ', '.').lstrip('.'),
                has_ext=False
            )

    @staticmethod
    def download_subtitles(download_link, dest_path, **params):
        session = get_session()
        download_url = None
        current_try = 0
        for current_try in xrange(15):
            download_url = session.open(
                urljoin(download_link, '/ajax/sub/downloadun.asp'),
                data=params['data_encoded'],
            ).read()
            if 'ERROR:' not in download_url:
                break
            time.sleep(1)

        if download_url:
            res = session.open(urljoin(download_link, download_url))
            if res:
                subtitle_name = ""
                zf = zipfile.ZipFile(StringIO(res.read()))
                for zif in zf.filelist:
                    if path.splitext(zif.filename)[1].lower().lstrip('.') in SUB_EXT:
                        subtitle_path = path.join(dest_path, zif.filename)
                        with open(subtitle_path, 'wb') as f:
                            f.write(zf.read(zif))
                            f.flush()
                        zf.close()
                        return subtitle_path
                zf.close()
