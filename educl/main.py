from educl import EduCL
import redis
import time
import os
import json

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DBBase = declarative_base()


class Chat(DBBase):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(64))
    active = Column(Boolean)


class EduCLWorker:
    def __init__(self):
        self.active_sessions = {}
        self.r = redis.Redis(host=os.environ.get('REDIS_HOST', "localhost"),
                             port=os.environ.get('REDIS_PORT', 6379), db=0)
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe("login_info")
        self.db_engine = create_engine('sqlite:///sqlite.db', echo=True)
        DBBase.metadata.create_all(self.db_engine)
        self.db = sessionmaker(bind=self.db_engine)()

    def run(self):
        while True:
            time.sleep(0.001)
            message = self.pubsub.get_message()
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
            chat = Chat(
                chat_id=payload['chat_id'],
                active=True
            )
            self.db.add(chat)
            self.db.commit()
        self.r.publish("login_results", json.dumps({
            "success": ok,
            "chat_id": payload['chat_id'],
        }))


EduCLWorker().run()
