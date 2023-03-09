# Balena Prometheus Exporter

A simple script that pulls down Balena metrics from the API and exposes it in Prometheus format.


## Usage

```bash
$ docker build -t balena-exporter .
$ docker run -d \
    -p 0.0.0.0:8000:8000 \
    -e BALENA_TOKEN=<your balena token> \
    balena-exporter
```

You should now be `curl` port 8000 to verify the result.

There's also an optional environment variable for `CRAWL_INTERVAL`, which is set to 60s by default.