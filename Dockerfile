# Use official Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy code
COPY . /app

# Install dependencies

RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose Streamlit port
EXPOSE 8051

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8051", "--server.enableCORS=false"]
