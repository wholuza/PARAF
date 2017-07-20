'''
MEDIÇÃO DE PARÂMETROS DO ALTO-FALANTE COM O ARDUINO

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
import serial.tools as tools
from time import sleep
from sys import byteorder
from decimal import *
import struct

class Proto(object):
    '''
    Protocolo de comunicação Serial
    '''
    # Códigos dos bytes enviados via serial
    mens_inicio         =   0x21 # !   - Inicio da Mensagem    
    mens_final          =   0x23 # #   - Fim da Mensagem
    
    setFreqIniInt       =   0x46 # F   - Seta a parte inteira da frequencia inicial
    setFreqIniDec       =   0x47 # G   - Seta a parte decimal da frequencia inicial
    setFreqFimInt       =   0x48 # H   - Seta a parte inteira da frequencia final
    setFreqFimDec       =   0x49 # I   - Seta a parte decimal da frequencia final
    setPassoInt         =   0x4A # J   - Seta a parte inteira do passo
    setPassoDec         =   0x4B # K   - Seta a parte decimal do passo
    
    setFreqRelIniInt    =   0x4C # L   - Seta a parte inteira da frequencia relevante inicial
    setFreqRelIniDec    =   0x4D # M   - Seta a parte decimal da frequencia relevante inicial
    setFreqRelFimInt    =   0x4E # N   - Seta a parte inteira da frequencia relevante final
    setFreqRelFimDec    =   0x4F # O   - Seta a parte decimal da frequencia relevante final
    setPassoRelInt      =   0x50 # P   - Seta a parte inteira do passo relevante
    setPassoRelDec      =   0x51 # Q   - Seta a parte decimal do passo relevante
    
    setFatorRegimeInt   =   0x52 # R   - Seta a parte inteira do fator de regime permanente
    setFatorRegimeDec   =   0x53 # S   - Seta a parte decimal do fator de regime permanente
    
    setMetodoZC         =   0X54 # T   - Seta o método de Cruzamento por Zero para o cálculo da Impedância
    setMetodoSWF        =   0X55 # U   - Seta o método de Ajuste de Curvas Senoidais para o cálculo da Impedância

    inicia_ensaio       =   0x41 # A   - Inicia o ensaio

    size                =   0x73 # s   - Tamanho do pacote
    byte_LS             =   0x61 # a   - Byte menos significativo
    byte_MS             =   0x7A # z   - Byte mais significativo
    
    rec_sucesso         =   0x79 # y   - Valor recebido com sucesso    
    rec_falha           =   0x6E # n   - Falha no recebimento do valor
    esc                 =   0x1B # ESC - Valor de escape que interrompe um envio

    # Porta serial
    ser = serial.Serial()
    serialDelay = 0.0  
      

    def __init__(self):
        # Configura a porta serial
        portNum = 0
        self.ser.baudrate = 230400        
         
        # Abre a porta serial
        while not self.ser.isOpen():
            try:
                self.ser.port = '/dev/ttyACM' + str(portNum)
                self.ser.open()
            except serial.serialutil.SerialException as exc:
                print("Erro Serial: %s"%(exc))
                portNum += 1
                self.ser.is_open = 0
                if portNum <= 10:
                    pass
                else:
                    print("Não foi possível abrir a porta Serial: %s"%(exc))
                    raise
                           
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
        
    def _setaValor(self, valor, codigoInt, codigoDec=None):
        valorInt, valorDec = divmod(valor, 1)      
       
        # Compõe a mensagem da parte inteira
        valorInt_LSB = (int(valorInt) & 0x00FF)
        valorInt_MSB = (int(valorInt) & 0xFF00) >> 8   
        mensagem = bytearray([self.mens_inicio,
                              codigoInt,
                              valorInt_LSB,
                              valorInt_MSB,
                              self.mens_final])
        
        # Envia a mensagem da parte inteira
        self.ser.write(mensagem)
        self.ser.flush()
        while(self.ser.out_waiting > 0):
            sleep(self.serialDelay)
        
        if codigoDec is not None:
            # Compõe a mensagem da parte decimal
            valorDec = int(valorDec*65536)
            valorDec_LSB = (valorDec & 0x00FF)
            valorDec_MSB = (valorDec & 0xFF00) >> 8
            mensagem = bytearray([self.mens_inicio,
                                  codigoDec,
                                  valorDec_LSB,
                                  valorDec_MSB,
                                  self.mens_final])
            
            # Envia a mensagem da parte decimal
            self.ser.write(mensagem)
            self.ser.flush()
            while(self.ser.out_waiting > 0):
                sleep(self.serialDelay)          
        
    def setaFrequenciaInicial(self, frequencia):
        self._setaValor(frequencia, self.setFreqIniInt, self.setFreqIniDec)
            
    def setaFrequenciaFinal(self, frequencia):
        self._setaValor(frequencia, self.setFreqFimInt, self.setFreqFimDec)
        
    def setaPasso(self, passo):        
        self._setaValor(passo, self.setPassoInt, self.setPassoDec)
        
    def setaFrequenciaRelInicial(self, frequencia):
        self._setaValor(frequencia, self.setFreqRelIniInt, self.setFreqRelIniDec)
            
    def setaFrequenciaRelFinal(self, frequencia):
        self._setaValor(frequencia, self.setFreqRelFimInt, self.setFreqRelFimDec)
        
    def setaPassoRel(self, passo):        
        self._setaValor(passo, self.setPassoRelInt, self.setPassoRelDec)
            
    def setaFrequencia(self, frequencia):
        self.setaFrequenciaInicial(frequencia)
        self.setaFrequenciaFinal(frequencia)
        self.setaPasso(0.0)  
        
    def setaFatorRegime(self, fator):
        self._setaValor(fator, self.setFatorRegimeInt, self.setFatorRegimeDec)
        
    def setaMetodoImpedancia(self, metodo):
        if metodo == 'SWF' or metodo == 0:
            self._enviaComando(self.setMetodoSWF)
        elif metodo == 'ZC' or metodo ==1:
            self._enviaComando(self.setMetodoZC)
        
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
    
    
    def recebeImpedancias(self):
        # Recebe as frequencias
        impFreq = []
        impFreqLSB = self.recebeValores()  
        impFreqMSB = self.recebeValores()
        for MSB, LSB in zip(impFreqMSB, impFreqLSB):
            iMSB = struct.pack('H', MSB)
            iLSB = struct.pack('H', LSB)
            valB = struct.pack('B'*4, iLSB[0], iLSB[1], iMSB[0], iMSB[1])
            valF = struct.unpack('f', valB)
            impFreq.append(valF[0])        
            
        # Recebe as magnitudes
        impMag = []
        impMagLSB = self.recebeValores()  
        impMagMSB = self.recebeValores()
        for MSB, LSB in zip(impMagMSB, impMagLSB):
            iMSB = struct.pack('H', MSB)
            iLSB = struct.pack('H', LSB)
            valB = struct.pack('B'*4, iLSB[0], iLSB[1], iMSB[0], iMSB[1])
            valF = struct.unpack('f', valB)
            impMag.append(valF[0])        
        
    # Recebe as fases
        impFas = []
        impFasLSB = self.recebeValores()  
        impFasMSB = self.recebeValores()
        for MSB, LSB in zip(impFasMSB, impFasLSB):
            iMSB = struct.pack('H', MSB)
            iLSB = struct.pack('H', LSB)
            valB = struct.pack('B'*4, iLSB[0], iLSB[1], iMSB[0], iMSB[1])
            valF = struct.unpack('f', valB)
            impFas.append(valF[0])
            
        return impFreq, impMag, impFas

        
    def __del__(self):        
        # Limpa o buffer
        while(self.ser.in_waiting > 0): self.ser.read(1)
        while(self.ser.out_waiting > 0): sleep(self.serialDelay)
        # Fecha a porta serial
        self.ser.close()
        