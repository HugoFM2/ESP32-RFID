import uasyncio
from definicoes import config_json
from machine import Signal

class RFID():
	DETECTADO = 0
	NAODETECTADO = 1
	def __init__(self,rdr,pinoOutput_pin,buzzer):
		self.rdr = rdr
		self.buzzer = buzzer
		self.pinoOutput = Signal(pinoOutput_pin,invert=True) 
		self.pinoOutput.value(0)
		self._lastUID = "XX:XX:XX:XX"

	def setLastUID(self,valor):
		self._lastUID = valor

	def getLastUID(self):
		return self._lastUID

	async def do_read(self):
		errorcounter = 0
		statusLeitor = None
		previousLeitor = None
		while True:
			#STAT = 0 OK
			#STAT = 2 ERR
			(stat, tag_type) = self.rdr.request(self.rdr.REQIDL)  # check if antenna idle
			if stat == self.rdr.OK:
				(stat, raw_uid) = self.rdr.anticoll()
				if(len(raw_uid) > 4): # Garante que pegou um uid vaildo
					errorcounter = 0
					uid = ("%02x:%02x:%02x:%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])).upper()
					self.setLastUID(uid)
					statusLeitor = self.DETECTADO

				else:
					print("LEITURA ERRADA")
			else:
				errorcounter += 1
				if(errorcounter > 1):
					statusLeitor = self.NAODETECTADO
					if(errorcounter > 100): # Resetando o errorcounter, ainda com erro
						errorcounter = 2

			if previousLeitor != statusLeitor:
				previousLeitor = statusLeitor
				if(statusLeitor == self.DETECTADO):
					print("CARTAO LIDO:",uid)
					
					
					if uid in config_json['CartoesAprovados']:
						print("CARTAO CORRETO")
						uasyncio.create_task(self.buzzer.somCerto())
						self.pinoOutput.on()
					else:
						self.pinoOutput.off()
						uasyncio.create_task(self.buzzer.somErrado())
						print("CARTAO INVALIDO")
				elif (statusLeitor == self.NAODETECTADO):
					self.pinoOutput.off()
					print("Cartao Removido")
			await uasyncio.sleep(0.1)
