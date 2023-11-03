-- Use the mysql root user to create a database and application dba user/application user for it

create database if not exists db_damg7245team7;
use db_damg7245team7;

create user if not exists 'application_dba'@'%' identified by 'password';
grant all privileges on db_damg7245team7.* to 'application_dba'@'%';
flush privileges;

create user if not exists 'application_user'@'%' identified by 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON db_damg7245team7.* TO 'application_user'@'%';
flush privileges;