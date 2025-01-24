#!/usr/bin/env python3

import sys
import socket
import subprocess

# Константы
ROUTER_ID = "192.168.134.1"  # Идентификатор роутера
NETWORKS_FILE = "/etc/bird/networks.conf"  # Файл для записи маршрутов

def resolve_hosts_to_ips(filename):
    """
    Читает файл с именами хостов, разрешает их в IP-адреса и возвращает уникальные сети /24.
    """
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
                    network = '.'.join(ip_address.split('.')[:3]) + '.0/24'
                    networks.add(network)
            except socket.gaierror:
                print(f"Could not resolve {line}")
    return networks

def write_networks_file(networks):
    """
    Записывает уникальные сети в файл networks.conf.
    """
    with open(NETWORKS_FILE, 'w') as file:
        for network in sorted(networks):
            file.write(f"route {network} via {ROUTER_ID};\n")

def reload_bird():
    """
    Перезагружает конфигурацию BIRD.
    """
    try:
        subprocess.run(['birdc', 'configure'], check=True)
        print("BIRD configuration reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload BIRD configuration: {e}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <hosts_file>")
        sys.exit(1)

    hosts_file = sys.argv[1]
    networks = resolve_hosts_to_ips(hosts_file)
    write_networks_file(networks)
    reload_bird()

if __name__ == "__main__":
    main()