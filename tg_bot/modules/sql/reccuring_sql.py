import threading

from sqlalchemy import Column, String, Boolean, UnicodeText, Integer, func, distinct

from tg_bot.modules.helper_funcs.msg_types import Types
from tg_bot.modules.sql import SESSION, BASE

class Reccuring(BASE):
    __tablename__ = "reccuring_message"
    chat_id = Column(Integer, primary_key=True)
    value = Column (UniCodeText, nullable=False)
    seconds = Column (Integer)


    def __init__(self, user_id, reason="", is_afk=True):
        self.chat_id = str(user_id)
        self.value = value
        self.seconds = seconds

    def __repr__(self):
        return "Null"

Reccuring.__table__.create(checkfirst=True)
RECCURING_INSERTION_LOCK = threading.RLock()

def get_reccuring_message (chat_id, value, seconds):
    reccuring=SESSION.query(Reccuring).get(str(chat_id))
    SESSION.close()
    if reccuring:
        return reccuring.chat_id, reccuring.value, reccuring.seconds
    else:
        return "Null"

