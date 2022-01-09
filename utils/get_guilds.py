from functools import reduce

from data import db_session
from data.discord_server import DiscordServer


def get_guilds() -> list:
    db_session.global_init("db/jessy.db")
    db_sess = db_session.create_session()
    return reduce(lambda x, y: list(x) + list(y), db_sess.query(DiscordServer.id).all())
