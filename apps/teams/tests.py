# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
from os import path
from django.conf import settings
from teams.models import Team, Invite
from messages.models import Message
from videos.models import Video, VIDEO_TYPE_YOUTUBE
from django.db.models import ObjectDoesNotExist
from auth.models import CustomUser as User
from django.contrib.contenttypes.models import ContentType

class TeamsTest(TestCase):
    
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
    
    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"
        }
        self.user = User.objects.get(username=self.auth["username"])
    
    def test_views(self):
        self.client.login(**self.auth)
        
        #------- create ----------
        response = self.client.get(reverse("teams:create"))
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "description": u"",
            "video_url": u"",
            "membership_policy": u"4",
            "video_policy": u"1",
            "logo": u"",
            "slug": u"new-team",
            "name": u"New team"
        }
        response = self.client.post(reverse("teams:create"), data)
        self.failUnlessEqual(response.status_code, 302)
        team = Team.objects.get(slug=data['slug'])

        #---------- index -------------
        response = self.client.get(reverse("teams:index"))
        self.failUnlessEqual(response.status_code, 200) 
               
        response = self.client.get(reverse("teams:index"), {'q': 'vol'})
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "q": u"vol",
            "o": u"date"
        }
        response = self.client.get(reverse("teams:index"), data)
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get(reverse("teams:index"), {'o': 'my'})
        self.failUnlessEqual(response.status_code, 200)
                
        #---------- edit ------------
        url = reverse("teams:edit", kwargs={"slug": team.slug})
        response = self.client.get(url)

        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:edit_logo", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 200)
        team = Team.objects.get(pk=team.pk)
        self.assertTrue(team.logo)
        
        data = {
            "name": u"New team",
            "video_url": u"http://www.youtube.com/watch?v=tGsHDUdw8As",
            "membership_policy": u"4",
            "video_policy": u"1",
            "description": u"",
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:edit", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 302)
        video = Video.objects.get(videourl__type=VIDEO_TYPE_YOUTUBE, videourl__videoid='tGsHDUdw8As')
        team = Team.objects.get(pk=team.pk)
        self.assertEqual(team.video, video)
        
        #-------------- edit members ---------------
        url = reverse("teams:edit_members", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        #-------------- edit videos -----------------
        url = reverse("teams:edit_videos", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)

        url = reverse("teams:edit", kwargs={"slug": "volunteer1"})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)

        self.client.logout()
        
        url = reverse("teams:edit", kwargs={"slug": "volunteer"})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 302)
        
        self.client.login(**self.auth)
        #-------------- applications ----------------
        url = reverse("teams:applications", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        #------------ detail ---------------------
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.pk})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url, {'q': 'Lions'})
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url, {'q': 'empty result'})
        self.failUnlessEqual(response.status_code, 200)        
        
        #------------ detail members -------------
        
        url = reverse("teams:detail_members", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail_members", kwargs={"slug": team.slug})
        response = self.client.get(url, {'q': 'test'})
        self.failUnlessEqual(response.status_code, 200)

        #-------------members activity ---------------
        #Deprecated
        #url = reverse("teams:members_actions", kwargs={"slug": team.slug})
        #response = self.client.get(url)
        #self.failUnlessEqual(response.status_code, 200)        
        
        #------------- add video ----------------------
        self.client.login(**self.auth)
        
        data = {
            "languages-MAX_NUM_FORMS": u"",
            "description": u"",
            "language": u"en",
            "title": u"",
            "languages-0-language": u"be",
            "languages-0-id": u"",
            "languages-TOTAL_FORMS": u"1",
            "video_url": u"http://www.youtube.com/watch?v=Hhgfz0zPmH4&feature=grec_index",
            "thumbnail": u"",
            "languages-INITIAL_FORMS": u"0"
        }
        tv_len = team.teamvideo_set.count()
        url = reverse("teams:add_video", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.assertEqual(tv_len+1, team.teamvideo_set.count())
        self.assertRedirects(response, reverse("teams:team_video", kwargs={"team_video_pk": 3}))

        #-------edit team video -----------------
        team = Team.objects.get(pk=1)
        tv = team.teamvideo_set.get(pk=1)
        tv.title = ''
        tv.description = ''
        tv.save()
        data = {
            "languages-MAX_NUM_FORMS": u"",
            "languages-INITIAL_FORMS": u"0",
            "title": u"change title",
            "languages-0-language": u"el",
            "languages-0-id": u"",
            "languages-TOTAL_FORMS": u"1",
            "languages-0-completed": u"on",
            "thumbnail": u"",
            "description": u"and description"
        }
        url = reverse("teams:team_video", kwargs={"team_video_pk": tv.pk})
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("teams:team_video", kwargs={"team_video_pk": tv.pk}))        
        tv = team.teamvideo_set.get(pk=1)
        self.assertEqual(tv.title, u"change title")
        self.assertEqual(tv.description, u"and description")
        
        #-----------delete video -------------
        url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 200)
        try:
            team.teamvideo_set.get(pk=1)
            self.fail()
        except ObjectDoesNotExist:
            pass
        
        #----------inviting to team-----------
        user2 = User.objects.get(username="alerion")
        data = {
            "username": user2.username,
            "note": u"asd",
            "team_id": team.pk
        }
        response = self.client.post(reverse("teams:invite"), data)
        self.failUnlessEqual(response.status_code, 200)
        
        invite = Invite.objects.get(user__username=user2.username, team=team)
        ct = ContentType.objects.get_for_model(Invite)
        message = Message.objects.get(object_pk=invite.pk, content_type=ct, user=user2)
        
        members_count = team.members.count()
        
        self.client.login(username = user2.username, password ='alerion')
        url = reverse("teams:accept_invite", kwargs={"invite_pk": invite.pk})
        response = self.client.get(url)
        
        self.assertEqual(members_count+1, team.members.count())
        
        self.client.login(**self.auth)

        url = reverse("teams:edit_members", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
 
        data = {
            "ot": u"desc",
            "page": u"1",
            "o": u"username"
        }
        url = reverse("teams:edit_members", kwargs={"slug": team.slug})
        response = self.client.get(url, data)
        self.failUnlessEqual(response.status_code, 200) 
        
        self.assertFalse(team.is_manager(user2))
        
        url = reverse("teams:promote_member", kwargs={"user_pk": user2.pk, "slug": team.slug})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("teams:edit_members", kwargs={"slug": team.slug}))
        
        self.assertTrue(team.is_manager(user2))
        
        url = reverse("teams:demote_member", kwargs={"user_pk": user2.pk, "slug": team.slug})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("teams:edit_members", kwargs={"slug": team.slug}))
        
        self.assertFalse(team.is_manager(user2))
        
        url = reverse("teams:remove_member", kwargs={"user_pk": user2.pk, "slug": team.slug})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 200)
        
        self.assertFalse(team.is_member(user2))
        
    def test_fixes(self):
        url = reverse("teams:detail", kwargs={"slug": 'slug-does-not-exist'})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)