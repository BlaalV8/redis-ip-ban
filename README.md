# Redis IP Banner

Simple CLI tool to ban and check IPv4 addresses and CIDR ranges using **Python + Redis**.

## Start

Start Redis:

```bash
docker compose up -d redis
```

Start the CLI:

```bash
docker compose run --rm app
```

## Commands

### Ban an IP

```text
ban 192.168.1.50
```

### Ban an IP range

```text
ban 192.168.1.0/24
```

### Check an IP

```text
check 192.168.1.42
```

Example:

```text
> check 192.168.1.42
🚫 192.168.1.42 is banned by 192.168.1.0/24
```

### List banned IPs/ranges

```text
list
```

### Exit

```text
quit
```

## Run

```bash
docker compose up -d redis
docker compose run --rm app
```
