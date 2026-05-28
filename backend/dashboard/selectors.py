"""Read-only context builders for dashboard HTML views."""


def get_home_context() -> dict:
    """Home dashboard context (v1: parity with Next.js mock components)."""
    stats = [
        {
            'name': 'Total Users',
            'value': '1,234',
            'change': '+12%',
            'change_type': 'positive',
        },
        {
            'name': 'Products',
            'value': '89',
            'change': '+5.2%',
            'change_type': 'positive',
        },
        {
            'name': 'Entities',
            'value': '156',
            'change': '+8.1%',
            'change_type': 'positive',
        },
        {
            'name': 'Revenue',
            'value': '$45,231',
            'change': '+8.2%',
            'change_type': 'positive',
        },
        {
            'name': 'Growth Rate',
            'value': '23.1%',
            'change': '+2.1%',
            'change_type': 'positive',
        },
        {
            'name': 'Active Sessions',
            'value': '89',
            'change': '-3.2%',
            'change_type': 'negative',
        },
    ]

    quick_actions = [
        {
            'name': 'Add User',
            'description': 'Create a new user account',
            'href': '#',
            'title': 'Coming soon',
        },
        {
            'name': 'Add Product',
            'description': 'Add a new product to catalog',
            'href': '#',
            'title': 'Coming soon',
        },
        {
            'name': 'Add Entity',
            'description': 'Create a new business entity',
            'href': '#',
            'title': 'Coming soon',
        },
        {
            'name': 'Log Interaction',
            'description': 'Record a new interaction',
            'href': '#',
            'title': 'Coming soon',
        },
    ]

    activities = [
        {
            'description': 'New user registered: John Doe',
            'time': '2 hours ago',
        },
        {
            'description': 'Revenue increased by 8.2%',
            'time': '4 hours ago',
        },
        {
            'description': 'New product added: Premium Package',
            'time': '6 hours ago',
        },
        {
            'description': 'New entity created: Acme Corp',
            'time': '8 hours ago',
        },
    ]

    return {
        'stats': stats,
        'quick_actions': quick_actions,
        'activities': activities,
    }
