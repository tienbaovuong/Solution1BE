FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /dir
COPY ./requirements.txt /dir/requirements.txt
RUN pip install -r /dir/requirements.txt

COPY ./app /dir/app
COPY ./config /dir/config
COPY ./main.py /dir/main.py
COPY ./Makefile /dir/Makefile
COPY ./ml_models /dir/ml_models
COPY ./.env /dir/.env

EXPOSE 8080

CMD ["make", "start"]