from time import sleep_ms
from machine import Pin, SPI,freq
from lib.mfrc522 import MFRC522
import uasyncio


p2 = Pin(2, Pin.OUT)

freq(240000000)

class STATUSRFID():
    DETECTADO = 0
    NAODETECTADO = 1
    

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
spi = SPI(baudrate=80000000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

sda = Pin(5, Pin.OUT)
cartoesAprovados = ["8A:A9:11:D9","88:04:A6:A0"]
uid = ""
lastUID = "XX:XX:XX:XX"

async def do_read():
    global lastUID
    global cartoesAprovados
    statusLeitor = None
    previousLeitor = None

    while True:
        rdr = MFRC522(spi, sda)
        uid = ""
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                uid = ("%02x:%02x:%02x:%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])).upper()
                statusLeitor = STATUSRFID.DETECTADO
                # await uasyncio.sleep(0.1)
        else:
            statusLeitor = STATUSRFID.NAODETECTADO

        if previousLeitor != statusLeitor:
            previousLeitor = statusLeitor
            if(statusLeitor == STATUSRFID.DETECTADO):
                print("CARTAO LIDO:",uid)
                lastUID = uid
                if uid in cartoesAprovados:
                    print("CARTAO CORRETO")
                    p2.on()
                else:
                    p2.off()
                    print("CARTAO INVALIDO")
            else:
                p2.off()
                print("Cartao Removido")
        print("Terminou while cartao")
        await uasyncio.sleep(0.5)
                



#Criando Rede
import network
# ssid = 'MicroPython-AP'
# password = '123456789'

# ap = network.WLAN(network.AP_IF)
# ap.active(True)
# ap.config(essid=ssid, password=password)


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Wesley ll', 'casanova@2021')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


do_connect()


# PArte NanoWEB
from lib.nanoweb import HttpError, Nanoweb, send_file
import uasyncio
naw = Nanoweb()

async def indexhtml(request):
    dicionario = {'cartoes': cartoesAprovados,'uid':lastUID}
    print("Pagina status carregando!")
    """API status endpoint"""
    # await send_file(request,"status.html")
    data = ""
    with open("status.html", "r") as f:
        for l in f:
            data += (l.format(**dicionario))
        #     await request.write(l.format(**context))
    await request.write(data)


async def DeletarCartaoHTML(request):
    print("Carregando pagina DeletarCartao")
    if request.method == "GET":
        argumentos = request.url.split('?')[-1].split('&')
        dicio = {}
        for argumento in argumentos:
            aux = argumento.split('=')
            dicio[aux[0]] = aux[1]
        cartoesAprovados.pop(int(dicio['i']))
        await indexhtml(request)

async def AdicionarCartaoHTML(request):
    print("Carregando pagina AdicionarCartao")
    if request.method == "GET":
        argumentos = request.url.split('?')[-1].split('&')
        dicio = {}
        for argumento in argumentos:
            aux = argumento.split('=')
            dicio[aux[0]] = aux[1]
        cartoesAprovados.append(dicio['addCartao'])
        # await indexhtml(request)  
        redirect = '<meta http-equiv="refresh" content="tempo em segundos; URL=\'/\'"/>'
        await request.write("HTTP/1.1 200 OK\r\n")
        await request.write(redirect)
# Declare route from a dict

naw.routes = {
    '/'   : indexhtml,
    '/removerCartao*' : DeletarCartaoHTML,
    '/adicionarCartao*' : AdicionarCartaoHTML,
}


# uasyncio.create_task( do_read() )

# loop = uasyncio.get_event_loop()
# loop.create_task(naw.run())
def updateRoutes():
    naw.routes = {
        '/status.html': {'cartoes': cartoesAprovados,'uid':lastUID}
    }

async def main():
    uasyncio.create_task( naw.run())
    uasyncio.create_task( do_read() )
    while True:
        print("passou")

        await uasyncio.sleep(5)

uasyncio.run(main())
# loop.run_forever()