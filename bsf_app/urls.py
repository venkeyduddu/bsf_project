from django.urls import path
from bsf_app.views import *


urlpatterns = [
	path('', login_view, name="login_view"),
    path('user/logout', logout, name="logout"),
	path('get/captche/<str:captch>/', captche_image, name="captche_image"),
    path('user/rules/', rules, name="rules"),
    path('user/dashboard/', home, name="home"),
    path('user/dashboard/schedule/', schedule, name="schedule"),
    path('user/dashboard/ledger/', ledger, name="ledger"),
    path('user/dashboard/ledger/<int:ledger_id>/', ledger_team, name="ledger_team"),
    path('user/market_detail/', market_detail, name="market_detail"),
    path('user/change-password/', change_password, name="change_password"),
    path('user/upcoming/', upcoming, name="upcoming"),
    path('user/matches/', inplay, name="inplay"),
    path('user/sign-in/', signin_view, name="signin"),
    path('user/settings/', settings_view, name="settings"),
    path('user/tournament/', tournament, name="tournament"),
    path('user/games/', games, name="games"),
    path('user/place-bet/', create_bet, name="create_bet"),
    path('update_market/', update_market, name="update_market"),
]
