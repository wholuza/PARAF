/*
 *
 * MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE
 *
 * Arquivo: Protocolo.cpp
 *
 * Linguagem: C++
 *
 * Descrição:
 * Protocolo de Comunicação Serial
 * Implementado no Arduino
 * (Código Fonte)
 *
 * Autor : Filipe Sgarabotto Luza
 */

#include "Protocolo.h"

Protocolo::Protocolo(){
}

void Protocolo::iniciaSerial(){
	// Inicializa a porta serial
	USBSERIAL.begin(230400);
	while(!USBSERIAL) {};
}

void Protocolo::atualizaSerial(){
	// Se houver dados na porta serial
	if (USBSERIAL.available()){
		volatile uint8_t byte_rec = USBSERIAL.read(); // Recebe um byte

		// Verifica o byte recebido
		switch (_nbyte){
			case 0:
				// Verifica se é o byte de início da mensagem
				if (byte_rec == codigos::mens_inicio) _nbyte++;
				break;
			case 1: // Primeiro byte da mensagem
				mensagem[0] = byte_rec;
				_nbyte++;
				break;
			case 2:	// Segundo byte da mensagem
				mensagem[1] = byte_rec;
				_nbyte++;
				break;
			case 3: // Terceiro byte da mensagem
				mensagem[2] = byte_rec;
				_nbyte++;
				break;
			case 4:
				// Verifica se é o byte final da mensagem
				if (byte_rec == codigos::mens_final)
				{
					_processa_mensagem();
				}
				// Descarta a mensagem caso não seja o byte final
				_nbyte = 0;
		}

	}
}

void Protocolo::_processa_mensagem(){
	// Variáveis utilizadas
	uint16_t freqIniInt, freqIniDec, freqFimInt, freqFimDec, passoInt, passoDec;
	uint16_t freqRelIniInt, freqRelIniDec, freqRelFimInt, freqRelFimDec, passoRelInt, passoRelDec;
	uint16_t fatorRegimeInt, fatorRegimeDec;

	// Analisa o código enviado na mensagem e chama a função correspondente
	switch(mensagem[0]){
				case codigos::inicia_ensaio:
					iniciaEnsaio();
					break;

				case codigos::setFreqIniInt:
					// Compõe o valor da parte inteira da frequencia inicial
					freqIniInt = mensagem[1] + (mensagem[2] << 8);
					setFreqIni(freqIniInt);
					break;

				case codigos::setFreqIniDec:
					// Compõe o valor da parte decimal da frequencia inicial
					freqIniDec = mensagem[1] + (mensagem[2] << 8);
					freqIniInt = abs(getFreqIni());
					setFreqIni((uint32_t)((freqIniInt << 16) + freqIniDec) /65536.0);
					break;

				case codigos::setFreqFimInt:
					// Compõe o valor da parte inteira da frequencia final
					freqFimInt = mensagem[1] + (mensagem[2] << 8);
					setFreqFim(freqFimInt);
					break;

				case codigos::setFreqFimDec:
					// Compõe o valor da parte decimal da frequencia final
					freqFimDec = mensagem[1] + (mensagem[2] << 8);
					freqFimInt = abs(getFreqFim());
					setFreqFim((uint32_t)((freqFimInt << 16) + freqFimDec) /65536.0);
					break;

				case codigos::setPassoInt:
					// Compõe o valor da parte inteira do passo
					passoInt = mensagem[1] + (mensagem[2] << 8);
					setPasso(passoInt);
					break;

				case codigos::setPassoDec:
					// Compõe o valor da parte decimal do passo
					passoDec = mensagem[1] + (mensagem[2] << 8);
					passoInt = abs(getPasso());
					setPasso((uint32_t)((passoInt << 16) + passoDec) /65536.0);
					break;

				case codigos::setFreqRelIniInt:
					// Compõe o valor da parte inteira da frequencia inicial relevante
					freqRelIniInt = mensagem[1] + (mensagem[2] << 8);
					setFreqRelIni(freqRelIniInt);
					break;

				case codigos::setFreqRelIniDec:
					// Compõe o valor da parte decimal da frequencia inicial relevante
					freqRelIniDec = mensagem[1] + (mensagem[2] << 8);
					freqRelIniInt = abs(getFreqRelIni());
					setFreqRelIni((uint32_t)((freqRelIniInt << 16) + freqRelIniDec) /65536.0);
					break;

				case codigos::setFreqRelFimInt:
					// Compõe o valor da parte inteira da frequencia final relevante
					freqRelFimInt = mensagem[1] + (mensagem[2] << 8);
					setFreqRelFim(freqRelFimInt);
					break;

				case codigos::setFreqRelFimDec:
					// Compõe o valor da parte decimal da frequencia final relevante
					freqRelFimDec = mensagem[1] + (mensagem[2] << 8);
					freqRelFimInt = abs(getFreqRelFim());
					setFreqRelFim((uint32_t)((freqRelFimInt << 16) + freqRelFimDec) /65536.0);
					break;

				case codigos::setaPassoRelInt:
					// Compõe o valor da parte inteira do passo relevante
					passoRelInt = mensagem[1] + (mensagem[2] << 8);
					setPassoRel(passoRelInt);
					break;

				case codigos::setPassoRelDec:
					// Compõe o valor da parte decimal do passo relevante
					passoRelDec = mensagem[1] + (mensagem[2] << 8);
					passoRelInt = abs(getPassoRel());
					setPassoRel((uint32_t)((passoRelInt << 16) + passoRelDec) /65536.0);
					break;

				case codigos::setFatorRegimeInt:
					// Compõe o valor da parte inteira do fator de regime permanente
					fatorRegimeInt = mensagem[1] + (mensagem[2] << 8);
					setFatorRegime(fatorRegimeInt);
					break;

				case codigos::setFatorRegimeDec:
					// Compõe o valor da parte decimal do fator de regime permanente
					fatorRegimeDec = mensagem[1] + (mensagem[2] << 8);
					fatorRegimeInt = abs(getFatorRegime());
					setFatorRegime((uint32_t)((fatorRegimeInt << 16) + fatorRegimeDec) /65536.0);
					break;

				case codigos::setMetodoSWF:
					setMetodoImp(0);
					break;

				case codigos::setMetodoZC:
					setMetodoImp(1);
					break;
			}
}

