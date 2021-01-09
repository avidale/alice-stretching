import logging
import os
import sentry_sdk
import tgalice
from tgalice.dialog import Context

from dm import StretchDM


logging.basicConfig(level=logging.DEBUG)

if os.getenv('SENTRY_DSN', None) is not None:
    sentry_sdk.init(os.environ['SENTRY_DSN'])


class CustomLogger(tgalice.storage.message_logging.MongoMessageLogger):
    def should_ignore_message(self, context: Context = None, **kwargs) -> bool:
        if super(self, CustomLogger).should_ignore_message(context=context, **kwargs):
            return True
        if context.yandex and context.yandex.request and context.yandex.request.type == 'Show.Pull':
            return True
        return False


manager = StretchDM()

db = tgalice.message_logging.get_mongo_or_mock()

connector = tgalice.dialog_connector.DialogConnector(
    dialog_manager=manager,
    storage=tgalice.storage.session_storage.BaseStorage(),
    log_storage=CustomLogger(collection=db.get_collection('logs'), detect_pings=True),
    alice_native_state='user',
)

handler = connector.serverless_alice_handler


if __name__ == '__main__':
    server = tgalice.server.flask_server.FlaskServer(connector=connector)
    server.parse_args_and_run()
