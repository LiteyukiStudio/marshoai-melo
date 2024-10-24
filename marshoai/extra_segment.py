from melobot.protocols.onebot.v11.adapter.segment import Segment
from typing import Literal
from typing_extensions import TypedDict

class _TouchData(TypedDict):
    id: str

TouchSegment = Segment.add_type(Literal['touch'], _TouchData)