/*
 *
 * MEDIÇÃO DE PARÂMETROS DO ALTO-FALANTE COM O ARDUINO
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
	analogWriteResolution(12);
	analogWrite(DAC0, 2048);

	// Seta a resolução da entrada analógica (12-bits)
	analogReadResolution(12);

	// Inicializa as frequencias, o passo, o fator de regime permamente e o método de cálculo
	_freqIni = 0;
	_freqFim = 0;
	_passo = 0;
	_freqRelIni = 0;
	_freqRelFim = 0;
	_passoRel = 0;
	_frequencia = 0;
	_fatorRegime = 0;
	_metodoImp = 0;

	// Inicializa todos os contadores utilizados no ensaio
		uAcumuladorFase = 0;
		uIncrementoFase = 0;
		indiceAmostras = 0;
		ciclosRealizados = 0;
		ciclosCapturar = 0;
}


void Ensaio::setFrequencia(float frequencia){
	// Seta a frequencia atual do ensaioo
	_frequencia = frequencia;

	// Calcula o incremento de fase a ser adicionado a cada interrupção
	uIncrementoFase = _frequencia*AMOSTRAS_POR_INTERRUPCAO_FP;

	// Calcula o número de ciclos completos necessários para obter as amostras
	ciclosCapturar = ceil(AMOSTRAS_CAPTURADAS/(TX_AMOSTRAGEM/_frequencia));
}


void Ensaio::iniciaEnsaio(){
	// Inicia o ensaio

	// Seta a frequencia inicial
	setFrequencia(_freqIni);

	// Zera todos os contadores
	uAcumuladorFase = 0;
	indiceAmostras = 0;
	ciclosRealizados = 0;
	
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
		ciclosRealizados++;

		// Caso não esteja no regime permanente
		if (ciclosRealizados < _fatorRegime*_frequencia) {
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

	//////////////////////////////

	// Grava o valor da saída
	// Placa velha
	//amostrasSaida[indiceAmostras] = saidaAnalogica;

	// Nova Placa
	volatile uint16_t entradaTensao = analogRead(0);
	amostrasSaida[indiceAmostras] = entradaTensao;

	// Le o valor da entrada analogica
	volatile uint16_t entradaAnalogica = analogRead(1);

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

		// Se já capturou todas as amostras para a frequência atual
		if (indiceAmostras >= AMOSTRAS_CAPTURADAS){
			
			// Se foi um ensaio com uma única frequencia
			if (abs(_passo) == 0 or _freqIni == _freqFim){
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC0,2048);
				
				continuar_ensaio = false;
				
				// Envia os valores das amostras da saída
				enviaValores(amostrasSaida, AMOSTRAS_CAPTURADAS);
				// Envia os valores das amostras da entrada
				enviaValores(amostrasEntrada, AMOSTRAS_CAPTURADAS);					
			}			
			
			// Se já terminou um ensaio de múltiplas frequências
			else if (_frequencia > _freqFim){	
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC0,2048);
				
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

			// Caso não tenha terminado o ensaio de múltiplas frequências
			else{
				// Desativa a interrupção
				NVIC_DisableIRQ(TC4_IRQn);
				// Seta o DAC no valor zero
				analogWrite(DAC0,2048);
				
				// Calcula a impedancia para essa frequencia
				if (_metodoImp == 0){
					calculaImpedanciaSWF();
				}
				else if (_metodoImp == 1){
					calculaImpedanciaZC();
				}

				// Caso esteja nas frequencias relevantes
				if ((_frequencia > _freqRelIni) and (_frequencia < _freqRelFim)){
					setFrequencia(_frequencia*_passoRel);
				}
				// Caso não esteja nas frequencias relevantes
				else{
					setFrequencia(_frequencia*_passo);
				}
				
				// Zera todos os contadores
				uAcumuladorFase = 0;
				indiceAmostras = 0;
				ciclosRealizados = 0;

				// Habilita a interrupção
				NVIC_EnableIRQ(TC4_IRQn);
			}
		}
	}
}

void Ensaio::calculaImpedanciaZC(){
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
	
	// Calcula a fase da impedancia
	float32_t impFas = 360.0*((zeroEntrada - zeroSaidaA)/(zeroSaidaB - zeroSaidaA));

	// Corrige o ângulo
	while   (impFas >  360.0) impFas -= 360.0;
	while   (impFas < -360.0) impFas += 360.0;
	if      (impFas >  180.0) impFas -= 360.0;
	else if (impFas < -180.0) impFas += 360.0;

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


void Ensaio::calculaImpedanciaSWF(){
	// Calcula a Impedância pelo Método de Ajuste de Curvas Senoidais

	float32_t N = AMOSTRAS_CAPTURADAS;
	float32_t T = 1/TX_AMOSTRAGEM;
	float32_t W = 2*PI*_frequencia;

	// Estimativas iniciais para as amplitudes em fase e quadratura
	float32_t pA1 = 2048.0;
	float32_t pA2 = 2048.0;
	float32_t pB1 = 2048.0;
	float32_t pB2 = 2048.0;

	// Calcula as matrizes E e G
	float32_t E[7][7] = { 0 };
	float32_t G[7] = { 0 };
	for (int n = 0; n < AMOSTRAS_CAPTURADAS; n++){
		float32_t WTn = W*T*n;

		float32_t cosWTn;
		float32_t sinWTn;
		cosWTn = cos(WTn);
		sinWTn = sin(WTn);

		float32_t r1 = -2.0*PI*pA1*T*n*sinWTn + 2.0*PI*pB1*T*n*cosWTn;
		float32_t r2 = -2.0*PI*pA2*T*n*sinWTn + 2.0*PI*pB2*T*n*cosWTn;

		E[0][0] += cosWTn*cosWTn;
		E[0][1] += cosWTn*sinWTn;
		E[0][2] += cosWTn;
		E[0][3] += cosWTn*r1;
		E[1][1] += sinWTn*sinWTn;
		E[1][2] += sinWTn;
		E[1][3] += sinWTn*r1;
		E[2][3] += r1;
		E[3][3] += r1*r1 + r2*r2;
		E[3][4] += cosWTn*r2;
		E[3][5] += sinWTn*r2;
		E[3][6] += r2;

		G[0] += cosWTn*amostrasSaida[n];
		G[1] += sinWTn*amostrasSaida[n];
		G[2] += amostrasSaida[n];
		G[3] += amostrasSaida[n]*r1 + amostrasEntrada[n]*r2;
		G[4] += cosWTn*amostrasEntrada[n];
		G[5] += sinWTn*amostrasEntrada[n];
		G[6] += amostrasEntrada[n];
	}

	// Define os demais valores de E
	E[1][0] = E[0][1];
	E[2][0] = E[0][2];
	E[2][1] = E[1][2];
	E[2][2] = N;
	E[3][0] = E[0][3];
	E[3][1] = E[1][3];
	E[3][2] = E[2][3];
	E[4][3] = E[3][4];
	E[4][4] = E[0][0];
	E[4][5] = E[0][1];
	E[4][6] = E[0][2];
	E[5][3] = E[3][5];
	E[5][4] = E[0][1];
	E[5][5] = E[1][1];
	E[5][6] = E[1][2];
	E[6][3] = E[3][6];
	E[6][4] = E[0][2];
	E[6][5] = E[1][2];
	E[6][6] = N;

	// Matriz E
	arm_matrix_instance_f32 E_matrix;
	arm_mat_init_f32(&E_matrix, 7, 7, (float32_t *)E);

	// Calcula a inversa da matriz E
	float32_t E_INV[7][7] = { 0 };
	arm_matrix_instance_f32 E_matrixINV;
	arm_mat_init_f32(&E_matrixINV, 7, 7, (float32_t *)E_INV);
	arm_mat_inverse_f32(&E_matrix, &E_matrixINV);

	// Vetor G
	arm_matrix_instance_f32 G_matrix;
	arm_mat_init_f32(&G_matrix, 7, 1, (float32_t *)G);

	// Multiplica a inversa de E por G
	float32_t X[7]  = { 0 };
	arm_matrix_instance_f32 X_matrix;
	arm_mat_init_f32(&X_matrix, 7, 1, (float32_t *)X);
	arm_mat_mult_f32(&E_matrixINV, &G_matrix, &X_matrix);

	// Calcula o módulo da Impedância
	float32_t magSaida;
	float32_t magEntrada;
	arm_sqrt_f32(X[0]*X[0] + X[1]*X[1], &magSaida);
	arm_sqrt_f32(X[4]*X[4] + X[5]*X[5], &magEntrada);
	float32_t impMag = magSaida/magEntrada;

	// Calcula a fase da Impedância
	float32_t fasSaida = atan(X[0] / X[1]);
	float32_t fasEntrada = atan(X[4] / X[5]);
	float32_t impFas = 180.0*(fasSaida - fasEntrada)/PI;

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

void Ensaio::setFreqIni(float frequenciaInicial){
		_freqIni = frequenciaInicial;
		// Caso a frequencia relevante não seja definida
		if (_freqRelIni == 0){
			_freqRelIni = _freqIni;
		}
}

void Ensaio::setFreqFim(float frequenciaFinal){
		_freqFim = frequenciaFinal;
		// Caso a frequencia relevante não seja definida
		if (_freqRelFim == 0){
			_freqRelFim = _freqFim;
		}
}

void Ensaio::setFreqRelIni(float freqRelevInicial){
		_freqRelIni = freqRelevInicial;
}

void Ensaio::setFreqRelFim(float freqRelevFinal){
		_freqRelFim = freqRelevFinal;
}

void Ensaio::setPasso(float passo){
		_passo = passo;
		// Caso o passo relevante não seja definido
		if (_passoRel == 0){
			_passoRel = _passo;
		}
}

void Ensaio::setPassoRel(float passoRelev){
		_passoRel = passoRelev;
}

void Ensaio::setFatorRegime(float fatorRegime){
	_fatorRegime = fatorRegime;
}

void Ensaio::setMetodoImp(int metodo){
	_metodoImp = metodo;
}

float Ensaio::getFreqIni(){
	return _freqIni;
}

float Ensaio::getFreqFim(){
	return _freqFim;
}

float Ensaio::getFreqRelIni(){
	return _freqRelIni;
}

float Ensaio::getFreqRelFim(){
	return _freqRelFim;
}

float Ensaio::getPasso(){
	return _passo;
}

float Ensaio::getPassoRel(){
	return _passoRel;
}

float Ensaio::getFatorRegime(){
	return _fatorRegime;
}

Ensaio::Protocolo::~Protocolo(){
	USBSERIAL.end();
}
