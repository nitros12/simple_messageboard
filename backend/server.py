import asyncio
import cgi
import json
import os

import models
from chameleon import PageTemplateLoader
from sanic import Sanic, request
from sanic.response import json as sanic_json
from sanic.response import html, redirect

BASE = os.path.dirname(os.path.abspath(__file__))
ThreadDatabase = os.path.join(BASE, "files", "threads.json")
TemplateDir = os.path.join(BASE, "templates")


templates = PageTemplateLoader(TemplateDir)
front_page_template = templates["front_page.pt"]
thread_template = templates["thread_page.pt"]
fail_page = templates["fail_page.pt"]

app = Sanic(__name__)

server = models.ThreadServer(ThreadDatabase)


@app.route("/")
async def front_page(request):
    return html(front_page_template.render(threads=server.front_page))


@app.route("/<thread:int>")
async def view_thread(request, thread):
    thread = server.get_thread(thread)
    if thread is None:
        return redirect("/", content_type="text/html; charset=utf-8")
    return html(thread_template.render(thread=thread.as_dict))


@app.route("/api/index")
async def index(request):
    return sanic_json(server.front_page)


@app.route("/api/new_thread", methods=["POST"])
async def new_thread(request):
    content = request.form.get("content")
    title = request.form.get("title")
    if (title and content) and ((0 < len(content) <= 50) and (0 < len(title) <= 200)):
        return server.add_thread(cgi.escape(title), cgi.escape(content))
    return html(fail_page.render(reason="Invalid content or title"), status=404)


@app.route("/api/<thread:int>/new_post", methods=["POST"])
async def new_post(request, thread):
    content = request.form.get("content")

    if content and (0 < len(content) <= 200):
        return server.add_post(thread, cgi.escape(content))
    return html(fail_page.render(reason="Invalid content"), status=404)


@app.route("/api/<thread:int>")
async def view_thread_api(request, thread):
    thread = server.get_thread(thread)
    if thread is None:
        return html(fail_page.render(reason="thread does not exist"), status=404)

    return sanic_json(thread.as_dict)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8082, after_stop=server.unload)
