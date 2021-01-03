from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
import json
from captcha.image import ImageCaptcha
from django.contrib import messages
import datetime
from django.template.loader import render_to_string
from functools import wraps
from datetime import date
from collections import defaultdict


# Create your views here.

CONST = 879


def bsf_login_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if not request.COOKIES.get("user_name"):
            return redirect(reverse("signin"))
        return f(request, *args, **kwargs)
    return decorated_function


def login_view(request):
    response = render(request, "login_page.html")
    response.delete_cookie('user_name')
    return response


def logout(request):
    return redirect("login_view")


def captche_image(request, captch):
    otp = str(int(captch) // CONST)
    image_captcha = ImageCaptcha()
    image = image_captcha.generate_image(otp)
    response = HttpResponse(content_type='image/jpeg')
    image.save(response, "JPEG")
    return response


def signin_view(request):
    if request.method == "GET":
        otp_response = requests.get(settings.OTP)
        if otp_response.status_code == 200:
            otp = str(int(otp_response.content) * CONST)
        else:
            otp = str(123 * CONST)
        return render(request, "sign_in.html", {"otp": otp})
    user_name = request.POST.get("user_name")
    password = request.POST.get("password")
    captcha = request.POST.get("captcha")
    data = {
        "UserID": user_name,
        "Password": password,
        "Passcode": captcha
    }
    captcha_key = request.POST.get("captcha_key")
    if int(captcha) == int(captcha_key) // CONST:
        result = requests.post(settings.AUTH,
                               json=data)
        if result.status_code == 200:
            if json.loads(result.content).get("IsAuthenticated") == "Authenticated":
                # import pdb; pdb.set_trace()
                profile_api_response = requests.get(
                    (settings.USER_PROFILE).format(user_id=user_name))
                if profile_api_response.status_code == 200:
                    user_profile = json.loads(profile_api_response.content)
                else:
                    user_profile = {}
                response = redirect("rules")
                response.set_cookie("user_name", user_name)
                response.set_cookie("userprofile_name",
                                    user_profile.get("UserName"))
                response.set_cookie(
                    "user_coins", user_profile.get("Total_Coins"))
                return response
            return render(request, "sign_in.html", {"error": "UserID or Password is incorrect", "otp": captcha_key})
    return render(request, "sign_in.html", {"error": "invalid captcha", "otp": captcha_key})


@bsf_login_required
def rules(request):
    request.COOKIES.get("user_name")
    user_name = request.COOKIES.get("user_name")
    return render(
        request, "rules.html",
        {"current_page": "rules", "user_name": user_name})


@bsf_login_required
def home(request):
    return render(request, "home.html")


@bsf_login_required
def schedule(request):
    return render(request, "schedule.html")


@bsf_login_required
def ledger(request):
    return render(
        request, "ledger.html",
        {"current_page": "ledger"})


@bsf_login_required
def ledger_team(request, ledger_id):
    import pdb; pdb.set_trace()
    response = requests.get((settings.MARKET_BET_DETAILS).format(userid='newuser2', market_id='xyz'))
    if response.status_code == 200:
        bet_details_list = json.loads(response.content)
        lagai_khai_list = [x for x in bet_details_list if x.get("market_type").upper() == 'LAGAI' or x.get("market_type").upper() == 'KHAI']
        yes_no_list = [x for x in bet_details_list if x.get("market_type").upper().startswith('YES') or x.get("market_type").upper().startswith('NO')]
        return render(
            request, "team.html",
            {"bet_details_list": bet_details_list,
             "lagai_khai_list": lagai_khai_list,
             "yes_no_list": yes_no_list})
    return render(
        request, "team.html",
        {"bet_details_list": [],
         "lagai_khai_list": [],
         "yes_no_list": []})


@bsf_login_required
def change_password(request):
    return render(
        request, "password.html",
        {"current_page": "change_password"})


@bsf_login_required
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


@bsf_login_required
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


@bsf_login_required
def market_detail(request):
    # import pdb; pdb.set_trace()
    market_id = request.GET.get("marketId")
    event_name = request.GET.get("eventName")
    event_id = request.GET.get("eventId")
    runner1 = request.GET.get("runnerName1")
    runner2 = request.GET.get("runnerName2")
    session_id = request.GET.get("seriesId")
    section_id1 = request.GET.get("selectionId1")
    section_id2 = request.GET.get("selectionId2")
    market_name = request.GET.get("marketName")
    market_type = request.GET.get("marketType")
    api_response = requests.get((settings.SCORE_API).format(event_id=event_id))
    score = []
    ball_status = ""
    # import pdb; pdb.set_trace()
    if api_response.status_code == 200:
        score_data = json.loads(api_response.content)
        if score_data:
            score = api_score(score_data)
            ball_status = get_ball_status(score_data)
    response = requests.get(
        (settings.ODDS_SESSION.format(market_id=market_id)))
    if response.status_code == 200:
        market_data = json.loads(response.content)
        if market_data:
            market_data['cricket'][0] = get_least_market_data(
                market_data['cricket'][0])

            return render(
                request, "market.html",
                {"market_data": market_data,
                 "event_name": event_name,
                 "runner1": runner1,
                 "runner2": runner2,
                 "event_id": event_id,
                 "session_id": session_id,
                 "section_id1": section_id1,
                 "section_id2": section_id2,
                 "market_name": market_name,
                 "market_type": market_type,
                 "market_id": market_id,
                 "score": score,
                 "ball_status": ball_status})
        return redirect("inplay")
    return render(request, "market.html")


@bsf_login_required
def tournament(request):
    return render(request, "tournament.html")


@bsf_login_required
def settings_view(request):
    return render(request, "settings.html")


@bsf_login_required
def games(request):
    return render(request, "games.html")


@bsf_login_required
def create_bet(request):
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        market_name = request.POST.get("market_name")
        market_type = request.POST.get("market_type")
        market_rate = request.POST.get("market_rate")
        market_id = request.POST.get("market_id")
        bet_amount = request.POST.get("stack")
        userid = request.COOKIES.get("user_name") or "newuser1"
        user_coins = request.COOKIES.get(
            "user_coins") or get_user_coins(userid)
        bet_date = date.today().strftime("%d-%m-%Y")
        event_name = request.POST.get("event_name")
        data = {
            "userid": userid,
            "market_name": market_name,
            "market_type": market_type,
            "market_rate": market_rate,
            "bet_amount": bet_amount,
            "bet_date": bet_date,
            "versus": event_name,
        }
        print(data)
        # import pdb; pdb.set_trace()
        user_coins = int(user_coins)
        bet_coins = int(bet_amount)
        if bet_coins > 499:
            if user_coins > bet_coins:
                result = requests.post(settings.CREATE_BET,
                                       json=data)
                if result.status_code == 200:
                    if json.loads(result.content).get("IsBetDone") == "done":
                        # messages.success(request, "Created BET Successfully")
                        response = JsonResponse(
                            {"status": "success",
                             "message": "BET Placed Successfully"})
                        user_coins = int(user_coins - bet_coins)
                        response.set_cookie("user_coins", user_coins)
                        return response
                # messages.error(request, "Created BET Failed")
                return JsonResponse(
                    {"status": "fail",
                     "message": "Created BET Failed"})
            return JsonResponse(
                {"status": "fail",
                 "message": "You Don't have coins for place BET"})
        return JsonResponse(
            {"status": "fail",
             "message": "500 is minimum amount for place BET"})


@bsf_login_required
def get_play_data():
    match_list = []
    response = requests.get(settings.INPLAY)
    if response.status_code == 200:
        data_list = json.loads(response.content)
        # for row in data_list:
        #     data = {}
        #     data["eve"]


def get_least_market_data(cricket):
    runner1_back = cricket.get('runners')[0].get('back')[0].get('price')
    runner2_back = cricket.get('runners')[1].get('back')[0].get('price')
    runner1_lay = cricket.get('runners')[0].get('lay')[0].get('price')
    runner2_lay = cricket.get('runners')[1].get('lay')[0].get('price')
    if float(runner1_back) < float(runner2_back):
        cricket['runners'][1]['back'][0]['price'] = ''
    else:
        cricket['runners'][0]['back'][0]['price'] = ''
    if float(runner1_lay) < float(runner2_lay):
        cricket['runners'][1]['lay'][0]['price'] = ''
    else:
        cricket['runners'][0]['lay'][0]['price'] = ''
    return cricket


def api_score(score_data):
    # event_id = request.GET.get("event_id")
    data = []
    if score_data:
        home_score = score_data[0].get("score").get("home")
        away_score = score_data[0].get("score").get("away")
        if home_score.get("highlight"):
            score = home_score.get("inning1")
            score1 = away_score.get("inning1")
            if score:
                score["name"] = home_score.get("name")
                data.append(score)
            else:
                data.append({"name": home_score.get("name")})
            if score1:
                score1["name"] = away_score.get("name")
                data.append(score1)
            else:
                data.append({"name": away_score.get("name")})
        elif away_score.get("highlight"):
            score = away_score.get("inning1")
            if score:
                score["name"] = away_score.get("name")
                score1 = home_score.get("inning1")
                data.append(score)
            else:
                data.append({"name": away_score.get("name")})
            if score1:
                score1["name"] = home_score.get("name")
                data.append(score1)
            else:
                data.append({"name": home_score.get("name")})
        print(data)
        return data
    return data


def get_ball_status(score):
    ball_status = score[0].get("stateOfBall")
    if ball_status.get("batsmanRuns") != "0":
        return ball_status.get("batsmanRuns")
    elif ball_status.get("wide") != "0":
        return "wide"
    elif ball_status.get("bye") != "0":
        return "bye"
    elif ball_status.get("legBye") != "0":
        return "legBye"
    elif ball_status.get("noBall") != "0":
        return "noBall"
    elif ball_status.get("dismissalTypeName") != "Not Out":
        return "Out"
    return ""


@bsf_login_required
def update_market(request):
    market_id = request.GET.get("marketId")
    event_name = request.GET.get("eventName")
    event_id = request.GET.get("eventId")
    runner1 = request.GET.get("runnerName1")
    runner2 = request.GET.get("runnerName2")
    session_id = request.GET.get("seriesId")
    section_id1 = request.GET.get("selectionId1")
    section_id2 = request.GET.get("selectionId2")
    market_name = request.GET.get("marketName")
    market_type = request.GET.get("marketType")
    api_response = requests.get((settings.SCORE_API).format(event_id=event_id))
    score = []
    ball_status = ""
    # import pdb; pdb.set_trace()
    if api_response.status_code == 200:
        score_data = json.loads(api_response.content)
        if score_data:
            score = api_score(score_data)
            ball_status = get_ball_status(score_data)
    response = requests.get(
        (settings.ODDS_SESSION.format(market_id=market_id)))
    if response.status_code == 200:
        market_data = json.loads(response.content)
        if market_data:
            market_data['cricket'][0] = get_least_market_data(
                market_data['cricket'][0])
            html = render_to_string(
                'update_market.html',
                {"market_data": market_data,
                 "event_name": event_name,
                 "runner1": runner1,
                 "runner2": runner2,
                 "event_id": event_id,
                 "session_id": session_id,
                 "section_id1": section_id1,
                 "section_id2": section_id2,
                 "market_name": market_name,
                 "market_type": market_type,
                 "market_id": market_id,
                 "score": score,
                 "ball_status": ball_status})
            return HttpResponse(html)
        return redirect("inplay")
    html = render_to_string('update_market.html')
    return HttpResponse(html)


def set_cookie(response, key, value,):
    max_age = 60 * 60  # one hour
    expires = datetime.datetime.strftime(datetime.datetime.utcnow(
    ) + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def get_user_coins(userid):
    profile_api_response = requests.get(
        (settings.USER_PROFILE).format(user_id=userid))
    if profile_api_response.status_code == 200:
        user_profile = json.loads(profile_api_response.content)
        return user_profile.get("Total_Coins")
    return 0


def get_bet_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content)
        tmp = defaultdict(list)
        for item in data:
            tmp[item['versus'], item["bet_date"]].append(
                [item['bet_amount'], item['market_name']])

        return temp


@bsf_login_required
def teen_patti_t20(request):
    return render(request, "teen_patti_t20.html")
