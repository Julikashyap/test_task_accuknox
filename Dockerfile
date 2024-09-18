# Step 1: Use official Python base image
FROM python:3.12-slim

# Step 2: Set working directory in the container
WORKDIR /app

# Step 3: Copy the requirements.txt file to the container
COPY requirements.txt .

# Step 4: Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the entire project to the container
COPY . .

RUN python manage.py makemigrations
RUN python manage.py migrate
# Step 8: Expose the port for Django to listen on
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
