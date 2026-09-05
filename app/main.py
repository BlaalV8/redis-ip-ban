import ipaddress

import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

REDIS_KEY = "banned_ranges"


def ip_to_int(ip: str) -> int:
    """
    192.168.1.50 -> 32-bit integer
    """
    return int(ipaddress.IPv4Address(ip))


def parse_target(target: str):
    """
    Accepts:
      192.168.1.50
      192.168.1.0/24

    Returns:
      start_int, end_int, label
    """

    if "/" in target:
        network = ipaddress.IPv4Network(target, strict=False)

        start = int(network.network_address)
        end = int(network.broadcast_address)

        return start, end, str(network)

    ip = ipaddress.IPv4Address(target)
    value = int(ip)

    return value, value, str(ip)


def ban(target: str):
    start, end, label = parse_target(target)

    member = f"{start}:{label}"

    # ZADD banned_ranges END "START:LABEL"
    r.zadd(REDIS_KEY, {member: end})

    print(f"[BAN] {label}")
    print(f"      start = {start}")
    print(f"      end   = {end}")


def is_banned(ip: str):
    ip_int = ip_to_int(ip)

    # ZRANGE banned_ranges IP +inf BYSCORE
    candidates = r.zrange(REDIS_KEY, ip_int, "+inf", byscore=True)

    for member in candidates:
        start_str, label = member.split(":", 1)
        start = int(start_str)

        if start <= ip_int:
            return True, label

    return False, None


def list_bans():
    results = r.zrange(REDIS_KEY, 0, -1, withscores=True)

    if not results:
        print("No banned IPs.")
        return

    print("\n--- BANS ---")

    for member, end in results:
        start_str, label = member.split(":", 1)
        print(f"{label:20} start={start_str} end={int(end)}")


def main():
    print("""
Commands:

  ban 192.168.1.50
  ban 192.168.1.0/24

  check 192.168.1.42

  list

  quit
""")

    while True:
        try:
            command = input("> ").strip()

            if not command:
                continue

            parts = command.split()

            if parts[0] == "quit":
                break

            elif parts[0] == "ban" and len(parts) == 2:
                ban(parts[1])

            elif parts[0] == "check" and len(parts) == 2:
                banned, label = is_banned(parts[1])

                if banned:
                    print(f"🚫 {parts[1]} is banned by {label}")
                else:
                    print(f"✅ {parts[1]} is not banned")

            elif parts[0] == "list":
                list_bans()

            else:
                print("Unknown command.")

        except ValueError as e:
            print(f"Invalid IP: {e}")

        except redis.RedisError as e:
            print(f"Redis error: {e}")


if __name__ == "__main__":
    main()
