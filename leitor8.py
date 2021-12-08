#!/usr/bin/python3
from threading import Thread
import smbus
import urllib.request
import time
from datetime import date
from datetime import datetime
from Cadastros import Funcionario
from Cadastros import RegistroPonto
import mysql.connector as mysql
from mysql.connector import errorcode
import RPi.GPIO as GPIO
from time import sleep
import sys
from RPLCD import i2c
from RPLCD import CharLCD
from time import sleep
from socket import gethostbyname,create_connection
import os
import signal
import time
import sys
from pirc522 import RFID
from gpiozero import Buzzer
import re
import serial

#ser = serial.Serial('/dev/ttyAMA0', 115200)
ser = serial.Serial('/dev/ttyUSB0', 115200)
#ser = serial.Serial('/dev/ttyS0', 115200)



buzzer = Buzzer(17)



#variaveis e funcoes para manipular teclado

L1 = 5
L2 = 6
L3 = 13
L4 = 19

C1 = 12
C2 = 16
C3 = 20
C4 = 21


keypadPressed = -1
input = ""
conectado = False
entrada_global = ""

GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



def readSerial():
 while True:
  try:
   recebido_bytes = ser.readline()
   recebido_str = recebido_bytes.decode('utf-8')
   recebido_str = re.sub('[^0-9]', '', recebido_str)
   if not recebido_str:
    print("Vazio recebido")
   else:
    print(recebido_str)
    registrar_ponto(recebido_str)
    sleep(5)
  except Exception as e: 
   print("Excessao, Erro no recebimento dos dados via serial")
   print(e)
   



loop0 = Thread(target=readSerial, args=[])
loop0.start()


def readLine(line, characters, entrada):
 GPIO.output(line, GPIO.HIGH)
 if(GPIO.input(C1) == 1):
  if(characters[0] == "1"):
   print("1 pressionado")
   entrada += "1"
   informar_linha_4(entrada)
  elif (characters[0] == "4"):
   print("4 pressionado")
   entrada += "4"
   informar_linha_4(entrada)
  elif (characters[0] == "7"):
   print("7 pressionado")
   entrada += "7"
   informar_linha_4(entrada)
  else:
   print("* pressionado")
 if(GPIO.input(C2) == 1):
  if(characters[1] == "2"):
   print("2 pressionado")
   entrada += "2"
   informar_linha_4(entrada)
  elif (characters[1] == "5"):
   print("5 pressionado")
   entrada += "5"
   informar_linha_4(entrada)
  elif (characters[1] == "8"):
   print("8 pressionado")
   entrada += "8"
   informar_linha_4(entrada)
  else:
   print("0 pressionado")
   entrada += "0"
   informar_linha_4(entrada)
 if(GPIO.input(C3) == 1):
  if(characters[2] == "3"):
   print("3 pressionado")
   entrada +=  "3"
   informar_linha_4(entrada)
  elif (characters[2] == "6"):
   print("6 pressionado")
   entrada += "6"
   informar_linha_4(entrada)
  elif (characters[2] == "9"):
   print("9 pressionado")
   entrada += "9"
   informar_linha_4(entrada)
  else:
   print("# pressionado")

 if(GPIO.input(C4) == 1):
  if(characters[3] == "A"):
   print("A pressionado")
   #os.system("nohup python3 /home/pi/leitor_rfid/leitor3.py &")
   restart_program()
  elif (characters[3] == "B"):
   print("B pressionado")
   restart_wifi()
   #os.system("pkill -9 -f /home/pi/leitor_rfid/leitor3.py")
  elif (characters[3] == "C"):
   print("C pressionado")
  else:
   print("D pressionado")
   os.system("reboot now")
 GPIO.output(line, GPIO.LOW)
 return entrada 


