🕒 Relógio de Ponto com Raspberry Pi e Python

Este projeto foi desenvolvido para operação em um Raspberry Pi 3 Model B+, que atua como unidade central dos relógios de ponto fabricados pela Titaniwm.

O sistema combina hardware IoT e software em Python, proporcionando uma solução completa para controle de ponto eletrônico com múltiplas interfaces de interação e comunicação.

⚙️ Estrutura eletrônica e componentes principais

Display LCD 20x4 (I2C) – Interface visual do sistema (IHM), exibindo informações de status, menus e mensagens de operação.

Teclado matricial 4x4 – Interface de entrada de dados que permite:

Registro de ponto via CPF

Reinicialização do sistema

Reinício da alimentação

Reinício da conexão Wi-Fi

Sensor RFID – Responsável pela leitura de tags ou cartões de ponto, garantindo identificação rápida e segura dos usuários.

Buzzer – Utilizado para feedbacks sonoros, indicando ações confirmadas ou falhas de operação.

Módulo NodeMCU (ESP8266) – Conectado via USB, realiza a ponte de comunicação entre relógios de ponto filiais por meio de módulos LoRa, possibilitando sincronização e troca de dados em rede.

💡 Características gerais

O sistema foi projetado para ser autônomo, robusto e escalável, permitindo fácil integração com servidores locais ou remotos.
O uso do Raspberry Pi aliado ao NodeMCU proporciona um equilíbrio ideal entre processamento, conectividade e custo, tornando o relógio de ponto uma solução eficiente e moderna para controle de jornada em ambientes corporativos ou industriais.

<p align="center">
  <img src=https://github.com/pkaislan123/RelogioDePontoRaspberryEPython/blob/main/relogio%20em%20funcionamento.jpg title="hover text">
</p>


