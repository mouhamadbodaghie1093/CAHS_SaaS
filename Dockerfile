FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y \
    nextflow \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8050
CMD ["python", "app.py"]