class LerTeclado(Thread):

                def __init__ (self):
                      Thread.__init__(self)
                      

               
                def run(self):
                  entrada = ""
                  try:
                   while True:
                    entrada = readLine(L1, ["1","2","3","A"], entrada)
                    entrada = readLine(L2, ["4","5","6","B"], entrada)
                    entrada = readLine(L3, ["7","8","9","C"], entrada)
                    entrada = readLine(L4, ["*","0","#","D"], entrada)
                    if len(entrada) == 4:
                     procurar_cpf(entrada)
                     entrada = ""
                    time.sleep(0.3)
                    
                  except KeyboardInterrupt:
                     print("\nApplication stopped!")





# Set-up some constants to initialise the LCD
lcdmode = 'i2c'
cols = 20
rows = 4
charmap = 'A00'
i2c_expander = 'PCF8574'
address = 0x3f # If you don't know what yours is, do i2cdetect -y 1
port = 1 # 0 on an older Pi

lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)
lcd.backlight_enabled = True


entrada_global = ""

def get_part_of_day(hour):
    return (
        "Bom Dia" if 5 <= hour <= 11
        else
        "Boa Tarde" if 12 <= hour <= 17
        else
        "Boa Noite" if 18 <= hour <= 22
        else
        "Boa Madrugada"
    )



def getData():
 return date.today().strftime('%d/%m/%Y')

def getDataReduzida():
 return date.today().strftime('%d/%m/%y')

def getHora():
 return datetime.now().strftime('%H:%M')

def getExpressao():
 return get_part_of_day(datetime.now().hour)

def apitar(intervalo, serie):
 x = 0
 while x < serie:
  buzzer.on() 
  sleep(intervalo)
  buzzer.off()
  sleep(intervalo)
  x = x + 1

def apitarInserido():
 x = 0
 while x < 2:
  buzzer.on()
  sleep(0.1)
  buzzer.off()
  sleep(0.1)
  x = x + 1


def apitarErro():
 x = 0
 while x < 5:
  buzzer.on()
  sleep(0.05)
  buzzer.off()
  sleep(0.05)
  x = x + 1


def mostrarLogoHora():
    while True:
        lcd.cursor_pos = (0,0)
        lcd.write_string("LD Armazens")
        lcd.cursor_pos = (1,3)
        lcd.write_string("%s %s" %(getData(), getHora()))
        lcd.cursor_pos = (2,0)
        lcd.write_string("                    ")
        lcd.cursor_pos = (2,5)
        lcd.write_string(getExpressao()) 
        lcd.cursor_pos = (3,0)
        lcd.write_string("                    ")
        time.sleep(20)

def informar_linha_3(msg):
 lcd.cursor_pos = (2,0)
 lcd.write_string("                    ")
 lcd.cursor_pos = (2,0)
 lcd.write_string(msg)

def informar_linha_4(msg):
 lcd.cursor_pos = (3,0)
 lcd.write_string("                    ")
 lcd.cursor_pos = (3,0)
 lcd.write_string(msg)

query_insert = "insert into registro_ponto (id_colaborador, data, hora, movimentacao, motivo) values (%s, %s, %s, %s, %s)"
query_select_rp = "select * from registro_ponto where id_colaborador = %d ORDER BY id_registro_ponto DESC limit 1"
query_select_num_rp = "SELECT count(*) from registro_ponto rp where rp.id_colaborador = %d and rp.data = '%s'"


def restart_program():
    informar_linha_4("REINICIAR")
    sleep(1)
    python = sys.executable
    os.execl(python, python, * sys.argv)

def restart_wifi():
 informar_linha_4("WIFI RESTART")
 os.system("ifdown --force wlan0")
 sleep(10)
 os.system("ifup --force wlan0")
 

def connect(host="http://google.com"):
    try:
        urllib.request.urlopen(host) 
        return True
    except:
        return False

loop1 = Thread(target=mostrarLogoHora, args=[])
loop1.start()

#ip = "192.168.0.150"
#ip = "192.168.100.155"
ip = "127.0.0.1"

def connect_local():
 try:
  if os.system("ping -c 1 " + ip) is 0:
   conectado = True
   return True
  else:
    print("Erro ao se conectar no ip: " + ip)
    return False
 except Exception as e:
   print("Excessao, Erro ao se conectar no ip: " + ip)
   print(e)
   return False


