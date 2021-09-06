FROM python:3.9-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
CMD mkdir estimate_project
COPY . /estimate_project
WORKDIR /estimate_project
RUN pip install -r requirements.txt
CMD chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "./entrypoint.sh"]
