# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import socket, sqlite3

mqtt_broker_ip = '10.23.192.193'
mqtt_broker_port = 1883

def on_connect(client, userdata, flags, rc):
    client.subscribe("TERM/#")

def on_message(client, userdata, msg):
    global my_ip
    commList = str(msg.payload).split('/')
    if commList[0] != my_ip:
        return()
    conn = sqlite3.connect('ft.db')
    req = conn.cursor()
    if commList[1] == 'RESETDB':
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_terminal_locked'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_terminal_hacked'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_power_all'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_lock_open'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_level_down'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='do_lock_open'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='do_level_down'")
        req.execute("UPDATE params SET value = 8 WHERE name='difficulty'")
        req.execute("UPDATE params SET value = 4 WHERE name='attempts'")
        req.execute("UPDATE params SET value = 10 WHERE name='count'")
    elif commList[1] == 'POWER':
        req.execute("UPDATE params SET value = ? WHERE name='is_power_all'", [commList[2]])
    elif commList[1] == 'LOCK':
        req.execute("UPDATE params SET value = ? WHERE name='is_terminal_locked'", [commList[2]])
    elif commList[1] == 'HACK':
        req.execute("UPDATE params SET value = ? WHERE name='is_terminal_hacked'", [commList[2]])
    elif commList[1] == 'ISOPEN':
        req.execute("UPDATE params SET value = ? WHERE name='is_lock_open'", [commList[2]])
    elif commList[1] == 'DOOPEN':
        req.execute("UPDATE params SET value = ? WHERE name='do_lock_open'", [commList[2]])
    elif commList[1] == 'ISLEVEL':
        req.execute("UPDATE params SET value = ? WHERE name='is_level_down'", [commList[2]])
    elif commList[1] == 'DOLEVEL':
        req.execute("UPDATE params SET value = ? WHERE name='do_level_down'", [commList[2]])
    elif commList[1] == 'ATTEMPTS':
        req.execute("UPDATE params SET value = ? WHERE name='attempts'", [commList[2]])
    elif commList[1] == 'DIFFICULTY':
        req.execute("UPDATE params SET value = ? WHERE name='difficulty'", [commList[2]])
    elif commList[1] == 'WORDSNUM':
        req.execute("UPDATE params SET value = ? WHERE name='count'", [commList[2]])
    elif commList[1] == 'MENULIST':
        req.execute("UPDATE params SET value = ? WHERE name='menu'", [commList[2]])
    elif commList[1] == 'MAILHEAD':
        req.execute("UPDATE params SET value = ? WHERE name='letter_head'", [commList[2]])
    elif commList[1] == 'MAILBODY':
        req.execute("UPDATE params SET value = ? WHERE name='letter'", [commList[2].decode('utf-8','ignore')])
    conn.commit()
    conn.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker_ip, mqtt_broker_port, 5)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((mqtt_broker_ip,mqtt_broker_port))
client.publish("TERMASK",'IP=' + s.getsockname()[0])
my_ip = s.getsockname()[0]
s.close()
client.loop_forever()