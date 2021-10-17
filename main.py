from network import WLAN, AUTH_OPEN,AP_IF
from definicoes import pinoConfiguracao,rfid,getMAC
import uasyncio
import gc

print() # Printar uma linha vazia para melhor visualizacao dos proximos prints


#Cria a rede AP dependendo co pino de configuracao
ap = WLAN(AP_IF)
ap.active(False)
print("Valor pinoConfiguracao:{}".format(pinoConfiguracao.value()))
webserver = None
if (pinoConfiguracao.value() == 0): # Caso o pino esteja ligado
	print("Habilitando rede e access-point")
	ap.active(True)         # activate the interface
	SSID = "RFID-" + ''.join(getMAC().upper().split(':')[-2:]) # a Rede é composta pela palavra RFID- mais os 4 ultimos algarismos MAC do dispositivo
	print("SSID:{}".format(SSID))
	ap.config( essid=SSID,authmode=AUTH_OPEN) # set the ESSID of the access point

	from webserver import WebServerClass
	webserver = WebServerClass()




async def main():
	gc.enable()
	uasyncio.create_task( rfid.do_read() )
	if (pinoConfiguracao.value() == 0): # Caso o pino esteja ligado
	    uasyncio.create_task( webserverClass.naw.run())
	
	while True:
		print("Memoria Livre: {}".format(gc.mem_free()))
		
		await uasyncio.sleep(5)

uasyncio.run(main())
# # loop.run_forever()