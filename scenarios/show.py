import random

from tgalice.cascade import Pr
from cascade import csc, Turn
from datetime import datetime, timedelta
from uuid import uuid4

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

    now = datetime.utcnow()
    turn.show_item_meta = dict(
        content_id=str(uuid4()),
        title='Упражнение на растяжку',
        # title_tts='Упражнение на растяжку',
        publication_date=str(now).replace(' ', 'T') + 'Z',
        # expiration_date=str(now + timedelta(days=7)) + 'Z',
    )
