from datetime import datetime
import logging

from nwmapi.db import DBSession, generate_query
from nwmapi.models.user import User, NON_ACTIVATION_AGE, Activation, USER_STATUS_INACTIVE, \
    USER_STATUS_ACTIVE, SIGNUP_METHOD_SIGNUP

log = logging.getLogger(__name__)


class UserService(object):
    def get_user_list(self, where=None, order_by=None, limit=None, offset=None, start=None, end=None):
        q = DBSession.query(User)
        q = generate_query(q, User,
                           where=where,
                           order_by=order_by,
                           limit=limit, offset=offset, start=start, end=end)
        return q.all()

    def create_user(self, dictionary=None):
        user = User()
        user.from_dict(dictionary)
        signup_method = dictionary.get('signup_method', SIGNUP_METHOD_SIGNUP)
        if user.status == USER_STATUS_INACTIVE:
            user.activation = Activation(signup_method)

        DBSession.add(user)
        DBSession.commit()
        return user

    def get_user(self, id=None, username=None, email=None):
        q = DBSession.query(User)

        if id is not None:
            return q.filter(User.id == id).first()

        if username is not None:
            return q.filter(User.username == username).first()

        if email is not None:
            return q.filter(User.email == email).first()

        return None

    def update_user(self, dictionary, id=None, username=None, email=None):
        user = self.get_user(id=id, username=username, email=email)
        user.from_dict(dictionary)
        DBSession.merge(user)
        DBSession.commit()
        return user

    def delete_user(self, id=None, username=None, email=None):
        user = None
        q = DBSession.query(User)

        if id is not None:
            user = q.filter(User.id == id).one()

        if username is not None:
            user = q.filter(User.username == username).one()

        if email is not None:
            user = q.filter(User.email == email).one()

        if not user:
            return None

        DBSession.delete(user)
        DBSession.commit()
        return user

    def activate(self, activation):
        """Remove this activation"""
        DBSession.delete(activation)

    def activation_count(self):
        """Count how many activations are in the system."""
        return DBSession.query(Activation).count()

    def get_user_by_activation_code(self, username, code):
        """Get the user for this code"""
        activation = DBSession.query(Activation) \
            .filter(Activation.code == code) \
            .filter(User.username == username) \
            .first()

        if activation is not None:
            return activation.user
        else:
            return None

    def activate_user(self, username, code, new_pass):
        """Given this code get the user with this code make sure they exist"""
        activation = DBSession.query(Activation) \
            .filter(Activation.code == code) \
            .filter(User.username == username) \
            .first()

        if self.acceptable_password(new_pass) and activation is not None:
            user = activation.user
            user.status = USER_STATUS_ACTIVE
            user.password = new_pass
            activation.activate()
            return user
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

        subquery = DBSession.query(Activation.id). \
            filter(Activation.valid_until < test_date). \
            subquery(name="query")

        user_query = DBSession.query(User). \
            filter(User.status == USER_STATUS_INACTIVE). \
            filter(User.id.in_(subquery))

        # Delete the non activated accounts only if it is asked to.
        if delete:
            for user in user_query.all():
                DBSession.delete(user)
        # If the non activated accounts are not asked to be deleted,
        # return their details.
        else:
            return user_query.all()

    def user_count(self):
        """Number of users in the system."""
        return DBSession.query(User).count()
