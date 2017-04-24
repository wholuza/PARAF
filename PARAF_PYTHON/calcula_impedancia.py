from numpy import loadtxt, zeros, pi, sqrt, sin, cos, arctan, fft, abs, angle, matmul, arange, arcsin
from scipy.signal import flattop
from numpy.linalg import inv
import matplotlib.pyplot as plt
import time

def main():
    # Lê os dados do ensiao dos arquivos .txt
    frequenciaArray = loadtxt('dados_frequencia.txt')
    valoresEntradaArray = loadtxt('dados_entrada.txt')
    valoresSaidaArray = loadtxt('dados_saida.txt')    
    
    # Calcula a impedância através dos 3 métodos
    timeZC, impFreqZC, impMagZC, impFasZC = calculaImpZC(frequenciaArray, valoresEntradaArray, valoresSaidaArray)
    timeFFT, impFreqFFT, impMagFFT, impFasFFT = calculaImpFFT(frequenciaArray, valoresEntradaArray, valoresSaidaArray)
    timeSWF, impFreqSWF, impMagSWF, impFasSWF = calculaImpfSWF(frequenciaArray, valoresEntradaArray, valoresSaidaArray)    
    
    # Plota os resultados
    plt.figure(1)    
    ax1 = plt.subplot(211)
    # ax1.set_title('Curvas de Magnitude e Fase da Impedância do Alto-Falante')    
    plt.plot(impFreqZC, impMagZC, '-g', label='ZC')
    plt.plot(impFreqFFT, impMagFFT, 'b', label='DFT')
    plt.plot(impFreqSWF, impMagSWF, '-r', label='SWF')
    plt.ylabel("Magnitude [bits]")
    ax1.legend(loc='upper right', fontsize='large')
    plt.xticks(arange(0, 1000+1, 100.0))
    ax1.grid(True)
    ax2 = plt.subplot(212, sharex=ax1)
    plt.plot(impFreqZC, impFasZC, '-g', label='ZC')
    plt.plot(impFreqFFT, impFasFFT, '-b', label='DFT')
    plt.plot(impFreqSWF, impFasSWF, '-r', label='SWF')
    plt.ylabel("Fase [°]")
    plt.xlabel("Frequência [Hz]")
    ax2.legend(loc='lower right', fontsize='large')
    ax2.grid(True)
    plt.figure(2)
    ax3 = plt.subplot(111)
    #ax3.set_title('Tempo Necessário para Calcular a Impedância')
    barwidth = 0.75
    ax3.bar(1, timeZC, barwidth, color='g')
    ax3.bar(2, timeFFT, barwidth, color='b')
    ax3.bar(3, timeSWF, barwidth, color='r')
    ax3.set_xticks((1, 2, 3))
    ax3.set_xticklabels(('ZC', 'DFT', 'SWF'))
    plt.ylabel("t [s]")        
    plt.show()


