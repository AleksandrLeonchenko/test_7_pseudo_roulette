FROM python:3.11

# ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt .

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y postgresql gcc python3-dev musl-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]



