import sqlalchemy
from sqlalchemy import ForeignKey
from datetime import datetime
from data.db_session import SqlAlchemyBase


class PremiumModule(SqlAlchemyBase):
    __tablename__ = 'PremiumModule'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    guild_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('DiscordServer.id'))
    date_bought = sqlalchemy.Column(sqlalchemy.DATETIME, default=datetime.now)
