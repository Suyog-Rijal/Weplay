from django.urls import path
from .views import SearchView

urlpatterns = [
	path('search/<str:query>/', SearchView.as_view(), name='youtube_search'),
]