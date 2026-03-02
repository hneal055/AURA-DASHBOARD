FROM python:3.11-alpine
WORKDIR /app
RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev linux-headers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
