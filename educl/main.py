import redis
import time
import os
import json

from educl import EduCL

r = redis.Redis(host=os.environ.get('REDIS_HOST', "localhost"),
                port=os.environ.get('REDIS_PORT', 6379), db=0)

pubsub = r.pubsub()
pubsub.subscribe("login_info")


active_sessions = {}


class EduCLWorker:
    def __init__(self):
        self.active_sessions = {}
        self.r = None
        self.pubsub = None

    def run(self):
        self.r = redis.Redis(host=os.environ['REDIS_HOST'],
                             port=os.environ.get('REDIS_PORT', 6379), db=0)
        self.pubsub = r.pubsub()
        while True:
            time.sleep(0.001)
            message = pubsub.get_message()
            if message:
                if message['type'] != 'message':
                    continue
                payload = json.loads(message['data'])
                if message['channel'] == b'login_info':
                    self.handle_login_info(payload)

    def handle_login_info(self, payload):
        print("LOGIN", payload)
        session = EduCL()
        ok = session.login(payload['username'], payload['password'])
        if ok:
            self.active_sessions[payload['chat_id']] = session
        r.publish("login_results", json.dumps({
            "success": ok,
            "chat_id": payload['chat_id'],
        }))


EduCLWorker().run()
