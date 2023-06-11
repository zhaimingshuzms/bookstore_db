"""Buyer related APIs."""

import time
import uuid
import json
import sqlalchemy
import logging
from be.model import error
from be.model.sql_manager import (
    get_session,
    user_id_exists,
    store_id_exists,
    order_id_exists,
    book_id_exists,
    Book,
    Order,
    OrdertoBooks,
    User,
    UsertoStore
)
from be.model.utils import check_expired, to_dict, serialize_dict
from sqlalchemy import and_,Enum
from sqlalchemy.exc import SQLAlchemyError

class BuyerAPI:
    """Backend APIs related to buyer manipulation."""

    @staticmethod
    def new_order(
        user_id: str,
        store_id: str,
        books: [(str, int)],
    ) -> (int, str, str):
        """Create an order to a store.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        store_id : str
            The store_id of the store.

        books : List[str, int]
            The books to be bought. A list of (book_id: str, count: int).

        Returns
        -------
        (code : int, msg : str, order_id : str)
            The return status. Note that it will return the corresponding order_id.
        """
        order_id = ""
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            total_price = 0
            order_data_books = []
            session = get_session()
            for book_id, count in books:
                cursor = session.query(Book).filter(and_(Book.store_id==store_id,Book.book_id==book_id)).scalar()
                if cursor is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                stock_level = cursor.stock_level
                price = cursor.price

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                cursor = session.query(Book).filter(and_(Book.store_id==store_id,Book.book_id==book_id)).update(
                    {"stock_level": Book.stock_level-count}
                )
                total_price += count * price
                order_data_books.append(
                    {"book_id": book_id, "count": count, "price": price}
                )
            order_id = uid
            now_time = time.time()
            session.add(
                Order(
                    order_id=order_id,
                    buyer=user_id,
                    store_id=store_id,
                    total_price=total_price,
                    state="unpaid",
                    timestamp=now_time,
                )
            )
            session.commit()
            for v in order_data_books:
                session.add(
                    OrdertoBooks(
                        order_id = order_id,
                        book_id = v["book_id"],
                        count = v["count"],
                        price = v["price"]
                    )
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
        return 200, "ok", order_id

    @staticmethod
    def payment(user_id: str, password: str, order_id: str) -> (int, str):
        """The buyer pay for an order.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer account.

        order_id : str
            The order the buyer pay for.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()

            cursor2 = session.query(User).filter(User.id==user_id).scalar()
            if cursor2 is None:
                return error.error_non_exist_user_id(user_id)
            if password != cursor2.password:
                return error.error_authorization_fail()
            
            cursor = session.query(Order).filter(Order.order_id==order_id).scalar()
            
            if cursor is None:
                return error.error_non_exist_order_id(order_id)
            if cursor.state != "unpaid":
                return error.error_order_state(cursor["state"])
            if cursor.buyer != user_id:
                return error.error_authorization_fail()
            # print("timestamp: ",cursor.timestamp)
            if check_expired(cursor.timestamp):
                code, message = BuyerAPI.cancel_order(user_id, password, order_id)
                if code != 200:
                    return code, message
                return error.error_order_state("canceled")

            total_price = cursor.total_price
            
            

            balance = cursor2.balance
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # buyer's balance -= total_price
            session.query(User).filter(User.id==user_id).update(
                {"balance": User.balance-total_price}
            )

            # cursor = get_store_col().find_one({"_id": store})
            # if cursor is None:
            #     return error.error_non_exist_store_id(store)
            # seller = cursor["owner"]
            # # seller's balance += total_price
            # get_user_col().update_one(
            #     {"_id": seller}, {"$inc": {"balance": total_price}}
            # )

            # # delete the order
            # result = get_order_col().delete_one({"_id": order_id})
            # assert result.deleted_count == 1

            # update the order state
            session.query(Order).filter(Order.order_id==order_id).update({"state": "paid"})
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def add_funds(user_id: str, password: str, add_value: int) -> (int, str):
        """Add funds for an account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        add_value : int
            The value of funds to be added.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).scalar()
            if cursor is None:
                return error.error_non_exist_user_id(user_id)

            if cursor.password != password:
                return error.error_authorization_fail()

            # balance += add_value
            session.query(User).filter(User.id==user_id).update(
                {"balance": User.balance+add_value}
            )
            session.commit()
            session.close()
        except sqlalchemy as e:
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def mark_order_received(user_id: str, password: str, order_id: str) -> (int, str):
        """Mark an order as received by user.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        order_id : str
            The order_id of the received order.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).scalar()
            if cursor is None:
                return error.error_non_exist_user_id(user_id)

            if cursor.password != password:
                return error.error_authorization_fail()

            cursor = session.query(Order).filter(Order.order_id==order_id).scalar()
            if cursor is None:
                return error.error_non_exist_order_id(order_id)
            if cursor.state != "delivered":
                return error.error_order_state(cursor.state)

            if cursor.buyer != user_id:
                return error.error_user_id_match(cursor.buyer, user_id)

            store_cursor = session.query(UsertoStore).filter(UsertoStore.store_id==cursor.store_id).scalar()
            if store_cursor is None:
                return error.error_non_exist_store_id(cursor.store_id)
            seller = store_cursor.user_id
            # seller's balance += total_price
            session.query(User).filter(User.id==seller).update(
                {"balance": User.balance+cursor.total_price}
            )
            # update the order state
            session.query(Order).filter(Order.order_id==order_id).update(
                {"state": "finished"}
            )
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def cancel_order(user_id: str, password: str, order_id: str) -> (int, str):
        """The buyer cancels an order.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        order_id : str
            The order_id of the canceled order.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            buyer = session.query(User).filter(User.id==user_id).scalar()
            if buyer is None:
                return error.error_non_exist_user_id(user_id)

            if buyer.password != password:
                return error.error_authorization_fail()

            if not order_id_exists(order_id):
                return error.error_non_exist_order_id(order_id)

            order = session.query(Order).filter(Order.order_id==order_id).scalar()
            if order.state == "canceled" or order.state == "finished":
                return error.error_order_state(order.state)
            cursor = session.query(OrdertoBooks).filter(OrdertoBooks.order_id==order_id).all()
            # for the book stock
            for book in cursor:
                book_cursor = session.query(Book).filter(
                        and_(
                            Book.store_id==order.store_id,
                            Book.book_id==book.book_id
                        )
                )
                # in the list of the order, so it must exist
                assert book_cursor.scalar() is not None
                
                book_cursor.update({"stock_level": Book.stock_level+book.count})
            # for back money
            if order.state == "paid" or order.state == "delivered":
                # buyer's balance -= total_price
                session.query(User).filter(User.id==user_id).update(
                    {"balance": buyer.balance+order.total_price}
                )
            # update the order state
            session.query(Order).filter(Order.order_id==order_id).update(
                {"state": "canceled"}
            )
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def query_all_orders(user_id: str, password: str) -> (int, str, list):
        """A buyer queries all his orders.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        Returns
        -------
        (code : int, msg : str, orders: List[dict])
            The return status and the queried orders.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).scalar()
            if cursor is None:
                return error.error_non_exist_user_id(user_id) + ([],)

            if cursor.password != password:
                return error.error_authorization_fail() + ([],)

            order_cursors = session.query(Order).filter(Order.buyer==user_id).all()
            ret = [to_dict(cursor) for cursor in order_cursors]
            for order in ret:
                book_cursors = session.query(OrdertoBooks).filter(OrdertoBooks.order_id==order["order_id"]).all()
                order["books"]=[to_dict(book) for book in book_cursors]
            session.close()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", ret

    @staticmethod
    def query_one_order(user_id: str, password: str, order_id: str) -> (int, str, dict):
        """A buyer queries one specified order.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        order_id : str
            the order_id of the queried order.

        Returns
        -------
        (code : int, msg : str, order : dict)
            The return status and the queried order.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id==user_id).scalar()
            if cursor is None:
                return error.error_non_exist_user_id(user_id) + ([],)
            if cursor.password != password:
                return error.error_authorization_fail() + ([],)
            order_cursors = session.query(Order).filter(Order.order_id==order_id).scalar()
            if order_cursors is None:
                return error.error_non_exist_order_id(order_id) + ([],)
            ret = to_dict(order_cursors)
            book_cursors = session.query(OrdertoBooks).filter(OrdertoBooks.order_id==ret["order_id"]).all()
            ret["books"]=[to_dict(book) for book in book_cursors]
            session.close()
            session.close()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", ret
