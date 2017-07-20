'''
MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE

Arquivo: PARAF.py

Linguagem: Python 3.6
Descrição:
Interface com o Usuário 

Implementado no Computador em Python 3.6
(Código Fonte)

@author: Filipe Sgarabotto Luza
'''

from __future__ import unicode_literals
import sys
import os
import matplotlib

# Garante o uso do Qt5
matplotlib.use('Qt5Agg')

from PARAF_ENSAIO import Ensaio

from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class DialogoNovoEnsaio(QtWidgets.QDialog):
    def __init__(self, curva):
        super().__init__()
        
        self.setWindowTitle('Novo Ensaio')
                
        # Frequencia Inicial
        l_freqInicial = QtWidgets.QLabel("Frequência Inicial")
        self.freqInicial = QtWidgets.QSpinBox(self)
        self.freqInicial.setRange(5, 10000)
        self.freqInicial.setSingleStep(10)
        self.freqInicial.setValue(curva.freqInicial)
        u_freqInicial = QtWidgets.QLabel("Hz")        
        # Frequencia Final
        l_freqFinal = QtWidgets.QLabel("Frequência Final")
        self.freqFinal = QtWidgets.QSpinBox(self)
        self.freqFinal.setRange(1, 10000)
        self.freqFinal.setSingleStep(100)
        self.freqFinal.setValue(curva.freqFinal)
        u_freqFinal = QtWidgets.QLabel("Hz")        
        # Passo
        l_passo = QtWidgets.QLabel("Passo")
        self.passo = QtWidgets.QSpinBox(self)
        self.passo.setRange(1, 100)
        self.passo.setSingleStep(1)
        self.passo.setValue((curva.passo-1)*100)
        u_passo = QtWidgets.QLabel("%")        
        # Frequencia Inicial da Região de Interesse
        l_freqRelInicial = QtWidgets.QLabel("Frequência Inicial da Região de Interesse")
        self.freqRelInicial = QtWidgets.QSpinBox(self)
        self.freqRelInicial.setRange(1, 10000)
        self.freqRelInicial.setSingleStep(10)
        self.freqRelInicial.setValue(curva.freqRelInicial)
        u_freqRelInicial = QtWidgets.QLabel("Hz")    
        # Frequencia Final da Região de Interesse
        l_freqRelFinal = QtWidgets.QLabel("Frequência Final da Região de Interesse")
        self.freqRelFinal = QtWidgets.QSpinBox(self)
        self.freqRelFinal.setRange(1, 10000)
        self.freqRelFinal.setSingleStep(10)
        self.freqRelFinal.setValue(curva.freqRelFinal)
        u_freqRelFinal = QtWidgets.QLabel("Hz")        
        # Passo da Região de Interesse
        l_passoRel = QtWidgets.QLabel("Passo da Região de Interesse")
        self.passoRel = QtWidgets.QSpinBox(self)
        self.passoRel.setRange(1, 100)
        self.passoRel.setSingleStep(1)
        self.passoRel.setValue((curva.passoRel-1)*100)
        u_passoRel = QtWidgets.QLabel("%")        
        # Fator de Regime Permanente
        l_fatorRegime = QtWidgets.QLabel("Fator de Regime Permanente")
        self.fatorRegime = QtWidgets.QDoubleSpinBox(self)
        self.fatorRegime.setRange(0, 100)
        self.fatorRegime.setDecimals(2)
        self.fatorRegime.setSingleStep(0.1)
        self.fatorRegime.setValue(curva.fatorRegime)
        u_fatorRegime = QtWidgets.QLabel("")        
        # Método de Cálculo
        l_metodo = QtWidgets.QLabel("Método de Cálculo da Impedância")
        self.metodo = QtWidgets.QComboBox(self)
        self.metodo.addItem('SWF', None)
        self.metodo.addItem('ZC', None)
        u_metodo = QtWidgets.QLabel("")
    
        # Leiaute dos campos       
        labelList = (l_freqInicial, l_freqFinal, l_passo, 
                     l_freqRelInicial, l_freqRelFinal, l_passoRel,
                     l_fatorRegime, l_metodo)
        
        widgetList = (self.freqInicial, self.freqFinal, self.passo, 
                     self.freqRelInicial, self.freqRelFinal, self.passoRel,
                     self.fatorRegime, self.metodo)
        
        unitList = (u_freqInicial, u_freqFinal, u_passo, 
                     u_freqRelInicial, u_freqRelFinal, u_passoRel,
                     u_fatorRegime, u_metodo)       
        
        leiaute_campos = QtWidgets.QGridLayout()        
        for i in range(0, len(labelList)):
            
            leiaute_campos.addWidget(labelList[i] ,i, 0)
            labelList[i].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            labelList[i].setAlignment(QtCore.Qt.AlignLeft)
            
            leiaute_campos.addWidget(widgetList[i] ,i, 1)
            if type(widgetList[i]) is QtWidgets.QSpinBox or type(widgetList[i]) is QtWidgets.QDoubleSpinBox:
                widgetList[i].setAlignment(QtCore.Qt.AlignRight)

            leiaute_campos.addWidget(unitList[i] ,i, 2)
            unitList[i].setAlignment(QtCore.Qt.AlignLeft)
        
        # Leiaute dos botoes
        leiaute_botoes = QtWidgets.QHBoxLayout()
        self.b_inicia = QtWidgets.QPushButton("Inicia", self)
        self.b_cancela = QtWidgets.QPushButton("Cancela", self)
        leiaute_botoes.addWidget(self.b_inicia)
        leiaute_botoes.addWidget(self.b_cancela)
        
        # Leiaute final do dialogo
        leiaute_dialogo = QtWidgets.QVBoxLayout()
        leiaute_dialogo.addLayout(leiaute_campos)
        leiaute_dialogo.addLayout(leiaute_botoes)      
        self.setLayout(leiaute_dialogo)


