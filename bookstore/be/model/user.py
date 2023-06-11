"""User (Auth) related APIs."""

import jwt
import time
import logging
import sqlalchemy
from be.model import sql_manager
from be.model import error
from .sql_manager import get_session, User
from sqlalchemy.exc import IntegrityError,SQLAlchemyError

def jwt_encode(user_id: str, terminal: str) -> str:
    """Tool function to encode a json to JWT.
    Encode a json string like:
    {
        "user_id": [user name],
        "terminal": [terminal code],
        "timestamp": [ts]} to a JWT
    }

    Parameters
    ----------
    user_id : str
        The "user_id" data in the user document.

    terminal : str
        The "terminal" data in the user document.

    Returns
    -------
    The encoded string.
    """
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


def jwt_decode(encoded_token: str, user_id: str) -> str:
    """Tool function to decode a JWT to a json string like:
    {
        "user_id": [user name],
        "terminal": [terminal code],
        "timestamp": [ts]} to a JWT
    }

    Parameters
    ----------
    encoded_token : str
        Token used in the jwt.

    user_id : str
        The "user_id" data in the user document.

    Returns
    -------
    The decoded string.
    """
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class UserAPI:
    """Backend APIs related to user manipulation."""

    token_lifetime: int = 3600  # 3600 second

    @staticmethod
    def __check_token(user_id, db_token, token) -> bool:
        """Check whether the token is matched in the database.

        Parameters
        ----------
        user_id : str
            The "user_id" data in the user document.

        db_token : str
            The token from the database.

        token : str
            The token waiting to be valided.

        Returns
        -------
        ret : bool
            Whether the token is valid.
        """
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if UserAPI.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    @staticmethod
    def register(user_id: str, password: str) -> (int, str):
        """User register.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        # print("register",user_id,password)
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            user = User(id=user_id,password=password,balance=0,token=token,terminal=terminal)
            session = get_session()
            # print(session.query(User).filter(User.id==user.id).scalar())
            session.add(user)
            session.commit()
            # print("commited")
            session.close()
        except IntegrityError as e:
            session.rollback()
            return error.error_exist_user_id(user_id)
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def check_token(user_id: str, token: str) -> (int, str):
        """Check token (public API).

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        token : str
            The token to be checked.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).first()
            if cursor is None:
                return error.error_authorization_fail()
            db_token = cursor.token
            session.close()
            if not UserAPI.__check_token(user_id, db_token, token):
                return error.error_authorization_fail()
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def check_password(user_id: str, password: str) -> (int, str):
        """Check password for an account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password to be checked.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).first()
            if cursor is None:
                return error.error_authorization_fail()
            if password != cursor.password:
                return error.error_authorization_fail()
            session.close()
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def login(user_id: str, password: str, terminal: str) -> (int, str, str):
        """Account login.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        terminal : str
            Terminal code of the account.

        Returns
        -------
        (code : int, msg : str, token : str)
            The return status. Note that it will return the token.
        """
        token = ""
        try:
            code, message = UserAPI.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).all()
            for user in cursor:
                user.token = token
                user.terminal = terminal
            session.commit()
            session.close()
            
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", token

    @staticmethod
    def logout(user_id: str, token: str) -> (int, str):
        """Account logout.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        token : str
            Token generated by last login.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            code, message = UserAPI.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            session = get_session()
            session.query(User).filter(User.id==user_id).update(
                {"token": dummy_token, "terminal": terminal}
            )
            session.commit()
            session.close()
            
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok"
    
    @staticmethod
    def unregister(user_id: str, password: str) -> (int, str):
        """Unregister the account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            code, message = UserAPI.check_password(user_id, password)
            if code != 200:
                return code, message

            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).all()
            if len(cursor) != 1:
                return error.error_authorization_fail()
            session.delete(cursor[0])
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def change_password(
        user_id: str, old_password: str, new_password: str
    ) -> (int, str):
        """Change password for an account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        old_password : str
            Old password of the account.

        new_password : str
            New password of the account.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            code, message = UserAPI.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).update({
                "token":token,
                "password":new_password,
                "terminal":terminal}
            )
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok"
