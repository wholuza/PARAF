'''
MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE

Arquivo: captura_impedancia.py

Linguagem: Python 3.6

Descrição:
Realiza ensaios em diferentes frequências e captura as impedâncias calculadas pelo Arduino.
Plota a curva de impedância.

Implementado no Computador em Python 3.6
(Código Fonte)

@author: Filipe Sgarabotto Luza
'''
# -*- coding: utf-8 -*-

import serial
from time import sleep
from sys import byteorder
from decimal import *

class Proto(object):
    '''
    Protocolo de comunicação Serial
    '''
    mens_inicio =         0x21 # !   - Inicio da Mensagem    
    mens_final =          0x23 # #   - Fim da Mensagem
    
    seta_freqIniInt  =    0x46 # F   - Seta a parte inteira da frequencia inicial
    seta_freqIniDec  =    0x47 # G   - Seta a parte decimal da frequencia inicial
    seta_freqFimInt  =    0x48 # H   - Seta a parte inteira da frequencia final
    seta_freqFimDec  =    0x49 # I   - Seta a parte decimal da frequencia final
    seta_passoInt    =    0x50 # P   - Seta a parte inteira do passo
    seta_passoDec    =    0x51 # Q   - Seta a parte decimal do passo

    seta_ciclos =         0x43 # C   - Seta o número de ciclos por frequencia
    inicia_ensaio =       0x41 # A   - Inicia o ensaio

    size =                0x73 # s   - Tamanho do pacote
    byte_LS =             0x61 # a   - Byte menos significativo
    byte_MS =             0x7A # z   - Byte mais significativo
    
    rec_sucesso =         0x79 # y   - Valor recebido com sucesso    
    rec_falha =           0x6E # n   - Falha no recebimento do valor
    esc =                 0x1B # ESC - Valor de escape que interrompe um envio

    # Porta serial
    ser = serial.Serial()
    serialDelay = 0.0  
      

    def __init__(self):
        # Configura a porta serial        
        self.ser.port = '/dev/ttyACM4'
        self.ser.baudrate = 230400
         
        # Abre a porta serial
        while not self.ser.isOpen():
            self.ser.open()           
        sleep(0.02)
        
        print("Porta serial %s aberta." %(self.ser.port))
       
        # Limpa o buffer
        while(self.ser.in_waiting > 0): self.ser.read(1)
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)
        
        # Envia o código de escape
        self.ser.write(bytes([self.esc]))
        self.ser.flush()
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)
        
    def _enviaComando(self, comando):        
        # Cria a mensagem
        mensagem = bytearray([self.mens_inicio,
                              comando,
                              comando,
                              comando,
                              self.mens_final])
        # Envia a mensagem
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)
          
        
    def setaFrequenciaInicial(self, frequencia):
        frequenciaInt, frequenciaDec = divmod(frequencia, 1)      
       
        # Compõe a mensagem da parte inteira
        frequenciaInt_LSB = (int(frequenciaInt) & 0x00FF)
        frequenciaInt_MSB = (int(frequenciaInt) & 0xFF00) >> 8   
        mensagem = bytearray([self.mens_inicio,
                              self.seta_freqIniInt,
                              frequenciaInt_LSB,
                              frequenciaInt_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte inteira
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)
            
        # Compõe a mensagem da parte decimal
        frequenciaDec = int(frequenciaDec*65536)
        frequenciaDec_LSB = (frequenciaDec & 0x00FF)
        frequenciaDec_MSB = (frequenciaDec & 0xFF00) >> 8
        mensagem = bytearray([self.mens_inicio,
                              self.seta_freqIniDec,
                              frequenciaDec_LSB,
                              frequenciaDec_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte decimal
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)
            
    def setaFrequenciaFinal(self, frequencia):
        frequenciaInt, frequenciaDec = divmod(frequencia, 1)      
       
        # Compõe a mensagem da parte inteira
        frequenciaInt_LSB = (int(frequenciaInt) & 0x00FF)
        frequenciaInt_MSB = (int(frequenciaInt) & 0xFF00) >> 8   
        mensagem = bytearray([self.mens_inicio,
                              self.seta_freqFimInt,
                              frequenciaInt_LSB,
                              frequenciaInt_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte inteira
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)
            
        # Compõe a mensagem da parte decimal
        frequenciaDec = int(frequenciaDec*65536)
        frequenciaDec_LSB = (frequenciaDec & 0x00FF)
        frequenciaDec_MSB = (frequenciaDec & 0xFF00) >> 8
        mensagem = bytearray([self.mens_inicio,
                              self.seta_freqFimDec,
                              frequenciaDec_LSB,
                              frequenciaDec_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte decimal
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)
            
    def setaFrequencia(self, frequencia):
        self.setaFrequenciaInicial(frequencia)
        self.setaFrequenciaFinal(frequencia)
        self.setaPasso(0.0)
            
    def setaPasso(self, passo):
        passoInt, passoDec = divmod(passo, 1)
       
        # Compõe a mensagem da parte inteira
        passoInt_LSB = (int(passoInt) & 0x00FF)
        passoInt_MSB = (int(passoInt) & 0xFF00) >> 8   
        mensagem = bytearray([self.mens_inicio,
                              self.seta_passoInt,
                              passoInt_LSB,
                              passoInt_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte inteira
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)
            
        # Compõe a mensagem da parte decimal
        passoDec = int(passoDec*65536)
        passoDec_LSB = (passoDec & 0x00FF)
        passoDec_MSB = (passoDec & 0xFF00) >> 8
        mensagem = bytearray([self.mens_inicio,
                              self.seta_passoDec,
                              passoDec_LSB,
                              passoDec_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte decimal
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)    

    
    def setaCiclosPorFrequencia(self, ciclosPF):      
        ciclosPF_LSB = (ciclosPF & 0x00FF)
        ciclosPF_MSB = (ciclosPF & 0xFF00) >> 8
        
        # Compõe a mensagem
        mensagem = bytearray([self.mens_inicio,
                              self.seta_ciclos,
                              ciclosPF_LSB,
                              ciclosPF_MSB,
                              self.mens_final])
        
        # Envia a mensagem
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)        
    
        
    def iniciaEnsaio(self):
        # Limpa o buffer
        while(self.ser.in_waiting > 0):
            self.ser.read(1)
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)  
            
        # Envia o código de escape
        self.ser.write(bytes([self.esc]))
        self.ser.flush()
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)
        
        # Envia comando para iniciar o ensaio
        self._enviaComando(self.inicia_ensaio)
        
        
    def recebeMensagem(self):
        sucesso = False
        mensagem = ['\x00','\x00']
        
        # Recebe até a mensagem ser válida
        while sucesso == False:
                    
            # Recebe o primeiro byte
            while(self.ser.in_waiting == 0): sleep(self.serialDelay)   
            byte_rec = self.ser.read(1)   
              
            # Checa o byte de inicio da mensagem
            if (byte_rec == bytes([self.mens_inicio])):
                
                # Recebe o segundo byte
                while(self.ser.in_waiting == 0): sleep(self.serialDelay)
                mensagem[0] = self.ser.read(1) 
                
                # Recebe o terceiro byte
                while(self.ser.in_waiting == 0): sleep(self.serialDelay)
                mensagem[1] = self.ser.read(1)
                
                # Recebe o quarto byte
                while(self.ser.in_waiting == 0): sleep(self.serialDelay)
                byte_rec = self.ser.read(1)                    
                       
                # Verifica o byte final da mensagem
                if (byte_rec == bytes([self.mens_final])):
                    sucesso = True         
                               
        return mensagem
    
    
    def recebeValor(self):
        nmensagem = 0
        valor_LSB = 0
        valor_MSB = 0        
        
        # Recebe mensagens até o valor ser válido
        while nmensagem < 2:            
            mensagem = self.recebeMensagem()
                        
            # Verifica se é o byte menos significativo
            if (nmensagem == 0) and (mensagem[0] == bytes([self.byte_LS])):
                # Grava o byte menos significativo
                valor_LSB = int.from_bytes(mensagem[1], byteorder='big')
                nmensagem += 1
            # Verifica se é o byte mais significativo
            elif (nmensagem == 1) and (mensagem[0] == bytes([self.byte_MS])):
                # Grava o byte menos significativo
                valor_MSB = int.from_bytes(mensagem[1], byteorder='big')
                
                # Compõe o valor
                valor = int.from_bytes([valor_MSB, valor_LSB], byteorder='big')               
                
                # Avisa que o valor foi recebido com sucesso
                self.ser.write(bytes([self.rec_sucesso]))
                self.ser.flush()
                while(self.ser.out_waiting > 0): sleep(self.serialDelay)            
                nmensagem += 1
            else:
                # Tenta novamente
                print("Falha ao receber valor.")
                self.ser.write(bytes([self.rec_falha]))
                self.ser.flush()
                while(self.ser.out_waiting > 0): sleep(self.serialDelay)
                nmensagem = 0
        
        return valor
    
    
    def recebeValores(self):
        # Recebe o número de valores
        tamanho = self.recebeValor()        
        
        valores = []
       
        # Recebe cada um dos valores
        while(len(valores) < tamanho):
            valores.append(self.recebeValor())
            
        return valores

        
    def __del__(self):        
        # Limpa o buffer
        while(self.ser.in_waiting > 0): self.ser.read(1)
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)
        # Fecha a porta serial
        self.ser.close()
        