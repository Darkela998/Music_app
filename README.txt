First of all, you need to import databse of app. 
One way is to in Microsoft SQL server managment studio, right click on Databases-> Import Data-tier Application-> Import from local disk -> Choose file Music_player.bacpac and name database Music_player. You might need to change variable serverName in server.py file. In Microsoft SQL server managment studio, run query "SELECT @@SERVERNAME" to see your server name.

After all configuration of database, you need to start server.py file before music_player.py

Sorry for poor GUI, i hope you will enjoy :)