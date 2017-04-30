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

import ProtocolPy
import matplotlib.pyplot as plt
import struct

def main():
    ard = ProtocolPy.Proto()
    
    freqInicial = 20
    freqFinal = 300

    ard.setaFrequenciaInicial(freqInicial)
    ard.setaFrequenciaFinal(freqFinal)
    ard.setaPasso(1.01)
    
    ard.iniciaEnsaio()

    # Recebe as frequencias
    impFreq = []
    impFreqLSB = ard.recebeValores()  
    impFreqMSB = ard.recebeValores()
    for MSB, LSB in zip(impFreqMSB, impFreqLSB):
        iMSB = struct.pack('H', MSB)
        iLSB = struct.pack('H', LSB)
        valB = struct.pack('B'*4, iLSB[0], iLSB[1], iMSB[0], iMSB[1])
        valF = struct.unpack('f', valB)
        impFreq.append(valF)
        
    print(impFreq)
        
    # Recebe as magnitudes
    impMag = []
    impMagLSB = ard.recebeValores()  
    impMagMSB = ard.recebeValores()
    for MSB, LSB in zip(impMagMSB, impMagLSB):
        iMSB = struct.pack('H', MSB)
        iLSB = struct.pack('H', LSB)
        valB = struct.pack('B'*4, iLSB[0], iLSB[1], iMSB[0], iMSB[1])
        valF = struct.unpack('f', valB)
        impMag.append(valF)
        
    print(impMag)
        
    # Recebe as fases
    impFas = []
    impFasLSB = ard.recebeValores()  
    impFasMSB = ard.recebeValores()
    for MSB, LSB in zip(impFasMSB, impFasLSB):
        iMSB = struct.pack('H', MSB)
        iLSB = struct.pack('H', LSB)
        valB = struct.pack('B'*4, iLSB[0], iLSB[1], iMSB[0], iMSB[1])
        valF = struct.unpack('f', valB)
        impFas.append(valF)
        
    print(impFas)
        
    # Plota os resultados
    plt.figure(1)    
    ax1 = plt.subplot(211)
    plt.plot(impFreq, impMag, ':go')
        
    plt.ylabel("Magnitude [bits]")
    #plt.xticks(arange(freqInicial, freqFinal, 10.0))
    ax1.grid(True)
    
    ax2 = plt.subplot(212, sharex=ax1)
    plt.plot(impFreq, impFas, ':go')    
    plt.ylabel("Fase [°]")
    plt.xlabel("Frequência [Hz]")
    ax2.grid(True)       
        
    plt.show()    
  
    
if __name__ == "__main__":
    main()
    