from google.appengine.ext import db

import feedparser
from datetime import datetime

from urllib import urlencode, quote
from urllib2 import urlopen

HC_URL  = 'https://api.hipchat.com/v1/rooms/message'



class RSSFeed(db.Model):
    name            = db.StringProperty(indexed=False)
    url             = db.LinkProperty()
    last_fetched    = db.DateTimeProperty()

    room            = db.StringProperty()
    token           = db.StringProperty()

    def getMessages(self):
        return self.hipchatmessage_set.order('-date')

    def update(self):
        feed_response = feedparser.parse(self.url)
        items = feed_response.get('entries')
        for item in items:
            exists = HipChatMessage.get_by_key_name(item.get('guid'))
            if not exists:
                t = item.published_parsed
                item_date = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                message = HipChatMessage(
                    feed        = self,
                    created     = datetime.now(),
                    date        = item_date,
                    title       = item.title,
                    summary     = item.summary,
                    key_name    = item.guid,
                )
                message.put()
        self.last_fetched = datetime.now()
        self.put()
        return



class HipChatMessage(db.Model):
    feed            = db.ReferenceProperty(RSSFeed)
    created         = db.DateTimeProperty()
    date            = db.DateTimeProperty()
    dispatched      = db.DateTimeProperty()
    summary         = db.TextProperty()
    title           = db.TextProperty()

    def dispatch(self):
        summary = self.summary
        title   = self.title
        if len(summary) > 200:
            summary = summary[:200] + '&hellip;'

        message = """
            <b>{title}</b><br>
            <p>
                {summary}
            </p>
            (<a href="{guid}">Status Page &raquo;</a>)
        """.format(
            title   = title,
            summary = summary,
            guid    = 'http://status.aws.amazon.com/',
        )

        if title.find('[RESOLVED]') > -1:
            color = 'green'
        elif title.find('Informational message') > -1:
            color = 'yellow'
        else:
            color = 'red'

        payload = {
            'auth_token'    : self.feed.token,
            'room_id'       : self.feed.room,
            'from'          : self.feed.name,
            'message'       : message,
            'notify'        : 1,
            'color'         : color,
        }
        params = []
        for param, value in payload.items():
            params.append('%s=%s' % (param, quote(str(value))))

        url = HC_URL + '?' + '&'.join(params)

        try:
            r = urlopen(url, data={})
        except:
            return False
        else:
            self.dispatched = datetime.now()
            self.put()
            return True


