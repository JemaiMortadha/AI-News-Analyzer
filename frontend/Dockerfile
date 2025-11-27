FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train CNN model (fixed filename)
RUN python analyzer/train_dl_model.py

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]