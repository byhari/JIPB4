#!/bin/bash

echo "Updating package list..."
apt-get update

echo "Installing required packages..."
apt-get install -y unixodbc unixodbc-dev wget unzip

echo "Downloading Oracle Instant Client..."
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip

echo "Unzipping Oracle Instant Client..."
unzip instantclient-basic-linux.x64-19.8.0.0.0dbru.zip -d /opt/oracle

echo "Setting environment variables..."
export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_8:$LD_LIBRARY_PATH
export PATH=/opt/oracle/instantclient_19_8:$PATH

echo "Configuring ODBC..."
echo "[OracleODBC-19.8]
Description=Oracle ODBC driver for Instant Client 19.8
Driver=/opt/oracle/instantclient_19_8/libsqora.so.19.1
" | tee -a /etc/odbcinst.ini

echo "[ODBC Data Sources]
OracleODBC-19.8=Oracle ODBC driver for Instant Client 19.8
" | tee -a /etc/odbc.ini

echo "[OracleODBC-19.8]
Driver=OracleODBC-19.8
DSN=OracleODBC-19.8
ServerName=empdb01.emp-one.com
UserName=fasdollar
Password=fasdollar
" | tee -a /etc/odbc.ini

echo "Setup script completed."
