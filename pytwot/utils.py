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

import datetime
from typing import TYPE_CHECKING, Any, Optional

from dateutil import parser

if TYPE_CHECKING:
    from .type import ID


def convert(o: object, annotations: Any) -> object:
    try:
        return annotations(o)
    except (ValueError, TypeError):
        return object


def guess_mimetype(byts: bytes) -> str:
    if byts[6:10] == b"\x1a\n\x00\x00":
        return "image/png"

    elif byts[6:10] == b"JFIF":
        return "image/jpeg"

    elif byts[6:10] == b"ypis":
        return "video/mp4"

    elif byts.startswith((b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")):
        return "image/gif"

    else:
        return "text/plain"


def time_parse_todt(date: Optional[Any]) -> datetime.datetime:
    """Parse time return from twitter to datetime object!

    Returns
    ---------
    :class:`datetime.datetime`


    .. versionadded: 1.1.3
    """
    date = str(parser.parse(date))
    y, mo, d = date.split("-")
    h, mi, s = date.split(" ")[1].split("+")[0].split(":")

    return datetime.datetime(
        year=int(y),
        month=int(mo),
        day=int(d.split(" ")[0]),
        hour=int(h),
        minute=int(mi),
        second=int(s),
    )


def compose_tweet(text: Optional[str] = None) -> str:
    """Make a link that let's you compose a tweet

    Parameters
    ------------
    text: :class:`str`
        The pre-populated text in the tweet. If none specified the user has to write their own message.


    Returns
    ---------
    :class:`str`


    .. versionadded: 1.3.5
    """
    if text:
        text = text.replace(" ", "%20")
    return "https://twitter.com/intent/tweet" if not text else f"https://twitter.com/intent/tweet" + f"?text={text}"


def compose_user_action(user_id: str, action: str, text: str = None) -> str:
    """Make a link that let's you interact with a user with certain actions.

    Parameters
    ------------
    user_id: :class:`str`
        The user's id.
    action: :class:`str`
        The action you are going to perform to the user. Must be either "follow" or "dm"
    text: :class:`str`
        The pre-populated text for the dm action.


    Returns
    ---------
    :class:`str`


    .. versionadded: 1.3.5
    """
    if action.lower() not in ("follow", "dm"):
        return TypeError("Action must be either 'follow' or 'dm'")
    if text:
        text = text.replace(" ", "%20")
    return (
        f"https://twitter.com/intent/user?user_id={user_id}"
        if action.lower() == "follow"
        else f"https://twitter.com/messages/compose?recipient_id={user_id}" + f"?text={text}"
        if text
        else f"https://twitter.com/messages/compose?recipient_id={user_id}"
    )


def compose_tweet_action(tweet_id: ID, action: str = None) -> str:
    """Make a link that let's you interact with a tweet with certain actions.

    Parameters
    ------------
    tweet_id: `ID`
        The tweet id you want to compose.
    action: :class:`str`
        The action that's going to get perform when you click the link. Must be either "retweet", "like", or "reply"

    Returns
    ---------
    :class:`str`


    .. versionadded: 1.3.5
    """
    if action.lower() not in ("retweet", "like", "reply"):
        return TypeError("Action must be either 'retweet', 'like', or 'reply'")
    return (
        f"https://twitter.com/intent/{action}?tweet_id={tweet_id}"
        if action != "reply"
        else f"https://twitter.com/intent/tweet?in_reply_to={tweet_id}"
    )
