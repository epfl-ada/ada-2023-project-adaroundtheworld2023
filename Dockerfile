# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "site/main.py", "--server.port=8501", "--server.address=0.0.0.0"]