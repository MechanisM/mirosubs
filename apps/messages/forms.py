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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/

from django import forms
from messages.models import Message
from auth.models import CustomUser as User
from utils.forms import AjaxForm
from django.utils.translation import ugettext_lazy as _

class SendMessageForm(forms.ModelForm, AjaxForm):
    
    class Meta:
        model = Message
        fields = ('user', 'subject', 'content')
        
    def __init__(self, author, *args, **kwargs):
        self.author = author
        super(SendMessageForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].queryset = User.objects.exclude(pk=author.pk)
    
    def clean(self):
        if not self.author.is_authenticated():
            raise forms.ValidationError(_(u'You should be authenticated to write messages'))
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(SendMessageForm, self).save(False)
        obj.author = self.author
        commit and obj.save()
        return obj