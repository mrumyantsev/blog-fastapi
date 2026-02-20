FROM python:3.11.14-alpine3.23

WORKDIR /app

COPY . .

RUN pip install -r ./requirements.txt

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--env-file", "./.env"]

EXPOSE 8000
