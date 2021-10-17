from definicoes import EscreverJSON,rfid, config_json
from lib.nanoweb import HttpError, Nanoweb, send_file



class WebServerClass():
    def __init__(self):
        self.naw = Nanoweb()

        self.naw.routes = {
            '/'   : self.indexhtml,
            '/removerCartao*' : self.DeletarCartaoHTML,
            '/adicionarCartao*' : self.AdicionarCartaoHTML,
        }

    async def indexhtml(self,request):
        
        dicionario = {'cartoes': config_json['CartoesAprovados'],'uid':rfid.getLastUID()}
        print("Pagina status carregando!")
        print(rfid.getLastUID())
        """API status endpoint"""
        # await send_file(request,"status.html")
        data = ""
        with open("status.html", "r") as f:
            for l in f:
                data += (l.format(**dicionario))
            #     await request.write(l.format(**context))
            print("Pagina status enviando dados!")
        await request.write(data)


    async def DeletarCartaoHTML(self,request):
        print("Carregando pagina DeletarCartao")
        if request.method == "GET":
            argumentos = request.url.split('?')[-1].split('&')
            dicio = {}
            for argumento in argumentos:
                aux = argumento.split('=')
                dicio[aux[0]] = aux[1]
            config_json['CartoesAprovados'].pop(int(dicio['i']))
            EscreverJSON('config.json',config_json)
            await self.RedirectPage(request)

    async def AdicionarCartaoHTML(self,request):
        print("Carregando pagina AdicionarCartao")
        if request.method == "GET":
            argumentos = request.url.split('?')[-1].split('&')
            dicio = {}
            for argumento in argumentos:
                aux = argumento.split('=')
                dicio[aux[0]] = aux[1]
            config_json['CartoesAprovados'].append(dicio['addCartao'].replace("%3A",":"))
            EscreverJSON('config.json',config_json)
            await self.RedirectPage(request)


    async def RedirectPage(self,request):
        data = ""
        with open("redirect.html", "r") as f:
            for l in f:
                data += l
        await request.write(data)




