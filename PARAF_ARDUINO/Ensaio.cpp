/*
 *
 * MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE
 *
 * Arquivo: Ensaio.cpp
 *
 * Linguagem: C++
 *
 * Descrição:
 * Medição da Impedância do Alto-Falante
 * Implementado no Arduino
 * (Código Fonte)
 *
 * Autor : Filipe Sgarabotto Luza
 */

#include "Ensaio.h"

Ensaio::Ensaio(){
	/// Executado apenas uma vez durante a inicialização

	// Gera a tabela da função seno com o número de amostras por ciclo
	// Valor mínimo: 0
	// Valor máximo: 4095 (12 bits do DAC = 4096)
	for (int n = 0; n < AMOSTRAS_POR_CICLO; n++){
		nTabelaSeno[n] = ( 1 + sin(n*2.0*PI/AMOSTRAS_POR_CICLO) )*4095.0/2;
	}

	// Permite escrever no Power Management Controller (PMC)
	pmc_set_writeprotect(false);
	// Habilita o Time Counter 4 no PMC
	pmc_enable_periph_clk(ID_TC4);
	// Configura o Timer Counter 4 (Ref.: pág 856 do Datasheet SAM3x8e)
	TC_Configure(
			// Time Counter 1
			TC1,
			// Canal 1 (TC4)
			1,
			// Modo WAVE (sem captura)
		    TC_CMR_WAVE |
			// Dispara quando o contador for igual ao valor do registrador RC
			TC_CMR_WAVSEL_UP_RC |
			// Clock do timer ( MCK/8 = 84Mhz/8 = 10.5 Mhz )
			TC_CMR_TCCLKS_TIMER_CLOCK2
			);
	// Configura o registrador RC do Timer Counter 4
	// O timer dispara a cada 238 pulsos do clock MCK/8
	// (MCK/8)/238 = 10.5Mhz/238 = 44117.647 Hz (Taxa de Amostragem)
	TC_SetRC(TC1, 1, 238);
	// Inicia o Timer Counter 4
	TC_Start(TC1, 1);
	// Habilita a intrrrupção
	TC1->TC_CHANNEL[1].TC_IER=TC_IER_CPCS;
	TC1->TC_CHANNEL[1].TC_IDR=~TC_IER_CPCS;
	// Inicializa o DAC
	analogWrite(DAC1,0);
	// Seta a resolução da entrada analógica (16-bits)
	analogReadResolution(12);

	// Inicializa as frequencias e o passo
	_frequenciaInicial = 100;
	_frequenciaFinal = 100;
	_frequencia = 0;
	_passo = 1.1;

	// Inicializa todos os contadores utilizados no ensaio
		uAcumuladorFase = 0;
		uIncrementoFase = 0;
		indiceAmostras = 0;
		indiceAmostrasMax = 0;
		ciclos = 0;
		_ciclosPorFreq = _frequencia;
		_ciclosCapturados = 10;
}


void Ensaio::setFrequencia(float frequencia){
	// Método para setar a frequencia atual do ensaioo
	_frequencia = frequencia;

	// Calcula o incremento de fase a ser adicionado a cada interrupção
	uIncrementoFase = _frequencia*AMOSTRAS_POR_INTERRUPCAO_FP;

	// Calcula o número de ciclos necessários para obter as amostras capturadas
	_ciclosCapturados = ceil(AMOSTRAS_CAPTURADAS/(TX_AMOSTRAGEM/_frequencia));
	
	_ciclosPorFreq = abs(_frequencia);
}


void Ensaio::setCiclosPorFreq(uint16_t ciclosPorFreq){
	// Método para setar o número de ciclos realizados por frequência

	if (ciclosPorFreq != 0){
		_ciclosPorFreq = ciclosPorFreq;
	}
	// Caso o número de ciclos for zero
	// Realizará tantos ciclos quanto for a frequência definida
	else{
		_ciclosPorFreq = abs(_frequencia);
	}
}


void Ensaio::iniciaEnsaio(){
	// Inicia o ensaio

	// Seta a frequencia inicial
	setFrequencia(_frequenciaInicial);

	// Zera todos os contadores
	uAcumuladorFase = 0;
	indiceAmostras = 0;
	indiceAmostrasMax = 0;
	ciclos = 0;
	
	// Limpa os vetores de frequência e impedância
	impFreqLSB.clear();
	impFreqMSB.clear();
	impMagLSB.clear();
	impMagMSB.clear();
	impFasLSB.clear();
	impFasMSB.clear();
	
	continuar_ensaio = true;

	// Ativa a interrupção
	NVIC_EnableIRQ(TC4_IRQn);
}


