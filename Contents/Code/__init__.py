import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
NAME = "HTVOnline"
BASE_URL = "http://www.htvonline.com.vn/livetv"
DEFAULT_ICO = 'http://static.htvonline.com.vn/layout/images/logo.png'

def Start():
    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['X-Requested-With'] = 'XMLHttpRequest'
####################################################################################################

@handler('/video/htvonline', NAME)
def MainMenu():
    oc = ObjectContainer()
    try:
        link = HTTP.Request(BASE_URL, cacheTime=3600).content
        soup = BeautifulSoup(link)
        divLiveTV = soup.findAll('div', {'id': 'divLiveTV'})
        aChannels = BeautifulSoup(str(divLiveTV[0]))('a', {'class': 'mh-grids5-img'})
        for channel in aChannels:
            channel_title = BeautifulSoup(str(channel))('a')[0]['title'].encode('utf-8')
            channel_link = BeautifulSoup(str(channel))('a')[0]['href'].encode('utf-8')
            channel_image = BeautifulSoup(str(channel))('img')[0]['src']

            oc.add(createMediaObject(
                url=channel_link,
                title=channel_title,
                thumb=channel_image,
                rating_key=channel_title
            ))

    except Exception, ex:
        Log("******** Error retrieving and processing latest version information. Exception is:\n" + str(ex))

    return oc
####################################################################################################

####################################################################################################

@route('/video/htvonline/createMediaObject')
def createMediaObject(url, title, thumb, rating_key, include_container=False):
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2
    track_object = EpisodeObject(
        key=Callback(
            createMediaObject,
            url=url,
            title=title,
            thumb=thumb,
            rating_key=rating_key,
            include_container=True
        ),
        title=title,
        thumb=thumb,
        rating_key=rating_key,
        items=[
            MediaObject(
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(Callback(PlayVideo, url=url))
                    )
                ],
                container=container,
                video_resolution='720',
                video_codec=video_codec,
                audio_codec=audio_codec,
                audio_channels=audio_channels,
                optimized_for_streaming=True
            )
        ]
    )
    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object


@indirect
def PlayVideo(url):
    url=videolinks(url)
    return IndirectResponse(VideoClipObject, key=url)

def videolinks(url):
    link = urllib2.urlopen(url).read()
    newlink = ''.join(link.splitlines()).replace('\t', '')
    vlink = re.compile('file: "(.+?)",').findall(newlink)
    return vlink[0]
####################################################################################################
