import urllib
import urllib2
import re
import json
from BeautifulSoup import BeautifulSoup
NAME = "HTVOnline"
ROOT_URL = 'http://hplus.com.vn/'
BASE_URL = "http://hplus.com.vn/en/categories/live-tv"
DEFAULT_ICO = 'http://static.hplus.com.vn/themes/front/images/logoFooter.png'

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
        # link = HTTP.Request(BASE_URL, cacheTime=3600).content
        # soup = BeautifulSoup(link)
        # page_title = soup('div',{'class':'page-title'})
        # for p in page_title:
        #     ptsoup = BeautifulSoup(str(p))
        #     ptlink = ptsoup('a')[1]['href']
        #     ptname = ptsoup('a')[1].contents[0]
        #     oc.add(DirectoryObject(
        #         key=Callback(Index, title=ptname, ilink=ptlink),
        #         title=ptname,
        #         thumb=R(DEFAULT_ICO)
        #     ))
        apilink = "http://api.htvonline.com.vn/tv_channels"
        reqdata = '{"pageCount":200,"category_id":"-1","startIndex":0}'
        data = getContent ( apilink , reqdata)
        print data
        for d in data ["data"] :
            res = d["link_play"][0]["resolution"]
            img = d["image"]
            title = d["name"]+' ('+res+')'
            link = d["link_play"][0]["mp3u8_link"]
            # addLink(title.encode('utf-8'), link,2,img)
            oc.add(createMediaObject(
                url=link,
                title=title,
                thumb=img,
                rating_key=title
            ))

    except Exception, ex:
        Log("******** Error retrieving and processing latest version information. Exception is:\n" + str(ex))

    return oc

@route('/video/htvonline/index')
def Index(title, ilink):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(ilink, cacheTime=3600).content
    soup = BeautifulSoup(link)
    divpanel = soup('div',{'class':'panel'})
    for d in range(1,len(divpanel)):
        dsoup = BeautifulSoup(str(divpanel[d]))
        dlink = ROOT_URL+dsoup('a')[1]['href']
        dtitle = dsoup('a')[1].contents[0].encode('utf-8')
        dimage = re.compile("background-image: url\('(.+?)'\)").findall(str(dsoup('a')[0]['style'].encode('utf-8')))[0]
        oc.add(createMediaObject(
                url=dlink,
                title=dtitle,
                thumb=dimage,
                rating_key=dtitle
        ))

    return oc
####################################################################################################

####################################################################################################

@route('/video/htvonline/createMediaObject')
def createMediaObject(url, title, thumb, rating_key, include_container=False,includeRelatedCount=None,includeRelated=None,includeExtras=None):
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
    # url=videolinks(url)
    return IndirectResponse(VideoClipObject, key=url)

def videolinks(url):
    # link = urllib2.urlopen(url).read()
    # newlink = ''.join(link.splitlines()).replace('\t', '')
    # vlink = re.compile('file: "(.+?)",').findall(newlink)
    # return vlink[0]
    link = urllib2.urlopen(url).read()
    vlink= re.compile('iosUrl = "(.+?)";').findall(link)
    return vlink[0]

def getContent(url, requestdata):
    req = urllib2 . Request(urllib . unquote_plus(url))
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', 'Basic YXBpaGF5aGF5dHY6NDUlJDY2N0Bk')
    req.add_header('User-Agent', 'Apache-HttpClient/UNAVAILABLE (java 1.4)')
    link = urllib . urlencode({'request': requestdata})
    resp = urllib2 . urlopen(req, link, 120)
    content = resp . read()
    resp . close()
    content = '' . join(content . splitlines())
    data = json . loads(content)
    return data
####################################################################################################
