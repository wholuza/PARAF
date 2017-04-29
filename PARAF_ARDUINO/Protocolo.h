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
	virtual void setaFrequenciaI(uint16_t) {};
	virtual void setaFrequenciaD(uint16_t) {};
	virtual void setaCiclosPorFreq(uint16_t) {};
	virtual void iniciaEnsaio() {};
	// Executado quando recebe o valor de escape
	virtual void escape() {};


	virtual ~Protocolo();
protected:
	uint8_t mensagem[3];	// Mensagem de 4 bytes recebida via porta serial
	int _nbyte = 0;			// Contador de bytes recebidos

	enum codigos {
		// Códigos dos bytes enviados via serial
		mens_inicio = 		0x21, // !   - Inicio da Mensagem
		mens_final = 		0x23, // #   - Fim da Mensagem

		seta_frequenciaI =  0x46, // F   - Comando para setar a parte inteira da frequencia
		seta_frequenciaD =  0x47, // G   - Comando para setar a parte decimal da frequencia
		seta_ciclos = 		0x43, // C   - Comando para setar o número de ciclos por frequencia
		inicia_ensaio =		0x41, // A   - Comando para iniciar o ensaio

		size = 				0x73, // s 	 - Tamanho do pacote
		byte_LS = 			0x61, // a   - Byte menos significativo
		byte_MS = 			0x7A, // z   - Byte mais significativo

	    rec_sucesso =	 	0x79, // y   - Valor recebido com sucesso
		rec_falha =         0x6E, // n   - Falha no recebimento do valor
		esc =            	0x1B  // ESC - Valor de escape que interrompe um envio
	};
};

#endif /* PROTOCOLO_H_ */
