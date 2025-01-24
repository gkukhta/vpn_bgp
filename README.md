# Настройка анонса сетей по BGP с сервера Wireguard VPN
TODO: Настроить firewall на сервере VPN и на Mikrotik  

Есть список имён DNS из Интернета, которые должны с офисного маршрутизатора Mikrotik,
на котором рабтает клиент Wireguard, 
маршрутизироваться на сервер VPN Wireguard в Интернете, а не напрямую в Интернет по маршруту по умолчанию.  
В тестовой установке в GNS3 используются следующии версии:
- Сервер VPN: `Debian 12`
- Клиент VPN: `Mikrotik RB450G 7.8`

1. Установка bird на сервере VPN.
```bash
sudo apt install bird
```
2. Конфигурация `bird` на сервере VPN.
```bash
sudo nano /etc/bird/bird.conf
```
[Текст конфигурации](bird.conf)  
Для теста конфигурации создадим файл `/etc/bird/networks.conf`
```bash
sudo touch /etc/bird/networks.conf
```
Перечитываем конфигурацию bird:
```bash
sudo birdc configure
```
Проверяем:
```bash
journalctl -u bird --since "2 minutes ago"
```
```log
Jan 24 08:29:46 debian bird[927]: Reconfiguring
Jan 24 08:29:46 debian bird[927]: Reconfigured
```
Создадим список имён DNS, на сервере VPN.
Сети, к которым они относятся будут анонсироваться по BGP для маршрутизации через VPN.
```bash
sudo nano /hostnames
```
Примерное содержимое файла:
```plaintext
bbc.com
www.cnn.com
www.nvidia.com
bbc.com
# Это комментарий, он будет пропущен
x.com
```
Создадим программу для генерации списка сетей:
```bash
sudo nano /usr/local/bin/update_routes.py
```
[Текст программы](update_routes.py).  
Сделаем её исполнимой:
```bash
sudo chmod +x /usr/local/bin/update_routes.py
```
Запустим для проверки:
```bash
sudo /usr/local/bin/update_routes.py /hostnames
```
Проверяем:
```bash
journalctl -u bird --since "2 minutes ago"
```
Проверим список сформированных сетей для анонса по BGP:
```bash
sudo cat /etc/bird/networks.conf
```
Создадим файл сервиса systemd, который будет запускать программу `update_routes.py`
```bash
sudo nano /etc/systemd/system/update-routes.service
```
[Текст файла сервиса](update-routes.service).  
Перечитать конфигурацию systemd:
```bash
sudo systemctl daemon-reload
```
Пробуем запустить сервис:
```bash
sudo systemctl start update-routes.service
```
Смотрим статус:
```bash
systemctl status update-routes.service
```
Создадим файл таймера systemd, который будет запускать update-routes.service
каждые 5 минут
```bash
sudo nano /etc/systemd/system/update-routes.timer
```
[Текст файла таймера](update-routes.timer).
Перечитать конфигурацию systemd:
```bash
sudo systemctl daemon-reload
```
Включить и запустить таймер:
```bash
sudo systemctl enable update-routes.timer
sudo systemctl start update-routes.timer
```
Проверить статус таймера:
```bash
systemctl list-timers
```
3. Установка Wireguard на сервере VPN
```bash
sudo apt install wireguard
```
Создайте приватный и публичный ключи для сервера:
```bash
sudo -i
umask 077
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
```
Создайте конфигурационный файл для интерфейса wg0:
```bash
sudo nano /etc/wireguard/wg0.conf
```
[Содержимое файла.](wg0.conf)  
Замените <ваш_приватный_ключ> на содержимое файла `/etc/wireguard/privatekey`  
Убедитесь, что файл конфигурации и ключи имеют правильные права доступа:
```bash
sudo chmod 600 /etc/wireguard/{privatekey,wg0.conf}
```
Включение IP-форвардинга. 
```bash
sudo nano /etc/sysctl.conf
```
Найдите и раскомментируйте строку:
```bash
net.ipv4.ip_forward=1
```
Примените изменения:
```bash
sudo sysctl -p
```
Включите интерфейс wg0 в автозагрузку при старте системы и запустите его:
```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```
4. Настройка Mikrotik RB450 RouterOS 7.8
Настройте интерфейс ether1 для получения параметров по DHCP:
```
/interface ethernet
set ether1 name=ether1
/ip dhcp-client
add interface=ether1
```
Создайте мост bridge1 и добавьте в него интерфейсы ether2-ether5:
```
/interface bridge
add name=bridge1
/interface bridge port
add bridge=bridge1 interface=ether2
add bridge=bridge1 interface=ether3
add bridge=bridge1 interface=ether4
add bridge=bridge1 interface=ether5
```
Настройте DHCP-сервер для выдачи адресов клиентам в сети bridge1. Например, пул адресов 192.168.88.0/24:
```
/ip pool
add name=dhcp_pool ranges=192.168.88.100-192.168.88.200
/ip dhcp-server
add interface=bridge1 address-pool=dhcp_pool disabled=no
/ip address
add address=192.168.88.1/24 interface=bridge1
/ip dhcp-server network
add address=192.168.88.0/24 gateway=192.168.88.1 dns-server=192.168.88.1
```
Включите маскарадинг для трафика, исходящего через ether1:
```
/ip firewall nat
add chain=srcnat out-interface=ether1 action=masquerade
```
Включите DNS-сервер и настройте его для кэширования:
```
/ip dns
set allow-remote-requests=yes servers=77.88.8.8,77.88.8.1
```
На всякий случай сохранить конфигурацию:
```
/system backup save
```