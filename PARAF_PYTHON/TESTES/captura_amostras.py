
'''
MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE

Arquivo: captura_amostras.py

Linguagem: Python 3.6

Descrição:
Captura os sinais de tensão e corrente para diversas frequências
Grava em arquivos .txt.

Implementado no Computador em Python 3.6
(Código Fonte)

@author: Filipe Sgarabotto Luza
'''
# -*- coding: utf-8 -*-

import ProtocolPy
import time
from numpy import savetxt

def main():
    frequenciaArray = []
    valoresEntradaArray = []
    valoresSaidaArray = []    
    
    # Protocolo de comunicação com o Arduino
    ard = ProtocolPy.Proto()

    # Frequencia inicial
    frequencia = 10
    # Frequencia final
    freqFinal = 2000
    # Passo (10% da frequência atual)
    passo = 1.1
    
    # Realiza um ensaio para cada frequência    
    start_time = time.time()    
    while frequencia < freqFinal:
        # Seta a frequencia e o número de ciclos a serem realizados
        ard.setaFrequencia(frequencia);
        ard.setaFatorRegime(0.5)
        
        print("Freq: %.2f" %(frequencia))       

        # Inicia o ensaio para a frequencia determinada
        ard.iniciaEnsaio()
        
        # Recebe os valores
        valoresSaida = ard.recebeValores()
        valoresEntrada = ard.recebeValores()
        
        # Inclui valores nos arrays
        frequenciaArray.append(frequencia)
        valoresEntradaArray.append(valoresEntrada)
        valoresSaidaArray.append(valoresSaida)        
        
        # Incrementa a frequencia 
        frequencia = frequencia*passo                  
        
    print("Tempo: %s\n" %(time.time() - start_time))
    
    # Salva os resultados do ensaio em arquivos .txt
    savetxt('dados_frequencia.txt', frequenciaArray)
    savetxt('dados_entrada.txt', valoresEntradaArray)
    savetxt('dados_saida.txt', valoresSaidaArray)
    
if __name__ == "__main__":
    main()
    