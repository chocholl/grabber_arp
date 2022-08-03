Для запуска необходимо выполнить следующие шаги:

1) Внести ip адрес и модель опрашиваемого оборудования в файл ip-list.txt

bash-3.00$ more ./ip-list.txt
ip;model;vendor;name
10.231.0.99;mx480;juniper;66-NTGL-AGG010-PEAGG-1
10.231.0.102;mx480;juniper;66-EKTB-BB01-BPE-3

2) Перейти в рабочую директорию и запустить оболочку
$ bash
bash-3.00$ cd /export/home/netcool/aandandr/analyzer/arp
bash-3.00$ python ./arp_get.py 
{'ip': '10.231.0.102', 'model': 'mx960', 'vendor': 'juniper'}
arp_list_len=42210
bash-3.00$

После отработки каждого запуска сборщик оставляет два типа файлов
В директории output_raw – сырой файл с выводом команды получения arp записей
В директории output разобранный файл csv с полями ip;int;mac;exp;vrf
Имя файла дополняется текущим часом и минутой.

bash-3.00$ more ./aandandr/analyzer/arp/output/arp_15_58.csv 
ip;int;mac;exp;vrf
5.140.168.6;ae1.344;cc:2d:e0:b5:a2:82;1400;INTUSI
5.140.168.10;ae4.2448;4c:02:89:0f:28:dc;1121;INTUSI
5.140.168.14;ae3.4812;4c:02:89:0d:e9:f3;937;INTUSI
5.140.168.18;ae3.4116;00:08:dc:00:00:2a;348;INTUSI
5.140.168.22;ae3.4115;00:08:dc:00:00:29;117;INTUSI

