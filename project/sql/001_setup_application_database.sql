CREATE DATABASE IF NOT EXISTS django CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER IF NOT EXISTS 'django'@'%' IDENTIFIED BY 'Password_django';
GRANT ALL PRIVILEGES ON django.* TO 'django'@'%';
GRANT ALL PRIVILEGES ON django_test.* TO 'django'@'%';
