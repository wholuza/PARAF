/*
 *
 * MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE
 *
 * Arquivo: Protocolo.h
 *
 * Linguagem: C++
 *
 * Descrição:
 * Protocolo de Comunicação Serial
 * Implementado no Arduino
 * (Cabeçalho)
 *
 * Autor : Filipe Sgarabotto Luza
 */

#ifndef PROTOCOLO_H_
#define PROTOCOLO_H_

#include "Arduino.h"

#define USBSERIAL SerialUSB
//#define USBSERIAL Serial

class Protocolo{
public:
	Protocolo();

	void iniciaSerial();
	void atualizaSerial();

	uint8_t enviaValor(uint16_t valor);
	bool enviaValores(uint16_t* valores, uint16_t tamanho);
	void _processa_mensagem();

	// Executado quando recebe o comando
	// Implementado no Ensaio
	virtual void setFreqIni(float) {};
	virtual void setFreqFim(float) {};
	virtual void setFreqRelIni(float) {};
	virtual void setFreqRelFim(float) {};
	virtual void setPasso(float) {};
	virtual void setPassoRel(float) {};
	virtual void setFatorRegime(float) {};
	virtual void setMetodoImp(int) {};

	virtual float getFreqIni() {return 0;};
	virtual float getFreqFim() {return 0;};
	virtual float getFreqRelIni() {return 0;};
	virtual float getFreqRelFim() {return 0;};
	virtual float getPasso() {return 0;};
	virtual float getPassoRel() {return 0;};
	virtual float getFatorRegime() {return 0;};

	virtual void iniciaEnsaio() {};

	virtual ~Protocolo();

protected:
	uint8_t mensagem[3];	// Mensagem de 4 bytes recebida via porta serial
	int _nbyte = 0;			// Contador de bytes recebidos

	enum codigos {
		// Códigos dos bytes enviados via serial
		mens_inicio 		= 	0x21, // !   - Inicio da Mensagem
		mens_final 			= 	0x23, // #   - Fim da Mensagem

		setFreqIniInt  		=  	0x46, // F   - Seta a parte inteira da frequencia inicial
		setFreqIniDec  		=  	0x47, // G   - Seta a parte decimal da frequencia inicial
		setFreqFimInt  		=  	0x48, // H   - Seta a parte inteira da frequencia final
		setFreqFimDec  		=  	0x49, // I   - Seta a parte decimal da frequencia final
		setPassoInt		 	=	0x4A, // J	 - Seta a parte inteira do passo
		setPassoDec		 	=  	0x4B, // K   - Seta a parte decimal do passo

		setFreqRelIniInt 	= 	0x4C, // L   - Seta a parte inteira da frequencia relevante inicial
		setFreqRelIniDec 	=  	0x4D, // M   - Seta a parte decimal da frequencia relevante inicial
		setFreqRelFimInt 	=  	0x4E, // N   - Seta a parte inteira da frequencia relevante final
		setFreqRelFimDec 	=  	0x4F, // O   - Seta a parte decimal da frequencia relevante final
		setaPassoRelInt 	=	0x50, // P	 - Seta a parte inteira do passo relevante
		setPassoRelDec 		=  	0x51, // Q   - Seta a parte decimal do passo relevante

		setFatorRegimeInt	= 	0x52, // R   - Seta a parte inteira do fator de regime permanente
		setFatorRegimeDec	= 	0x53, // S   - Seta a parte decimal do fator de regime permanente

		setMetodoZC			=   0X54, // T   - Seta o método de Cruzamento por Zero para o cálculo da Impedância
		setMetodoSWF		=   0X55, // U   - Seta o método de Ajuste de Curvas Senoidais para o cálculo da Impedância

		inicia_ensaio 		=	0x41, // A   - Inicia o ensaio

		size 				=	0x73, // s 	 - Tamanho do pacote
		byte_LS 			=	0x61, // a   - Byte menos significativo
		byte_MS 			=	0x7A, // z   - Byte mais significativo

	    rec_sucesso 		=	0x79, // y   - Valor recebido com sucesso
		rec_falha 			=   0x6E, // n   - Falha no recebimento do valor
		esc 				=  	0x1B  // ESC - Valor de escape que interrompe um envio
	};
};

#endif /* PROTOCOLO_H_ */
