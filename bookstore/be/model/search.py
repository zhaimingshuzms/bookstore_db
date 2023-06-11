"""Search related APIs."""

import sqlalchemy
import logging
from be.model import error
from be.model.sql_manager import (
    get_session,
    user_id_exists,
    store_id_exists,
    book_id_exists,
    order_id_exists,
    Book
)
from be.model.error import error_invalid_query_book_behaviour
from sqlalchemy.exc import SQLAlchemyError
from be.model.utils import to_dict

class SearchAPI:
    @staticmethod
    def query_book(**kwargs) -> (int, str, list):
        """
        Query books

        Parameters
        ----------
        kwargs : dict
            The restriction of this query.

            The keys of this dict can be:
                book_id
                store_id
                title
                author
                publisher
                original_title
                translator
                pub_year
                pages
                price
                currency_unit
                binding
                isbn
                author_intro
                book_intro
                content
                title_keyword
        Do not use id!!!
        
        Returns
        -------
        (code : int, msg : str, books: list)
            The return status and the queried books.
        """
        try:
            session = get_session()
            cursor = session.query(Book)
            if "_id" in kwargs:
                return error_invalid_query_book_behaviour() + ([],)
            if "title_keyword" in kwargs:
                if "title" in kwargs:
                    return error_invalid_query_book_behaviour() + ([],)

                kwd = kwargs["title_keyword"]
                del kwargs["title_keyword"]
                # kwargs["$text"] = {"$search": kwd}
                cursor = cursor.filter(Book.title.like(f'%{kwd}%'))
            cursor = cursor.filter_by(**kwargs).all()
            session.close()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), None
        except BaseException as e:
            return 530, "{}".format(str(e)), None
        ret = [to_dict(v) for v in cursor]
        return 200, "ok", ret
