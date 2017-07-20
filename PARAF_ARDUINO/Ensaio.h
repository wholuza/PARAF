/*
 *
 * MEDIÇÃO DE PARÂMETROS DO ALTO-FALANTE COM O ARDUINO
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

#ifndef ARM_MATH_CM3
#define ARM_MATH_CM3
#endif

#include "Protocolo.h"
#include <vector>
#include <math.h>
#include <arm_math.h>

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

	// Frequencias iniciais/finais do Ensaio, Passo e fator de Regime Permanente
	float _freqIni;
	float _freqFim;
	float _passo;
	float _freqRelIni;
	float _freqRelFim;
	float _passoRel;
	float _frequencia;
	float _fatorRegime;

	// Método de cálculo da impedância (0 = SWF, 1 = ZC)
	uint16_t _metodoImp;

	// Acumulador de fase que é incrementado a cada interrupção
	uint32_t uAcumuladorFase;
	volatile uint32_t uIncrementoFase;

	// Ciclos de onda completos a serem capturados para a frequência atual
	uint16_t ciclosCapturar;
	// Ciclos de onda completos já realizados para a frequência atual
	uint16_t ciclosRealizados;

	// Buffer que armazena os valores das amostras enviadas e recebidas
	uint16_t amostrasSaida[AMOSTRAS_CAPTURADAS+1];
	uint16_t amostrasEntrada[AMOSTRAS_CAPTURADAS+1];
	int indiceAmostras;

	// Vetores com as frequencias utilizadas no ensaio
	std::vector<uint16_t> impFreqLSB;
	std::vector<uint16_t> impFreqMSB;
	// Vetores com as magnitudes e fases da impedancia
	std::vector<uint16_t> impMagLSB;
	std::vector<uint16_t> impMagMSB;
	std::vector<uint16_t> impFasLSB;
	std::vector<uint16_t> impFasMSB;

	bool continuar_ensaio = false;

	Ensaio();
	void setFrequencia(float);

	void iniciaEnsaio();

	void InterrupcaoTC4();
	void atualizaEnsaio();

	void calculaImpedanciaZC();
	void calculaImpedanciaSWF();

	void setFreqIni(float);
	void setFreqFim(float);
	void setFreqRelIni(float);
	void setFreqRelFim(float);
	void setPasso(float);
	void setPassoRel(float);
	void setFatorRegime(float);
	void setMetodoImp(int);

	float getFreqIni();
	float getFreqFim();
	float getFreqRelIni();
	float getFreqRelFim();
	float getPasso();
	float getPassoRel();
	float getFatorRegime();
};

#endif /* ENSAIO_H_ */
