from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from utils.translation import get_languages_list

ALL_LANGUAGES = tuple((val, _(name))for val, name in settings.ALL_LANGUAGES)

class SearchForm(forms.Form):
    SORT_TYPE_CHOICES = (
        ('asc', _(u'Ascending')),
        ('desc', _(u'Descending'))
    )
    SORT_CHOICES = (
        ('', _('Most relevant')),
        ('date', _(u'Newest')),
        ('sub_fetch', _(u'Most subtitle plays')),
        ('page_loads', _(u'Most page loads')),
        ('comments', _(u'Most commented')),
        ('languages', _(u'Most languages')),
        ('edited', _(u'Last edited')),
        ('contributors', _(u'Most commented')),
        ('activity', _(u'Most activity'))
    )
    DISPLAY_CHOICES = (
        ('all', _(u'all')),
        ('thumbnails', _(u'thumbnails')),
        #('details', _(u'details')),
    )
    q = forms.CharField(required=False, label=_(u'query'))
    #st = forms.ChoiceField(choices=SORT_TYPE_CHOICES, required=False, initial='desc', 
    #                       label=_(u'sort order'))
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial='', 
                             label=_(u'sort type'))
    langs = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'languages'),
                              help_text=_(u'Left blank for any language'))
    video_lang = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'video language'),
                              help_text=_(u'Left blank for any language'))
    display = forms.ChoiceField(choices=DISPLAY_CHOICES, required=False, initial='all')
    
    
    def __init__(self, user, user_langs, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        choices = list(get_languages_list())
        self.user_langs = user_langs
        choices[:0] = (
            ('my_langs', _(u'My languages')),
            ('', _(u'Any Language')),
            ('not_selected', 'Not ---'),
        )
        self.fields['langs'].choices = choices
        self.fields['video_lang'].choices = choices
        self.user = user

        
    def search_qs(self, qs):
        q = self.cleaned_data.get('q')
        ordering = self.cleaned_data.get('sort', '')
        langs = self.cleaned_data.get('langs')
        video_language = self.cleaned_data.get('video_lang')
        
        order_fields = {
            'date': 'created',
            'sub_fetch': 'subtitles_fetched_count',
            'page_loads': 'widget_views_count',
            'comments': 'comments_count',
            'languages': 'languages_count',
            'contributors': 'contributors_count',
            'activity': 'activity_count',
            'edited': 'edited'
        }
        
        qs = qs.auto_query(q)
        
        if video_language:
            if video_language == 'my_langs':
                qs = qs.filter(video_language__in=self.user_langs)
            elif video_language == 'not_selected' and langs not in ['', 'not_selected']:
                if langs == 'my_langs':
                    qs = qs.exclude(video_language__in=self.user_langs)
                else:
                    qs = qs.exclude(video_language=langs)
            else:
                qs = qs.filter(video_language=video_language)
        
        if langs:
            if langs == 'my_langs':
                qs = qs.filter(languages__in=self.user_langs)
            elif langs == 'not_selected' and video_language not in ['', 'not_selected']:
                if video_language == 'my_langs':
                    qs = qs.exclude(languages__in=self.user_langs)
                else:
                    qs = qs.exclude(languages=langs)
            else:
                qs = qs.filter(languages=langs)
        
        if ordering:
            qs = qs.order_by('-'+order_fields[ordering])

        return qs