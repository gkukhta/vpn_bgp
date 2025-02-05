# Минимальная версия CMake
cmake_minimum_required(VERSION 3.10)

# Название проекта
project(DNSResolver)

# Установка стандартной версии C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Добавление исполняемого файла
add_executable(dns_resolver dns_resolver.cpp)

# Связывание библиотеки resolv
target_link_libraries(dns_resolver resolv)

# Установка исполняемого файла в /usr/local/bin
install(TARGETS dns_resolver DESTINATION bin)