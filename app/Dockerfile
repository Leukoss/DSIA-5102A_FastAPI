# Use a Python base image
FROM python:3.11.8

# Set the working directory inside the container
WORKDIR .

# Copy all the files
COPY . .

# Install pipenv and the dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Expose FastAPI on port 8000
EXPOSE 8000

# Command to run FastAPI with uvicorn
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
