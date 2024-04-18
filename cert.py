import ssl
import socket
import os
import datetime
import openpyxl

def getSSLInfo(hostname, sheet):
  date_fmt = r'%d/%m/%Y %H:%M:%S'
  ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
  ctx = ssl.create_default_context()
  try:
    with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
      s.settimeout(3.0)
      s.connect((hostname, 443))
      cert = s.getpeercert()
      hoje = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
      inicio = datetime.datetime.strptime(cert['notBefore'], ssl_date_fmt)
      fim = datetime.datetime.strptime(cert['notAfter'], ssl_date_fmt)
      expira = abs((fim - hoje).days)
      print("{};{};{};{}".format(hostname, inicio.strftime(date_fmt), fim.strftime(date_fmt), expira))
      sheet.append([hostname, inicio.strftime(date_fmt), fim.strftime(date_fmt), expira])
  except Exception as error:
    errnum = error.args[0]
    if errnum != -5:
      print("{};{};{};{}".format(hostname, 'ERRO', "ERRO", error))
      sheet.append([hostname, 'ERRO', 'ERRO', str(error)])
    pass

def getFiles(PATH):
  try:
    ROOTFILES = [f for f in os.listdir(PATH) if os.path.isfile(PATH+f)] 
    for obj in ROOTFILES:
      with open(os.path.join(PATH, obj)) as file:
        book = openpyxl.open('modelo.xlsx')
        sheet_hosts = book['Hosts']
        LINES = [lin for lin in file.readlines()]
        for line in LINES:
          hostname = line.strip()
          getSSLInfo(hostname, sheet_hosts)
        book.save('certificados-' + obj + '.xlsx')
  except Exception as error: 
    print("Não foi possível abrir arquivos! {}".format(error))
    pass

getFiles('hosts/')


### cat lista | rev | sort | uniq | rev

#### openssl s_client -connect dominio:443 -showcerts </dev/null | openssl x509 -outform pem > dominio.pem
#### openssl x509 -in dominio.pem -noout -text