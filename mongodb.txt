
*********************************************
MONGODB

configuration file
/usr/local/etc/mongod.conf

log directory
/usr/local/var/log/mongodb

data directory
/usr/local/var/mongodb

brew services start mongodb-community@4.4

brew services stop mongodb-community@4.4

mongod --config /usr/local/etc/mongod.conf --fork


To stop a mongod running as a background process, connect to the mongod from the mongo shell, and issue the shutdown command as needed.

brew services list
ps aux | grep -v grep | grep mongod


*********************************************

sudo pkill php-fpm