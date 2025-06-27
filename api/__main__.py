import uvicorn
from api.app import app
from plugins import load_plugins
from mqtt_client import setup as mqtt_setup
import config


def main():
    load_plugins()
    mqtt_setup()
    uvicorn.run(app, host=config.WEB_HOST, port=config.WEB_PORT)


if __name__ == "__main__":
    main()

