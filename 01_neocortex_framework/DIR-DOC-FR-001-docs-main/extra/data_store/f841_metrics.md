# F841 Metrics Store API Documentation

## Overview

The F841 Metrics Store is a high-performance, thread-safe metrics storage system with support for multiple aggregation types, compression, and efficient batch operations.

## Installation

```python
from src.data_store.f841_metrics_store import F841MetricsStore, MetricPoint, MetricType, AggregationType
```

## Basic Usage

### Initialization

```python
# Basic initialization
store = F841MetricsStore()

# With custom storage path and compression disabled
store = F841MetricsStore(
    storage_path="./custom_metrics",
    compress_data=False
)
```

### Adding Metrics

```python
from datetime import datetime
import time

# Create a metric point
metric = MetricPoint(
    metric_id="api_requests",
    metric_type=MetricType.COUNTER,
    value=1.0,
    timestamp=int(time.time()),
    labels={"endpoint": "/api/users", "method": "GET", "status": "200"},
    metadata={"source": "nginx", "environment": "production"}
)

# Add single metric
metric_id = store.add_metric(metric)
print(f"Added metric with ID: {metric_id}")

# Add multiple metrics in batch
metrics_batch = []
for i in range(10):
    metric = MetricPoint(
        metric_id="cpu_usage",
        metric_type=MetricType.GAUGE,
        value=i * 5.0,
        timestamp=int(time.time()) + i,
        labels={"host": "server-01", "core": str(i % 4)},
        metadata={}
    )
    metrics_batch.append(metric)

results = store.add_metrics_batch(metrics_batch)
print(f"Added {len(results)} metrics in batch")
```

### Retrieving Metrics

```python
# Get latest metric
latest = store.get_metric("api_requests")
if latest:
    print(f"Latest value: {latest.value} at {latest.timestamp}")

# Get metric at specific timestamp
specific = store.get_metric("api_requests", timestamp=1672531200)

# Get metrics within time range
start_time = int(time.time()) - 3600  # 1 hour ago
end_time = int(time.time())
metrics_range = store.get_metrics_range("cpu_usage", start_time, end_time)
print(f"Found {len(metrics_range)} metrics in range")
```

## Aggregation Examples

### Basic Aggregations

```python
# Calculate sum of metrics
sum_result = store.aggregate_metrics(
    metric_id="api_requests",
    aggregation_type=AggregationType.SUM,
    start_time=start_time,
    end_time=end_time
)
if sum_result:
    print(f"Total requests: {sum_result.value}")

# Calculate average
avg_result = store.aggregate_metrics(
    metric_id="cpu_usage",
    aggregation_type=AggregationType.AVG,
    start_time=start_time,
    end_time=end_time
)

# Get minimum and maximum
min_result = store.aggregate_metrics(
    metric_id="response_time",
    aggregation_type=AggregationType.MIN,
    start_time=start_time,
    end_time=end_time
)

max_result = store.aggregate_metrics(
    metric_id="response_time",
    aggregation_type=AggregationType.MAX,
    start_time=start_time,
    end_time=end_time
)
```

### Statistical Aggregations

```python
# Percentiles
p95 = store.aggregate_metrics(
    metric_id="response_time",
    aggregation_type=AggregationType.P95,
    start_time=start_time,
    end_time=end_time
)

p99 = store.aggregate_metrics(
    metric_id="response_time",
    aggregation_type=AggregationType.P99,
    start_time=start_time,
    end_time=end_time
)

# Standard deviation and variance
stddev = store.aggregate_metrics(
    metric_id="cpu_usage",
    aggregation_type=AggregationType.STDDEV,
    start_time=start_time,
    end_time=end_time
)

variance = store.aggregate_metrics(
    metric_id="cpu_usage",
    aggregation_type=AggregationType.VARIANCE,
    start_time=start_time,
    end_time=end_time
)

# Median and mode
median = store.aggregate_metrics(
    metric_id="memory_usage",
    aggregation_type=AggregationType.MEDIAN,
    start_time=start_time,
    end_time=end_time
)

mode = store.aggregate_metrics(
    metric_id="concurrent_users",
    aggregation_type=AggregationType.MODE,
    start_time=start_time,
    end_time=end_time
)
```

### Time-based Aggregations

```python
# Rate calculation (change per second)
rate = store.aggregate_metrics(
    metric_id="bytes_transferred",
    aggregation_type=AggregationType.RATE,
    start_time=start_time,
    end_time=end_time
)
print(f"Transfer rate: {rate.value} bytes/second")

# Delta (total change)
delta = store.aggregate_metrics(
    metric_id="queue_size",
    aggregation_type=AggregationType.DELTA,
    start_time=start_time,
    end_time=end_time
)

# First and last values
first = store.aggregate_metrics(
    metric_id="temperature",
    aggregation_type=AggregationType.FIRST,
    start_time=start_time,
    end_time=end_time
)

last = store.aggregate_metrics(
    metric_id="temperature",
    aggregation_type=AggregationType.LAST,
    start_time=start_time,
    end_time=end_time
)
```

