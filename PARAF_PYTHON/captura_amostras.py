import ProtocolPy
import time
from numpy import savetxt
from math import floor

def main():
    frequenciaArray = []
    valoresEntradaArray = []
    valoresSaidaArray = []    
    
    # Protocolo de comunicação com o Arduino
    ard = ProtocolPy.Proto()

    # Frequencia inicial
    frequencia = 20
    # Frequencia final
    freqFinal = 1000
    # Passo (10% da frequência atual)
    passo = 1.1
    
    # Realiza um ensaio para cada frequência    
    start_time = time.time()    
    while frequencia < freqFinal:
        # Seta a frequencia e o número de ciclos a serem realizados
        ard.setaFrequencia(frequencia);
        ard.setaCiclosPorFrequencia(0)
        
        print("Freq: %d" %(frequencia))       

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
        frequencia = floor(frequencia*passo)                  
        
    print("Tempo: %s\n" %(time.time() - start_time))
    
    # Salva os resultados do ensaio em arquivos .txt
    savetxt('frequencia.txt', frequenciaArray)
    savetxt('entrada.txt', valoresEntradaArray)
    savetxt('saida.txt', valoresSaidaArray)
    
if __name__ == "__main__":
    main()
    