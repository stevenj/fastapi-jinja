import inspect
import os
from functools import wraps
from typing import Optional

import fastapi

from fastapi import FastAPI, Request

from fastapi.templating import Jinja2Templates
from jinja2.environment import TemplateStream
# from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from fastapi_jinja.exceptions import FastAPIJinjaException

__initialized = None
template_path: Optional[str] = None
templates = None

def global_init(template_folder: str):
    global __initialized, template_path, templates

    
    if __initialized:
        return


    if not template_folder:
        msg = f"The template_folder must be specified."
        raise FastAPIJinjaException(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise FastAPIJinjaException(msg)

    template_folder

    templates = Jinja2Templates(directory=template_folder)
    __initialized = True


def clear():
    global __initialized, template_path
    __initialized = None
    template_path = None


def render(template_file: str, **template_data):
    if not __initialized:
        raise Exception("You must call global_init() before rendering templates.")

    # page: Template = __env.get_template(template_file)
    # rendered_page = page.render(template_data)

    print(templates)
    rendered_page = templates.TemplateResponse(template_file, template_data)
    return rendered_page


def response(
    template_file: str, mimetype="text/html", status_code=200, **template_data
):
    html = render(template_file, **template_data)
    return fastapi.Response(content=html, media_type=mimetype, status_code=status_code)


def template(template_file: str, mimetype: str = "text/html"):
    """
    Decorate a FastAPI view method to render an HTML response.

    :param str template_file: The Chameleon template file (path relative to template folder, *.pt).
    :param str mimetype: The mimetype response (defaults to text/html).
    :return: Decorator to be consumed by FastAPI
    """
    if not template_file:
        raise FastAPIJinjaException("You must specify a template file.")

    def response_inner(f):
        @wraps(f)
        def sync_view_method(*args, **kwargs):
            response_val, request = f(*args, **kwargs)
            return __render_response(template_file, response_val, request, mimetype)

        @wraps(f)
        async def async_view_method(*args, **kwargs):
            response_val, request = await f(*args, **kwargs)
            return __render_response(template_file, response_val, request, mimetype)

        if inspect.iscoroutinefunction(f):
            return async_view_method
        else:
            return sync_view_method

    return response_inner


def __render_response(template_file, response_val, request, mimetype):

    # print(f"template_file : {template_file}")
    # print(f"response_val : {response_val}")

    if isinstance(response_val, fastapi.Response):
        return response_val

    if isinstance(response_val, dict):
        model = dict(response_val)
    else:
        model = {}

    if "request" in model:
        msg = f"'request' can't be used as a key to be processed by jinja."
        raise FastAPIJinjaException(msg)
    else:
        model["request"] = request
    
    # print(f"model : {model}")

    if template_file and not isinstance(response_val, dict):
        msg = f"Invalid return type {type(response_val)}, we expected a dict as the return value."
        raise FastAPIJinjaException(msg)

    return render(template_file, **model)
