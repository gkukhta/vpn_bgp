# Настройка анонса сетей по BGP с сервера Wireguard VPN
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



