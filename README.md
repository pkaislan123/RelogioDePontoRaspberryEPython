# RelogioDePontoRaspberryEPython

O Código a seguir é usado num rasperry pi 3 model b+. Esse pi é a placa mãe dos relogios de pontos fabricados pela TItaniwm.

O sistema eletrônico desses relógios consiste em:

-> Um display 20x4 i2c para Interface IHM

-> Um teclado matricial 4x4 para Interface IHM, nele é possível efetuar operações como registro de ponto por CPF, reinicio do sistema, reinicio da alimentação e reinicio do wifi.

-> Um sensor RFID para leitura da tag ou cartão de ponto

-> Um buzzer para respostas usando efeito sonoro

-> Um módulo NodeMcu Esp8266 conectado via usb, responsável por fazer a intermediação entre relógios de pontos filias usando a conexão a rádio dos módulos Lora.

<p align="center">
  <img src=https://github.com/pkaislan123/RelogioDePontoRaspberryEPython/blob/main/relogio%20em%20funcionamento.jpg title="hover text">
</p>


