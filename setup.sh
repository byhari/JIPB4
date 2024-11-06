#!/bin/bash

# Install unixODBC
sudo apt-get update
sudo apt-get install -y unixodbc unixodbc-dev

# Download and install Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip
unzip instantclient-basic-linux.x64-19.8.0.0.0dbru.zip -d /opt/oracle
export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_8:$LD_LIBRARY_PATH

# Configure ODBC
echo "[OracleODBC-19.8]
Description=Oracle ODBC driver for Instant Client 19.8
Driver=/opt/oracle/instantclient_19_8/libsqora.so.19.1
" | sudo tee -a /etc/odbcinst.ini

echo "[ODBC Data Sources]
OracleODBC-19.8=Oracle ODBC driver for Instant Client 19.8
" | sudo tee -a /etc/odbc.ini

echo "[OracleODBC-19.8]
Driver=OracleODBC-19.8
DSN=OracleODBC-19.8
ServerName=172.25.1.83:1521
UserName=fasdollar
Password=fasdollar
" | sudo tee -a /etc/odbc.ini
