# -*- coding: utf-8 -*-

import sys
import urllib
import shutil
import urlparse
from os import path
        
import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import xbmcplugin

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__ = xbmc.translatePath(path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__ = xbmc.translatePath(path.join(__profile__, 'temp', '')).decode("utf-8")

sys.path.append(__resource__)

from bsplayer import BSPlayer
from torec import Torec


def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module, msg)).encode('utf-8'), level=xbmc.LOGDEBUG)


def get_params(params_str=""):
    params_str = params_str or sys.argv[2]
    return dict(urlparse.parse_qsl(params_str.lstrip('?')))


def get_video_path(xbmc_path=''):
    xbmc_path = xbmc_path or urlparse.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))

    if xbmc_path.startswith('rar://'):
        return path.dirname(xbmc_path.replace('rar://', ''))
    elif xbmc_path.startswith('stack://'):
        return xbmc_path.split(" , ")[0].replace('stack://', '')

    return xbmc_path


def search(engine_name, params=get_params()):
    video_name = get_video_path()
    log("BSPlayers.video_path", "Current Video Path: %s." % video_name)

    with globals()[engine_name](log=log) as engine:
        for subtitle in engine.search_subtitles(video_name, **params):
            subtitle_name = subtitle['subtitle_name']
            if subtitle.get('has_ext', False):
                subtitle_name = path.splitext(subtitle['subtitle_name'])[0]
            list_item = xbmcgui.ListItem(
                label=engine_name,
                label2=subtitle_name,
                thumbnailImage='he'
            )

            plugin_url = "plugin://{path}/?{query}".format(
                path=__scriptid__,
                query=urllib.urlencode(dict(
                    action='download',
                    engine_name=engine_name,
                    **subtitle
                ))
            )
            log("BSPlayers.plugin_url", "Plugin Url Created: %s." % plugin_url)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=plugin_url, listitem=list_item, isFolder=False)


def download(params=get_params()):
    if xbmcvfs.exists(__temp__):
        shutil.rmtree(__temp__)
    xbmcvfs.mkdirs(__temp__)
    
    engine = globals()[params['engine_name']]
    download_link = params.pop('download_link', None)
    subtitle_path = engine.download_subtitles(download_link, __temp__, **params)
    if subtitle_path and path.splitext(subtitle_path)[1] in [".srt", ".sub", ".ssa"]:
        log("BSPlayer.download_subtitles", "Subtitles Download Successfully From: %s." % download_link)
        list_item = xbmcgui.ListItem(label=subtitle_path)
        log("BSPlayer.download", "Downloaded Subtitle Path: %s." % subtitle_path)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=subtitle_path, listitem=list_item, isFolder=False)


if __name__ == '__main__':
    params=get_params()
    engines = [
        'BSPlayer', 'Torec'
    ]
    log("BSPlayers.params", "Current Action: %s." % params['action'])

    if params['action'] == 'search':
        for engine in engines:
            log("Tomerz", engine)
            search(engine)
    elif params['action'] == 'manualsearch':
        log("BSPlayer.manualsearch", "Cannot Search Manually.")
    elif params['action'] == 'download':
        download()

    xbmcplugin.endOfDirectory(int(sys.argv[1]))