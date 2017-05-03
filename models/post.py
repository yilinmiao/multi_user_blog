from google.appengine.ext import db
from helper import *


class Post(db.Model):
    user_id = db.IntegerProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        # everytime there is a new line, the new line needs a linebreak
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)
