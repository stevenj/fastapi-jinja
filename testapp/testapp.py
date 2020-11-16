import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

import fastapi_jinja


app = FastAPI()

folder = os.path.dirname(__file__)
print(f"folder = {folder}")
template_folder = os.path.join(folder, "templates")
print(template_folder)
template_folder = os.path.abspath(template_folder)


fastapi_jinja.global_init(template_folder)


@app.get("/")
@fastapi_jinja.template("test.j2")
async def root(request: Request):
  render_dict = {
    "title": "Test Title",
  }

  user_ids = ["user-"+str(i) for i in range(10)]

  users = [{"url": f"http://site/{user}", "username": user} for user in user_ids]

  render_dict["users"] = users  

  return render_dict, request