run = True
rdr = RFID( bus = 0 , device = 0 , speed = 1000000 , pin_rst = 25 ,
            pin_ce = 1 , pin_irq = 24 , pin_mode  =  GPIO.BCM)

util = rdr.util()
util.debug = True

def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    sys.exit()


signal.signal(signal.SIGINT, end_read)



a = LerTeclado()
a.start()

def procurar_cpf(cpf):
 try:
     if connect_local() :
      db = mysql.connect(
           host = ip,
           user = "aislan",
           passwd = "1234",
           database = "bd_ldarmazens"
      )
      cursor = db.cursor()
      #verificar se este cartao esta cadastrado
      cursor.callproc('buscar_cpf', [cpf, ])
      for result in cursor.stored_results():
       resultado = result.fetchone()
       if resultado is not None:
          func = Funcionario(resultado[0], resultado[1],resultado[2])
          if func is not None and resultado[2] > 0:
           nome = "%s" %func.nome
           print(nome)
           informar_linha_3(nome)
           cursor.execute(query_select_rp %(func.id))
           ultimo_rp = cursor.fetchone()
           if ultimo_rp is not None:
            rp = RegistroPonto(ultimo_rp[0],ultimo_rp[1],ultimo_rp[2],ultimo_rp[3])
            print("Data Ultimo RP: %s " %rp.data, " Hora Ultimo RP: %s " %rp.hora)
           
            hora_ultimo_rp = datetime.strptime("%s %s" %(rp.data, rp.hora) ,'%d/%m/%Y %H:%M')
            dif = (datetime.strptime("%s %s" %(getData(), getHora()), '%d/%m/%Y %H:%M') - hora_ultimo_rp).total_seconds()
            i_dif = dif/60;  
            print("Diferenca de tempos: %d" %i_dif)
            if i_dif > 5:
             print("id fun %d, data: %s" %(func.id, getData()))
             cursor.execute(query_select_num_rp %(func.id, getData()))
             num_rp = cursor.fetchone()
             if num_rp is not None:
              i_num_rp = num_rp[0]
              print("Num rp: %d" %i_num_rp)
              i_num_rp = i_num_rp + 1
              values = (func.id, getData(), getHora(), i_num_rp, "Registro Automatico no Relogio")
              cursor.execute(query_insert, values)
              db.commit()
              print(cursor.rowcount, "Inserido")
              informar_linha_4("Ponto Inserido")
              apitarInserido()
             else:
              values = (func.id, getData(), getHora(), 1, "Registro Automatico no Relogio")
              cursor.execute(query_insert, values)
              db.commit()
              print(cursor.rowcount, "Inserido")
              informar_linha_4("Ponto Inserido")
              apitarInserido()
            else:
             print("Aguarde 5 minutos para poder registrar outro ponto")
             informar_linha_4("Aguarde 5 min")
             apitarErro() 
           else:
            print("Nenhum RP Encontrato")
            print("ID %d " %func.id)
            values = (func.id, getData(), getHora(), 1, "Registro Automatico no Relogio")
            cursor.execute(query_insert, values)
            db.commit()
            print(cursor.rowcount, "Inserido")
            apitarInserido()

          else:
           informar_linha_4(str_id)

       else:
           print("CPF Não Associado a nenhum Colaborador")
           informar_linha_4("Nao Cadastrado")
           apitarErro()
      sleep(2)
      db.close()

     else:
      print("Sem conexão com o servidor!")
      informar_linha_4("Sem Conexao")
 

    
 except KeyboardInterrupt:
    GPIO.cleanup()
    raise
 except Exception as e:
   print("Banco de Dados Não encontrado")
   apitarErro()
   informar_linha_4("BD DESCONECTADO")
   sleep(2)


