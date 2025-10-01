"""
URL configuration for websites app.
"""

from django.urls import path
from . import views

app_name = 'websites'

urlpatterns = [
    path('events/page-view/', views.PageViewEventView.as_view(), name='page_view_event'),
    path('events/page-read/', views.PageReadEventView.as_view(), name='page_read_event'),
    path('events/click/', views.ClickEventView.as_view(), name='click_event'),
    path('events/form-submit/', views.FormSubmitEventView.as_view(), name='form_submit_event'),
    path('events/download/', views.DownloadEventView.as_view(), name='download_event'),
    path('events/video-play/', views.VideoPlayEventView.as_view(), name='video_play_event'),
    path('events/search/', views.SearchEventView.as_view(), name='search_event'),
    path('events/newsletter-signup/', views.NewsletterSignupEventView.as_view(), name='newsletter_signup_event'),
]
