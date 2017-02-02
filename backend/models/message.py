import time


class Message:

    def __init__(self, content, id, *, timestamp=None):
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.content = content
        self.id = id

    @property
    def as_dict(self):
        return {"timestamp": self.timestamp, "content": self.content, "id": self.id}


class Thread:

    def __init__(self, title, id, *, last_bump=None, messages=None):
        self.title = title
        self.last_bump = last_bump if last_bump is not None else time.time()
        self.id = id
        self.messages_ = messages if messages is not None else []

    def add_message(self, message):
        self.messages_.append(message)
        self.last_bump = time.time()

    @property
    def first_3(self):
        return self.messages[-3:]

    @property
    def messages(self):
        """Return list of messages in sorted order of oldest (first) to youngest (last)"""
        return sorted(self.messages_, key=lambda x: x.timestamp)

    @property
    def as_dict(self):
        return {"title": self.title, "bump": self.last_bump, "id": self.id,
                "messages": [i.as_dict for i in self.messages], "posturl": "api/{}/new_post".format(self.id)}

    @classmethod
    def from_dict(cls, d):
        thread = Thread(d["title"], d["id"], last_bump=d["bump"])
        thread.messages_ = [Message(**i) for i in d["messages"]]
        return thread
