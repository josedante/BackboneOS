"""
Minimal test fixtures for interactions HTML and API tests.
"""

from django.contrib.auth import get_user_model

from entities.models import Person
from world.models import Country

from .models import (
    Action,
    ActionType,
    Agent,
    Channel,
    Interaction,
    Medium,
    Touchpoint,
    TouchpointType,
)

User = get_user_model()


def create_test_country(**overrides):
    defaults = {
        'iso3_code': 'TST',
        'iso2_code': 'TS',
        'name': 'Test Country',
        'official_name': 'Republic of Test Country',
    }
    defaults.update(overrides)
    return Country.objects.create(**defaults)


def create_interaction_graph(*, user=None, country=None):
    """
    Create a minimal channel → touchpoint → interaction chain for template tests.

    Returns a dict of created objects for assertions.
    """
    country = country or create_test_country()
    user = user or User.objects.create_user(
        username='interactionshtml',
        email='interactionshtml@example.com',
        password='testpass123',
    )
    medium = Medium.objects.create(name='Web Form', code='WEBFORM')
    channel = Channel.objects.create(name='Website', code='WEBSITE', source_type='owned')
    action_type = ActionType.objects.create(name='Click', code='CLICK')
    action = Action.objects.create(name='Button Click', code='BTN_CLICK', action_type=action_type)
    agent = Agent.objects.create(agent_type='browser', name='Test Browser Agent')
    touchpoint_type = TouchpointType.objects.create(name='Web Page', code='WEB_PAGE')
    touchpoint = Touchpoint.objects.create(
        touchpoint_type=touchpoint_type,
        channel=channel,
        medium=medium,
        name='Homepage',
        code='HOMEPAGE',
    )
    person = Person.objects.create(
        first_name='John',
        last_name='Doe',
        country_of_nationality=country,
    )
    interaction = Interaction.objects.create(
        person=person,
        touchpoint=touchpoint,
        action=action,
        agent=agent,
        representative=user,
        session_id='test_session_123',
        duration_seconds=30,
        payload={'button': 'cta_main'},
    )
    return {
        'user': user,
        'country': country,
        'medium': medium,
        'channel': channel,
        'action': action,
        'agent': agent,
        'touchpoint': touchpoint,
        'person': person,
        'interaction': interaction,
    }
