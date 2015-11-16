from datetime import datetime
import logging

from nwmapi.db import DBSession, generate_query
from nwmapi.models.user import User, NON_ACTIVATION_AGE, USER_STATUS_DISABLED, \
    USER_STATUS_ENABLED

log = logging.getLogger(__name__)


def get_user_list(filters=None, order_by=None, limit=None, offset=None, start=None, end=None):
    q = generate_query(User,
                       filters=filters,
                       order_by=order_by,
                       limit=limit, offset=offset, start=start, end=end)
    return q.all()


def create_user(dictionary=None):
    user = User()
    user.from_dict(dictionary)
    # created_by = dictionary.get('created_by', CREATED_BY_SIGNUP)
    # if user.status == USER_STATUS_DISABLED:
    #     user.activation = Activation(created_by)

    DBSession.add(user)
    DBSession.commit()
    return user


def get_user(id=None, username=None, email=None):
    q = DBSession.query(User)

    if id is not None:
        return q.filter(User.id == id).first()

    if username is not None:
        return q.filter(User.username == username).first()

    if email is not None:
        return q.filter(User.email == email).first()

    return None


def update_user(dictionary, id=None, username=None, email=None):
    user = get_user(id=id, username=username, email=email)
    if not user:
        return None

    user.from_dict(dictionary)
    DBSession.merge(user)
    DBSession.commit()
    return user


def delete_user(id=None, username=None, email=None):
    user = get_user(id=id, username=username, email=email)
    if not user:
        return None

    DBSession.delete(user)
    DBSession.commit()
    return user


def activate(activation):
    """Remove this activation"""
    DBSession.delete(activation)


def activation_count(self):
    """Count how many activations are in the system."""
    return DBSession.query(Activation).count()


def get_user_by_activation_code(username, code):
    """Get the user for this code"""
    activation = DBSession.query(Activation) \
        .filter(Activation.code == code) \
        .filter(User.username == username) \
        .first()

    if activation is not None:
        return activation.user
    else:
        return None


def activate_user(username, code, new_pass):
    """Given this code get the user with this code make sure they exist"""
    activation = DBSession.query(Activation) \
        .filter(Activation.code == code) \
        .filter(User.username == username) \
        .first()

    if acceptable_password(new_pass) and activation is not None:
        user = activation.user
        user.status = USER_STATUS_ENABLED
        user.password = new_pass
        activation.activate()
        return user
    else:
        return None


def acceptable_password(password):
    """Verify that the password is acceptable
    """
    if password is not None:
        log.debug(len(password))

    if password is None:
        return False

    if len(password) < 8:
        return False

    return True


def non_activated_account(delete=False):
    """Get a list of  user accounts which are not verified since 30 days of signup"""
    test_date = datetime.utcnow() - NON_ACTIVATION_AGE

    subquery = DBSession.query(Activation.id). \
        filter(Activation.valid_until < test_date). \
        subquery(name="query")

    user_query = DBSession.query(User). \
        filter(User.status == USER_STATUS_DISABLED). \
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