void Ensaio::InterrupcaoTC4(){
	// Executado cada vez que a interrupção é disparada

	// Desabilita a interrupção
	TC_GetStatus(TC1, 1);
	NVIC_DisableIRQ(TC4_IRQn);

	// Incrementa o acumulador de fase
	uAcumuladorFase += uIncrementoFase;

	// Caso o acumulador exceda o número de amostras por ciclo
	if(uAcumuladorFase > AMOSTRAS_POR_CICLO_FP){
		// Inicia um novo ciclo
		uAcumuladorFase -= AMOSTRAS_POR_CICLO_FP;
		ciclos++;

		// Caso não esteja nos últimos ciclos
		if (ciclos <= _ciclosPorFreq - _ciclosCapturados){
			// Reseta o contador de amostras
			indiceAmostras = 0;
		}
	}

	// Caso exceda o número de amostras capturadas
	if (indiceAmostras > AMOSTRAS_CAPTURADAS){
		// Descarta a amostra
		indiceAmostras = AMOSTRAS_CAPTURADAS;
	}

	// Busca na tabela o valor da saída analógica
	volatile uint16_t saidaAnalogica = nTabelaSeno[uAcumuladorFase>>20];
	
	// Envia para o DAC o valor da saída analógica
	dacc_write_conversion_data(DACC_INTERFACE, saidaAnalogica);

	// Grava o valor da saída
	amostrasSaida[indiceAmostras] = saidaAnalogica;


	// Le o valor da entrada analogica
	volatile uint16_t entradaAnalogica = analogRead(0);

	// Grava o valor da entrada analógica
	amostrasEntrada[indiceAmostras] = entradaAnalogica;

	// Incrementa o indice das amostras capturadas
	indiceAmostras++;

	// Habilita a interrupção
	NVIC_EnableIRQ(TC4_IRQn);
}


void Ensaio::atualizaEnsaio(){
	// Executado no loop principal

	if (continuar_ensaio == true){

		// Se já capturou todas as amostras para essa frequência
		if (ciclos >= _ciclosPorFreq){
			
			// Se foi um ensaio com uma única frequencia
			if (abs(_passo) == 0 or _frequenciaInicial == _frequenciaFinal){
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC1,0);
				
				continuar_ensaio = false;
				
				// Envia os valores das amostras da saída
				enviaValores(amostrasSaida, AMOSTRAS_CAPTURADAS);
				// Envia os valores das amostras da entrada
				enviaValores(amostrasEntrada, AMOSTRAS_CAPTURADAS);					
			}			
			
			// Caso já tenha terminado o ensaio com múltiplas frequencias
			else if (_frequencia > _frequenciaFinal){	
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC1,0);
				
				continuar_ensaio = false;
				
				// Envia os valores das frequencias do ensaio
				uint16_t *impFreqLSB_Ptr = &impFreqLSB[0];
				enviaValores(impFreqLSB_Ptr, impFreqLSB.size());
				uint16_t *impFreqMSB_Ptr = &impFreqMSB[0];
				enviaValores(impFreqMSB_Ptr, impFreqMSB.size());
				
				// Envia os valores das magnitudes da impedancia
				uint16_t *impMagLSB_Ptr = &impMagLSB[0];
				enviaValores(impMagLSB_Ptr, impMagLSB.size());
				uint16_t *impMagMSB_Ptr = &impMagMSB[0];
				enviaValores(impMagMSB_Ptr, impMagMSB.size());
				
				// Envia os valores das fases da impedancia
				uint16_t *impFasLSB_Ptr = &impFasLSB[0];
				enviaValores(impFasLSB_Ptr, impFasLSB.size());
				uint16_t *impFasMSB_Ptr = &impFasMSB[0];
				enviaValores(impFasMSB_Ptr, impFasMSB.size());
			}
			// Caso não tenha terminado o ensaio
			else{
				// Calcula a impedancia para essa frequencia
				calculaImpedancia();
				
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC1,0);
				
				// Incrementa a frequencia
				setFrequencia(_frequencia*_passo);
				
				// Zera todos os contadores
				uAcumuladorFase = 0;
				indiceAmostras = 0;
				indiceAmostrasMax = 0;
				ciclos = 0;

				// Habilita a interrupção
				NVIC_EnableIRQ(TC4_IRQn);
			}
		}
	}
}

