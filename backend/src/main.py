from fastapi import FastAPI
from src.utils.utils import lifespan
from src.crud.models import *

app = FastAPI(lifespan=lifespan)
