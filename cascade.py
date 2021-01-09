from typing import Optional

import attr
from tgalice.cascade import DialogTurn, Cascade
from tgalice.dialog import Response
from tgalice.utils.serialization import Serializeable


@attr.s
class UserState(Serializeable):
    last_day: int = attr.ib(default=0)
    session_count: int = attr.ib(default=0)
    current_step: int = attr.ib(default=0)
    day_is_complete: bool = attr.ib(default=False)


@attr.s
class Turn(DialogTurn):
    us: UserState = attr.ib(default=None)
    image_id: str = attr.ib(default=None)

    def make_response(self) -> Optional[Response]:
        resp = super(Turn, self).make_response()
        if not resp:
            return
        if self.image_id:
            resp.image_id = self.image_id
        return resp


csc = Cascade()
