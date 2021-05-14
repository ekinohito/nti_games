import datetime


def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        sessionid = request.headers.get('sessionid', None)
        if sessionid:
            max_age = 365 * 24 * 60 * 60  # 10 years
            expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
            request.set_cookie('sessionid', sessionid, expires=expires.utctimetuple(), max_age=max_age)

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware