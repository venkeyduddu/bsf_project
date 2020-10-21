from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.conf import settings
import json
from captcha.image import ImageCaptcha


# Create your views here.

CONST = 879


def login_view(request):
    return render(request, "login_page.html")


def captche_image(request, captch):
    otp = str(int(captch)//CONST)
    image_captcha = ImageCaptcha()
    image = image_captcha.generate_image(otp)
    response = HttpResponse(content_type='image/jpeg')
    image.save(response, "JPEG")
    return response


def signin_view(request):
    if request.method == "GET":
        otp_response = requests.get(settings.OTP)
        if otp_response.status_code == 200:
            otp = str(int(otp_response.content)*CONST)
        else:
            otp = str(123*CONST)
        return render(request, "sign_in.html", {"otp": otp})
    # import pdb; pdb.set_trace()
    user_name = request.POST.get("user_name")
    password = request.POST.get("password")
    captcha = request.POST.get("captcha")
    captcha_key = request.POST.get("captcha_key")
    if int(captcha) == int(captcha_key)//CONST:
    	return redirect("rules")
    return render(request, "sign_in.html", {"error": "invalid captcha", "otp": captcha_key})


def rules(request):
    return render(request, "rules.html", {"current_page": "rules"})


def home(request):
    return render(request, "home.html")


def schedule(request):
    return render(request, "schedule.html")


def ledger(request):
    return render(
        request, "ledger.html",
        {"current_page": "ledger"})


def ledger_team(request, ledger_id):
    return render(request, "team.html")


def change_password(request):
    return render(
        request, "password.html",
        {"current_page": "change_password"})


def upcoming(request):
    if request.method == "GET":
        # import pdb; pdb.set_trace()
        response = requests.get(settings.UPCOMING)
        if response.status_code == 200:
            match_list = json.loads(response.content)
            return render(
                request, "upcoming.html",
                {"match_list": match_list,
                 "current_page": "upcoming"})
        return render(request, "upcoming.html", {"current_page": "upcoming"})


def inplay(request):
    if request.method == "GET":
        # import pdb; pdb.set_trace()
        response = requests.get(settings.INPLAY)
        if response.status_code == 200:
            match_list = json.loads(response.content)
            return render(
                request, "inplay.html",
                {"match_list": match_list,
                 "current_page": "inplay"})
        return render(request, "inplay.html", {"current_page": "inplay"})


def market_detail(request):
    market_id = request.GET.get("marketId")
    event_name = request.GET.get("eventName")
    runner1 = request.GET.get("runnerName1")
    runner2 = request.GET.get("runnerName2")
    response = requests.get(
        (settings.ODDS_SESSION.format(market_id=market_id)))
    if response.status_code == 200:
        market_data = json.loads(response.content)
        return render(
            request, "market.html",
            {"market_data": market_data,
             "event_name": event_name,
             "runner1": runner1,
             "runner2": runner2})
    return render(request, "market.html")


def tournament(request):
    return render(request, "tournament.html")


def settings_view(request):
    return render(request, "settings.html")


def games(request):
    return render(request, "games.html")


def get_play_data():
    match_list = []
    response = requests.get(settings.INPLAY)
    if response.status_code == 200:
        data_list = json.loads(response.content)
        # for row in data_list:
        #     data = {}
        #     data["eve"]

