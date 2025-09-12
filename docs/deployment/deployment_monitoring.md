# 🚀 Deployment & Monitoring Blueprints

## **Purpose**
This document provides comprehensive blueprints for deploying and monitoring the Z-Beam Generator system. It covers containerization, orchestration, health monitoring, logging, metrics collection, and operational procedures.

## 📋 Deployment Requirements

### **Containerization**
- **Docker** for containerization with multi-stage builds
- **Docker Compose** for local development and testing
- **Kubernetes** manifests for production deployment
- **Helm charts** for package management

### **Infrastructure**
- **AWS/GCP/Azure** cloud provider support
- **Load balancing** and auto-scaling
- **Database** for configuration and caching
- **CDN** for static asset de        expr: histogram_quantile(0.5, rate(z_beam_ai_detection_score_bucket[10m])) < 70
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low AI detection scores detected"
          description: "Median AI detection score is below 70 (content appears too AI-generated)."
### **Monitoring Stack**
- **Prometheus** for metrics collection
- **Grafana** for visualization
- **ELK Stack** (Elasticsearch, Logstash, Kibana) for logging
- **AlertManager** for alerting

## 🏗️ Containerization Architecture

### **Dockerfile Patterns**

```dockerfile
# Multi-stage Dockerfile for Python application
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
FROM base as dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy installed dependencies
COPY --from=dependencies /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "run.py"]
```

### **Docker Compose Configuration**

```yaml
# docker-compose.yml for development
version: '3.8'

services:
  z-beam-generator:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    volumes:
      - ./config:/app/config:ro
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    networks:
      - z-beam-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - z-beam-network
    restart: unless-stopped

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: z_beam_generator
      POSTGRES_USER: z_beam_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - z-beam-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - z-beam-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - z-beam-network
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  z-beam-network:
    driver: bridge
```

## 🚀 Kubernetes Deployment

### **Deployment Manifests**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: z-beam-generator
  labels:
    app: z-beam-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: z-beam-generator
  template:
    metadata:
      labels:
        app: z-beam-generator
    spec:
      containers:
      - name: z-beam-generator
        image: z-beam-generator:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: config-volume
        configMap:
          name: z-beam-config
      - name: logs-volume
        emptyDir: {}
```

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: z-beam-generator-service
spec:
  selector:
    app: z-beam-generator
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: z-beam-generator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: z-beam-generator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### **ConfigMap and Secrets**

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: z-beam-config
data:
  config.yaml: |
    api:
      deepseek:
        base_url: "https://api.deepseek.com/v1"
        timeout: 30
      winston:
        base_url: "https://api.winston.ai"
        timeout: 15

    generation:
      max_tokens: 1000
      temperature: 0.7
      quality_threshold: 75.0

    caching:
      redis_url: "redis://redis-service:6379"
      ttl_seconds: 3600

    logging:
      level: "INFO"
      format: "json"
```

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: z-beam-secrets
type: Opaque
data:
  # Base64 encoded values
  deepseek-api-key: <base64-encoded-key>
  winston-api-key: <base64-encoded-key>
  database-password: <base64-encoded-password>
