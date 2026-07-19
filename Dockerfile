# Use an official lightweight python image 
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port 5000(the port your Flask app runs on)
EXPOSE 5000

# Command to run your application 
CMD ["python","app.py"]