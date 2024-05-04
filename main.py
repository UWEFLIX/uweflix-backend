import os
from dotenv import load_dotenv
load_dotenv()

from src.main import app


if __name__ == '__main__':
    import uvicorn

    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))

    _ssl = int(os.getenv("SSL"))

    if _ssl:
        cert = os.getenv('SSL_CERT_FILE')
        key = os.getenv('SSL_PRIVATE_KEY')
        uvicorn.run(
            host=host,
            app=app,
            port=port,
            ssl_certfile=cert,
            ssl_keyfile=key,
        )
    else:
        uvicorn.run(
            host=host,
            app=app,
            port=port
        )
