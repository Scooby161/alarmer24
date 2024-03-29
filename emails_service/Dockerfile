FROM python:3.8
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python","email_to_db.py"]