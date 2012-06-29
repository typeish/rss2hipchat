import webapp2

from google.appengine.ext.webapp    import template
from google.appengine.ext.webapp    import util

from models import RSSFeed, HipChatMessage

from datetime import datetime
import settings
import os



def render(template_name, context={}):
    path = os.path.join(settings.TEMPLATE_DIRECTORY, template_name)
    return template.render(path, context)


def renderIndex(response):
    context = {
        'feeds'     : RSSFeed.all(),
    }
    result = render('index.html.django', context)
    response.out.write(result)



class MainHandler(webapp2.RequestHandler):
    def get(self):
        renderIndex(self.response)

    def post(self):
        feed_name   = self.request.get('name')
        feed_url    = self.request.get('url')
        target_room = self.request.get('room')
        auth_token  = self.request.get('token')
        q = RSSFeed.all()
        q = q.filter("url =", feed_url)
        q = q.filter("token =", auth_token)
        q = q.filter("room =", target_room)
        if q.count() == 0:
            feed = RSSFeed(
                name    = feed_name,
                url     = feed_url,
                room    = target_room,
                token   = auth_token,
            )
            feed.put()
        renderIndex(self.response)



app = webapp2.WSGIApplication(
    [
        ('/', MainHandler)
    ], debug=settings.DEBUG)


