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
	uint16_t frequenciaIniInt;
	uint16_t frequenciaIniDec;
	uint16_t frequenciaFimInt;
	uint16_t frequenciaFimDec;
	uint16_t passoInt;
	uint16_t passoDec;

	// Analisa o código enviado na mensagem e chama a função correspondente
	switch(mensagem[0]){
				case codigos::inicia_ensaio:
					iniciaEnsaio();
					break;

				case codigos::seta_freqIniInt:
					// Compõe o valor da parte inteira da frequencia inicial
					frequenciaIniInt = mensagem[1] + (mensagem[2] << 8);
					setFrequenciaInicial(frequenciaIniInt);
					break;

				case codigos::seta_freqIniDec:
					// Compõe o valor da parte decimal da frequencia inicial
					frequenciaIniDec = mensagem[1] + (mensagem[2] << 8);
					frequenciaIniInt = abs(getFrequenciaInicial());
					setFrequenciaInicial((uint32_t)((frequenciaIniInt << 16) + frequenciaIniDec) /65536.0);
					break;

				case codigos::seta_freqFimInt:
					// Compõe o valor da parte inteira da frequencia final
					frequenciaFimInt = mensagem[1] + (mensagem[2] << 8);
					setFrequenciaFinal(frequenciaFimInt);
					break;

				case codigos::seta_freqFimDec:
					// Compõe o valor da parte decimal da frequencia final
					frequenciaFimDec = mensagem[1] + (mensagem[2] << 8);
					frequenciaFimInt = abs(getFrequenciaFinal());
					setFrequenciaFinal((uint32_t)((frequenciaFimInt << 16) + frequenciaFimDec) /65536.0);
					break;

				case codigos::seta_passoInt:
					// Compõe o valor da parte inteira do passo
					passoInt = mensagem[1] + (mensagem[2] << 8);
					setPasso(passoInt);
					break;

				case codigos::seta_passoDec:
					// Compõe o valor da parte decimal do passo
					passoDec = mensagem[1] + (mensagem[2] << 8);
					passoInt = abs(getPasso());
					setPasso((uint32_t)((passoInt << 16) + passoDec) /65536.0);
					break;

				case codigos::seta_ciclos:
					// Compõe o valor do número de ciclos por frequência
					setCiclosPorFreq(mensagem[1] + (mensagem[2] << 8));
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
