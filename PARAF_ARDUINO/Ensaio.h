/*
 *
 * MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE
 *
 * Arquivo: Ensaio.h
 *
 * Linguagem: C++
 *
 * Descrição:
 * Medição da Impedância do Alto-Falante
 * Implementado no Arduino
 * (Cabeçalho)
 *
 * Autor : Filipe Sgarabotto Luza
 */

#ifndef ENSAIO_H_
#define ENSAIO_H_

#include "Protocolo.h"
#include <vector>
#include <math.h>

class Ensaio : public Protocolo {
public:
	// Taxa de amostragem em que a interrupção é ativada (Aprox. 44.1Khz)
	const float TX_AMOSTRAGEM = 10500000/238;
	// Número de amostras escritas na tabela do seno para um ciclo de onda completo
	const static long int AMOSTRAS_POR_CICLO = 2*1024;
	// Número de amostras capturadas para uma determinada frequencia do ensaio
	const static int AMOSTRAS_CAPTURADAS = 4*1024;

	// Valores em ponto fixo (para calcular rapidamente os decimais durante a interrupção)
	// Os 20 primeiros bytes são a parte inteira do valor e os demais são a parte decimal
	const uint32_t AMOSTRAS_POR_CICLO_FP = (AMOSTRAS_POR_CICLO << 20);
	const uint32_t AMOSTRAS_POR_INTERRUPCAO_FP = (float) AMOSTRAS_POR_CICLO_FP / TX_AMOSTRAGEM;

	// Tabela com os valores da função seno
	uint16_t nTabelaSeno[AMOSTRAS_POR_CICLO];

	// Acumulador de fase que é incrementado a cada interrupção
	uint32_t uAcumuladorFase;
	volatile uint32_t uIncrementoFase;

	// Frequencia do Ensaio
	float _frequenciaInicial;
	float _frequenciaFinal;
	float _passo;
	float _frequencia;

	// Ciclos de onda realizados e capturados
	uint16_t _ciclosPorFreq;
	uint16_t _ciclosCapturados;
	uint16_t ciclos;

	// Buffer que armazena os valores das amostras enviadas e recebidas
	uint16_t amostrasSaida[AMOSTRAS_CAPTURADAS+1];
	uint16_t amostrasEntrada[AMOSTRAS_CAPTURADAS+1];
	int indiceAmostras;
	int indiceAmostrasMax;

	// Vetores com as frequencias utilizadas no ensaio
	std::vector<uint16_t> impFreqLSB;
	std::vector<uint16_t> impFreqMSB;
	// Vetores com as magnitudes e fases da impedancia
	std::vector<uint16_t> impMagLSB;
	std::vector<uint16_t> impMagMSB;
	std::vector<uint16_t> impFasLSB;
	std::vector<uint16_t> impFasMSB;

	bool continuar_ensaio = false;
	bool grava_amostras = true;

	Ensaio();
	void setFrequenciaInicial(float);
	void setFrequenciaFinal(float);
	void setFrequencia(float);
	void setCiclosPorFreq(uint16_t);
	void setPasso(float);
	float getFrequenciaInicial();
	float getFrequenciaFinal();
	float getPasso();

	void calculaImpedancia();

	void iniciaEnsaio();
	void InterrupcaoTC4();
	void atualizaEnsaio();
};

#endif /* ENSAIO_H_ */
