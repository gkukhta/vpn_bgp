$TTL    300
@       IN      SOA     ns1.example.com. admin.example.com. (
                          2025020301         ; Serial
                             300             ; Refresh
                             300             ; Retry
                         2419200             ; Expire
                          604800 )           ; Negative Cache TTL
;
@       IN      NS      ns1.example.com.
@       IN      NS      ns2.example.com.
ns1     IN      A       192.168.88.5
ns2     IN      A       192.168.88.6
ns      IN      A       192.168.88.7
gw      IN      A       192.168.88.1