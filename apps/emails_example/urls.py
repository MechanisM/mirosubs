# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.conf.urls.defaults import *

urlpatterns = patterns('emails_example.views',
    url('^$', 'index', name='index'),
    url('^send_email/$', 'send_email', name='send_email'),
    url('^email_title_changed/$', 'email_title_changed', name='email_title_changed'),
    url('^email_video_url_add/$', 'email_video_url_add', name='email_video_url_add'),
    url('^email_start_notification/$', 'email_start_notification', name='email_start_notification'),
)
