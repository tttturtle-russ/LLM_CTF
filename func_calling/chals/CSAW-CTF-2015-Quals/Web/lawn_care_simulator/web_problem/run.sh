#!/bin/bash
service mysql start
echo 1
mysql -pAdmin2015 < /tmp/create_tables.sql
echo 1
rm /tmp/create_tables.sql
echo 1

cd /var/www/example.com/public_html
git init
git add index.html jobs.html js/*.js sign_up.php premium.php validate_pass.php ___HINT___
git config user.email "john@lawncaresimulator2015thegame.com"
git config user.name "John G."
git commit -m "I think I'll just put mah source code riiiiighhhht here. Perfectly safe place for some source code."
git update-server-info

/usr/sbin/apache2ctl -D FOREGROUND
