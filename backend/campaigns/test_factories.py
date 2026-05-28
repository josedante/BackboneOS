"""
Minimal test fixtures for campaigns HTML tests.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model

from interactions.models import Channel, Medium, Touchpoint, TouchpointType
from our_institution.models import Division, OurOrganization, Team

from .models import Campaign, CampaignTouchpoint

User = get_user_model()


def create_campaign_graph(*, user=None):
    """
    Organization → division → team → campaign → touchpoint link.

    Returns created objects for template view assertions.
    """
    user = user or User.objects.create_user(
        username='campaignshtml',
        email='campaignshtml@example.com',
        password='testpass123',
    )
    organization = OurOrganization.objects.create(name='Campaign Test Org')
    division = Division.objects.create(
        name='Marketing Division',
        code='MKT_DIV',
        organization=organization,
    )
    team = Team.objects.create(
        name='Growth Team',
        code='GROWTH',
        division=division,
    )
    campaign = Campaign.objects.create(
        name='Spring Launch',
        code='SPRING_2026',
        description='Q2 product launch',
        start_date=date.today(),
        end_date=date.today() + timedelta(days=60),
        budget=Decimal('25000.00'),
        division=division,
        team=team,
        funnel_stage=Campaign.DO,
    )
    medium = Medium.objects.create(name='Email', code='EMAIL_CP')
    channel = Channel.objects.create(
        name='Newsletter',
        code='NEWSLETTER_CP',
        source_type='owned',
    )
    touchpoint_type = TouchpointType.objects.create(name='Landing', code='LANDING_CP')
    touchpoint = Touchpoint.objects.create(
        touchpoint_type=touchpoint_type,
        channel=channel,
        medium=medium,
        name='Launch Landing',
        code='LAUNCH_LANDING',
    )
    link = CampaignTouchpoint.objects.create(
        campaign=campaign,
        touchpoint=touchpoint,
        weight=1.0,
        priority=10,
    )
    return {
        'user': user,
        'organization': organization,
        'division': division,
        'team': team,
        'campaign': campaign,
        'touchpoint': touchpoint,
        'link': link,
    }
