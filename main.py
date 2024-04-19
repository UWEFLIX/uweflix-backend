import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from src.main import app


if __name__ == '__main__':
    import uvicorn

    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))

    uvicorn.run(
        host="0.0.0.0",
        app=app,
        port=443,
        ssl_certfile=f"ssl/certificate.crt",
        ssl_keyfile=f"ssl/private.key",
    )
