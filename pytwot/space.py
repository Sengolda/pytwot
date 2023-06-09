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

import datetime
from typing import Any, Dict, List, Optional, Union

from .constants import MEDIA_FIELD, PLACE_FIELD, POLL_FIELD, TWEET_EXPANSION, TWEET_FIELD, USER_FIELD
from .dataclass import Topic
from .enums import SpaceState
from .objects import Comparable
from .tweet import Tweet
from .user import User
from .utils import time_parse_todt

__all__ = ("Space",)


class Space(Comparable):
    """Represents a twitter space.

    .. versionadded:: 1.3.5
    """

    __slots__ = ("__original_payload", "_payload", "http_client", "_include")

    def __init__(self, data: Dict[str, Any], http_client: object):
        self.__original_payload = data
        self._includes = self.__original_payload.get("includes")
        self._payload = self.__original_payload.get("data") or self.__original_payload
        self.http_client = http_client
        super().__init__(self.id)

    def __repr__(self) -> str:
        return "Space(name={0.title} id={0.id} state={0.state})".format(self)

    @property
    def title(self) -> str:
        """:class:`str`: The space's title.

        .. versionadded:: 1.3.5
        """
        return self._payload.get("title")

    @property
    def id(self) -> str:
        """:class:`str`: The space's unique id.

        .. versionadded:: 1.3.5
        """
        return self._payload.get("id")

    @property
    def raw_state(self) -> str:
        """:class:`str`: The raw space's state in  a string.

        .. versionadded:: 1.3.5
        """
        return self._payload.get("state")

    @property
    def state(self) -> SpaceState:
        """:class:`SpaceState`: The type of the space's state.

        .. versionadded:: 1.3.5
        """
        return SpaceState(self.raw_state)

    @property
    def lang(self) -> str:
        """:class:`str`: The space's language.

        .. versionadded:: 1.3.5
        """
        return self._payload.get("lang")

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object with the space's created datetime.

        .. versionadded:: 1.3.5
        """
        return time_parse_todt(self._payload.get("created_at"))

    @property
    def started_at(self) -> Optional[datetime.datetime]:
        """Optional[:class:`datetime.datetime`]: Returns a datetime.datetime object with the space's started time. Only available if the space has started.

        .. versionadded:: 1.3.5
        """
        return time_parse_todt(self._payload.get("started_at")) if self._payload.get("started_at") else None

    @property
    def updated_at(self) -> Optional[datetime.datetime]:
        """Optional[:class:`datetime.datetime`]: Returns a datetime.datetime object with the space's last update to any of this Space's metadata, such as the title or scheduled time. Only available if the space has started.

        .. versionadded:: 1.3.5
        """
        return time_parse_todt(self._payload.get("updated_at"))

    @property
    def ticketed(self) -> bool:
        """Returns a bool indicate if the space is ticketed.

        Returns
        ---------
        :class:`bool`
            This method returns a :class:`bool` object.


        .. versionadded:: 1.5.0
        """
        return self._payload.get("is_ticketed")

    @property
    def topics(self) -> Optional[List[Topic]]:
        """Optional[List[:class:`Topic`]]: Returns a list of the space's topics, returns None if the space has no topic

        .. versionadded:: 1.5.0
        """
        if self._includes.get("topics"):
            return [Topic(**data) for data in self._includes["topics"]]
        return None

    @property
    def participant_count(self) -> int:
        """:class:`int`: Returns the current number of users in the Space, including Hosts and Speakers.

        .. versionadded:: 1.5.0
        """
        return int(self._payload.get("participant_count"))

    @property
    def subscriber_count(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns the number of people who set a remainder to this Space. This requires you to authenticate the request using the Access Token of the creator of the requested Space aka using OAuth 2.0 Authorization Code with PKCE.

        .. versionadded:: 1.5.0
        """
        if self._payload.get("subscriber_count"):
            return int(self._payload["subscriber_count"])
        return None

    def fetch_creator(self) -> User:
        """Fetches the creator's using the id.

        Returns
        ---------
        :class:`User`
            This method returns a :class:`User` object.


        .. versionadded:: 1.3.5

        .. versionchanged:: 1.5.0
            Made as a function that returns :class:`User`.
        """
        id = int(self._payload.get("creator_id"))
        return self.http_client.fetch_user(id)

    def fetch_invited_users(self) -> Optional[List[User]]:
        """Fetches the invited users. Usually, users in this list are invited to speak via the Invite user option and have a Speaker role when the Space starts. Returns None if there isn't invited users.

        Returns
        ---------
        Optional[List[:class:`User`]]
            This method returns a list of users or an empty list if not found.


        .. versionadded:: 1.3.5

        .. versionchanged:: 1.5.0
            Made as a function that returns a list of :class:`User`.
        """
        if self._payload.get("invited_users"):
            ids = [int(id) for id in self._payload["invited_users"]]
            return self.http_client.fetch_users(ids)
        return None

    def fetch_hosts(self) -> Optional[List[User]]:
        """Fetches the space's hosts.

        Returns
        ---------
        Optional[List[:class:`User`]]
            Returns a list of :class:`User`.


        .. versionadded:: 1.3.5

        .. versionchanged:: 1.5.0
            Made as a function that returns a list of :class:`User`.
        """
        if self._payload.get("host_ids"):
            ids = [int(id) for id in self._payload["host_ids"]]
            return self.http_client.fetch_users(ids)
        return None

    def fetch_tweets(self) -> Optional[List[Tweet]]:
        """Fetches users who purchased a ticket to the space. This requires you to authenticate the request using the Access Token of the creator of the requested Space aka using OAuth 2.0 Authorization Code with PKCE.

        Returns
        ---------
        Optional[List[:class:`Tweet`]]
            This method returns a list of :class:`Tweet` objects or an empty list.


        .. versionadded:: 1.5.0
        """
        res = self.http_client.request(
            "GET",
            "2",
            f"/spaces/{self.id}/tweets",
            params={
                "expansions": TWEET_EXPANSION,
                "tweet.fields": TWEET_FIELD,
                "user.fields": USER_FIELD,
                "media.fields": MEDIA_FIELD,
                "place.fields": PLACE_FIELD,
                "poll.fields": POLL_FIELD,
            },
        )

        if not res or not res.get("data"):
            return []

        return [Tweet(data, http_client=self.http_client) for data in res["data"]]

    def fetch_buyers(self) -> Union[List[User], list]:
        """Fetches users who purchased a ticket to the space. This requires you to authenticate the request using the Access Token of the creator of the requested Space aka using OAuth 2.0 Authorization Code with PKCE.

        Returns
        ---------
        Union[List[:class:`User`], list]
            This method returns a list of users.


        .. versionadded:: 1.5.0
        """
        res = self.http_client.request(
            "GET",
            "2",
            f"/spaces/{self.id}/buyers",
            params={
                "expansions": TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "media.fields": MEDIA_FIELD,
                "place.fields": PLACE_FIELD,
                "poll.fields": POLL_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )
        if not res:
            return []
        return [User(data, http_client=self.http_client) for data in res["data"]]

    def is_ticketed(self) -> bool:
        """An alias to :meth:`Space.ticketed`.

        Returns
        ---------
        :class:`bool`
            This method returns a :class:`bool` object.


        .. versionadded:: 1.3.5

        .. versionchanged:: 1.5.0
            Made as an alias to :meth:`Space.ticketed`.
        """
        return self.ticketed
