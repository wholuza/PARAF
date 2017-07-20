# Medição de Parâmetros do Alto-falante com o Arduino

Esse projeto realiza a medição dos Parâmetros Thiele-Small do Alto-falante com o uso da placa Arduino Due.

O projeto é dividido em duas partes: 
#### PARAF_ARDUINO (Executado na placa Arduino Due) 
#### PARAF_PYTHON (Executado em um computador)

## PARAF_ARDUINO 
Desenvolvida na linguagem C++, contém os protocolos de comunicacão com o computador, a técnica de síntese do sinal (DDS) e os metodos de cálculo da impedância (ZC e SWF).
A compilacão desse programa é realizada com o uso da última versão da plataforma compatível com o Arduino Due (1.6.11).
A implementacão da SWF utiliza funcões da biblioteca CMSIS, por isso é necessário modificar a plataforma Arduino para habilitar esse recurso. 

## PARAF_PYTHON 
Desenvolvida na linguagem Python 3.6.1, contém o protocolo de comunicacão com o Arduino, a plotagem das curvas de impedancia, o cálculo dos parâmetros e a interface com o usuário.
As principais bibliotecas utilizadas são: PySerial, MatplotLib, NumPy, SciPy e PyQt5.
Para instalar todas as dependências Python, utilize o comando Pip da seguinte forma:
#### pip install -r requirements.txt
