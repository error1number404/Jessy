import sqlalchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from data.db_session import SqlAlchemyBase


class DiscordServer(SqlAlchemyBase):
    __tablename__ = 'DiscordServer'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    premium_modules = relationship("PremiumModule")

