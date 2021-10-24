"""
MIT License

Copyright (c) 2021 TheFarGG & TheGenocides

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
from dateutil import parser
from typing import Dict, List, Any

class Media:
    """Represent a Media attachment in a tweet.
    Version Added: 1.1.0

    Parameters:
    ===================
    data: Dict[str, Any]
        The full data of the media in a dictionary. 

    Attributes:
    ====================
    _payload
        Represent the main data of a Media. 
    """
    def __init__(self, data: Dict[str, Any]):
        self._payload = data

    def __repr__(self) -> str:
        return "Media(type={0.type} url={0.url} width={0.widht} height={0.height} media_key={0.media_key})".format(
            self
        )

    @property
    def type(self) -> str:
        """str: Return the media's type.
        Version Added: 1.1.0
        """
        return self._payload.get("type")

    @property
    def url(self) -> str:
        """str: Return the media's url.
        Version Added: 1.1.0
        """
        return self._payload.get("url")

    @property
    def width(self) -> int:
        """int: Return the media's width.
        Version Added: 1.1.0
        """
        return int(self._payload.get("width"))

    @property
    def height(self) -> int:
        """int: Return the media's height.
        Version Added: 1.1.0
        """
        return int(self._payload.get("height"))

    @property
    def media_key(self) -> str:
        """Return the media's unique key.
        Version Added: 1.1.0
        """
        return self._payload.get("media_key")

class PollOptions:
    """Represent the Poll Options, The minimum option of a poll is 2 and maximum is 4.
    Version Added: 1.1.0

    Parameters:
    ===================
    options: List[dict]
        An array of dictionary filled with position, label, and votes.
    """
    def __init__(self, options: Dict[str, Any]):
        self.options = options

    def __repr__(self) -> str:
        return "PollOption({0.position} {0.label} {0.votes})".format(
            self
        )

    @property
    def position(self) -> int:
        """int: The option's position.
        Version Added: 1.1.0
        """
        return int(self.options.get("position"))
    
    @property
    def label(self) -> str:
        """str: The option's label.
        Version Added: 1.1.0
        """
        return self.options.get("label")
    
    @property
    def votes(self) -> int:
        """int: The option's votes.
        Version Added: 1.1.0
        """
        return int(self.options.get("votes"))

    def __eq__(self, other):
        if not isinstance(other, PollOptions):
            raise ValueError("== operation cannot be done with one of the element not a valid PollOptions")
        return self.position == other.position

    def __lt__(self, other): 
        if not isinstance(other, PollOptions):
            raise ValueError("< operation cannot be done with one of the element not a valid PollOptions")
        return self.position < other.position
 
    def __gt__(self, other): 
        if not isinstance(other, PollOptions):
            raise ValueError("> operation cannot be done with one of the element not a valid PollOptions")
        return self.position > other.position
 
    def __le__(self, other): 
        if not isinstance(other, PollOptions):
            raise ValueError("<= operation cannot be done with one of the element not a valid PollOptions")
        return self.position <= other.position
 
    def __ge__(self, other): 
        if not isinstance(other, PollOptions):
            raise ValueError(">= operation cannot be done with one of the element not a valid PollOptions")
        return self.position >= other.position

class Poll:
    """Represent a Poll attachment in a tweet.
    Version Added: 1.1.0

    Parameters:
    ===================
    data: Dict[str, Any]
        The full data of the poll in a dictionary. 

    Attributes:
    ====================
    _payload
        The complete data of a Poll keep inside a dictionary.
    """
    def __init__(self, data: Dict[str, Any]):
        self._payload = data

    def __repr__(self) -> str:
        return "Poll(id={0.id}, voting_status={0.voting_status}, duration={0.duration}, end_date={0.end_date} options={0.options})".format(
            self
        )

    def __len__(self) -> int: 
        return len(self.options)

    @property
    def id(self) -> int:
        """int: Return the poll's unique ID.
        Version Added: 1.1.0.
        """
        return int(self._payload.get("id"))

    @property
    def options(self) -> List[PollOptions]:
        """List[PollOptions]: Return a list of :class: PollOptions.
        Version Added: 1.1.0.
        """
        return [PollOptions(option) for option in self._payload.get("options")]

    @property
    def voting_status(self) -> bool:
        """bool: Return True if the poll is still open for voting, if its closed it return False.
        Version Added: 1.1.0
        """
        return True if self._payload.get("voting_status") == "open" else False

    @property
    def duration(self) -> int:
        """int: Return the poll duration in seconds.
        Version Added: 1.1.0
        """
        return int(self._payload.get("duration_minutes")) * 60

    @property
    def end_date(self) -> datetime.datetime:
        """datetime.datetime: Return the end date in datetime.datetime object.
        Version Added: 1.1.0
        """
        date = str(parser.parse(self._payload.get("end_datetime")))
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