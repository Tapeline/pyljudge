# pyljudge

```
sudo apt install mysql-server
sudo mysql_secure_installation
```

```
create user 'mainserver'@'localhost' identified by 'mainserver';
create user 'judgeserver'@'localhost' identified by 'judgeserver';
create database `judgeserverdb`;
grant all on `judgeserverdb` . * to 'mainserver'@'localhost';
grant all on `judgeserverdb` . * to 'judgeserver'@'localhost';
flush privileges;
```

```
sudo apt-get install python3 python3-pip
```

```
cd mainserver
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../judgeserver
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```
cd mainserver
./run.sh

cd ../judgeserver
./run.sh
```
