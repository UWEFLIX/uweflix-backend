FROM python:3.12

COPY ".env" .

WORKDIR uweflix-backend/

COPY * .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]