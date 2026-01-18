# EchoVault
Agent to answer question based on spotify, youtube and youtube music history.

# Run locally

```
uv run chainlit run src/frontend.py -w
```

# Development

```
podman build -t echovault .
```

```
podman run -it -e DATA_DIR=/data -v ./data:/data:Z -p 8000:8000 --env-file=.env echovault
```


dockerfile
```
services:
  echovault:
    image: ghcr.io/hakonskogsrud/echovault:{{ echovault_version }}
    container_name: echovault
    environment:
      - UV_CACHE_DIR=/home/appuser/.cache/uv
      - GOOGLE_API_KEY={{ GOOGLE_API_KEY }}
      - DATA_DIR=/data
    ports:
      - "{{ echovault_port }}:8000"
    volumes:
      - {{ echovault_storage_path }}:/data:Z
    restart: unless-stopped
    networks:
      - echovault

networks:
  echovault:
    driver: bridge

```
