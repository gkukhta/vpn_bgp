#!/usr/bin/env python3

import socket
import sys
import subprocess
from ipaddress import IPv4Network

# Константы
DEFAULT_ROUTE = "10.10.12.254"  # Маршрут по умолчанию

def resolve_hosts_to_ips(filename):
    networks = set()
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith("#"):
                continue
            try:
                # Получаем все IP-адреса для имени хоста
                ips = socket.getaddrinfo(line, None, socket.AF_INET)
                for ip in ips:
                    ip_address = ip[4][0]
                    # Преобразуем IP в сеть /24
                    network = IPv4Network(f"{ip_address}/24", strict=False)
                    networks.add(network)
            except (socket.gaierror, ValueError) as e:
                print(f"Ошибка при обработке {line}: {e}")
    return sorted(networks)  # Сортируем сети для удобства чтения

def update_bird_config(networks):
    with open('/etc/bird/networks.conf', 'w') as file:
        for network in networks:
            file.write(f"route {network} via {DEFAULT_ROUTE};\n")

    # Перезагружаем BIRD для применения изменений
    subprocess.run(['sudo', 'birdc', 'configure'], check=True)

def main():
    if len(sys.argv) != 2:
        print("Использование: update_routes.py <файл_с_хостами>")
        sys.exit(1)

    filename = sys.argv[1]
    networks = resolve_hosts_to_ips(filename)
    update_bird_config(networks)

if __name__ == "__main__":
    main()