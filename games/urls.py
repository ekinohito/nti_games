from django.urls import path
from . import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Nti Games",
        default_version='v1',
        description="Some description",
    ),
    public=True,
)

urlpatterns = [
    path('', views.index_page, name='index'),
    path('login/', views.login_page, name='login'),
    path('auth/', views.auth_page, name='auth'),
    path('logout/', views.logout_page, name='logout'),
    path('user/', views.user_page, name='user_page'),

    path('analyse/', views.analyse_page, name='analyse'),
    path('analyse/dota/', views.dota_analyse, name='analyse-dota'),
    path('analyse/cs', views.cs_analyse, name='analyse-cs'),
    path('analyse/status/<str:task_id>/', views.task_status, name='task_status'),

    path('steam/login/', views.steam_login, name='steam_login'),
    path('steam/auth/', views.steam_auth, name='steam_auth'),
    path('steam/logout/', views.steam_logout, name='steam_logout'),

    path('api/user', views.CurrentUserView.as_view(), ),
    path('api/user/games', views.CurrentTalentUserView.as_view(), ),

    path('api/docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
