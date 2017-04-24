/*
 *
 * MEDIÇÃO DE PARÂMETROS DE ALTO-FALANTES COM O ARDUINO DUE
 *
 * Arquivo: AFPAR_ARDUINO.ino
 *
 * Linguagem: C++
 *
 * Descrição:
 * Arquivo de Esboço (sketch)
 * Implementado no Arduino
 * (Código Fonte)
 *
 * Autor : Filipe Sgarabotto Luza
 */

#include "Arduino.h"
#include "Ensaio.h"

// Cria o objeto
Ensaio ens = Ensaio();

void setup()
{
	// Inicializa a porta serial
	ens.iniciaSerial();
}


void loop(){
	// Atualiza a porta serial e o ensaio
	ens.atualizaSerial();
	ens.atualizaEnsaio();
}

// Interrupção do Time Counter 4
extern "C"{
	void TC4_Handler(){
		ens.InterrupcaoTC4();
	}

}

