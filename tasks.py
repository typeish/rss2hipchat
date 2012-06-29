
import webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import util

from datetime import datetime

from models import RSSFeed, HipChatMessage
import settings


class FetchTask(webapp2.RequestHandler):
    def get(self):
        self.post()
    def post(self):
        for feed in RSSFeed.all():
            feed.update()
        return



class DispatchTask(webapp2.RequestHandler):
    def get(self):
        self.post()
    def post(self):
        messages = HipChatMessage.all().filter('dispatched =', None).order('-date')
        for message in messages:
            message.dispatch()
        return



app = webapp2.WSGIApplication(
    [
        ('/tasks/fetch'    , FetchTask),
        ('/tasks/dispatch' , DispatchTask),
    ], debug=settings.DEBUG)
