import random

from tgalice.cascade import Pr
from cascade import csc, Turn

from scenarios.exercising import EXERCISES, Exercise


def is_morning_show(turn: Turn) -> bool:
    if not turn.ctx.yandex or not turn.ctx.yandex.request:
        return False
    r = turn.ctx.yandex.request
    if r.type != 'Show.Pull':
        return False
    return r.show_type == 'MORNING'


@csc.add_handler(priority=Pr.CRITICAL, checker=is_morning_show)
def morning_show(turn: Turn):
    ex: Exercise = random.choice(list(EXERCISES.values()))
    turn.response_text = f'А теперь - упражнение из навыка "Шпагат за месяц".\n{ex.text}'
