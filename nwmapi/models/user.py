from nwmapi import BaseModel
from sqlalchemy import Column, String, Text, Integer


class User(BaseModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(Text)