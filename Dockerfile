## old version start ##



# # Use the official Python image as the base image
# FROM python:3.12

# # Set the working directory inside the container
# WORKDIR /app

# RUN apt-get update

# # Copy the requirements.txt file and install dependencies
# COPY fastapiservice/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# RUN apt install -y unixodbc-dev

# # Copy your application code into the container
# RUN cd /app && mkdir fastapiservice
# COPY fastapiservice/ /app/fastapiservice/

# # Install uvicorn
# RUN pip install uvicorn

# # Expose the port on which your FastAPI app will run
# EXPOSE 8000

# # Start your FastAPI application
# CMD ["uvicorn", "fastapiservice.main:app", "--host", "0.0.0.0:8000"]


## old version end ##

# Use an official Python runtime as a parent image
FROM python:3.9

# Install Pipenv
RUN pip install pipenv
RUN pip install --upgrade pipenv


# Set the working directory to /app
WORKDIR /app

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

# Define environment variables
ENV DB_USER=DB_USER
ENV DB_PASSWORD=DB_PASSWORD
ENV DB_SERVER=DB_SERVER
ENV DB_NAME=DB_NAME
ENV SECRET_KEY=OPEN_AI_KEY
ENV PINECONE_API_KEY=PINECONE_API_KEY
ENV FASTAPI_SERVER_URL=FASTAPI_SERVER_URL
ENV INDEX_NAME=index_name
ENV ENVIRONMENT=ENVIRONMENT

# Run app.py when the container launches
CMD ["uvicorn", "fastapiservice.main:app", "--host", "0.0.0.0", "--port", "8000"]

