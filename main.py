#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from helper import *
from models.post import Post
from models.user import User


# from handlers.register import Register
from handlers.blog import BlogHandler
from handlers.register import Register
from handlers.login import Login
from handlers.login import Logout

class BlogFront(BlogHandler):
    def get(self):
        # look up all the posts by creation time
        # google's procedural language
        posts = Post.all().order('-created')
        # GQL
        # posts = db.GqlQuery(
        # "select * from Post order by created desc limit 10")
        self.render('front.html', posts=posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent=blog_key(), user_id=self.user.key().id(),
                     subject=subject, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject,
                        content=content, error=error)

class DeletePost(BlogHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if self.user and self.user.key().id() == int(post.user_id):
            post.delete()
            self.redirect('/')

        elif not self.user:
            self.redirect('/login')

        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            comments = db.GqlQuery(
                "select * from Comment where ancestor is :1 order by created desc limit 10", key)

            error = "no permission"
            self.render("permalink.html", post=post, comments=comments, error=error)


class EditPost(BlogHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if self.user and self.user.key().id() == post.user_id:
            self.render('editpost.html', subject=post.subject,
                        content=post.content, post_id=post_id)

        elif not self.user:
            self.redirect('/login')

        else:
            self.write("no permission")

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not self.user:
            return self.redirect('/login')

        if self.user and self.user.key().id() == post.user_id:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                post = db.get(key)

                post.subject = subject
                post.content = content

                post.put()

                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                error = "subject and content, please!"
                self.render("newpost.html", subject=subject,
                            content=content, error=error)

        else:
            self.write("no permission")

app = webapp2.WSGIApplication([
    ('/', BlogFront),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)/delete', DeletePost),
    ('/blog/([0-9]+)/edit', EditPost),
    ('/signup', Register),
    ('/login', Login),
    ('/logout', Logout),
], debug=True)
