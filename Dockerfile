FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y sqlite3

COPY . .

EXPOSE 5001

CMD ["flask", "run", "--host=0.0.0.0", "--port", "5001"]

# docker build -t tripresapp .
# docker run -p 5001:5001 --name tripresapp-container tripresapp