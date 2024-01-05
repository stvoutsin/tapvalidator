# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory to /app
WORKDIR /app

# Copy the local poetry files to the container
COPY pyproject.toml poetry.lock /app/

# Install poetry and project dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the local code to the container
COPY . /app/

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Define the command to run your application
RUN poetry build
RUN poetry install

CMD ["poetry", "run", "python", "/app/src/tapvalidator/tap_validator.py"]
