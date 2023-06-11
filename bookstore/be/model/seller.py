"""Seller related APIs."""

import sqlalchemy
import logging
from be.model import error
from be.model.sql_manager import (
    get_session,
    user_id_exists,
    store_id_exists,
    book_id_exists,
    order_id_exists,
    Book,
    UsertoStore,
    Order
)
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from be.model.utils import serialize_dict

class SellerAPI:
    """Backend APIs related to seller manipulation."""

    @staticmethod
    def add_book(
        user_id: str,
        store_id: str,
        book_id: str,
        book_info: dict,
        stock_level: int,
    ) -> (int, str):
        """Add a book to a store.

        Parameters
        ----------
        user_id : str
            The user_id of the seller.

        store_id : str
            The store_id of the store.

        book_id : str
            The book_id of the book.

        book_info : dict
            The book info dict.

        stock_level : int
            The stock_level of the book in this store.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)
            assert book_info.pop("id") == book_id
            book_info = serialize_dict(book_info)
            session = get_session()
            session.add(Book(store_id=store_id,book_id=book_id,stock_level=stock_level,**book_info))
            session.commit()
            session.close()
        except IntegrityError as e:
            session.rollback()
            return error.error_exist_book_id(book_id)
        except SQLAlchemyError as e:
            session.rollback()
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def add_stock_level(
        user_id: str, store_id: str, book_id: str, add_stock_level: int
    ) -> (int, str):
        """Add the stock_level of a book in a store.

        Parameters
        ----------
        user_id : str
            The user_id of the seller.

        store_id : str
            The store_id of the store.

        book_id : str
            The book_id of the book.

        add_stock_level : int
            The stock_level of the book to be added.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)

            session = get_session()
            cursor = session.query(Book).filter(
                and_(Book.store_id==store_id,Book.book_id==book_id)
            )
            if cursor.scalar() is None:
                return error.error_non_exist_book_id(book_id)
            
            cursor.update({"stock_level":Book.stock_level+add_stock_level})
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            session.rollback()
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def create_store(user_id: str, store_id: str) -> (int, str):
        """A user create a store.

        Parameters
        ----------
        user_id : str
            The user_id of the creator.

        store_id : str
            The store_id of the created store.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id)
            
            session = get_session()
            session.add(UsertoStore(user_id=user_id,store_id=store_id))
            session.commit()
            session.close()
        except IntegrityError as e:
            session.rollback()
            return error.error_exist_store_id(store_id)
        except SQLAlchemyError as e:
            session.rollback()
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def mark_order_shipped(store_id: str, order_id: str) -> (int, str):
        """The seller marks an order as shipped.

        Parameters
        ----------
        store_id : str
            The store_id of the order.

        order_id : str
            The shipped order.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)

            session = get_session()
            cursor = session.query(Order).filter(Order.order_id==order_id).scalar()
            if cursor is None:
                return error.error_non_exist_order_id(order_id)
            if cursor.state != "paid":
                return error.error_order_state(cursor.state)

            if cursor.store_id != store_id:
                return error.error_store_id_match(cursor.store_id, store_id)
            # update the order state
            session.query(Order).filter(Order.order_id==order_id).update({"state":"delivered"})
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"
