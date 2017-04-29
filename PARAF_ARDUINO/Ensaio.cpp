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

	// Inicializa todos os contadores utilizados no ensaio
		uAcumuladorFase = 0;
		uIncrementoFase = 0;
		indiceAmostras = 0;
		indiceAmostrasMax = 0;
		ciclos = 0;
		_ciclosPorFreq = _frequencia;
		_ciclosCapturados = 10;
}

void Ensaio::setaFrequenciaI(uint16_t frequenciaInt){
	// Método para setar a frequencia atual do ensaioo
	_frequencia = frequenciaInt;

	// Calcula o incremento de fase a ser adicionado a cada interrupção
	uIncrementoFase = _frequencia*AMOSTRAS_POR_INTERRUPCAO_FP;

	// Calcula o número de ciclos necessários para obter as amostras capturadas
	_ciclosCapturados = ceil(AMOSTRAS_CAPTURADAS/(TX_AMOSTRAGEM/_frequencia));
}

void Ensaio::setaFrequenciaD(uint16_t frequenciaDec){
	// Método para setar a parte decimal da frequencia do ensaio
	uint16_t frequenciaInt = abs(_frequencia);
	uint32_t frequenciaFP = (frequenciaInt << 16) + frequenciaDec;
	_frequencia = frequenciaFP/65536.0;

	// Calcula o incremento de fase a ser adicionado a cada interrupção
	uIncrementoFase = _frequencia*AMOSTRAS_POR_INTERRUPCAO_FP;

	// Calcula o número de ciclos necessários para obter as amostras capturadas
	_ciclosCapturados = ceil(AMOSTRAS_CAPTURADAS/(TX_AMOSTRAGEM/_frequencia));
}

void Ensaio::setaCiclosPorFreq(uint16_t ciclosPorFreq){
	// Método para setar o número de ciclos realizados por frequência

	if (ciclosPorFreq != 0){
		_ciclosPorFreq = ciclosPorFreq;
	}
	// Caso o número de ciclos for zero
	// Realizará tantos ciclos quanto for a frequência definida
	else{
		_ciclosPorFreq = _frequencia;
	}
}


void Ensaio::iniciaEnsaio(){
	// Inicia o ensaio

	continuar_ensaio = true;

	// Zera todos os contadores
	uAcumuladorFase = 0;
	indiceAmostras = 0;
	indiceAmostrasMax = 0;
	ciclos = 0;

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

	// Grava o valor da saída
	amostrasSaida[indiceAmostras] = saidaAnalogica;

	// Envia para o DAC o valor da saída analógica
	dacc_write_conversion_data(DACC_INTERFACE, saidaAnalogica);

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

		// Verifica se é o momento de finalizar o ensaio
		if (ciclos >= _ciclosPorFreq){
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC1,0);

				// Envia os valores das amostras da saída
				enviaValores(amostrasSaida, AMOSTRAS_CAPTURADAS);
				// Envia os valores das amostras da entrada
				enviaValores(amostrasEntrada, AMOSTRAS_CAPTURADAS);

				continuar_ensaio = false;
		}
	}
}


Ensaio::Protocolo::~Protocolo(){
	USBSERIAL.end();
}