class DialogoCalibrar(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Calibração')
        
        # Resistor de Calibração
        l_R = QtWidgets.QLabel("Valor do Restitor de Calibração")
        self.R = QtWidgets.QDoubleSpinBox(self)
        self.R.setRange(0.1, 10000)
        self.R.setSingleStep(0.1)
        self.R.setValue(5)
        self.R.setAlignment(QtCore.Qt.AlignRight)
        u_R = QtWidgets.QLabel("Ohm")        
       
        # Leiaute dos campos
        leiaute_campos = QtWidgets.QGridLayout()
        leiaute_campos.addWidget(l_R ,0, 0)
        leiaute_campos.addWidget(self.R ,0, 1)
        leiaute_campos.addWidget(u_R ,0, 2)
        
        # Leiaute dos botoões
        leiaute_botoes = QtWidgets.QHBoxLayout()
        self.b_inicia = QtWidgets.QPushButton("Inicia", self)
        self.b_cancela = QtWidgets.QPushButton("Cancela", self)
        leiaute_botoes.addWidget(self.b_inicia)
        leiaute_botoes.addWidget(self.b_cancela)
        
        # Leiaute final do dialogo
        leiaute_dialogo = QtWidgets.QVBoxLayout()
        leiaute_dialogo.addLayout(leiaute_campos)
        leiaute_dialogo.addLayout(leiaute_botoes)      
        self.setLayout(leiaute_dialogo)   


class DialogoSinalTeste(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Sinal')
        
        # Frequencia
        l_freq = QtWidgets.QLabel("Frequência")
        self.freq = QtWidgets.QSpinBox(self)
        self.freq.setRange(1, 10000)
        self.freq.setSingleStep(10)
        self.freq.setValue(100)
        self.freq.setAlignment(QtCore.Qt.AlignRight)
        u_freq = QtWidgets.QLabel("Hz")
        
        # Duração
        l_dur = QtWidgets.QLabel("Duração")
        self.dur = QtWidgets.QSpinBox(self)
        self.dur.setRange(1, 10000)
        self.dur.setSingleStep(1)
        self.dur.setValue(1)
        self.dur.setAlignment(QtCore.Qt.AlignRight)
        u_dur = QtWidgets.QLabel("s")
        
        # Leiaute dos campos
        leiaute_campos = QtWidgets.QGridLayout()
        leiaute_campos.addWidget(l_freq ,0, 0)
        leiaute_campos.addWidget(self.freq ,0, 1)
        leiaute_campos.addWidget(u_freq ,0, 2)
        leiaute_campos.addWidget(l_dur ,1, 0)
        leiaute_campos.addWidget(self.dur ,1, 1)
        leiaute_campos.addWidget(u_dur ,1, 2)
        
        # Leiaute dos botoões
        leiaute_botoes = QtWidgets.QHBoxLayout()
        self.b_inicia = QtWidgets.QPushButton("Inicia", self)
        self.b_cancela = QtWidgets.QPushButton("Cancela", self)
        leiaute_botoes.addWidget(self.b_inicia)
        leiaute_botoes.addWidget(self.b_cancela)
        
        # Leiaute final do dialogo
        leiaute_dialogo = QtWidgets.QVBoxLayout()
        leiaute_dialogo.addLayout(leiaute_campos)
        leiaute_dialogo.addLayout(leiaute_botoes)      
        self.setLayout(leiaute_dialogo)   


class Grafico(FigureCanvas):
    """Contorno do Gráfico"""    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
              
        self.fig = Figure(figsize=(width, height), dpi=dpi)    
       
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        
class BarraLateral(QtWidgets.QGridLayout):
    def __init__(self, parent):
        QtWidgets.QGridLayout.__init__(self, parent)
        
        labelList = []
        self.widgetList = []
        unitList = []
        
        self.setAlignment(QtCore.Qt.AlignTop)
        
        # RE
        l_RE = QtWidgets.QLabel("RE: ")        
        self.RE = QtWidgets.QDoubleSpinBox(parent)
        self.RE.setRange(0, 500)
        self.RE.setSingleStep(0.1)
        self.RE.setValue(0)
        self.RE.setAlignment(QtCore.Qt.AlignRight)
        self.RE.setAlignment(QtCore.Qt.AlignTop)
        u_RE = QtWidgets.QLabel("Ohm")
        labelList.append(l_RE)
        self.widgetList.append(self.RE)
        unitList.append(u_RE)        
        
        # FS
        l_FS = QtWidgets.QLabel("FS: ")
        self.FS = QtWidgets.QDoubleSpinBox(parent)
        self.FS.setRange(0, 1000)
        self.FS.setSingleStep(0.1)
        self.FS.setValue(0)
        self.FS.setAlignment(QtCore.Qt.AlignRight)
        self.FS.setAlignment(QtCore.Qt.AlignTop)
        u_FS = QtWidgets.QLabel("Hz")
        labelList.append(l_FS)
        self.widgetList.append(self.FS)
        unitList.append(u_FS)      
        
        # RS
        l_RS = QtWidgets.QLabel("RS: ")
        self.RS = QtWidgets.QDoubleSpinBox(parent)
        self.RS.setRange(0, 500)
        self.RS.setSingleStep(0.1)
        self.RS.setValue(0)
        self.RS.setAlignment(QtCore.Qt.AlignRight)
        u_RS = QtWidgets.QLabel("Ohm")
        labelList.append(l_RS)
        self.widgetList.append(self.RS)
        unitList.append(u_RS)   
        
        # QMS
        l_QMS = QtWidgets.QLabel("QMS: ")
        self.QMS = QtWidgets.QDoubleSpinBox(parent)
        self.QMS.setRange(0, 100)
        self.QMS.setSingleStep(0.1)
        self.QMS.setValue(0)
        self.QMS.setAlignment(QtCore.Qt.AlignRight)
        u_QMS = QtWidgets.QLabel("")
        labelList.append(l_QMS)
        self.widgetList.append(self.QMS)
        unitList.append(u_QMS)
        
        # QES
        l_QES = QtWidgets.QLabel("QES: ")
        self.QES = QtWidgets.QDoubleSpinBox(parent)
        self.QES.setRange(0, 100)
        self.QES.setSingleStep(0.1)
        self.QES.setValue(0)
        self.QES.setAlignment(QtCore.Qt.AlignRight)
        self.QES.setEnabled(False)
        u_QES = QtWidgets.QLabel("")
        labelList.append(l_QES)
        self.widgetList.append(self.QES)
        unitList.append(u_QES)  
        
        # QTS
        l_QTS = QtWidgets.QLabel("QTS: ")
        self.QTS = QtWidgets.QDoubleSpinBox(parent)
        self.QTS.setRange(0, 100)
        self.QTS.setSingleStep(0.1)
        self.QTS.setValue(0)
        self.QTS.setAlignment(QtCore.Qt.AlignRight)
        self.QTS.setEnabled(False)
        u_QTS = QtWidgets.QLabel("")
        labelList.append(l_QTS)
        self.widgetList.append(self.QTS)
        unitList.append(u_QTS)          
        
        # LE
        l_LE = QtWidgets.QLabel("LE: ")
        self.LE = QtWidgets.QDoubleSpinBox(parent)
        self.LE.setRange(0, 100)
        self.LE.setSingleStep(0.1)
        self.LE.setValue(0)
        self.LE.setAlignment(QtCore.Qt.AlignRight)
        u_LE = QtWidgets.QLabel("mH")
        labelList.append(l_LE)
        self.widgetList.append(self.LE)
        unitList.append(u_LE)
            
        # RED
        l_RED = QtWidgets.QLabel("RED: ")
        self.RED = QtWidgets.QDoubleSpinBox(parent)
        self.RED.setRange(0, 100)
        self.RED.setSingleStep(0.1)
        self.RED.setValue(0)
        self.RED.setAlignment(QtCore.Qt.AlignRight)
        u_RED = QtWidgets.QLabel("")
        labelList.append(l_RED)
        self.widgetList.append(self.RED)
        unitList.append(u_RED)        
        
        for i in range(0, len(labelList)):    
            self.addWidget(labelList[i] ,i, 0)
            #labelList[i].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            labelList[i].setAlignment(QtCore.Qt.AlignLeft)
            
            self.addWidget(self.widgetList[i] ,i, 1)
            if type(self.widgetList[i]) is QtWidgets.QSpinBox or type(self.widgetList[i]) is QtWidgets.QDoubleSpinBox:
                self.widgetList[i].setAlignment(QtCore.Qt.AlignRight)
        
            self.addWidget(unitList[i] ,i, 2)
            unitList[i].setAlignment(QtCore.Qt.AlignLeft)
            
        # CheckBoxes
        self.plotaAnalitica = QtWidgets.QCheckBox(parent)
        l_plotaAnalitica = QtWidgets.QLabel("Curva Analítica")
        self.addWidget(self.plotaAnalitica, i+1, 0)
        self.addWidget(l_plotaAnalitica, i+1, 1)
        
        self.sobreporCurvas = QtWidgets.QCheckBox(parent)
        l_sobreporCurvas = QtWidgets.QLabel("Sobrepor")
        self.addWidget(self.sobreporCurvas, i+2, 0)
        self.addWidget(l_sobreporCurvas, i+2, 1)
        
        self.eixoLog = QtWidgets.QCheckBox(parent)
        l_eixoLog = QtWidgets.QLabel("Log")
        self.addWidget(self.eixoLog, i+3, 0)
        self.addWidget(l_eixoLog, i+3, 1)  
            
    def setaParametros(self, ensaio):
        RE = ensaio.RE
        FS = ensaio.FS
        RS = ensaio.RS
        QMS = ensaio.QMS
        QES = ensaio.QES
        QTS = ensaio.QTS
        LE = ensaio.LE
        RED = ensaio.RED        
        self.RE.setValue(RE)
        self.FS.setValue(FS)
        self.RS.setValue(RS)
        self.QMS.setValue(QMS)
        self.QES.setValue(QES)
        self.QTS.setValue(QTS)
        self.LE.setValue(LE)
        self.RED.setValue(RED)
        
    def Disable(self):
        count = self.count()
        for i in range(0, count):
            self.itemAt(i).widget().hide()
            
    def Enable(self):
        count = self.count()
        for i in range(0, count):
            self.itemAt(i).widget().show()

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):        
        QtWidgets.QMainWindow.__init__(self)        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)        
        self.setWindowTitle("Medição de Parâmetros de Alto-falantes com o Arduino Due")
        
        # Objeto Ensaio
        self.ensaio = Ensaio()
        
        # Widget principal
        self.main_widget = QtWidgets.QWidget(self)        
        # Gráfico
        self.grafico = Grafico(self.main_widget, width=25, height=20, dpi=100)               

        ## Menus
        # Arquivo
        self.menu_arquivo = QtWidgets.QMenu('&Arquivo', self)
        # Arquivo - Novo Ensaio
        self.diaglogoNovoEnsaio = DialogoNovoEnsaio(self.ensaio)
        self.diaglogoNovoEnsaio.b_cancela.clicked.connect(self.diaglogoNovoEnsaio.close)
        self.diaglogoNovoEnsaio.b_inicia.clicked.connect(self.iniciaEnsaio)
        self.menu_arquivo.addAction('&Novo Ensaio', self.diaglogoNovoEnsaio.exec,
                         QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        # Arquivo - Carrega Ensaio
        self.menu_arquivo.addAction('&Carrega', self.arquivoCarrega,
                         QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        # Arquivo - Salva Ensaio
        self.menu_arquivo.addAction('&Salva', self.arquivoSalva,
                         QtCore.Qt.CTRL + QtCore.Qt.Key_S)        
        # Arquivo - Sair
        self.menu_arquivo.addAction('&Sair', self.arquivoSair,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.menu_arquivo)
        
        ## Calibração
        self.menu_calibracao = QtWidgets.QMenu('&Calibração', self)
        # Calibrar
        self.dialogoCalibrar = DialogoCalibrar()
        self.dialogoCalibrar.b_cancela.clicked.connect(self.dialogoCalibrar.close)
        self.dialogoCalibrar.b_inicia.clicked.connect(self.iniciaCalibracao)
        self.menu_calibracao.addAction('&Calibrar', self.dialogoCalibrar.exec,
                                       QtCore.Qt.CTRL + QtCore.Qt.Key_C)
        self.menuBar().addMenu(self.menu_calibracao)        
        
        # Sinal Teste
        self.dialogoSinalTeste = DialogoSinalTeste()
        self.dialogoSinalTeste.b_cancela.clicked.connect(self.dialogoSinalTeste.close)
        self.dialogoSinalTeste.b_inicia.clicked.connect(self.iniciaTeste)
        self.menu_calibracao.addAction('&Sinal Teste', self.dialogoSinalTeste.exec,
                                    QtCore.Qt.CTRL + QtCore.Qt.Key_T)
        self.menuBar().addMenu(self.menu_calibracao)        
        
        # Sobre
        self.menuBar().addAction('&Sobre', self.sobre)        

        # Barra de Controle do Gráfico
        self.barra_grafico = NavigationToolbar(self.grafico, self)
        self.grafico.mpl_connect('key_press_event', self.on_key_press)
        
        # Leiaute Vertical com o gráfico e barra
        leiauteVertical = QtWidgets.QVBoxLayout()
        leiauteVertical.addWidget(self.grafico)
        leiauteVertical.addWidget(self.barra_grafico)
        
        # Barra lateral com os parâmetros
        self.barraLateral = BarraLateral(self)
        self.barraLateral.Disable()      
        self.barraLateral.plotaAnalitica.stateChanged.connect(self.atualizaGrafico)
        self.barraLateral.sobreporCurvas.stateChanged.connect(self.atualizaGrafico)
        self.barraLateral.eixoLog.stateChanged.connect(self.atualizaGrafico)
        self.barraLateral.RE.valueChanged.connect(self.atualizaGrafico)
        self.barraLateral.FS.valueChanged.connect(self.atualizaGrafico)
        self.barraLateral.RS.valueChanged.connect(self.atualizaGrafico)
        self.barraLateral.QMS.valueChanged.connect(self.atualizaGrafico)
        self.barraLateral.QTS.valueChanged.connect(self.atualizaGrafico)
        self.barraLateral.LE.valueChanged.connect(self.atualizaGrafico)
        self.barraLateral.RED.valueChanged.connect(self.atualizaGrafico)        
       
        # Leiaute horizontal principal do programa
        leiauteHorizontal = QtWidgets.QHBoxLayout()
        leiauteHorizontal.addLayout(leiauteVertical)
        leiauteHorizontal.addLayout(self.barraLateral)
        
        self.main_widget.setLayout(leiauteHorizontal)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # Barra de Status
        self.statusBar().showMessage(".", 2000)
        
    def iniciaCalibracao(self):
        R = self.dialogoCalibrar.R.value()
        self.ensaio.Calibra(R)
        
        self.dialogoCalibrar.close()
        
    def iniciaTeste(self):
        # Seta as configuraçòes do teste
        self.ensaio.testFreq = self.dialogoSinalTeste.freq.value()
        self.ensaio.testDuracao = self.dialogoSinalTeste.dur.value() 
        
        # Captura os sinais do teste
        self.ensaio.CapturaSinalTeste()
        
        # Atualiza o gráfico
        self.grafico.fig.clear()
        self.ensaio.PlotaSinalTeste(self.grafico.fig)
        self.grafico.draw()
        
        self.dialogoSinalTeste.close()
        self.barraLateral.Disable()       

        
    def iniciaEnsaio(self):
        # Seta as configurações do ensaio
        self.ensaio.freqInicial = self.diaglogoNovoEnsaio.freqInicial.value()
        self.ensaio.freqFinal = self.diaglogoNovoEnsaio.freqFinal.value() 
        self.ensaio.passo = 1+self.diaglogoNovoEnsaio.passo.value()/100
        self.ensaio.freqRelInicial = self.diaglogoNovoEnsaio.freqRelInicial.value()
        self.ensaio.freqRelFinal = self.diaglogoNovoEnsaio.freqRelFinal.value() 
        self.ensaio.passoRel = 1+self.diaglogoNovoEnsaio.passoRel.value()/100 
        self.ensaio.fatorRegime = self.diaglogoNovoEnsaio.fatorRegime.value() 
        self.ensaio.metodo = self.diaglogoNovoEnsaio.metodo.currentText()
        
        # Captura
        self.ensaio.CapturaImpedancia()       
        
        # Calcula os parâmetros e seta na barra lateral
        try:
            self.ensaio.CalculaParametros()
        except:
            pass
        self.barraLateral.setaParametros(self.ensaio)
        self.barraLateral.Enable()
        self.diaglogoNovoEnsaio.close()
        
        self.atualizaGrafico()
        
    def arquivoCarrega(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fd = QtWidgets.QFileDialog(self)
        fd.setDefaultSuffix('npy')
        fileName, _ = fd.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Ensaios (*.npy)", options=options)
        if fileName:
            self.ensaio.Carrega(fileName)
            # Atualiza o gráfico
            self.grafico.fig.clear()
            self.ensaio.grafico(self.grafico.fig, sobrepor=False)
            self.grafico.draw()
            
            # Calcula os parâmetros e seta na barra lateral
            self.ensaio.CalculaParametros()
            self.barraLateral.setaParametros(self.ensaio)
            self.barraLateral.Enable()
        
    def arquivoSalva(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fd = QtWidgets.QFileDialog(self)
        fd.setDefaultSuffix('.npy')
        fileName, _ = fd.getSaveFileName(self,"QFileDialog.getSaveFileName()","","Ensaios (*.npy)", options=options)
        if fileName:
            self.ensaio.Salva(fileName)

    def arquivoSair(self):
        self.close()
        
    def on_key_press(self, event):
        key_press_handler(event, self.grafico, self.barra_grafico)
        
    def atualizaGrafico(self):
        # Atualiza com os valores da barra lateral
        self.ensaio.RE = self.barraLateral.RE.value()
        self.ensaio.FS = self.barraLateral.FS.value()
        self.ensaio.RE = self.barraLateral.RE.value()
        self.ensaio.FS = self.barraLateral.FS.value()
        self.ensaio.RS = self.barraLateral.RS.value()
        self.ensaio.QMS = self.barraLateral.QMS.value()
        self.ensaio.QTS = self.barraLateral.QTS.value()
        self.ensaio.LE = self.barraLateral.LE.value()/1000
        self.ensaio.RED = self.barraLateral.RED.value()       
            
        # Obtem o estado das checkboxes
        analitica = self.barraLateral.plotaAnalitica.isChecked()
        sobrepor = self.barraLateral.sobreporCurvas.isChecked()
        eixolog = self.barraLateral.eixoLog.isChecked()

        # Plota novamente o gráfico       
        self.grafico.fig.clear()
        self.ensaio.grafico(self.grafico.fig, sobrepor)
        # Plota a curva analítica
        if analitica is True:
            self.ensaio.PlotaCurvasAnaliticas(self.grafico.fig)
        # Altera o eixo
        ax = self.grafico.fig.axes
        if eixolog:
            ax[0].set_xscale('log')
        else:
            ax[0].set_xscale('linear')
            
        self.grafico.draw()

    def closeEvent(self, ce):
        self.arquivoSair()

    def sobre(self):
        mensagemSobre = """
Medição de Parâmetros de Alto-falantes com o Arduino Due

Autor
Filipe Sgarabotto Luza

Sob orientação de
Sidnei Noceti Filho e Homero Sette

UNIVERSIDADE FEDERAL DE SANTA CATARINA
2017
"""        
        QtWidgets.QMessageBox.about(self, "Sobre", mensagemSobre)

def main():
    qApp = QtWidgets.QApplication(sys.argv)    
    aw = ApplicationWindow()
    
    progname = 'Medição de Parâmetros de Alto-falantes com o Arduino Due'
    aw.setWindowTitle("%s" % progname)
    
    aw.show()
    sys.exit(qApp.exec_())
    
if __name__ == "__main__":
    main()