def registrar_ponto(id):
 try:
     print("Registrar ponto chamado")
     print(id)
     if connect_local() :
      db = mysql.connect(
           host =  ip,
           user = "aislan",
           passwd = "1234",
           database = "bd_ldarmazens"
      )
      cursor = db.cursor()
      #verificar se este cartao esta cadastrado
      cursor.callproc('buscar_uid', [id, ])
      for result in cursor.stored_results():
       resultado = result.fetchone()
       if resultado is not None:
          func = Funcionario(resultado[0], resultado[1],resultado[2])
          if func is not None and resultado[2] > 0:
           nome = "%s" %func.nome
           #ser.write(("@%s \n" %(nome)).encode())
           print(nome)
           informar_linha_3(nome)
           cursor.execute(query_select_rp %(func.id))
           ultimo_rp = cursor.fetchone()
           if ultimo_rp is not None:
            rp = RegistroPonto(ultimo_rp[0],ultimo_rp[1],ultimo_rp[2],ultimo_rp[3])
            print("Data Ultimo RP: %s " %rp.data, " Hora Ultimo RP: %s " %rp.hora)
           
            hora_ultimo_rp = datetime.strptime("%s %s" %(rp.data, rp.hora) ,'%d/%m/%Y %H:%M')
            dif = (datetime.strptime("%s %s" %(getData(), getHora()), '%d/%m/%Y %H:%M') - hora_ultimo_rp).total_seconds()
            i_dif = dif/60;  
            print("Diferenca de tempos: %d" %i_dif)
            if i_dif > 5:
             print("id fun %d, data: %s" %(func.id, getData()))
             cursor.execute(query_select_num_rp %(func.id, getData()))
             num_rp = cursor.fetchone()
             if num_rp is not None:
              i_num_rp = num_rp[0]
              print("Num rp: %d" %i_num_rp)
              i_num_rp = i_num_rp + 1
              values = (func.id, getData(), getHora(), i_num_rp, "Registro Automatico no Relogio 2")
              cursor.execute(query_insert, values)
              db.commit()
              print(cursor.rowcount, "Inserido")
              informar_linha_4("Ponto Inserido")
              #ser.write(b"Ponto Inserido\n") 
              ser.write(("%s %s \n" %(nome, "Ponto Inserido") ).encode())
              apitarInserido()
              sleep(2)
             else:
              values = (func.id, getData(), getHora(), 1, "Registro Automatico no Relogio 2")
              cursor.execute(query_insert, values)
              db.commit()
              print(cursor.rowcount, "Inserido")
              informar_linha_4("Ponto Inserido")
              #ser.write(b"Ponto Inserido\n")
              ser.write(("%s %s \n" %(nome, "Ponto Inserido") ).encode())
              apitarInserido()
              sleep(2)
            else:
             print("Aguarde 5 minutos para poder registrar outro ponto")
             informar_linha_4("Aguarde 5 min")
             ser.write(("%s %s \n" %(nome, "Aguarde 5 min") ).encode())
             apitarErro()
             sleep(2)
           else:
            print("Nenhum RP Encontrato")
            print("ID %d " %func.id)
            values = (func.id, getData(), getHora(), 1, "Registro Automatico no Relogio 2")
            cursor.execute(query_insert, values)
            db.commit()
            print(cursor.rowcount, "Inserido")
            apitarInserido()
            sleep(2)

          
          else:
           informar_linha_4(str_id)
           ser.write(("%s \n" &(str_id) ).encode()) 
           sleep(2)

       else:
           print("Cartão Não Associado a nenhum Colaborador, UID: %s" %id)
           informar_linha_3(id)
           informar_linha_4("Nao Cadastrado")
           ser.write(b"Nao Cadastrado\n")
           apitarErro()
           sleep(2)
      sleep(2)
      db.close()

     else:
      print("Sem conexão com o servidor!")
      informar_linha_4("Sem Conexao")
      ser.write(b"Sem Conexao\n")
      apitarErro()
      sleep(2)

    
 except KeyboardInterrupt:
    GPIO.cleanup()
    raise
 except Exception as e:
   print(e)
   print("Banco de Dados Não encontrado")
   apitarErro()
   informar_linha_4("BD DESCONECTADO")
   ser.write(b"BD Desconectado\n")
   sleep(2)


