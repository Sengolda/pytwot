"""
The MIT License (MIT)

Copyright (c) 2021-present UnrealFar & TheGenocides
Copyright (c) 2023-present Sengolda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from .errors import NoPageAvailable

if TYPE_CHECKING:
    from .http import HTTPClient
    from .type import Payload


class Pagination:
    """Represents the base class of all pagination objects.


    .. versionadded:: 1.5.0
    """

    __slots__ = (
        "__original_payload",
        "_payload",
        "_meta",
        "_next_token",
        "_previous_token",
        "_count",
        "_paginate_over",
        "_current_page_number",
        "_params",
        "item_type",
        "endpoint_request",
        "http_client",
        "pages_cache",
    )

    def __init__(
        self,
        data: Payload,
        *,
        item_type: Any,
        endpoint_request: str,
        http_client: HTTPClient,
        **kwargs: Any,
    ) -> None:
        self.__original_payload = data
        self._payload = self.__original_payload.get("data")
        self._meta = self.__original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0
        self._paginate_over = 0
        self._current_page_number = 1
        self._params = kwargs.get("params", None)
        self.item_type = item_type
        self.endpoint_request = endpoint_request
        self.http_client = http_client
        self.pages_cache = {1: {obj.id: obj for obj in self.content}}

    @property
    def original_payload(self) -> Payload:
        return self.__original_payload

    @original_payload.setter
    def original_payload(self, other: dict) -> Payload:
        self.__original_payload = other
        return self.original_payload

    @property
    def payload(self) -> dict:
        return self._payload

    @payload.setter
    def payload(self, other: dict) -> dict:
        self._payload = other
        return self._payload

    @property
    def content(self) -> list:
        """:class:`list`: Returns a list of objects from the current page's content.

        .. versionadded:: 1.5.0
        """
        return [self.item_type(data, http_client=self.http_client) for data in self.payload]

    @property
    def paginate_over(self) -> int:
        """:class:`int`: Returns how many times you change page over the pagination.

        .. versionadded:: 1.5.0
        """
        return self._paginate_over

    @property
    def current_page_number(self) -> int:
        """:class:`int`: Returns the current page number.

        .. versionadded:: 1.5.0
        """
        return self._current_page_number

    @property
    def pages(self) -> List[Tuple[int, list]]:
        """List[Tuple[:class:`int`, :class:`list`]]: Returns the zipped pages with the page number and content from a cache. If you never been into the page you want, it might not be returns in this property. example to use:

        .. code-block:: py

            for page_number, page_content in pagination.pages:
                ... #do something


        .. versionadded:: 1.5.0
        """
        fulldata = []
        for page_number in self.pages_cache.keys():
            fulldata.append(list(self.pages_cache.get(page_number).values()))
        return zip(range(1, len(self.pages_cache) + 1), fulldata)

    def get_page_content(self, page_number: int) -> Optional[list]:
        """Gets the page `content` from the pagination pages cache. If you never been into the page you want, it might not be returns.

        .. note::
            Note that, if the page_number is 0 it automatically would returns None. Specify number 1 or above.

        Returns
        ---------
        Optional[:class:`list`]
            This method returns a list of objects.


        .. versionadded:: 1.5.0
        """
        content = self.pages_cache.get(page_number)
        if not content:
            return None
        return list(content.values())

    def next_page(self) -> None:
        raise NotImplementedError

    def previous_page(self) -> None:
        raise NotImplementedError


class UserPagination(Pagination):
    """Represents a pagination that handles users object. This inherits :class:`Pagination`. These following methods return this object:

    * :meth:`User.fetch_following`
    * :meth:`User.fetch_followers`
    * :meth:`User.fetch_muters`
    * :meth:`User.fetch_blockers`
    * :meth:`Tweet.fetch_likers`
    * :meth:`Tweet.fetch_retweeters`
    * :meth:`List.fetch_members`


    .. versionadded:: 1.5.0
    """

    def __init__(self, data, **kwargs) -> None:
        from .user import User  # Avoid circular import error.

        super().__init__(data, item_type=User, **kwargs)

    def next_page(self) -> None:
        """Change `content` property to the next page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._next_token:
            raise NoPageAvailable()
        self._params["pagination_token"] = self._next_token

        res = self.http_client.request(
            "GET",
            "2",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number += 1
        self.original_payload = res
        self.payload = self.original_payload.get("data")
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {user.id: user for user in self.content}

    def previous_page(self) -> None:
        """Change `content` property to the previous page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._previous_token:
            raise NoPageAvailable()
        self._params["pagination_token"] = self._previous_token

        res = self.http_client.request(
            "GET",
            "2",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number -= 1
        self.original_payload = res
        self.payload = self.original_payload.get("data")
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {user.id: user for user in self.content}


class TweetPagination(Pagination):
    """Represents a pagination that handles tweets object. This inherits :class:`Pagination`. These following methods return this object:

    * meth:`User.fetch_timelines`
    * meth:`User.fetch_liked_tweets`
    * meth:`List.fetch_tweets`


    .. versionadded:: 1.5.0
    """

    def __init__(self, data, **kwargs) -> None:
        from .tweet import Tweet  # Avoid circular import error.

        super().__init__(data, item_type=Tweet, **kwargs)

    @property
    def content(self) -> list:
        """:class:`list`: Returns a list of objects from the current page's content.

        .. versionadded:: 1.5.0
        """

        return [
            self.item_type(data, http_client=self.http_client)
            for data in self.http_client.payload_parser.insert_pagination_object_author(self.original_payload)
        ]

    def next_page(self) -> None:
        """Change `content` property to the next page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._next_token:
            raise NoPageAvailable()
        self._params["pagination_token"] = self._next_token

        res = self.http_client.request(
            "GET",
            "2",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number += 1
        self.original_payload = res
        self.payload = self.content
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {tweet.id: tweet for tweet in self.content}

    def previous_page(self) -> None:
        """Change `content` property to the previous page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._previous_token:
            raise NoPageAvailable()
        self._params["pagination_token"] = self._previous_token

        res = self.http_client.request(
            "GET",
            "2",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number -= 1
        self.original_payload = res
        self.payload = self.content
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {tweet.id: tweet for tweet in self.content}


class ListPagination(Pagination):
    """Represents a pagination that handles list objects. This inherits :class:`Pagination`. These following methods return this object:

    * :meth:`User.fetch_lists`
    * :meth:`User.fetch_list_memberships`


    .. versionadded:: 1.5.0
    """

    def __init__(self, data, **kwargs) -> None:
        from .list import List as TwitterList  # Avoid circular import error

        super().__init__(data, item_type=TwitterList, **kwargs)

    @property
    def content(self) -> list:
        """:class:`list`: Returns a list of objects from the current page's content.

        .. versionadded:: 1.5.0
        """

        return [
            self.item_type(data, http_client=self.http_client)
            for data in self.http_client.payload_parser.insert_pagination_object_author(self.original_payload)
        ]

    def next_page(self) -> None:
        """Change `content` property to the next page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._next_token:
            raise NoPageAvailable()
        self._params["pagination_token"] = self._next_token

        res = self.http_client.request(
            "GET",
            "2",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number += 1
        self.original_payload = res
        self.payload = self.content
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {
                _TwitterList.id: _TwitterList for _TwitterList in self.content
            }

    def previous_page(self) -> None:
        """Change `content` property to the previous page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._previous_token:
            raise NoPageAvailable()
        self._params["pagination_token"] = self._previous_token

        res = self.http_client.request(
            "GET",
            "2",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number -= 1
        self.original_payload = res
        self.payload = self.content
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {
                _TwitterList.id: _TwitterList for _TwitterList in self.content
            }


class MessagePagination(Pagination):
    """ "Represents a pagination for message objects.
    These methods returns this pagination object:

    * :meth:`Client.fetch_message_history`


    .. versionadded:: 1.5.0
    """

    def __init__(self, data, **kwargs) -> None:
        from .message import DirectMessage  # Avoid circular import error.

        data = kwargs.get("http_client").payload_parser.parse_message_to_pagination_data(data)
        super().__init__(data, item_type=DirectMessage, **kwargs)

    def next_page(self) -> None:
        """Change `content` property to the next page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._next_token:
            raise NoPageAvailable()
        self._params["cursor"] = self._next_token

        res = self.http_client.request(
            "GET",
            "1.1",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number += 1
        self.original_payload = self.http_client.payload_parser.parse_message_to_pagination_data(res)
        self.payload = self.content
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {message.id: message for message in self.content}

    def previous_page(self) -> None:
        """Change `content` property to the previous page's contents..

        Raises
        --------
        :class:`NoPageAvailable`
            Raises when you reached the end of the pagination.


        .. versionadded:: 1.5.0
        """
        if not self._previous_token:
            raise NoPageAvailable()
        self._params["cursor"] = self._previous_token

        res = self.http_client.request(
            "GET",
            "1.1",
            self.endpoint_request,
            auth=True,
            params=self._params,
        )
        if not res:
            raise NoPageAvailable()

        previous_content = self.content
        self._current_page_number -= 1
        self.original_payload = self.http_client.payload_parser.parse_message_to_pagination_data(res)
        self.payload = self.content
        self._meta = self.original_payload.get("meta")
        self._next_token = self._meta.get("next_token")
        self._previous_token = self._meta.get("previous_token")
        self._count = 0

        if not previous_content[0] == self.content[0]:
            self.pages_cache[len(self.pages_cache) + 1] = {message.id: message for message in self.content}
