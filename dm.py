import logging
import os
import time
from typing import Optional

import attr
import tgalice
import yaml
from tgalice.cascade import Cascade

from tgalice.dialog import Response, Context
from tgalice.interfaces.yandex import extract_yandex_forms
from tgalice.nlu.basic_nlu import like_help, fast_normalize
from tgalice.nlu.matchers import make_matcher_with_regex, TFIDFMatcher, TextNormalization
from tgalice.nlu.regex_expander import load_intents_with_replacement
from tgalice.utils.serialization import Serializeable

from cascade import Turn, csc, UserState
from utils import match_forms
from scenarios import menu, exercising  # noqa

logger = logging.getLogger(__name__)


class StretchDM(tgalice.dialog_manager.BaseDialogManager):
    def __init__(self, cascade: Cascade = None, **kwargs):
        super(StretchDM, self).__init__(**kwargs)
        self.cascade = cascade or csc

        logger.debug('loading intents..')
        self.intents = load_intents_with_replacement(
            intents_fn='texts/intents.yaml',
            expressions_fn='texts/expressions.yaml',
        )
        self.intents_matcher = make_matcher_with_regex(
            intents=self.intents,
            base_matcher=TFIDFMatcher(threshold=0.3, text_normalization=TextNormalization.FAST_LEMMATIZE)
        )

    def respond(self, ctx: Context):
        t0 = time.time()
        text, forms, intents = self.nlu(ctx)
        turn = Turn(
            ctx=ctx,
            text=text,
            intents=intents,
            forms=forms,
            user_object=ctx.user_object,
            us=UserState.from_dict(ctx.user_object.get('user_state', {})),
        )
        logger.debug(f'current stage is: {turn.stage}')
        handler_name = self.cascade(turn)
        logger.debug(f"Handler name: {handler_name}")
        self.cascade.postprocess(turn)
        resp = turn.make_response()
        resp.updated_user_object['user_state'] = turn.us.to_dict()
        logger.debug(f'FULL RESPONSE TIME: {time.time() - t0}')
        logger.debug(f'final state: {resp.updated_user_object}')
        return resp

    def nlu(self, ctx):
        text = fast_normalize(ctx.message_text or '')
        forms = match_forms(text=text, intents=self.intents)
        if ctx.yandex:
            ya_forms = extract_yandex_forms(ctx.yandex)
            forms.update(ya_forms)

        logger.debug(f"Extracted forms: {forms}")
        intents = self.intents_matcher.aggregate_scores(text=text)
        for intent_name in forms:
            intents[intent_name] = 1

        if tgalice.nlu.basic_nlu.like_help(ctx.message_text):
            intents['help'] = max(intents.get('help', 0), 0.9)
        if tgalice.nlu.basic_nlu.like_yes(ctx.message_text):
            intents['yes'] = max(intents.get('yes', 0), 0.9)
        if tgalice.nlu.basic_nlu.like_no(ctx.message_text):
            intents['no'] = max(intents.get('no', 0), 0.9)

        logger.debug(f"Intents: {intents}")
        logger.debug(f"Forms: {forms}")
        return text, forms, intents
