import logging
import tgalice

from dm import StretchDM


logging.basicConfig(level=logging.DEBUG)


manager = StretchDM()

db = tgalice.message_logging.get_mongo_or_mock()

connector = tgalice.dialog_connector.DialogConnector(
    dialog_manager=manager,
    storage=tgalice.storage.session_storage.BaseStorage(),
    log_storage=tgalice.storage.message_logging.MongoMessageLogger(
        collection=db.get_collection('logs'), detect_pings=True,
    ),
    alice_native_state='user',
)

handler = connector.serverless_alice_handler


if __name__ == '__main__':
    server = tgalice.server.flask_server.FlaskServer(connector=connector)
    server.parse_args_and_run()
