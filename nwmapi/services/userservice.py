from datetime import datetime
import logging

from nwmapi.models.user import User, NON_ACTIVATION_AGE, Activation, USER_STATUS_INACTIVE, \
    USER_STATUS_ACTIVE, SIGNUP_METHOD_INVITE, SIGNUP_METHOD_SIGNUP

log = logging.getLogger(__name__)


class UserService(object):

    def __init__(self, db):
        self.db = db
        
    def get_user_list(self, status=None, role=None, order=None, limit=None):
        """Get a list of all of the user accounts"""
        q = self.db.query(User).order_by(User.username)

        if status is not None:
            q = q.filter(User.status == status)

        if role is not None:
            q = q.filter(User.role == role)

        if order:
            q = q.order_by(getattr(User, order))
        else:
            q = q.order_by(User.created)

        if limit:
            q = q.limit(limit)

        return q.all()

    def get_user(self, id=None, username=None, email=None):
        """Get the user instance for this information """
        q = self.db.query(User)

        if username is not None:
            return q.filter(User.username == username).first()

        if id is not None:
            return q.filter(User.id == id).first()

        if email is not None:
            return q.filter(User.email == email).first()

        return None

    def signup_user(self, email, username, signup_method=SIGNUP_METHOD_SIGNUP):
        # Get this invite party started, create a new user acct.
        new_user = User()
        new_user.email = email.lower()
        new_user.username = username
        new_user.reactivate(signup_method)

        self.db.add(new_user)
        return new_user

    def activate(self, activation):
        """Remove this activation"""
        self.db.delete(activation)

    def activation_count(self):
        """Count how many activations are in the system."""
        return self.db.query(Activation).count()

    def get_user_by_activation_code(self, username, code):
        """Get the user for this code"""
        activation = self.db.query(Activation)\
            .filter(Activation.code == code)\
            .filter(User.username == username)\
            .first()

        if activation is not None:
            return activation.user
        else:
            return None

    def activate_user(self, username, code, new_pass):
        """Given this code get the user with this code make sure they exist"""
        activation = self.db.query(Activation) \
            .filter(Activation.code == code) \
            .filter(User.username == username) \
            .first()

        if self.acceptable_password(new_pass) and activation is not None:
            user = activation.user
            user.status = USER_STATUS_ACTIVE
            user.password = new_pass
            activation.activate()

            log.debug(dict(user))

            return True
        else:
            return None

    def acceptable_password(self, password):
        """Verify that the password is acceptable
        """
        if password is not None:
            log.debug(len(password))

        if password is None:
            return False

        if len(password) < 8:
            return False

        return True

    def non_activated_account(self, delete=False):
        """Get a list of  user accounts which are not verified since 30 days of signup"""
        test_date = datetime.utcnow() - NON_ACTIVATION_AGE

        subquery = self.db.query(Activation.id). \
            filter(Activation.valid_until < test_date). \
            subquery(name="query")

        user_query = self.db.query(User). \
            filter(User.status == USER_STATUS_INACTIVE). \
            filter(User.last_login.is_(None)). \
            filter(User.id.in_(subquery))

        # Delete the non activated accounts only if it is asked to.
        if delete:
            for user in user_query.all():
                self.db.delete(user)
        # If the non activated accounts are not asked to be deleted,
        # return their details.
        else:
            return user_query.all()

    def user_count(self):
        """Number of users in the system."""
        return self.db.query(User).count()

