import attr
from tgalice.cascade import DialogTurn, Cascade
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


csc = Cascade()
