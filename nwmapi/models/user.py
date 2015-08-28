import logging
import uuid
from datetime import datetime, timedelta

import bcrypt
from nwmapi.common import gen_api_key
from nwmapi.models import GUID, Base, CoerceUTF8, session_scope
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Enum, UnicodeText, Integer
from sqlalchemy.orm import relationship, backref, synonym

log = logging.getLogger(__name__)


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
USER_STATUS_NON_ACTIVATED = 'nonactivated'
USER_STATUS_SUSPENDED = 'suspended'
USER_STATUS_CLOSED = 'closed'

ACTIVATION_AGE = timedelta(days=3)
NON_ACTIVATION_AGE = timedelta(days=30)

SIGNUP_METHOD_INVITE = 'invite'
SIGNUP_METHOD_WEB = 'web'
SIGNUP_METHOD_MOBILE = 'mobile'
SIGNUP_METHOD_TEST = 'test'


# Based on Open-Source 'Bookie' python bookmark app
class User(Base):
    __tablename__ = u'user'

    id = Column(GUID, default=uuid.uuid4, primary_key=True)
    username = Column(CoerceUTF8(255), unique=True)
    _password = Column('password', CoerceUTF8(60))
    email = Column(String(255), unique=True)  # lowercase only?
    fullname = Column(CoerceUTF8(255), nullable=False)
    profile_id = Column(GUID, ForeignKey('profile.id'))
    profile = relationship(
        "Profile",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        backref=backref("user", uselist=False),
        lazy='joined'
    )
    type = Column(Enum(USER_TYPE_CONSUMER,
                       USER_TYPE_BUSINESS,
                       USER_TYPE_ADMIN),
                  name='user_type',
                  default=USER_TYPE_CONSUMER)
    status = Column(Enum(USER_STATUS_ACTIVE,
                         USER_STATUS_NON_ACTIVATED,
                         USER_STATUS_SUSPENDED,
                         USER_STATUS_CLOSED),
                    name='user_status',
                    default=USER_STATUS_NON_ACTIVATED)
    last_login = Column(DateTime, nullable=True)
    signup = Column(DateTime, default=func.now())
    api_key = Column(CoerceUTF8(12))
    invite_ct = Column(Integer, default=0)
    invited_by = Column('invited_by', CoerceUTF8(255))
    activation = relationship(
        'Activation',
        cascade="all, delete, delete-orphan",
        uselist=False,
        backref='user')
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    # groups = relationship(
    #     Group,
    #     secondary='user_group',
    #     lazy='dynamic',
    # )

    def __init__(self):
        """By default a user starts out deactivated"""
        self.activation = Activation(u'signup')
        self.status = USER_STATUS_NON_ACTIVATED

    def _set_password(self, password):
        """Hash password on the fly."""
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        # Hash a password for the first time, with a randomly-generated salt
        salt = bcrypt.gensalt(10)
        hashed_password = bcrypt.hashpw(password_8bit, salt)

        # Make sure the hased password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # fields
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the password hashed"""
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password))

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.

        """
        # the password might be null as in the case of morpace employees
        # logging in via ldap. We check for that here and return them as an
        # incorrect login
        if self.password:
            salt = self.password[:29]
            return self.password == bcrypt.hashpw(password, salt)
        else:
            return False

    def safe_data(self):
        """Return safe data to be sharing around"""
        hide = ['_password', 'password', 'is_admin', 'api_key']
        return dict(
            [(k, v) for k, v in dict(self).iteritems() if k not in hide]
        )

    def deactivate(self):
        """In case we need to disable the login"""
        self.status = USER_STATUS_NON_ACTIVATED

    def reactivate(self, creator):
        """Put the account through the reactivation process

        This can come about via a signup or from forgotten password link

        """
        # if we reactivate then reinit this
        self.activation = Activation(creator)
        self.status = USER_STATUS_NON_ACTIVATED

    def has_invites(self):
        """Does the user have any invitations left"""
        return self.invite_ct > 0

    def __repr__(self):
        return "<User {} {} {} {}>".format(self.username, self.email, self.type, self.status)


class Profile(Base):
    __tablename__ = u'profile'
    id = Column(GUID, primary_key=True)
    about_me = Column(CoerceUTF8)
    phone = Column(String)
    location = Column(CoerceUTF8(255))
    member_since = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now())
    avatar_hash = Column(String(32))
    custom_data = Column(UnicodeText)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    def __repr__(self):
        return "<Profile {}>".format(self.name)


class Activation(Base):
    """Handle activations/password reset items for users

    The id is the user's id. Each user can only have one valid activation in
    process at a time

    The code should be a random hash that is valid only one time
    After that hash is used to access the site it'll be removed

    The created by is a system: new user registration, password reset, forgot
    password, etc.

    """
    __tablename__ = u'activation'

    user_id = Column(GUID, ForeignKey('user.id'), primary_key=True)
    code = Column(CoerceUTF8(60))
    valid_until = Column(DateTime, default=lambda: datetime.utcnow() + ACTIVATION_AGE)
    created_by = Column('created_by', CoerceUTF8(255))

    def __init__(self, created_system):
        """Create a new activation"""
        self.code = Activation._gen_activation_hash()
        self.created_by = created_system
        self.valid_until = datetime.utcnow() + ACTIVATION_AGE

    @staticmethod
    def _gen_activation_hash():
        """Generate a random activation hash for this user account"""
        # for now just cheat and generate an api key, that'll work for now
        return gen_api_key()

    def activate(self):
        """Remove this activation"""
        with session_scope() as db:
            db.delete(self)

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