```

## 📊 Monitoring Architecture

### **Prometheus Configuration**

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'z-beam-generator'
    static_configs:
      - targets: ['z-beam-generator:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### **Application Metrics**

```python
# utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Request metrics
REQUEST_COUNT = Counter(
    'z_beam_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'z_beam_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Generation metrics
GENERATION_COUNT = Counter(
    'z_beam_generations_total',
    'Total number of content generations',
    ['component', 'material', 'success']
)

GENERATION_LATENCY = Histogram(
    'z_beam_generation_duration_seconds',
    'Content generation duration',
    ['component', 'material']
)

AI_DETECTION_SCORE = Histogram(
    'z_beam_ai_detection_score',
    'AI detection scores',
    ['component']
)

# API client metrics
API_REQUEST_COUNT = Counter(
    'z_beam_api_requests_total',
    'API requests to external services',
    ['service', 'method', 'status']
)

API_REQUEST_LATENCY = Histogram(
    'z_beam_api_request_duration_seconds',
    'API request duration',
    ['service', 'method']
)

# Circuit breaker metrics
CIRCUIT_BREAKER_STATE = Gauge(
    'z_beam_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)',
    ['service']
)

CIRCUIT_BREAKER_FAILURES = Counter(
    'z_beam_circuit_breaker_failures_total',
    'Circuit breaker failure count',
    ['service']
)

# Cache metrics
CACHE_HITS = Counter(
    'z_beam_cache_hits_total',
    'Cache hit count',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'z_beam_cache_misses_total',
    'Cache miss count',
    ['cache_type']
)

def record_request(method, endpoint, status, duration):
    """Record HTTP request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def record_generation(component, material, success, duration):
    """Record content generation metrics"""
    GENERATION_COUNT.labels(
        component=component,
        material=material,
        success=str(success)
    ).inc()
    GENERATION_LATENCY.labels(component=component, material=material).observe(duration)

def record_ai_detection_score(component, score):
    """Record AI detection score"""
    AI_DETECTION_SCORE.labels(component=component).observe(score)

def record_api_request(service, method, status, duration):
    """Record API request metrics"""
    API_REQUEST_COUNT.labels(service=service, method=method, status=status).inc()
    API_REQUEST_LATENCY.labels(service=service, method=method).observe(duration)

def update_circuit_breaker_state(service, state):
    """Update circuit breaker state metric"""
    state_value = {'closed': 0, 'open': 1, 'half-open': 2}[state]
    CIRCUIT_BREAKER_STATE.labels(service=service).set(state_value)

def record_cache_operation(cache_type, hit):
    """Record cache operation"""
    if hit:
        CACHE_HITS.labels(cache_type=cache_type).inc()
    else:
        CACHE_MISSES.labels(cache_type=cache_type).inc()

def get_metrics():
    """Get current metrics for /metrics endpoint"""
    return generate_latest()
```

### **Health Check Endpoints**

```python
# app/health.py
from flask import Blueprint, jsonify
from utils.metrics import get_metrics
from api.client_manager import APIClientManager
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'z-beam-generator'
    })

@health_bp.route('/ready')
def readiness_check():
    """Readiness check for Kubernetes"""
    checks = {
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'api_clients': check_api_clients()
    }

    all_healthy = all(checks.values())

    return jsonify({
        'status': 'ready' if all_healthy else 'not ready',
        'checks': checks,
        'timestamp': time.time()
    }), 200 if all_healthy else 503

@health_bp.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

def check_database_connection():
    """Check database connectivity"""
    try:
        # Implement database connection check
        return True
    except Exception:
        return False

def check_redis_connection():
    """Check Redis connectivity"""
    try:
        # Implement Redis connection check
        return True
    except Exception:
        return False

def check_api_clients():
    """Check API client health"""
    try:
        manager = APIClientManager()
        # Check if API clients can be initialized
        return manager.health_check()
    except Exception:
        return False
```

## 📝 Logging Configuration

### **Structured Logging**

```python
# utils/logging_config.py
import logging
import json
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add custom fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['service'] = 'z-beam-generator'
        log_record['version'] = '1.0.0'

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id

        # Add component context
        if hasattr(record, 'component'):
            log_record['component'] = record.component

        if hasattr(record, 'material'):
            log_record['material'] = record.material

def setup_logging(log_level='INFO', json_format=True):
    """Setup structured logging configuration"""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if json_format:
        # JSON formatter for production
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(service)s %(levelname)s %(name)s %(message)s'
        )
    else:
        # Human-readable formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger

# Logger instances for different components
api_logger = logging.getLogger('api')
generation_logger = logging.getLogger('generation')
monitoring_logger = logging.getLogger('monitoring')
```

### **Log Aggregation with ELK**

```yaml
# monitoring/logstash.conf
input {
  file {
    path => "/var/log/z-beam-generator/*.log"
    start_position => "beginning"
    type => "z-beam-logs"
  }
}

filter {
  if [type] == "z-beam-logs" {
    json {
      source => "message"
    }

    # Add geoip information
    geoip {
      source => "client_ip"
      target => "geoip"
    }

    # Parse timestamp
    date {
      match => ["timestamp", "ISO8601"]
      target => "@timestamp"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "z-beam-logs-%{+YYYY.MM.dd}"
  }

  stdout {
    codec => rubydebug
  }
}
```

## 🚨 Alerting Configuration

### **AlertManager Rules**

```yaml
# monitoring/alert_rules.yml
groups:
  - name: z-beam-alerts
    rules:
      # Service availability alerts
      - alert: z-beamServiceDown
        expr: up{job="z-beam-generator"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Z-Beam Generator service is down"
          description: "Z-Beam Generator has been down for more than 5 minutes."

      # High error rate alerts
      - alert: HighErrorRate
        expr: rate(z_beam_requests_total{status=~"5.."}[5m]) / rate(z_beam_requests_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% over the last 5 minutes."

      # API circuit breaker alerts
      - alert: CircuitBreakerOpen
        expr: z_beam_circuit_breaker_state == 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker is open"
          description: "Circuit breaker for {{ $labels.service }} is open."

      # High latency alerts
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(z_beam_request_duration_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency"
          description: "95th percentile latency is {{ $value }}s."

      # Low AI detection quality alerts
      - alert: LowAIDetectionQuality
        expr: histogram_quantile(0.5, rate(z_beam_ai_detection_score_bucket[10m])) < 70
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Low AI detection quality"
          description: "Median AI detection score is below 70."

      # Resource usage alerts
      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 90%."

      - alert: HighCPUUsage
        expr: rate(node_cpu_seconds_total{mode!="idle"}[5m]) / rate(node_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is above 80%."
```

### **AlertManager Configuration**

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@z-beam-generator.com'
  smtp_auth_username: 'alerts@z-beam-generator.com'
  smtp_auth_password: 'your-smtp-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-notifications'
  routes:
  - match:
      severity: critical
    receiver: 'critical-notifications'

receivers:
- name: 'team-notifications'
  email_configs:
  - to: 'team@z-beam-generator.com'
    send_resolved: true

- name: 'critical-notifications'
  email_configs:
  - to: 'oncall@z-beam-generator.com'
    send_resolved: true
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    send_resolved: true
```

## 🔄 CI/CD Pipeline

### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest --cov=components --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Build Docker image
      run: |
        docker build -t z-beam-generator:${{ github.sha }} .
        docker tag z-beam-generator:${{ github.sha }} z-beam-generator:latest

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push z-beam-generator:${{ github.sha }}
        docker push z-beam-generator:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v2

    - name: Configure kubectl
      run: |
        echo ${{ secrets.KUBE_CONFIG }} | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Deploy to Kubernetes
      run: |
        sed -i 's|image: z-beam-generator:.*|image: z-beam-generator:${{ github.sha }}|g' k8s/deployment.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/z-beam-generator

    - name: Run smoke tests
      run: |
        # Wait for deployment to be ready
        kubectl wait --for=condition=available --timeout=300s deployment/z-beam-generator

        # Run basic health checks
        curl -f http://z-beam-generator-service/health

        # Run integration tests against deployed service
        pytest tests/integration/ --tb=short
```

## 📈 Grafana Dashboards

### **Main Dashboard Configuration**

```json
{
  "dashboard": {
    "title": "Z-Beam Generator Overview",
    "tags": ["z-beam", "monitoring"],
    "timezone": "UTC",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(z_beam_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(z_beam_requests_total{status=~\"5..\"}[5m]) / rate(z_beam_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ]
      },
      {
        "title": "Generation Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(z_beam_generation_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "AI Detection Scores",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.5, rate(z_beam_ai_detection_score_bucket[5m]))",
            "legendFormat": "Median Score"
          }
        ]
      },
      {
        "title": "Circuit Breaker States",
        "type": "table",
        "targets": [
          {
            "expr": "z_beam_circuit_breaker_state",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Cache Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(z_beam_cache_hits_total[5m]) / (rate(z_beam_cache_hits_total[5m]) + rate(z_beam_cache_misses_total[5m])) * 100",
            "legendFormat": "Cache Hit Rate %"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Operational Procedures

### **Deployment Checklist**

- [ ] Run full test suite locally
- [ ] Build and test Docker image
- [ ] Update configuration values
- [ ] Backup current production data
- [ ] Deploy to staging environment
- [ ] Run integration tests against staging
- [ ] Monitor staging for 30 minutes
- [ ] Deploy to production
- [ ] Monitor production deployment
- [ ] Update documentation

### **Incident Response**

1. **Detection**: Alerts trigger via AlertManager
2. **Assessment**: Check Grafana dashboards for symptoms
3. **Containment**: Scale down problematic services if needed
4. **Recovery**: Roll back to previous version if necessary
5. **Analysis**: Review logs and metrics for root cause
6. **Prevention**: Implement fixes and update monitoring

### **Maintenance Tasks**

- **Daily**: Review error logs and alert history
- **Weekly**: Update dependencies and security patches
- **Monthly**: Review performance metrics and optimize
- **Quarterly**: Conduct security audit and penetration testing

This comprehensive deployment and monitoring framework ensures the Z-Beam Generator system runs reliably in production with full observability and automated operations.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/deployment/deployment_monitoring.md
