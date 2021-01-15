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
    path('user/', views.user_page, name='user_page'),
    path('analyse/', views.analyse_page, name='analyse'),

    path('api/auth/login/talent', views.AuthLoginTalent.as_view(), name='api_auth_login_talent'),
    path('api/auth/complete/talent', views.AuthCompleteTalent.as_view(), name='api_auth_complete_talent'),
    path('api/logout/talent', views.LogoutTalent.as_view(), name='logout'),

    path('api/auth/login/steam/', views.AuthLoginSteam.as_view(), name='steam_login'),
    path('api/auth/complete/steam/', views.AuthCompleteSteam.as_view(), name='steam_auth'),
    path('api/logout/steam', views.LogoutSteam.as_view(), name='steam_logout'),

    path('api/auth/login/blizzard/', views.AuthLoginBlizzard.as_view(), name='blizzard_login'),
    path('api/auth/complete/blizzard/', views.AuthCompleteBlizzard.as_view(), name='blizzard_auth'),
    path('api/logout/blizzard', views.LogoutBlizzard.as_view(), name='blizzard_logout'),

    path('api/analyse/dota/start', views.DotaAnalyseStart.as_view(), name='analyse-dota'),
    path('api/analyse/cs/start', views.CsAnalyseStart.as_view(), name='analyse-cs'),
    path('api/analyse/dota/result', views.CurrentUserDotaResultView.as_view(), name='analyse_dota_result'),
    path('api/analyse/cs/result', views.CurrentUserCsResultView.as_view(), name='analyse_cs_result'),
    path('api/analyse/status/', views.TaskStatus.as_view(), name='task_status'),

    path('api/user', views.CurrentUserView.as_view(), ),
    path('api/user/games', views.CurrentTalentUserView.as_view(), ),

    path('api/docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
