"""Views page - configures redirects"""
import sqlite3
from typing import List, Optional

from django.shortcuts import HttpResponse, redirect

from bunny.models import BunnyRedirect

DEFAULT_URL = "http://www.google.com/search?q=%s"


def index(request):
    """
    Index page - the most basic of readmes
    """
    return HttpResponse("Try .*/bunny/?=")


def query(request, input_query: Optional[str] = None):
    """
    Takes a query and tries to find an appropriate redirect
    If it sees the redirect, it takes it
    Defaults to google
    """
    if not input_query:
        return redirect(DEFAULT_URL % "")

    # Fetch query from input_query
    input_query_array: List[str] = input_query.split(" ", 1)
    key = input_query_array[0]
    arg = None
    if len(input_query_array) > 1:
        arg = input_query_array[1]

    # Fetch known redirects from DB
    try:
        known_redirects: List[BunnyRedirect] = BunnyRedirect.objects.all()
    except sqlite3.OperationalError:
        return redirect(DEFAULT_URL % "")

    for bunny_redirect in known_redirects:
        if key == bunny_redirect.key:
            if arg is not None:
                return redirect(bunny_redirect.arg_return % arg)

            return redirect(bunny_redirect.no_arg_return)

    return redirect(DEFAULT_URL % input_query)
