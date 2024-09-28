FROM python:3.12.6 AS image

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock files if they exist
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install other dependencies using Poetry
RUN poetry install --no-dev

# Copy the rest of the application code
COPY . .

# Add Poetry's virtual environment bin directory to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the command to run on container start
CMD ["poetry", "run", "uvicorn", "hi_q_img_capt.app:app", "--host", "0.0.0.0", "--port", "8000"]