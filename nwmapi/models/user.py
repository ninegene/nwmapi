import logging
from datetime import timedelta
import uuid

import bcrypt
from dateutil.tz import tzutc
from nwmapi.db import GUID, Base, CoerceUTF8, UTCDateTime, ordered_uuid1, utcnow
from sqlalchemy import Column, String, func, ForeignKey, Enum, UnicodeText
from sqlalchemy.orm import relationship, synonym

log = logging.getLogger(__name__)


# http://docs.sqlalchemy.org/en/improve_toc/orm/basic_relationships.html
# http://docs.sqlalchemy.org/en/improve_toc/orm/loading_relationships.html
# http://docs.sqlalchemy.org/en/improve_toc/orm/loading_relationships.html#what-kind-of-loading-to-use
# http://docs.sqlalchemy.org/en/improve_toc/orm/cascades.html#unitofwork-cascades
# http://docs.sqlalchemy.org/en/improve_toc/orm/relationship_api.html#sqlalchemy.orm.relationship
# http://docs.sqlalchemy.org/en/improve_toc/orm/backref.html
# Introduction to SQLAlchemy - Pycon 2013 - https://www.youtube.com/watch?v=woKYyhLCcnU

USER_ROLE_CONSUMER = 'consumer'
USER_ROLE_BUSINESS = 'business'
USER_ROLE_ADMIN = 'admin'

USER_STATUS_ENABLED = 'ENABLED'
USER_STATUS_DISABLED = 'DISABLED'
USER_STATUS_UNVERIFIED = 'UNVERIFIED'

ACTIVATION_AGE = timedelta(days=3)
NON_ACTIVATION_AGE = timedelta(days=30)

SIGNUP_METHOD_INVITE = 'invite'
SIGNUP_METHOD_SIGNUP = 'signup'
SIGNUP_METHOD_TEST = 'test'


# Based on Open-Source 'Bookie' python bookmark app
class User(Base):
    __tablename__ = u'user'

    id = Column(GUID, default=ordered_uuid1, primary_key=True)
    username = Column(CoerceUTF8(255), unique=True)
    email = Column(String(255), unique=True)
    _password = Column('password', CoerceUTF8(255))
    firstname = Column(CoerceUTF8(255))
    middlename = Column(CoerceUTF8(255))
    lastname = Column(CoerceUTF8(255))
    about_me = Column(CoerceUTF8)
    phone = Column(String)
    location = Column(CoerceUTF8(255))
    avatar_hash = Column(String(32))
    role = Column(
        Enum(USER_ROLE_CONSUMER,
             USER_ROLE_BUSINESS,
             USER_ROLE_ADMIN),
        default=USER_ROLE_CONSUMER)
    status = Column(
        Enum(USER_STATUS_ENABLED,
             USER_STATUS_DISABLED,
             USER_STATUS_UNVERIFIED),
        default=USER_STATUS_UNVERIFIED)
    activation = relationship(
        'Activation',
        cascade="all, delete, delete-orphan",
        uselist=False,
        backref='user',
        lazy='joined')
    custom_data = Column(UnicodeText)
    created = Column(UTCDateTime, default=func.now(tz=tzutc()))
    updated = Column(UTCDateTime, server_default=func.now(tz=tzutc()), onupdate=func.current_timestamp())

    # groups = relationship(
    #     Group,
    #     secondary='user_group',
    #     lazy='dynamic',
    # )

    def __init__(self):
        """By default a user starts out deactivated"""
        self.activation = Activation()
        self.status = USER_STATUS_UNVERIFIED

    def _set_password(self, password):
        """Hash password on the fly."""
        # hashed_password = password

        if isinstance(password, unicode):
            pw = password.encode('UTF-8')
        else:
            pw = password

        # Hash a password for the first time, with a randomly-generated salt
        salt = bcrypt.gensalt(10)
        hashed_password = bcrypt.hashpw(pw, salt)

        # Make sure the hased password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode fields
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the password hashed"""
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password))

    @property
    def fullName(self):
        firstName = self.firstname or ''
        middleName = self.middlename or ''
        lastName = self.lastname or ''
        return firstName.strip() + ' ' + middleName.strip() + ' ' + lastName.strip()

    @property
    def active(self):
        return self.status == USER_STATUS_ENABLED

    @active.setter
    def active(self, value):
        if value:
            self.status = USER_STATUS_ENABLED

    @property
    def inactive(self):
        return self.status == USER_STATUS_DISABLED

    @inactive.setter
    def inactive(self, value):
        if value:
            self.status = USER_STATUS_DISABLED

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.

        """
        if self.password:
            salt = self.password[:29]
            return self.password == bcrypt.hashpw(password, salt)
        else:
            return False

    def to_dict(self, excluded=None, included=None):
        excluded = excluded or set()
        excluded = excluded | {'password'}   # always exclude password
        included = included or set()
        result = super(User, self).to_dict(excluded=excluded, included=included)
        if self.status == USER_STATUS_UNVERIFIED:
            result['email_verification_token'] = self.activation.code
        return result

    def from_dict(self, dictionary):
        dictionary = dictionary or {}
        email = dictionary.get('email', None)
        if email:
            dictionary['email'] = email.lower()
        dictionary.setdefault('status', USER_STATUS_DISABLED)
        return super(User, self).from_dict(dictionary)

    @property
    def json(self):
        return super(User, self).to_json()

    def __repr__(self):
        return "<User {} {} {} {}>".format(self.username, self.email, self.role, self.status)


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
    valid_until = Column(UTCDateTime, default=lambda: utcnow() + ACTIVATION_AGE)
    created_by = Column('created_by', CoerceUTF8(255))

    def __init__(self, created_by=SIGNUP_METHOD_SIGNUP):
        """Create a new activation"""
        self.code = uuid.uuid4().hex
        self.created_by = created_by
        self.valid_until = utcnow() + ACTIVATION_AGE

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
