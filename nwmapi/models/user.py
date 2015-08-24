import uuid

from nwmapi.models import GUID, Base, CoerceUTF8
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum, UnicodeText
from sqlalchemy.orm import relationship, backref


# http://docs.sqlalchemy.org/en/improve_toc/orm/basic_relationships.html
# http://docs.sqlalchemy.org/en/improve_toc/orm/loading_relationships.html
# http://docs.sqlalchemy.org/en/improve_toc/orm/loading_relationships.html#what-kind-of-loading-to-use
# http://docs.sqlalchemy.org/en/improve_toc/orm/cascades.html#unitofwork-cascades
# http://docs.sqlalchemy.org/en/improve_toc/orm/relationship_api.html#sqlalchemy.orm.relationship
# http://docs.sqlalchemy.org/en/improve_toc/orm/backref.html
# Introduction to SQLAlchemy - Pycon 2013 - https://www.youtube.com/watch?v=woKYyhLCcnU

USER_TYPE_CONSUMER = 'consumer'
USER_TYPE_BUSINESS = 'business'
USER_TYPE_ADMIN = 'admin'

USER_STATUS_ACTIVE = 'active'
USER_STATUS_SUSPENDED = 'suspended'
USER_STATUS_CLOSED = 'closed'

class User(Base):
    __tablename__ = 'user'

    id = Column(GUID, default=uuid.uuid4, primary_key=True)
    username = Column(CoerceUTF8(100), unique=True)
    password = Column(CoerceUTF8)  # password hash
    email = Column(String(100), unique=True)  # lowercase only?
    fullname = Column(CoerceUTF8(100), nullable=False)
    profile_id = Column(GUID, ForeignKey('profile.id'))
    profile = relationship("Profile", backref=backref("user", uselist=False), lazy='joined')
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String)
    email_verification_expired = Column(DateTime)
    # role_id = Column(GUID, ForeignKey('role.id'))
    type = Column(Enum(USER_TYPE_CONSUMER, USER_TYPE_BUSINESS, USER_TYPE_ADMIN),
                  name='user_type',
                  default=USER_TYPE_CONSUMER)
    status = Column(Enum(USER_STATUS_ACTIVE, USER_STATUS_SUSPENDED, USER_STATUS_CLOSED),
                    name='user_status',
                    default=USER_STATUS_ACTIVE)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())
    # groups = relationship(
    #     Group,
    #     secondary='user_group',
    #     lazy='dynamic',
    # )

    def __repr__(self):
        return "<User {} {} {} {}>".format(self.username, self.email, self.type, self.status)

#
# class UserSchema(colander.MappingSchema):
#     username = colander.SchemaNode(colander.String(), validator=colander.Length(min=3, max=100))
#     email = colander.SchemaNode(colander.String(), validator=colander.Email())
#     # type = colander.SchemaNode(colander.String(),
#     #                            validator=colander.OneOf(
#     #                                [USER_TYPE_CONSUMER, USER_TYPE_BUSINESS, USER_TYPE_ADMIN]),
#     #                            missing=USER_TYPE_CONSUMER)
#

class Profile(Base):
    __tablename__ = 'profile'
    id = Column(GUID, primary_key=True)
    location = Column(CoerceUTF8(255))
    about_me = Column(CoerceUTF8(1024))
    member_since = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now())
    avatar_hash = Column(String(32))
    custom_data = Column(UnicodeText)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    def __repr__(self):
        return "<Profile {}>".format(self.name)


# class Group(Base):
#     __tablename__ = 'group'
#
#     id = Column(GUID, primary_key=True)
#     name = Column(CoerceUTF8(64), unique=True)
#     description = Column(CoerceUTF8(255))
#     users = relationship(
#         User,
#         secondary='user_group',
#         lazy='dynamic',
#     )
#
#     def __repr__(self):
#         return "<Group {}>".format(self.name)
#
#
# class UserGroup(Base):
#     __tablename__ = 'user_group'
#
#     user_id = Column(GUID,
#                      ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"),
#                      primary_key=True)
#     group_id = Column(GUID,
#                       ForeignKey('group.id', onupdate="CASCADE", ondelete="CASCADE"),
#                       primary_key=True)
#     custom_data = Column(String(1024))
#     # A backref is a common shortcut to place a second relationship() onto the destination table
#     # Put group_assoc on user model instance
#     user = relationship(
#         User,
#         backref=backref("group_assoc")
#     )
#     # Put user_assoc on group model instance
#     group = relationship(
#         Group,
#         backref=backref("user_assoc")
#     )


# class Role(Base):
#     __tablename__ = 'role'
#
#     id = Column(GUID, primary_key=True)
#     name = Column(CoerceUTF8(64), unique=True)
#     permissions = Column(Integer)
#     users = relationship(
#         'User',
#         backref='role',
#         lazy='dynamic'
#     )
#
#     def __repr__(self):
#         return '<Role %r>' % self.name