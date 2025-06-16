from django.urls import path
from .views import SearchView, VideoDetailView

urlpatterns = [
	path('search/<str:query>/', SearchView.as_view(), name='youtube_search'),
	path('detail/<str:video_id>/', VideoDetailView.as_view(), name='youtube_detail'),
]