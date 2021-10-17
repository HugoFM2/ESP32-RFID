
from machine import freq, Pin
from os import uname
from lib.mfrc522 import MFRC522
import json
# import network

from network import WLAN, AUTH_OPEN,AP_IF

from buzzer import Buzzer

config_json = json.load(open('config.json'))
buzzer = Buzzer(5,config_json['enableBuzzer'])

from RFID import RFID

# Definicao de Funcoes
def getMAC():
	from ubinascii import hexlify
	mac = hexlify(WLAN().config('mac'),':').decode()
	return mac

def EscreverJSON(file,json_var):
	print("Escrevendo no arquivo")
	with open(file, 'w') as f:
		json.dump(json_var, f)





#Definicao da placa
board = uname()[0]
if board == 'esp8266':
	freq(160000000) # set the CPU frequency to 160 MHz
	rfid = RFID(rdr=MFRC522(14, 13, 12, 15),pinoOutput_pin=Pin(0, Pin.OUT),buzzer=buzzer)
	pinoConfiguracao = Pin(4,Pin.IN,Pin.PULL_UP)

elif board == 'esp32':
	freq(240000000)
	# sck = Pin(18, Pin.OUT)
	rdr = MFRC522(18, 23, 19, 2, 5)
	pinoConfiguracao = Pin(22,Pin.IN,Pin.PULL_UP)