def calculaImpZC(frequenciaArray, valoresEntradaArray, valoresSaidaArray):
    impFreq = []
    impMag =[]
    impFas = []
    
    start_time = time.time()
    for (frequencia, valoresEntrada, valoresSaida) in zip(frequenciaArray, valoresEntradaArray, valoresSaidaArray):       

        # Número de amostras
        N = (4*1024)
              
        # Valor Médio DC
        saidaDC = 0
        entradaDC = 0
        for n in range(0, N):
            saidaDC += valoresSaida[n]/N
            entradaDC += valoresEntrada[n]/N        
        
        # Valor RMS da Saída e da Entrada
        rmsSaida = 0
        rmsEntrada = 0
        for n in range(0, N):
            rmsSaida += (valoresSaida[n] - saidaDC)**2/N
            rmsEntrada += (valoresEntrada[n] - entradaDC)**2/N
        rmsSaida = sqrt(rmsSaida)
        rmsEntrada = sqrt(rmsEntrada)
        
        # Magnitude da Impedância
        magImped = rmsSaida / rmsEntrada    
                
        # Primeira passagem por zero da Saída
        i = 0
        while not (valoresSaida[i] < saidaDC and valoresSaida[i+1] > saidaDC):
            i += 1                
        # Interpolação linear para aproximar a passagem por zero
        S0 = valoresSaida[i] - saidaDC
        S1 = valoresSaida[i+1] - saidaDC
        zeroSaidaA = i - S0/(S1 - S0)
                
        # Segunda passagem por zero da Saída
        i += 1     
        while not (valoresSaida[i] < saidaDC and valoresSaida[i+1] > saidaDC):
            i += 1
        # Interpolação linear para aproximar a passagem por zero
        S0 = valoresSaida[i] - saidaDC
        S1 = valoresSaida[i+1] - saidaDC
        zeroSaidaB = i - S0/(S1 - S0)
        
        # Primeira passagem por zero da Entrada
        i = 0
        while not (valoresEntrada[i] < entradaDC and valoresEntrada[i+1] > entradaDC):
            i += 1                
        # Interpolação linear para aproximar a passagem por zero
        E0 = valoresEntrada[i] - entradaDC
        E1 = valoresEntrada[i+1] - entradaDC
        zeroEntrada = i - E0/(E1 - E0)           
                
        # Calcula a fase da impedancia
        angImped = 360*(zeroEntrada - zeroSaidaA)/(zeroSaidaB - zeroSaidaA)        
        
        # Corrige o quadrante do ângulo
        if angImped > 180:
            angImped = -(360 - angImped)
        if angImped < -180:
            angImped = (360 + angImped)
            
        # Guarda os valores da impedância
        impFreq.append(frequencia)
        impMag.append(magImped)
        impFas.append(angImped)
        
        # Calcula o tempo necessário para esse método
        end_time = time.time()
        timeZC = end_time - start_time
        
    return timeZC, impFreq, impMag, impFas  


def calculaImpFFT(frequenciaArray, valoresEntradaArray, valoresSaidaArray):
    impFreq = []
    impMag =[]
    impFas = []
    
    start_time = time.time()
    for (frequencia, valoresEntrada, valoresSaida) in zip(frequenciaArray, valoresEntradaArray, valoresSaidaArray):      
        
        #Remove o valor DC
        entradaDC = (max(valoresEntrada) - min(valoresEntrada))/2 + min(valoresEntrada)
        saidaDC = (max(valoresSaida) - min(valoresSaida))/2 + min(valoresSaida)
        valoresSaida[:] = [x - saidaDC for x in valoresSaida]
        valoresEntrada[:] = [x - entradaDC for x in valoresEntrada]              

        # Número de amostras
        N = (4*1024)
        # Janela FlatTop
        window = flattop(N)
        # Cálculo do ganho devido ao janelamento
        cgain = sum(window)/N
        
        # Calcula a FFT da entrada e da saída        
        fSaida = 2*fft.rfft(valoresSaida*window/cgain)/N
        fEntrada = 2*fft.rfft(valoresEntrada*window/cgain)/N
        
        # Calcula o módulo e ângulo
        fSaidaMag = abs(fSaida)
        fSaidaAng = angle(fSaida, deg=True)  
        fEntradaMag = abs(fEntrada)
        fEntradaAng = angle(fEntrada, deg=True)
        
        # Encontra o valor máximo do módulo da saída
        magSaida = 0
        iSaida = 0
        for i in range(4,len(fSaidaMag)):
            if fSaidaMag[i] > magSaida:
                magSaida = fSaidaMag[i] 
                iSaida = i
        angSaida = fSaidaAng[iSaida]        
        
        # Encontra o valor máximo do módulo da entrada  
        magEntrada = 0
        iEntrada = 0
        for i in range(4,len(fEntradaMag)):
            if fEntradaMag[i] > magEntrada:
                magEntrada = fEntradaMag[i]
                iEntrada = i
        angEntrada = fEntradaAng[iEntrada]
        
        # Calcula o módulo e ângulo da impedância
        magImped = magSaida / magEntrada
        angImped = angSaida - angEntrada
        
        # Guarda os valores da impedância
        impFreq.append(frequencia)
        impMag.append(magImped)
        impFas.append(angImped)
        
        # Calcula o tempo necessário para esse método
        end_time = time.time()
        timeFFT = end_time - start_time
        
    return timeFFT, impFreq, impMag, impFas 