void Ensaio::calculaImpedancia(){
	// Calcula a Impedância pelo Método do Cruzamento por Zero
	
	// Valor Médio DC
	double saidaDC = 0.0;
	double entradaDC = 0.0;
	double N = AMOSTRAS_CAPTURADAS;
	for(int n = 0; n < AMOSTRAS_CAPTURADAS; n++){
		saidaDC += amostrasSaida[n]/N;
		entradaDC += amostrasEntrada[n]/N;
	}
	
	// Valor RMS
	double rmsSaida = 0.0;
	double rmsEntrada = 0.0;
	for(int n = 0; n < AMOSTRAS_CAPTURADAS; n++){
		rmsSaida +=    pow(amostrasSaida[n] - saidaDC, 2.0)/N;
		rmsEntrada +=  pow(amostrasEntrada[n] - entradaDC, 2.0)/N;
	}
	rmsSaida = sqrt(rmsSaida);
	rmsEntrada = sqrt(rmsEntrada);
	
	float impMag = rmsSaida / rmsEntrada;
	
	// Primeira passagem por zero da Saída
	int i = 0;
	double zeroSaidaA = 0.0;
	while (!(amostrasSaida[i] < saidaDC and amostrasSaida[i+1] > saidaDC)){
		i++;
	}
	// Interpolação linear para aproximar a passagem por zero
	double S0 = amostrasSaida[i] - saidaDC;
	double S1 = amostrasSaida[i+1] - saidaDC;
	zeroSaidaA = i - S0/(S1 - S0);
	
	
	// Segunda passagem por zero da Saída
	i++;
	double zeroSaidaB = 0.0;
	while (!(amostrasSaida[i] < saidaDC and amostrasSaida[i+1] > saidaDC)){
		i++;
	}
	// Interpolação linear para aproximar a passagem por zero
	S0 = amostrasSaida[i] - saidaDC;
	S1 = amostrasSaida[i+1] - saidaDC;
	zeroSaidaB = i - S0/(S1 - S0);
	
	
	// Primeira passagem por zero da Entrada
	i = 0;
	double zeroEntrada = 0.0;
	while (!(amostrasEntrada[i] < saidaDC and amostrasEntrada[i+1] > saidaDC)){
		i++;
	}
	// Interpolação linear para aproximar a passagem por zero
	double E0 = amostrasEntrada[i] - entradaDC;
	double E1 = amostrasEntrada[i+1] - entradaDC;
	zeroEntrada = i - E0/(E1 - E0);	
	
	// Calcula a fase da impedancia (Evita valores negativos)
	float impFas = 360.0*((zeroEntrada - zeroSaidaA)/(zeroSaidaB - zeroSaidaA));

	// Corrige angulos no quarto quadrante
	if (impFas - 270.0 > 0.0){
		impFas = impFas - 360.0;
	}
	if (impFas + 270.0 < 0.0){
		impFas = impFas + 360.0;
	}

	// Guarda os valores da frequencia e impedância
	uint16_t* freqPtr = (uint16_t*)(&_frequencia);
	impFreqLSB.push_back(freqPtr[0]);
	impFreqMSB.push_back(freqPtr[1]);
	uint16_t* impMagPtr = (uint16_t*)(&impMag);
	impMagLSB.push_back(impMagPtr[0]);
	impMagMSB.push_back(impMagPtr[1]);
	uint16_t* impFasPtr = (uint16_t*)(&impFas);
	impFasLSB.push_back(impFasPtr[0]);
	impFasMSB.push_back(impFasPtr[1]);
}

void Ensaio::setFrequenciaInicial(float frequenciaInicial){
		_frequenciaInicial = frequenciaInicial;
}

void Ensaio::setFrequenciaFinal(float frequenciaFinal){
		_frequenciaFinal = frequenciaFinal;
}

void Ensaio::setPasso(float passo){
		_passo = passo;
}

float Ensaio::getFrequenciaInicial(){
	return _frequenciaInicial;
}

float Ensaio::getFrequenciaFinal(){
	return _frequenciaFinal;
}

float Ensaio::getPasso(){
	return _passo;
}

Ensaio::Protocolo::~Protocolo(){
	USBSERIAL.end();
}
