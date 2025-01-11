from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='general_search'),
    path('video/ingredient-method/<str:id>/', views.IngredientMethodView.as_view(), name="ingredient_method"),
    path('video/<str:id>/', views.VideoView.as_view(), name='video'),
    path('history/search/', views.HistorySearchView.as_view(), name='history_search'),
    path('history/', views.HistoryListView.as_view(), name='history'),
    path('recommended/', views.RecommendationView.as_view(), name='trending'),
    path('update-watch-history/', views.UpdateWatchHistoryView.as_view(), name="update_watch_history"),
    path('playlists/', views.PlayListView.as_view(), name='playlist-list'),
    path('playlists/<int:pk>/', views.PlayListDetailView.as_view(), name='playlist-detail'),
]