while run:
 try:
     
    print("Aproxime o cartão do leitor")
    rdr.wait_for_tag()
    (error, data) = rdr.request()
    if not error:
      print("\nDetected: " + format(data, "02x"))
    (error, uid) = rdr.anticoll()
    if not error:
     id = str_id = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
     print(str_id)
     if connect_local() :
      db = mysql.connect(
           host =  ip,
           user = "aislan",
           passwd = "1234",
           database = "bd_ldarmazens"
      )
      cursor = db.cursor()
      #verificar se este cartao esta cadastrado
      cursor.callproc('buscar_uid', [id, ])
      for result in cursor.stored_results():
       resultado = result.fetchone()
       if resultado is not None:
          func = Funcionario(resultado[0], resultado[1],resultado[2])
          if func is not None and resultado[2] > 0:
           nome = "%s" %func.nome
           print(nome)
           informar_linha_3(nome)
           cursor.execute(query_select_rp %(func.id))
           ultimo_rp = cursor.fetchone()
           if ultimo_rp is not None:
            rp = RegistroPonto(ultimo_rp[0],ultimo_rp[1],ultimo_rp[2],ultimo_rp[3])
            print("Data Ultimo RP: %s " %rp.data, " Hora Ultimo RP: %s " %rp.hora)
           
            hora_ultimo_rp = datetime.strptime("%s %s" %(rp.data, rp.hora) ,'%d/%m/%Y %H:%M')
            dif = (datetime.strptime("%s %s" %(getData(), getHora()), '%d/%m/%Y %H:%M') - hora_ultimo_rp).total_seconds()
            i_dif = dif/60;  
            print("Diferenca de tempos: %d" %i_dif)
            if i_dif > 5:
             print("id fun %d, data: %s" %(func.id, getData()))
             cursor.execute(query_select_num_rp %(func.id, getData()))
             num_rp = cursor.fetchone()
             if num_rp is not None:
              i_num_rp = num_rp[0]
              print("Num rp: %d" %i_num_rp)
              i_num_rp = i_num_rp + 1
              values = (func.id, getData(), getHora(), i_num_rp, "Registro Automatico no Relogio")
              cursor.execute(query_insert, values)
              db.commit()
              print(cursor.rowcount, "Inserido")
              informar_linha_4("Ponto Inserido")
              apitarInserido()
              sleep(2)
             else:
              values = (func.id, getData(), getHora(), 1, "Registro Automatico no Relogio")
              cursor.execute(query_insert, values)
              db.commit()
              print(cursor.rowcount, "Inserido")
              informar_linha_4("Ponto Inserido")
              apitarInserido()
              sleep(2)
            else:
             print("Aguarde 5 minutos para poder registrar outro ponto")
             informar_linha_4("Aguarde 5 min")
             apitarErro()
             sleep(2)
           else:
            print("Nenhum RP Encontrato")
            print("ID %d " %func.id)
            values = (func.id, getData(), getHora(), 1, "Registro Automatico no Relogio")
            cursor.execute(query_insert, values)
            db.commit()
            print(cursor.rowcount, "Inserido")
            apitarInserido()
            sleep(2)

          
          else:
           informar_linha_4(str_id)
           sleep(2)

       else:
           print("Cartão Não Associado a nenhum Colaborador, UID: %s" %id)
           informar_linha_3(str_id)
           informar_linha_4("Nao Cadastrado")
           apitarErro()
           sleep(2)
      sleep(2)
      db.close()

     else:
      print("Sem conexão com o servidor!")
      informar_linha_4("Sem Conexao")
      apitarErro()
      sleep(2)

    
 except KeyboardInterrupt:
    GPIO.cleanup()
    raise
 except Exception as e:
   print(e)
   print("Banco de Dados Não encontrado")
   apitarErro()
   informar_linha_4("BD DESCONECTADO")
   sleep(2)
 




