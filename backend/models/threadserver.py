import json

from sanic.response import json as sanic_json
from sanic.response import redirect

from .message import Message, Thread


class ThreadServer:
    """
    Manager for server posts/ threads
    """

    def __init__(self, file):
        self.file = file
        try:
            with open(file) as fp:
                js = json.load(fp)
                self.threads = {int(k): Thread.from_dict(
                    j) for k, j in js["threads"].items()}
                self.id_counter = js["id_counter"]
                print(self.id_counter)
                print(js["id_counter"])
        except Exception as e:
            print(e)
            self.threads = dict()
            self.id_counter = 0

    def get_thread(self, id):
        """Return a thread object from the server"""
        return self.threads.get(id)

    def unload(self, *_):
        """Unload the server"""
        with open(self.file, mode='w+') as fp:
            json.dump({"id_counter": self.id_counter, "threads": {
                      k: j.as_dict for k, j in self.threads.items()}}, fp)

    def add_thread(self, title, initial_post, api=False):
        """Add thread to database"""
        thread = Thread(title, self.id_counter)
        self.id_counter += 1
        thread.add_message(Message(initial_post, self.id_counter))
        self.id_counter += 1
        self.threads[thread.id] = thread

        if api:
            return sanic_json({"new_thread": thread.id})
        return redirect("/{}".format(thread.id))

    def add_post(self, thread, content, api=False):
        """Add a post to a thread"""
        thread = self.get_thread(thread)
        if thread is None:
            return sanic_json({"reason": "thread_does_not_exist"}, status=404)

        message = Message(content, self.id_counter)
        thread.add_message(message)
        self.id_counter += 1

        if api:
            return sanic_json({"new_post": message.id, "thread": thread.id})
        return redirect("/{}".format(thread.id))

    @property
    def front_page(self):
        """Returns dict of front page view"""
        return [{"title": i.title, "bump": i.last_bump, "id": i.id, "messages": i.first_3} for i in sorted(self.threads.values(), key=lambda x: x.last_bump)[::-1]]