uint8_t Protocolo::enviaValor(uint16_t valor){
	// Envia um valor de 16 bits

	// Isola o byte menos significativo
	volatile uint8_t valor_LSB = (valor & 0x00FF);
	// Isola o byte mais significativo
	volatile uint8_t valor_MSB = (valor & 0xFF00) >> 8;

	// Envia uma mensagem para o byte menos significativo
	USBSERIAL.write(codigos::mens_inicio);
	USBSERIAL.write(codigos::byte_LS);
	USBSERIAL.write(valor_LSB);
	USBSERIAL.write(codigos::mens_final);

	// Envia uma mensagem para o byte mais significativo
	USBSERIAL.write(codigos::mens_inicio);
	USBSERIAL.write(codigos::byte_MS);
	USBSERIAL.write(valor_MSB);
	USBSERIAL.write(codigos::mens_final);

	// Recebe a resposta
	while (!USBSERIAL.available()) {};
	uint8_t resposta = USBSERIAL.read();

	return resposta;
}

bool Protocolo::enviaValores(uint16_t* valores, uint16_t tamanho){
	// Envia o número de valores
	uint8_t resposta = enviaValor(tamanho);

	// Se receber o código de escape interrompe o envio
	if (resposta == codigos::esc){
		return false;
	}

	// Envia cada um dos valores
	int n = 0;
	while(n < tamanho)
	{
		uint8_t resposta = enviaValor(valores[n]);

		// Se foi enviado com sucesso parte para o próximo valor
		if (resposta == codigos::rec_sucesso){
			n++;
		}
		// Se receber o código de escape interrompe o envio
		else if (resposta == codigos::esc){
			return false;
		}
	}
	return true;
}
