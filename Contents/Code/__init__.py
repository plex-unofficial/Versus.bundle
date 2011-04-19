import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VERSUS_PREFIX                   = '/video/versus'

VERSUS_URL                      = 'http://www.versus.com/'
VERSUS_METADATA                 = 'http://oln.web.entriq.net/nw/article/view/%s/?tf=DayPortMetadataRetriever_getItemsByArticle.tpl&DataRequestor=DPM&TextViewTracking=false&UserDef=true&mt=2'
VERSUS_GROUP_SELECTOR           = 'http://oln.web.entriq.net/nw/article/archive/%s/?tf=DayPortCategoryRetriever_getCategories.tpl&DataRequestor=DPM&Limit=1&Country=&subcat=true'
VERSUS_GROUP_BROWSER            = 'http://oln.web.entriq.net/nw/article/archive/%s/?tf=DayPortMetadataRetriever_getItemsByCategory.tpl&DataRequestor=DPM&Country=&Limit=43&Offset=0&UserDef=true&mt=2'
# Categories that have a 'view all' list view eg IndyCar
VERSUS_LIST_CATEGORIES               = [ 'tdfvideos', 'nhlvideos', 'indycarvideos', 'bullvideos' ]
# Categories that have several sub groups in an integrated player - eg WEC/MMA
VERSUS_GROUP_CATEGORIES         = [ 'collegefootball', 'wecmma' ]

DEBUG_XML_RESPONSE		     = True
CACHE_INTERVAL                       = 1800 # Since we are not pre-fetching content this cache time seems reasonable 
CACHE_METADATA_INTERVAL              = 604800 # 1 Week - Meta data for videos is not expected to change

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(VERSUS_PREFIX, MainMenu, L('versus'), 'icon-default.png', 'art-default.png')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.png')
  MediaContainer.viewGroup = 'Details'
  HTTP.SetCacheTime(CACHE_INTERVAL)

def MainMenu():

  dir = MediaContainer()
  dir.title1 = L('versus')
  dir.viewGroup = 'List'

  for category in VERSUS_LIST_CATEGORIES:
    dir.Append(Function(DirectoryItem(ListBrowser, title=L(category), summary='', subtitle='', thumb=R('icon-default.png')), category=category))

  for category in VERSUS_GROUP_CATEGORIES:
    dir.Append(Function(DirectoryItem(GroupSelector, title=L(category), summary='', subtitle='', thumb=R('icon-default.png')), category=category))


  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir

def ListBrowser(sender, category):

  dir = MediaContainer()
  dir.title1 = L('versus')
  dir.title2 = L(category)

  page = XML.ElementFromURL(VERSUS_URL + category, isHTML=True, errors='ignore')

  videos = page.xpath("//td/a[starts-with(@onclick, 'playerArticleID')]")

  for video in videos:

    onclick = video.get('onclick')

    id = re.search(r'\((\d+)\)', onclick).group(1)

    metadata = XML.ElementFromURL(VERSUS_METADATA % id, isHTML=False, cacheTime=CACHE_METADATA_INTERVAL)

    title = metadata.xpath("//Data[@name='Name']/text()")[0]
    description = metadata.xpath("//Data[@name='Intro']/text()")[0]
    duration = metadata.xpath("//Data[@name='DurationSeconds']/text()")[0]
    duration = int(duration) * 1000
    thumb = metadata.xpath("//Data[@name='PreviewImageURL']/text()")[0]

    url = metadata.xpath("//VideoData[@name='FormatID' and text()='4']/../VideoData[@name='URL']/text()")[0]
    url = re.sub (r' ', r'%20', url)

    dir.Append(VideoItem(url, title=title, subtitle='', summary=description, duration=duration, thumb=thumb))

  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir

def GroupSelector(sender, category):

  dir = MediaContainer()
  dir.title1 = L('versus')
  dir.title2 = L(category)
  dir.viewGroup = 'List'

  if category == 'collegefootball':
    groupId = '1211'
  else:
    # WEC/MMA
    groupId = '1133'

  page = XML.ElementFromURL(VERSUS_GROUP_SELECTOR % groupId, isHTML=False, errors='ignore')

  groups = page.xpath("//Category")

  for group in groups:
    name = str(group.xpath("./Data[@name='Name']/text()")[0])
    id = str(group.xpath("./Data[@name='ID']/text()")[0])

    dir.Append(Function(DirectoryItem(GroupBrowser, title=L(name), summary='', subtitle='', thumb=R('icon-default.png')), category=category, name=name, id=id))

  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir


def GroupBrowser(sender, category, name, id):

  dir = MediaContainer()
  dir.title1 = L(category)
  dir.title2 = name

  page = XML.ElementFromURL(VERSUS_GROUP_BROWSER % id, isHTML=False, cacheTime=CACHE_METADATA_INTERVAL)

  articles = page.xpath("//Article")

  for article in articles:

    title = article.xpath("./Data[@name='Name']/text()")[0]
    description = article.xpath("./Data[@name='Intro']/text()")[0]
    duration = article.xpath("./Data[@name='DurationSeconds']/text()")[0]
    duration = int(duration) * 1000
    thumb = article.xpath("./Data[@name='PreviewImageURL']/text()")[0]

    url = article.xpath("./Data[@name='Video']/VideoData[@name='FormatID' and text()='4']/../VideoData[@name='URL']/text()")[0]

    dir.Append(VideoItem(url, title=title, subtitle='', summary=description, duration=duration, thumb=thumb))


  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir



