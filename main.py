from time import sleep_ms
from machine import Pin, SPI,freq
from lib.mfrc522 import MFRC522
import uasyncio
import json
import gc

p2 = Pin(2, Pin.OUT)

# ESP8266
freq(160000000) # set the CPU frequency to 160 MHz

# #ESP32
# freq(240000000)

class STATUSRFID():
	DETECTADO = 0
	NAODETECTADO = 1
	
#ESP32
# sck = Pin(18, Pin.OUT)
# rdr = MFRC522(18, 23, 19, 2, 5)
# mosi = Pin(23, Pin.OUT)
# miso = Pin(19, Pin.OUT)
# spi = SPI(2,baudrate=8000000, polarity=0, phase=0, bits=8, firstbit=0)
# sda = Pin(5, Pin.OUT)


#ESP8266
sck = Pin(14, Pin.OUT)
rdr = MFRC522(14, 13, 12, 15)
# mosi = Pin(13, Pin.OUT)
# miso = Pin(12, Pin.OUT)
# spi = SPI(baudrate=80000000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
# sda = Pin(15, Pin.OUT)

# rdr = MFRC522(spi, sda)

config_json = json.load(open('config.json'))
# uid = ""
lastUID = "XX:XX:XX:XX"

async def do_read():
	global lastUID
	# global uid
#     global cartoesAprovados
#     statusLeitor = None
#     previousLeitor = None

	errorcounter = 0
	statusLeitor = None
	previousLeitor = None
	while True:
		#STAT = 0 OK
		#STAT = 2 ERR
		(stat, tag_type) = rdr.request(rdr.REQIDL)  # check if antenna idle
		# print("STATUS1: {}".format(stat))
		if stat == rdr.OK:
			(stat, raw_uid) = rdr.anticoll()
			# print("STATUS2: {}".format(stat))
			if(len(raw_uid) > 4): # Garante que pegou um uid vaildo
				errorcounter = 0
				
				uid = ("%02x:%02x:%02x:%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])).upper()
				# if(stat == rdr.OK):
				statusLeitor = STATUSRFID.DETECTADO
					# print("cartao detectado: {}".format(uid))
					# if uid in config_json['CartoesAprovados']:
					# 	p2.on()
			else:
				print("LEITURA ERRADA")
		else:
			errorcounter += 1
			if(errorcounter > 1):
				# print("CARTAO REMOVIDO")
				statusLeitor = STATUSRFID.NAODETECTADO
				if(errorcounter > 100): # Resetando o errorcounter, ainda com erro
					errorcounter = 2

		if previousLeitor != statusLeitor:
			previousLeitor = statusLeitor
			if(statusLeitor == STATUSRFID.DETECTADO):
				print("CARTAO LIDO:",uid)
				lastUID = uid
				if uid in config_json['CartoesAprovados']:
					print("CARTAO CORRETO")
					p2.on()
				else:
					p2.off()
					print("CARTAO INVALIDO")
			elif (statusLeitor == STATUSRFID.NAODETECTADO):
				p2.off()
				print("Cartao Removido")
		# sleep_ms(100)
		await uasyncio.sleep(0.1)


			


#PARTE JSON
def EscreverJSON(file,json_var):
	print("Escrevendo no arquivo")
	with open(file, 'w') as f:
		json.dump(json_var, f)

#Criando Rede

# ssid = 'MicroPython-AP'
# password = '123456789'
#ESP32
# P5 = Pin(22,Pin.IN,Pin.PULL_UP)
#ESP8266
P5 = Pin(5,Pin.IN,Pin.PULL_UP)
import network
ap = network.WLAN(network.AP_IF)
ap.active(False)
print("Valor P5:{}".format(P5.value()))
if (P5.value() == 0): # Caso o pino esteja ligado
	print("Habilitando rede e access-point")
	ap.active(True)         # activate the interface
	print("SSID:{}".format("RFID" + config_json['Name']))
	ap.config( essid=("RFID" + config_json['Name']),authmode=network.AUTH_OPEN) # set the ESSID of the access point


	# PArte NanoWEB
	from lib.nanoweb import HttpError, Nanoweb, send_file
	import uasyncio
	naw = Nanoweb()

	async def indexhtml(request):
		dicionario = {'cartoes': config_json['CartoesAprovados'],'uid':lastUID}
		print("Pagina status carregando!")
		"""API status endpoint"""
		# await send_file(request,"status.html")
		data = ""
		with open("status.html", "r") as f:
			for l in f:
				data += (l.format(**dicionario))
			#     await request.write(l.format(**context))
			print("Pagina status enviando dados!")
		await request.write(data)


	async def DeletarCartaoHTML(request):
		print("Carregando pagina DeletarCartao")
		if request.method == "GET":
			argumentos = request.url.split('?')[-1].split('&')
			dicio = {}
			for argumento in argumentos:
				aux = argumento.split('=')
				dicio[aux[0]] = aux[1]
			config_json['CartoesAprovados'].pop(int(dicio['i']))
			EscreverJSON('config.json',config_json)
			await RedirectPage(request)

	async def AdicionarCartaoHTML(request):
		print("Carregando pagina AdicionarCartao")
		if request.method == "GET":
			argumentos = request.url.split('?')[-1].split('&')
			dicio = {}
			for argumento in argumentos:
				aux = argumento.split('=')
				dicio[aux[0]] = aux[1]
			config_json['CartoesAprovados'].append(dicio['addCartao'].replace("%3A",":"))
			EscreverJSON('config.json',config_json)
			await RedirectPage(request)
	# Declare route from a dict

	async def RedirectPage(request):
		data = ""
		with open("redirect.html", "r") as f:
			for l in f:
				data += l
		await request.write(data)

	naw.routes = {
		'/'   : indexhtml,
		'/removerCartao*' : DeletarCartaoHTML,
		'/adicionarCartao*' : AdicionarCartaoHTML,
	}







	# else:
	# 	(stat, raw_uid) = rdr.anticoll()
	# 	if(stat == rdr.ERR):
	# 		print("cartao removido")
	# 		p2.off()
	# 	else:
	# 		print("cartao detectado: {}".format(uid))
	# 		if uid in config_json['CartoesAprovados']:
	# 			p2.on()

			
# print("Terminou while")

async def main():
	global i
	gc.enable()
	if (P5.value() == 0): # Caso o pino esteja ligado
	    uasyncio.create_task( naw.run())
	# else:	
	uasyncio.create_task( do_read() )
	
	while True:
		# (stat, tag_type) = rdr.request(rdr.REQIDL)  # check if antenna idle
		# if stat == rdr.OK:
		# 	(stat, raw_uid) = rdr.anticoll()
		# 	if(stat == rdr.OK):
		# 		print("cartao detectado")
		# 	else:
		# 		print("cartao removido")
				

		# i +=1
		# print("STATUS {}:{}".format(i,stat))
		# do_read()
		# await_removal()
		# write_once()
		# await_removal()  
		print("Memoria Livre: {}".format(gc.mem_free()))
		# # print("passou")
		# # print("Valor P5:{}".format(P5.value()))
		await uasyncio.sleep(5)

uasyncio.run(main())
# # loop.run_forever()