### Label Filtering

```python
# Aggregate with label filters
filtered_avg = store.aggregate_metrics(
    metric_id="api_requests",
    aggregation_type=AggregationType.AVG,
    start_time=start_time,
    end_time=end_time,
    labels_filter={"method": "POST", "status": "201"}
)

# Multiple label filters
complex_filter = store.aggregate_metrics(
    metric_id="application_metrics",
    aggregation_type=AggregationType.P95,
    start_time=start_time,
    end_time=end_time,
    labels_filter={
        "environment": "production",
        "region": "us-east-1",
        "service": "user-api"
    }
)
```

## Advanced Operations

### Batch Operations with Optimization

```python
# Large batch with chunking
large_metrics = [...]  # List of 50,000+ metrics
results = store.add_metrics_batch_optimized(
    large_metrics,
    chunk_size=1000  # Process in chunks of 1000
)
print(f"Processed {len(results)} metrics with optimized batch")

# Error handling in batch operations
try:
    results = store.add_metrics_batch(metrics_list)
except RuntimeError as e:
    print(f"Batch operation failed: {e}")
    # The store automatically cleans up partially written files
```

### Store Management

```python
# Get store statistics
stats = store.get_store_stats()
print(f"Total metrics: {stats['total_metrics']}")
print(f"Storage size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
print(f"Compression enabled: {stats['compression_enabled']}")

# Cleanup old metrics (older than 30 days)
cleaned = store.cleanup_old_metrics(max_age_days=30)
print(f"Cleaned up {cleaned} old metrics")

# Delete specific metrics
deleted_count = store.delete_metrics(
    metric_id="test_metrics",
    start_time=start_time,
    end_time=end_time
)
print(f"Deleted {deleted_count} metrics")
```

### Error Handling Examples

```python
# Handling invalid metrics
try:
    invalid_metric = "not a MetricPoint"
    store.add_metric(invalid_metric)
except TypeError as e:
    print(f"Type error: {e}")

# Handling invalid values
try:
    metric = MetricPoint(
        metric_id="test",
        metric_type=MetricType.GAUGE,
        value=float('inf'),  # Invalid: infinite value
        timestamp=int(time.time()),
        labels={},
        metadata={}
    )
    store.add_metric(metric)
except ValueError as e:
    print(f"Validation error: {e}")

# Graceful handling of missing metrics
result = store.get_metric("non_existent_metric")
if result is None:
    print("Metric not found")

empty_range = store.get_metrics_range("no_data", 0, 100)
if not empty_range:
    print("No metrics in specified range")
```

## Performance Tips

1. **Use batch operations** for inserting multiple metrics
2. **Enable compression** for storage efficiency (default: enabled)
3. **Use label filtering** to reduce aggregation computation
4. **Regular cleanup** to remove old metrics
5. **Cache aggregations** when querying the same data repeatedly

## Metric Types

| Type | Description | Use Case |
|------|-------------|----------|
| `COUNTER` | Monotonically increasing value | Request counts, error counts |
| `GAUGE` | Can increase or decrease | CPU usage, memory usage |
| `HISTOGRAM` | Tracks distribution of values | Response times, request sizes |
| `SUMMARY` | Pre-calculated quantiles | Service level indicators |

## Aggregation Types Reference

| Aggregation | Description | Formula |
|-------------|-------------|---------|
| `SUM` | Sum of all values | Σx |
| `AVG` | Average value | Σx / n |
| `MIN` | Minimum value | min(x) |
| `MAX` | Maximum value | max(x) |
| `COUNT` | Number of samples | n |
| `P50/P75/P90/P95/P99/P999` | Percentiles | Various |
| `STDDEV` | Standard deviation | √(Σ(x - μ)²/(n-1)) |
| `VARIANCE` | Variance | Σ(x - μ)²/(n-1) |
| `MEDIAN` | Median (P50) | Middle value |
| `MODE` | Most frequent value | argmax frequency(x) |
| `RANGE` | Range of values | max(x) - min(x) |
| `FIRST` | First value in range | x₀ |
| `LAST` | Last value in range | xₙ |
| `RATE` | Rate of change | (xₙ - x₀) / (tₙ - t₀) |
| `DELTA` | Total change | xₙ - x₀ |

## Thread Safety

All operations are thread-safe using reentrant locks. Multiple threads can safely read and write metrics concurrently.

## Storage Format

Metrics are stored as compressed JSON files with the following structure:
```
{
  "metric_id": "string",
  "metric_type": "counter|gauge|histogram|summary",
  "value": float,
  "timestamp": int,
  "labels": {"key": "value", ...},
  "metadata": {"key": value, ...},
  "_version": "1.0",
  "_checksum": "md5_hash"
}
```