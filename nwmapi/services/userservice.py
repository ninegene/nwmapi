from datetime import datetime
import logging

from nwmapi.common import gen_api_key
from nwmapi.models import session_scope, Session
from nwmapi.models.user import User, NON_ACTIVATION_AGE, Activation, USER_STATUS_NON_ACTIVATED, \
    USER_STATUS_ACTIVE, SIGNUP_METHOD_INVITE

log = logging.getLogger(__name__)


class UserService(object):
    @staticmethod
    def user_count():
        """Number of users in the system."""
        return User.query.count()

    @staticmethod
    def non_activated_account(delete=False):
        """Get a list of  user accounts which are not verified since 30 days of signup"""
        test_date = datetime.utcnow() - NON_ACTIVATION_AGE
        with session_scope() as db:
            query = db.query(Activation.id). \
                filter(Activation.valid_until < test_date). \
                subquery(name="query")
            qry = db.query(User). \
                filter(User.status == USER_STATUS_NON_ACTIVATED). \
                filter(User.last_login.is_(None)). \
                filter(User.id.in_(query))
        # Delete the non activated accounts only if it is asked to.
        if delete:
            # TODO: delete using 'id in subquery'
            for user in qry.all():
                with session_scope as db:
                    db.delete(user)
        # If the non activated accounts are not asked to be deleted,
        # return their details.
        else:
            return qry.all()

    @staticmethod
    def get_user_list(active=None, order=None, limit=None):
        """Get a list of all of the user accounts"""
        session = Session()
        user_query = session.query(User).order_by(User.username)

        if active is not None:
            user_query = user_query.filter(User.status == USER_STATUS_ACTIVE)

        if order:
            user_query = user_query.order_by(getattr(User, order))
        else:
            user_query = user_query.order_by(User.signup)

        if limit:
            user_query = user_query.limit(limit)

        return user_query.all()

    @staticmethod
    def get_user(id=None, username=None, email=None, api_key=None):
        """Get the user instance for this information """
        session = Session()
        user_query = session.query(User)

        if username is not None:
            return user_query.filter(User.username == username).first()

        if id is not None:
            return user_query.filter(User.id == id).first()

        if email is not None:
            return user_query.filter(User.email == email).first()

        if api_key is not None:
            return user_query.filter(User.api_key == api_key).first()

        return None

    @staticmethod
    def acceptable_password(password):
        """Verify that the password is acceptable

        Basically not empty, has more than 3 chars...

        """
        log.debug("PASS")
        log.debug(password)

        if password is not None:
            log.debug(len(password))

        if password is None:
            return False

        if len(password) < 3:
            return False

        return True

    @staticmethod
    def invite(username, email, has_invites, invite_ct):
        """Invite a user"""
        if not has_invites():
            return False
        if not email:
            raise ValueError('You must supply an email address to invite')
        else:
            # get this invite party started, create a new useracct
            new_user = UserService.signup_user(email, username, SIGNUP_METHOD_INVITE)

            # decrement the invite counter
            invite_ct -= 1
            with session_scope as db:
                db.add(new_user)
            return new_user

    @staticmethod
    def signup_user(email, username, signup_method):
        # Get this invite party started, create a new user acct.
        new_user = User()
        new_user.email = email.lower()
        new_user.username = username
        new_user.invited_by = signup_method
        new_user.api_key = gen_api_key()

        # they need to be deactivated
        new_user.reactivate(u'invite')

        with session_scope as db:
            db.add(new_user)
        return new_user

    @staticmethod
    def activation_count():
        """Count how many activations are in the system."""
        return Activation.query.count()

    @staticmethod
    def get_user_by_activation_code(username, code):
        """Get the user for this code"""
        qry = Activation.query. \
            filter(Activation.code == code). \
            filter(User.username == username)

        res = qry.first()

        if res is not None:
            return res.user
        else:
            return None

    @staticmethod
    def activate_user(username, code, new_pass):
        """Given this code get the user with this code make sure they exist"""

        qry = Activation.query. \
            filter(Activation.code == code). \
            filter(User.username == username)

        res = qry.first()

        if UserService.acceptable_password(new_pass) and res is not None:
            user = res.user
            user.status = USER_STATUS_ACTIVE
            user.password = new_pass
            res.activate()

            log.debug(dict(user))

            return True
        else:
            return None
