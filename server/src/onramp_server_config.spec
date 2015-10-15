[server]
socket_host = string()
socket_port = integer(0, 65535)
url_docroot = string()

[logging]
log_level = option('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
log_file = string()
