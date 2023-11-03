# Use an official Python runtime as a parent image
FROM python:3.9

# Install Pipenv
RUN pip install pipenv
RUN pip install --upgrade pipenv


# Set the working directory to /app
WORKDIR /app

# Install the python-dotenv library to load environment variables from .env
RUN pip install python-dotenv

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
COPY Pipfile Pipfile.lock ./

# Install the dependency
RUN pipenv install --system --deploy --ignore-pipfile

# Install system-level dependencies
RUN apt-get update && apt-get install -y libssl-dev libffi-dev

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "-c", "import os; from dotenv import load_dotenv; load_dotenv(); os.system('uvicorn fastapiservice.main:app --host 0.0.0.0 --port 8000')"]


