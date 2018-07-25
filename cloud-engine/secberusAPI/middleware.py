from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime, date
from secberusAPI.constants import TRIAL_PERIOD_ACCESS

def TrialPeriodValidationMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        path = request.get_full_path()
        if 'logout' in path or 'docs' in path:
            return get_response(request)

        if request.user.is_authenticated():
            joined_date = request.user.date_joined.date()
            current_date = date.today()
            app_access = (current_date - joined_date)
            if app_access.days > TRIAL_PERIOD_ACCESS:
                response = HttpResponse("Trial period expired.")
            else:
                response = get_response(request)
        else:
            response = get_response(request)

        return response

    return middleware