def calculaImpfSWF(frequenciaArray, valoresEntradaArray, valoresSaidaArray):   
    impFreq = []
    impMag =[]
    impFas = []
    
    start_time = time.time()
    for (frequencia, valoresEntrada, valoresSaida) in zip(frequenciaArray, valoresEntradaArray, valoresSaidaArray):
                
        # Número de amostras
        N = 1024
        
        # Período de amostragem (1 / 44.1kHz)
        T = 238/10500000
        
        # Frequencia discreta * Período de amostragem
        w = 2*pi*frequencia
        
        # Estimativas iniciais para as amplitudes em fase e quadratura
        A1 = (2**12)/2
        A2 = (2**12)/2
        B1 = (2**12)/2
        B2 = (2**12)/2
        
        # Calcula r1 e r2
        r1 = zeros((N,1))
        r2 = zeros((N,1))        
        for n in range(0, N):
            r1[n][0] = -2*pi*A1*T*n*sin(w*T*n) + 2*pi*B1*T*n*cos(w*T*n)
            r2[n][0] = -2*pi*A2*T*n*sin(w*T*n) + 2*pi*B2*T*n*cos(w*T*n)       

        # calcula E e G       
        E = zeros((7,7))
        G = zeros((7,1))    
        for n in range(0, N):
            # E11
            E[0][0] += cos(w*T*n)**2
            # E12
            E[0][1] += cos(w*T*n)*sin(w*T*n)
            # E13
            E[0][2] += cos(w*T*n)
            # E14
            E[0][3] += cos(w*T*n)*r1[n][0]
            # E22
            E[1][1] += sin(w*T*n)**2
            # E23
            E[1][2] += sin(w*T*n)
            # E24
            E[1][3] += sin(w*T*n)*r1[n][0]
            # E34
            E[2][3] += r1[n][0]
            # E44
            E[3][3] += r1[n][0]**2 + r2[n][0]**2
            # E45
            E[3][4] += cos(w*T*n)*r2[n][0]
            # E46
            E[3][5] += sin(w*T*n)*r2[n][0]
            # E47
            E[3][6] += r2[n][0]
            
            G[0][0] += cos(w*T*n)*valoresSaida[n]
            G[1][0] += sin(w*T*n)*valoresSaida[n]
            G[2][0] += valoresSaida[n]
            G[3][0] += valoresSaida[n]*r1[n] + valoresEntrada[n]*r2[n]
            G[4][0] += cos(w*T*n)*valoresEntrada[n]
            G[5][0] += sin(w*T*n)*valoresEntrada[n]
            G[6][0] += valoresEntrada[n]
                   
        # Define os demais valores de E 
        # E21 = E12
        E[1][0] = E[0][1]
        # E31 = E13
        E[2][0] = E[0][2]
        # E32 = E23
        E[2][1] = E[1][2]
        # E33 = N
        E[2][2] = N
        # E41 = E14
        E[3][0] = E[0][3]
        # E42 = E24
        E[3][1] = E[1][3]
        # E43 = E34
        E[3][2] = E[2][3]
        # E54 = E45
        E[4][3] = E[3][4]
        # E55 = E11
        E[4][4] = E[0][0]
        # E56 = E12
        E[4][5] = E[0][1]
        # E57 = E13
        E[4][6] = E[0][2]
        # E64 = E46
        E[5][3] = E[3][5]
        # E65 = E12
        E[5][4] = E[0][1]
        # E66 = E22
        E[5][5] = E[1][1]
        #E67 = E23
        E[5][6] = E[1][2]
        #E74 = E47
        E[6][3] = E[3][6]
        #E75 = E13
        E[6][4] = E[0][2]
        #E76 = E23
        E[6][5] = E[1][2]
        #E77 = N
        E[6][6] = N        
           
        #Calcula a inversa de E
        Einv = inv(E)
        
        # Multiplica a inversa de E por G         
        x = matmul(Einv, G)        
        
        # Calcula os modulos
        magSaida = sqrt(x[0]**2 + x[1]**2)
        magEntrada = sqrt(x[4]**2 + x[5]**2)
        magImped = magSaida / magEntrada
        
        # Calcula os ângulos
        angSaida = 180*arctan(x[0]/x[1])/pi
        angEntrada = 180*arctan(x[4]/x[5])/pi
        angImped = angSaida - angEntrada
        
        # Guarda o valor da impedância
        impFreq.append(frequencia)
        impMag.append(magImped)
        impFas.append(angImped)
        
        # Calcula o tempo necessário para esse método
        end_time = time.time()
        timeSWF = end_time - start_time
        
    return timeSWF, impFreq, impMag, impFas

    
if __name__ == "__main__":
    main()
    