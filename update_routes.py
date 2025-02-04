#!/usr/bin/env python3

import socket
import sys
import subprocess
from ipaddress import IPv4Network

# Константы
# DEFAULT_ROUTE = "10.10.12.254"  # Маршрут по умолчанию
NETWORKS_FILE = "/run/networks.conf"  # Файл с сетями

def get_default_route():
    try:
        # Выполняем команду `ip route`
        output = subprocess.check_output(['ip', 'route'], text=True)
        
        # Ищем строку, содержащую default
        for line in output.splitlines():
            if line.startswith('default'):
                parts = line.split()
                # Возвращаем следующий за default gateway
                gateway_index = parts.index('via') + 1
                return parts[gateway_index]
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    return None


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
    with open(NETWORKS_FILE, 'w') as file:
        default_route = get_default_route()
        if not default_route:
            print("Не удалось получить маршрут по умолчанию")
            return
        for network in networks:
            file.write(f"route {network} via {default_route};\n")

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