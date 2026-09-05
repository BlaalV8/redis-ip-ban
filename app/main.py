import ipaddress

import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

REDIS_KEY = "banned_ranges"


def ip_to_int(ip: str) -> int:
    """
    192.168.1.50 -> entier 32 bits
    """
    return int(ipaddress.IPv4Address(ip))


def parse_target(target: str):
    """
    Accepte :
      192.168.1.50
      192.168.1.0/24

    Retourne :
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
    r.execute_command("ZADD", REDIS_KEY, end, member)

    print(f"[BAN] {label}")
    print(f"      start = {start}")
    print(f"      end   = {end}")


def is_banned(ip: str):
    ip_int = ip_to_int(ip)

    # ZRANGE banned_ranges IP +inf BYSCORE
    candidates = r.execute_command("ZRANGE", REDIS_KEY, ip_int, "+inf", "BYSCORE")

    for member in candidates:
        start_str, label = member.split(":", 1)
        start = int(start_str)

        if start <= ip_int:
            return True, label

    return False, None


def list_bans():
    results = r.execute_command("ZRANGE", REDIS_KEY, 0, -1, "WITHSCORES")

    if not results:
        print("Aucune IP bannie.")
        return

    print("\n--- BANS ---")

    for i in range(0, len(results), 2):
        member = results[i]
        end = int(float(results[i + 1]))

        start_str, label = member.split(":", 1)

        print(f"{label:20} start={start_str} end={end}")


def main():
    print("""
Commandes :

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
                    print(f"🚫 {parts[1]} est bannie par {label}")
                else:
                    print(f"✅ {parts[1]} n'est pas bannie")

            elif parts[0] == "list":
                list_bans()

            else:
                print("Commande inconnue.")

        except ValueError as e:
            print(f"IP invalide : {e}")

        except redis.RedisError as e:
            print(f"Erreur Redis : {e}")


if __name__ == "__main__":
    main()
