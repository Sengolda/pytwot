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
from typing import Optional, Union

from .enums import ActionEventType, UserActionEventType
from .tweet import Tweet
from .type import Payload
from .user import User
from .utils import time_parse_todt

# Events type


class Event:
    """The base class of all event, this provides a type property that the event belongs to.

    .. versionadded:: 1.5.0
    """

    __slots__ = ("_payload", "_type")

    def __init__(self, data: Payload):
        self._type = list(data.keys())[1]
        self._payload = data.get(self._type)[0]

    @property
    def type(self) -> Union[UserActionEventType, ActionEventType]:
        """Union[:class:`UserActionEventType`, :class:`ActionEventType`]: Returns the event's action type.

        .. versionadded:: 1.5.0
        """
        try:
            return ActionEventType(self._type)
        except ValueError:
            return UserActionEventType(self._type)

    @property
    def payload(self) -> Payload:
        """Returns the event payload.

        .. versionadded:: 1.5.0
        """
        return self._payload


class UserActionEvent(Event):
    """Represents a user action event, this could be but not limited to: follow or unfollow. This is also a parent class to all UserAction events, this class inherits :class:`Event`.

    .. versionadded:: 1.5.0
    """

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object with the action's created timestamp.

        .. versionadded:: 1.5.0
        """
        return datetime.datetime.fromtimestamp(int(self.payload.get("created_timestamp")) / 1000)

    @property
    def target(self) -> User:
        """:class:`User`: Returns the user that was targeted by the source.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("target")

    @property
    def source(self) -> User:
        """:class:`User`: Returns a user object that trigger this event.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("source")

    @property
    def author(self):
        """:class:`User`: An alias to source.

        .. versionadded:: 1.5.0
        """
        return self.source


class DirectMessageEvent(Event):
    def __init__(self, data: Payload, *, http_client: object):
        super().__init__(data)
        self.http_client = http_client

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object with the action's created timestamp.

        .. versionadded:: 1.5.0
        """
        return datetime.datetime.fromtimestamp(int(self.payload.get("created_at") / 1000))

    @property
    def recipient(self) -> User:
        """:class:`User`: Returns the user that :meth:`DirectMessageEvent.sender` interacted.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("target", {}).get("recipient")

    @property
    def sender(self) -> User:
        """:class:`User`: Returns the user that trigger the event.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("target", {}).get("sender", None)


# Events


class DirectMessageTypingEvent(DirectMessageEvent):
    """Represents a typing event object for `on_typing` event, this inherits :class:`DirectMessageEvent`. This object contains the event information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    @property
    def typer(self) -> User:
        """:class:`User`: An alias to :meth:`DirectMessageEvent.sender`.

        .. versionadded:: 1.5.0
        """
        return self.sender


class DirectMessageReadEvent(DirectMessageEvent):
    """Represents a direct message read event object for `on_direct_message_read` event, this inherits :class:`DirectMessageEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    @property
    def reader(self) -> Optional[User]:
        """:class:`User`: An alias to :meth:`DirectMessageEvent.sender`.

        .. versionadded:: 1.5.0
        """
        return self.sender

    @property
    def last_read_message(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns the last message that got read, returns the event id if none found.

        .. versionadded:: 1.5.0
        """
        event_id = self.payload.get("last_read_event_id")
        message = self.http_client.message_cache.get(int(event_id))
        if not message:
            return event_id
        return message


class TweetFavoriteActionEvent(Event):
    """Represents a tweet favorite event object for `on_tweet_favorite` event, this inherits :class:`Event`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    @property
    def id(self) -> str:
        """:class:`str`: Returns the action's unique ID.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("id")

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object with the action's created timestamp.

        .. versionadded:: 1.5.0
        """
        return datetime.datetime.fromtimestamp(int(self.payload.get("timestamp_ms")) / 1000)

    @property
    def favorited_tweet(self) -> Tweet:
        """:class:`Tweet`: Returns the favorited tweet.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("tweet")

    @property
    def liker(self) -> User:
        """:class:`User`: Returns the user who favorited the tweet.

        .. versionadded:: 1.5.0
        """
        return self.payload.get("liker")


class UserRevokeEvent(Event):
    """Represents a revoke access event by the subcription user, this inherits :class:`Event`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    def __init__(self, data: Payload):
        super().__init__(data.get("revoke"))

    @property
    def revoked_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object with the action's created timestamp.

        .. versionadded:: 1.5.0
        """
        return time_parse_todt(self.payload.get("date_time"))

    @property
    def app_id(self) -> int:
        """:class:`int`: Returns an application id who the user revoked from.

        .. versionadded:: 1.5.0
        """
        return int(self.payload.get("target").get("app_id"))

    @property
    def user_id(self) -> int:
        """:class:`int`: Returns a user id who revoked the access.

        .. versionadded:: 1.5.0
        """
        return int(self.payload.get("source").get("user_id"))


class UserFollowActionEvent(UserActionEvent):
    """Represents a follow action event by user or of user, This inherits :class:`UserActionEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    @property
    def follower(self) -> User:
        """:class:`User`: An alias to :meth:`UserActionEvent.source`. The user who followed/unfollowed the target.

        .. versionadded:: 1.5.0
        """
        return self.source


class UserBlockActionEvent(UserActionEvent):
    """Represents a block action event by user, This inherits :class:`UserActionEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    @property
    def blocker(self) -> User:
        """:class:`User`: An alias to :meth:`UserActionEvent.source`. The user who blocked/unblocked the target.

        .. versionadded:: 1.5.0
        """
        return self.source


class UserMuteActionEvent(UserActionEvent):
    """Represents a mute action event by user, This inherits :class:`UserActionEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    @property
    def muter(self) -> User:
        """:class:`User`: An alias to :meth:`UserActionEvent.source`. The user who muted/unmuted the target.

        .. versionadded:: 1.5.0
        """
        return self.source


class UserUnfollowActionEvent(UserFollowActionEvent):
    """Represents an unfollow action event by user, This inherits :class:`UserFollowActionEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    ...


class UserUnblockActionEvent(UserBlockActionEvent):
    """Represents an unblock action event by user, This inherits :class:`UserBlockActionEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    ...


class UserUnmuteActionEvent(UserMuteActionEvent):
    """Represents an unmute action event by user, This inherits :class:`UserMuteActionEvent`. This object contains information that twitter posts through the webhook url.

    .. versionadded:: 1.5.0
    """

    ...
