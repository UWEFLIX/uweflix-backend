import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from src.main import app


if __name__ == '__main__':
    import uvicorn

    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))

    uvicorn.run(
        host=host,
        port=port,
        app=app
    )
