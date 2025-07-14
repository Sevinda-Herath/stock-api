# Stock API Docker Setup

This guide explains how to run the Stock API application using Docker.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### Using Docker Compose (Recommended)

1. Build and start the container:
```bash
docker-compose up --build
```

2. The API will be available at `http://localhost:8000`

3. To run in detached mode:
```bash
docker-compose up -d --build
```

4. To stop the container:
```bash
docker-compose down
```

### Using Docker directly

1. Build the image:
```bash
docker build -t stock-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -v $(pwd)/datasets:/app/datasets \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/sentiments:/app/sentiments \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/model-metrics-charts:/app/model-metrics-charts \
  stock-api
```

## API Endpoints

- `GET /` - Health check
- `GET /sentiment_summary/{symbol}` - Get sentiment summary for a stock symbol
- `GET /sentiment_chart/{symbol}` - Get sentiment chart for a stock symbol
- `GET /predictions/{symbol}` - Get predictions for a stock symbol
- `GET /metrics/{symbol}` - Get model metrics for a stock symbol

## Data Persistence

The following directories are mounted as volumes to persist data:
- `datasets/` - Stock data
- `models/` - Trained ML models
- `results/` - Prediction results
- `sentiments/` - Sentiment analysis results
- `logs/` - Application logs
- `model-metrics-charts/` - Model performance charts

## Scheduler

The application includes a background scheduler that runs daily at 3:30 AM UTC (9:00 AM Sri Lanka time) to:
1. Download new stock data
2. Generate sentiment analysis
3. Save predictions

## Troubleshooting

### Check container logs
```bash
docker-compose logs -f stock-api
```

### Access container shell
```bash
docker-compose exec stock-api /bin/bash
```

### Rebuild container
```bash
docker-compose down
docker-compose up --build
```
