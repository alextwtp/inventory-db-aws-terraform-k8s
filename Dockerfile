FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list first for better Docker cache usage
COPY requirements.txt /tmp/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project files into container
COPY app ./app
COPY config ./config
COPY core ./core
COPY repository ./repository
COPY tests ./tests
COPY pytest.ini .
COPY api ./api
COPY .coveragerc .
COPY data ./data
COPY index.html ./index.html

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]