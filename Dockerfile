FROM python:3.8
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["gunicorn","-b", "0.0.0.0:5001", "alarmer_app_main:app"]