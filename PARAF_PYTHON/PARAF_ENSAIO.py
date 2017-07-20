'''
MEDIÇÃO DE PARÂMETROS DO ALTO-FALANTE COM O ARDUINO

Arquivo: PARAF_ENSAIO.py

Linguagem: Python 3.6
Descrição:
CapturaImpedancia as Curvas de Impedância do Arduino
Calcula os Parâmetros do Alto-falante
Plota as Curvas de Magnitude e Fase

Implementado no Computador em Python 3.6
(Código Fonte)

@author: Filipe Sgarabotto Luza
'''
# -*- coding: utf-8 -*-

import ProtocolPy
import matplotlib.pyplot as plt
from matplotlib import ticker
from numpy import save, load, array, arange, ones
from numpy import sqrt, pi, fft, abs, angle, cos
from scipy.signal import flattop

class Ensaio(object):
    '''
    Ensaio para Obter os Parâmetros de um Alto-falante
    '''    
    def __init__(self):     
        # Propriedades padrão para o ensaio do alto-falante
        self.freqInicial = 20
        self.freqFinal = 2000
        self.passo = 1.1
        self.freqRelInicial = 80
        self.freqRelFinal = 160
        self.passoRel = 1.03
        self.fatorRegime = 1
        self.metodo = 'SWF'
        
        # Fator de calibração
        # TEÓRICO
        self.fatorCal = 1.8907793
        # BOM PARA 4 Ohm
        #self.fatorCal = 2.16
        # BOM PARA 100 Ohm
        #self.fatorCal = 1.92247542178
        
        # Sinal utilizado para teste do dispositivo
        self.testFreq = 100
        self.testDuracao = 1
        self.testTens = None
        self.testCorr = None    
       
        # Valores de frequencia, magnitude e fase da curva de impedância
        self.impFreq = None
        self.impMag = None
        self.impFas = None
        
        # Parâmetros do Alto-falante
        self.RE = 0
        self.FS = 0
        self.RS = 0
        self.QMS = 0
        self.QES = 0
        self.QTS = 0
        self.LE = 0
        self.RED = 0
        
        
    def Calibra(self, R):
        '''
        Determina o Fator de Calibração de acordo com uma Resistencia Conhecida
        '''
        # Inicializa a Comunicação com o Arudinotype filter text
        ard = ProtocolPy.Proto()    
        # Seta as Propriedades do Ensaio Realizado na Resistência Conhecida 
        ard.setaFrequenciaInicial(11)
        ard.setaFrequenciaFinal(15)
        ard.setaPasso(2.0)
        ard.setaFrequenciaRelInicial(11)
        ard.setaFrequenciaRelFinal(15)
        ard.setaPassoRel(2.0)
        ard.setaFatorRegime(1)
        ard.setaMetodoImpedancia('SWF')
        
        # Inicia o ensaio e captura os dados
        ard.iniciaEnsaio()
        freq, mag, fas = ard.recebeImpedancias()           
        impMag = array(mag)

        # Calcula a Média dos Valores dos Bits   
        mediaBits = 0
        for i in range(0, len(impMag)):
            mediaBits += impMag[i]
        mediaBits = mediaBits/len(impMag)      

        # Seta o Fator de Calibração        
        self.fatorCal = R/mediaBits
        
        print(self.fatorCal)
        
    def CapturaSinalTeste(self):
        '''
        Captura os Sinais de Tensão e Corrente em uma Frequencia para o Teste do Dispositivo
        '''
        ard = ProtocolPy.Proto()
        ard.setaFrequencia(self.testFreq)
        ard.setaFatorRegime(self.testDuracao)
        ard.iniciaEnsaio()
        tens = ard.recebeValores()
        corr = ard.recebeValores()
        
        self.testTens = array(tens)
        self.testCorr = array(corr)
        
        def comVal():
            #Corrige os valores de acordo com a calibração
            fatorTens = 2*sqrt(2)/4096
            self.testTens = (self.testTens - 4096/2)*fatorTens
            self.testCorr = (self.testCorr - 4096/2)*(fatorTens/self.fatorCal)        
            ## Corrente em miliamperes
            self.testCorr = self.testCorr*1000       
            
        #comVal() 

    def CapturaImpedancia(self):
        '''
        Captura a Curva de Impedância a partir do Arduino Due 
        ''' 
        # Inicializa a Comunicação com o Arudino
        ard = ProtocolPy.Proto()    
        # Seta a frequencia inicial e final do ensaio 
        ard.setaFrequenciaInicial(self.freqInicial)
        ard.setaFrequenciaFinal(self.freqFinal)
        # Seta o passo do ensaio
        ard.setaPasso(self.passo)
        # Seta a frequencia inicial e final relevante
        ard.setaFrequenciaRelInicial(self.freqRelInicial)
        ard.setaFrequenciaRelFinal(self.freqRelFinal)
        # Seta o passo para as frequencias relevantes
        ard.setaPassoRel(self.passoRel)
        # Seta o fator de regime permanente
        ard.setaFatorRegime(self.fatorRegime)
        # Seta o método de cálculo da impedância
        ard.setaMetodoImpedancia(self.metodo)
        
        # Inicia o ensaio
        ard.iniciaEnsaio()
        
        # Recebe os valores das impedâncias
        freq, mag, fas = ard.recebeImpedancias()           
        
        # Guarda os valores
        self.impFreq = array(freq)
        self.impMag = array(mag)
        self.impFas = array(fas)        
                
        # Corrige a magnitude de acordo com o fator de correção
        self.impMag = self.fatorCal*self.impMag       
        
    def Salva(self, filename='dados_curva.npy'):
        '''
        Salva em um Arquivo os Valores da Curva
        '''
        valores = self.impFreq, self.impMag, self.impFas 
        save(filename, valores)
        
        
    def Carrega(self, filename='dados_curva.npy'):
        '''
        Carrega os Valores da Curva a partir de um Arquivo
        '''
        self.impFreq, self.impMag, self.impFas = load(filename)
        
    def PlotaSinalTeste(self, fig):
        '''
        Plota a Tensão e Corrente do Sinal de Teste
        '''
        # Taxa de Amostragem do Dispositivo
        Ts = 238/10500000     
       
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        
        ax1.set_title("%.0f [Hz]" %self.testFreq)
        
        # Eixo do tempo
        nAmostra = arange(0, 4096*Ts, Ts)                       
       
        ax1.plot(nAmostra, self.testTens, 'ro', label='Tensão')      
        ax2.plot(nAmostra, self.testCorr, 'bo', label='Corrente')
        ax1.set_xlabel("t [ms]")
        ax1.legend(loc='upper right', fontsize='medium')
        ax2.legend(loc='lower right', fontsize='medium')       
        ax1.grid(True)
        ax2.grid(True)

        # Limites do gráfico e ticks
        
        def comVal():
            ax1.set_ylabel("Tensão [V]")
            ax2.set_ylabel("Corrente [mA]")
            ax1.axis([-0.1*4096*Ts, 1.1*4096*Ts, 1.2*min(self.testTens), 1.2*max(self.testTens)])
            ax1.set_yticks((min(self.testTens), 0, max(self.testTens)))
            if (min(self.testCorr) < 0) and (max(self.testCorr) < 0):
                ax2.axis('off')
                ax2.axis([-0.1*4096*Ts, 1.1*4096*Ts, -0.1, 0.1])
            else:
                ax2.set_yticks((min(self.testCorr), 0, max(self.testCorr)))
                ax2.axis([-0.1*4096*Ts, 1.1*4096*Ts, 1.2*min(self.testCorr), 1.2*max(self.testCorr)])
                
        def semVal():
            ax1.set_ylabel("Tensão [12 bits]")
            ax2.set_ylabel("Corrente [12 bits]")
            ax1.axis([-0.1*4096*Ts, 1.1*4096*Ts, 0.8*min(self.testTens), 1.2*max(self.testTens)])
            ax1.set_yticks((min(self.testTens), max(self.testTens)))
            ax2.axis([-0.1*4096*Ts, 1.1*4096*Ts, 0.8*min(self.testCorr), 1.2*max(self.testCorr)])
            ax2.set_yticks((min(self.testCorr), max(self.testCorr)))            
                
        semVal()
           
        # Ajusta o eixo do tempo
        x_ticks = []
        k = 1
        kmax = 30
        while k/self.testFreq < 4096*Ts:
            x_ticks.append(k/self.testFreq)
            if (k > kmax):
                x_ticks = [1/self.testFreq, 4096*Ts]
            k+=1
        ax1.set_xticks(x_ticks)
        scale_x = 1e-3
        ticks_x = ticker.FuncFormatter(lambda x, pos: ('$%.1f$'%(x/scale_x)).replace('.',','))
        ax1.xaxis.set_major_formatter(ticks_x)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)
            
            
    def PlotaSinalTesteFFT(self, fig, flat=False):
        '''
        Plota a FFT do Sinal de Teste
        '''    
        # Numero de Amostras
        nAmostras = (4*1024)
        # Janela
        if flat is True:
            window = flattop(nAmostras)
        else:
            window = ones(nAmostras)
        # Correção do Ganho
        cgain = sum(window)/nAmostras
        # FFT dos sinais de Tensão e Corrente        
        fftTensao = 2*fft.rfft(self.testTens*window/cgain)/nAmostras
        fftCorrente = 2*fft.rfft(self.testCorr*window/cgain)/nAmostras
        # Magnitue e Fase
        fftTensaoMag = abs(fftTensao)
        fftTensaoFas = angle(fftTensao)  
        fftCorrMag = abs(fftCorrente)
        fftCorrFas = angle(fftCorrente)          

        # Plota os resultados
        ax1 = fig.add_subplot(411)
        ax2 = fig.add_subplot(412, sharex=ax1)
        ax3 = fig.add_subplot(413, sharex=ax1)
        ax4 = fig.add_subplot(414, sharex=ax1)
        
        ax1.plot(fftTensaoMag, '-ro')
        ax2.plot(fftTensaoFas, '-ro')        
        ax3.plot(fftCorrMag, '-bo')
        ax4.plot(fftCorrFas, '-bo')


    def grafico(self, fig, sobrepor=False):
        '''
        Plota o gráfico das Curvas de Magnitude e Fase da Impedância
        ''' 
        
        # Caso o gráfico seja sobreposto
        if sobrepor is True:
            ax1 = fig.add_subplot(111)
            ax2 = ax1.twinx()
            ax1.set_xlabel("Frequência [Hz]")
        else:
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212, sharex=ax1)
            ax2.set_xlabel("Frequência [Hz]")
        
        ax1.grid(True)
        ax2.grid(True)
        ax1.set_ylabel("Magnitude [$\Omega$]")
        ax2.set_ylabel("Fase [°]")        

        ax1.plot(self.impFreq, self.impMag, '-ro')            
        ax2.plot(self.impFreq, self.impFas, '-bo')
        
    
    def PlotaCurvasAnaliticas(self, fig):
        '''
        Plota o gráfico Analítico das Curvas de Magnitude e Fase 
        De acordo com os Parâmetros do Alto-falante
        '''
        impFreq = []
        impMag = []
        impFas = []
        
        ws = self.FS*2*pi
        res = self.RS - self.RE 
        
        for f in arange(0.1, self.freqFinal, 0.1):
            
            impFreq.append(f)        
            
            S = 2*pi*f*1j
            
            impLin = self.RE + res/(1 + self.QMS * (S/ws + ws/S))       
            imp = self.RED*S + self.LE*S + impLin
                    
            impMag.append(abs(imp))
            impFas.append(angle(imp, deg=True))   
                
        # Plota os resultados
        axlist = fig.axes
        ax1 = axlist[0]
        ax2 = axlist[1]        
        ax1.plot(impFreq, impMag, '-.r')
        ax2.plot(impFreq, impFas, '-.b') 
        
        
    def CalculaParametros(self):
        '''
        Calcula os Valores dos Parâmetros do Alto-falante
        '''
        impFreq = self.impFreq
        impMag = self.impMag
        
        # Encontra o primeiro máximo da curva de impedância
        k = 7
        for i in range(k, len(impFreq) - k):
            topo = True
            for ki in range(1, k):
                if (impMag[i] - impMag[i-ki] > 0) and (impMag[i] - impMag[i+ki] > 0):
                    topo = topo and True
                else:
                    topo = False
    
            if topo is True:
                iS = i
                    
        A = impFreq[iS-1]
        B = impFreq[iS]
        C = impFreq[iS+1]
        fA = impMag[iS-1]
        fB = impMag[iS]
        fC = impMag[iS+1]
        
        # Determina o avalor da Frequencia de Ressonancia (interpolação parabólica) 
        self.FS = B + (1/2) * ( (fA - fB)*(C-B)**2 - (fC - fB)*(B-A)**2 )/( (fA - fB)*(C-B) + (fC - fB)*(B-A) )
        # Determina o valor da Impedância na Frequencia de ressonancia
        self.RS = fA*((self.FS-B)*(self.FS-C))/((A-B)*(A-C)) +\
                  fB*((self.FS-C)*(self.FS-A))/((B-C)*(B-A)) +\
                  fC*((self.FS-A)*(self.FS-B))/((C-A)*(C-B))
        
        # Determina o valor da Resistência CC 
        self.RE = min(impMag)  
        
        # Determina a impedância Z12
        z12 = sqrt(self.RE*self.RS)
        
        # Encontra a primeira frequencia
        iB = 0
        for i in range (1, len(impFreq) - 1):
            if impMag[i] > z12:
                iB = i
                break
        iA = i - 1
        # Interpolação linear    
        F1 =   (  impFreq[iA] * (1 - (z12 - impMag[iA])/(impMag[iB] - impMag[iA])) 
                + impFreq[iB] * ((z12 - impMag[iA])/(impMag[iB] - impMag[iA])))
    
        # Encontra a segunda frequencia
        iB = 0
        for i in range (iS, len(impFreq) - 1):
            if impMag[i] < z12:
                iB = i
                break
        iA = i - 1
        # Interpolação linear    
        F2 =   (  impFreq[iA] * (1 - (z12 - impMag[iA])/(impMag[iB] - impMag[iA])) 
                + impFreq[iB] * ((z12 - impMag[iA])/(impMag[iB] - impMag[iA])))
        
        #Calcula QMS
        self.QMS = (self.FS/(F2-F1))*sqrt(self.RS/self.RE)
        # Calcula QES
        self.QES = self.QMS/(self.RS/self.RE - 1)
        #Calcula QTS
        self.QTS = self.QMS*(self.RE/self.RS)
                
def main():
    ens = Ensaio()
    ens.Calibra(100.00)
    print(ens.fatorCal)
    
if __name__ == "__main__":
    main()
