UPDATE mysql.user SET Password=PASSWORD('#$QTL#=^$a623k') WHERE User='root';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';
CREATE DATABASE django;
CREATE USER 'onramp'@'%' IDENTIFIED BY 'OnRamp_16';
GRANT ALL PRIVILEGES ON django.* TO 'onramp'@'%';
FLUSH PRIVILEGES;

