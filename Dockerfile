FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir --default-timeout=100 -r ./requirements.txt

COPY . ./

ARG ENV_FILE=.env
COPY $ENV_FILE /app/.env

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["python", "run.py", "app:streamlit"]
