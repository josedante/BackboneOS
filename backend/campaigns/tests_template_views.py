"""
Tests for campaigns HTML views (operator CRUD).

Campaigns and campaign–touchpoint links are editable here; interaction logging
does not happen in this namespace.
"""

import uuid
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Campaign, CampaignTouchpoint
from .test_factories import create_campaign_graph

User = get_user_model()


class CampaignsTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        graph = create_campaign_graph()
        self.user = graph['user']
        self.campaign = graph['campaign']
        self.link = graph['link']
        self.touchpoint = graph['touchpoint']

    def test_anonymous_list_redirects_to_login(self):
        response = self.client.get(reverse('campaigns_html:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_list_renders_campaign(self):
        self.client.login(username='campaignshtml', password='testpass123')
        response = self.client.get(reverse('campaigns_html:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spring Launch')

    def test_touchpoints_tab(self):
        self.client.login(username='campaignshtml', password='testpass123')
        response = self.client.get(reverse('campaigns_html:list'), {'tab': 'touchpoints'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Launch Landing')

    def test_campaign_create(self):
        self.client.login(username='campaignshtml', password='testpass123')
        response = self.client.post(
            reverse('campaigns_html:create'),
            {
                'name': 'Winter Promo',
                'code': 'WINTER_2026',
                'description': 'Seasonal promo',
                'start_date': str(date.today()),
                'end_date': str(date.today() + timedelta(days=14)),
                'budget': '5000',
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Campaign.objects.get(code='WINTER_2026')
        self.assertEqual(created.name, 'Winter Promo')

    def test_campaign_detail_update(self):
        self.client.login(username='campaignshtml', password='testpass123')
        response = self.client.post(
            reverse('campaigns_html:detail', kwargs={'pk': self.campaign.pk}),
            {
                'name': 'Spring Launch Updated',
                'code': self.campaign.code,
                'description': self.campaign.description,
                'start_date': str(self.campaign.start_date),
                'end_date': str(self.campaign.end_date),
                'budget': str(self.campaign.budget),
                'content_type': '',
                'funnel_stage': Campaign.DO,
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.name, 'Spring Launch Updated')

    def test_campaign_delete(self):
        self.client.login(username='campaignshtml', password='testpass123')
        pk = self.campaign.pk
        response = self.client.post(reverse('campaigns_html:delete', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Campaign.objects.filter(pk=pk).exists())

    def test_touchpoint_link_create(self):
        self.client.login(username='campaignshtml', password='testpass123')
        from interactions.models import Medium, Touchpoint, TouchpointType

        medium = Medium.objects.create(name='SMS', code='SMS_CP2')
        channel = self.touchpoint.channel
        tp_type = TouchpointType.objects.create(name='SMS Page', code='SMS_PAGE_CP2')
        other_touchpoint = Touchpoint.objects.create(
            touchpoint_type=tp_type,
            channel=channel,
            medium=medium,
            name='SMS CTA',
            code='SMS_CTA',
        )
        response = self.client.post(
            reverse('campaigns_html:touchpoint_create'),
            {
                'campaign': str(self.campaign.pk),
                'touchpoint': str(other_touchpoint.pk),
                'weight': '2.5',
                'priority': '5',
            },
        )
        if response.status_code != 302:
            self.fail(response.context['form'].errors.as_json())
        self.assertTrue(
            CampaignTouchpoint.objects.filter(
                campaign=self.campaign, touchpoint=other_touchpoint
            ).exists()
        )

    def test_touchpoint_link_detail_update(self):
        self.client.login(username='campaignshtml', password='testpass123')
        response = self.client.post(
            reverse('campaigns_html:touchpoint_detail', kwargs={'pk': self.link.pk}),
            {
                'campaign': str(self.campaign.pk),
                'touchpoint': str(self.touchpoint.pk),
                'weight': '3.0',
                'priority': '20',
            },
        )
        if response.status_code != 302:
            self.fail(response.context['form'].errors.as_json())
        self.link.refresh_from_db()
        self.assertEqual(self.link.weight, 3.0)

    def test_touchpoint_link_delete(self):
        self.client.login(username='campaignshtml', password='testpass123')
        link_pk = self.link.pk
        response = self.client.post(
            reverse('campaigns_html:touchpoint_delete', kwargs={'pk': link_pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CampaignTouchpoint.objects.filter(pk=link_pk).exists())

    def test_campaign_detail_404(self):
        self.client.login(username='campaignshtml', password='testpass123')
        response = self.client.get(
            reverse('campaigns_html:detail', kwargs={'pk': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)
