#include <iostream>
#include <cstring>
#include <resolv.h>
#include <arpa/inet.h>

int main(int argc, char* argv[]) {
    // Проверяем количество аргументов командной строки
    if (argc != 3) {
        std::cerr << "Использование: " << argv[0] << " <DNS_SERVER_IP> <HOSTNAME>" << std::endl;
        return 1;
    }

    const char* dns_server = argv[1]; // Адрес DNS-сервера
    const char* hostname = argv[2];   // Доменное имя для разрешения

    // Инициализация resolver'а
    res_init();

    // Устанавливаем адрес DNS-сервера
    _res.nscount = 1; // Количество DNS-серверов
    inet_aton(dns_server, &_res.nsaddr_list[0].sin_addr);

    // Выполняем DNS-запрос
    unsigned char response[NS_PACKETSZ];
    int response_len = res_query(hostname, C_IN, T_A, response, sizeof(response));

    if (response_len < 0) {
        // Ошибка при разрешении DNS
        //std::cerr << "Не удалось разрешить домен: " << hostname << std::endl;
        return 1;
    }

    // Если разрешение прошло успешно, выводим сообщение
    //std::cout << "Домен успешно разрешен: " << hostname << std::endl;

    return 0;
}