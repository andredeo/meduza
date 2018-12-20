#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Importa as bibliotecas
from pyzabbix import ZabbixSender,ZabbixMetric
from zabbix_api import ZabbixAPI
from datetime import datetime, timedelta
from time import localtime, strftime
import sys
import serial
import math
import struct
import time

# Zerando as variáveis, em situações normais não é preciso, mas ajuda se ocorrerem erros no loop
Valor_USD = 0
Valor_MQA = 0
Valor_QAS = 0
Valor_MVS = 0
Valor_MXS = 0
Valor_MNS = 0
Valor_LMS = 0
Valor_TMP = 0
Valor_UMD = 0

# Configuracao da Serial
n_serial1 = "/dev/ttyUSB0"

# Seta valores da serial
ser = serial.Serial(n_serial1, 9600, timeout=0.5,parity=serial.PARITY_NONE)

# Espera 2 segundos para a comunicacao com a serial ser estabelecida
time.sleep(2)

# Tempo de Resposta e Pooling
TEMPO1 = 1.0  # Tempo de Resposta, eh tempo entre o envio do pacote da base para sensor e da devolucao do pacote do sensor para base

# Identificacao da Base
ID_base1 = 0

# Identificacao do Sensor
ID_sensor1 = 1

# Variavel de Data e Hora
timenow = datetime.now()

# Configuracoes do Zabbix na Biliblioteca zabbix_api
zapi = ZabbixAPI(server="http://127.0.0.1/zabbix")
zapi.login("Admin", "zabbix")

# Inicio o sistema

# Se o primeiro argumento informado for 1, entra no modo interativo
if int(sys.argv[1]) == 1:
	# Cria o vetor Pacote
	PacoteTX = {}
	PacoteRX = {}

	# Cria o vetor para salvar os valores das potências
	listaPotDesviod ={}
	listaPotDesviou ={}

	# Cria Pacote de 52 Bytes com valor "0" em todas as posições
	for i in range(52):
		PacoteTX[i] = 0
		PacoteRX[i] = 0
	
	# Solicita identificação da Base e do Sensor
	ID_base = raw_input('ID_base: ')
	ID_sensor = raw_input('ID_sensor: ')
	
	# Inicia o loop infinito
	while True:
		try:
			# Cria as variáveis para calcular desvio de potência
			contador_tot = 0
			contador_pot = 0
			potmediad = 0.0
			potacumulad = 0.0
			PotMedDbd = 0.0
			contador_err = 0
			potmediau = 0.0
			potacumulau = 0.0
			PotMedDbu = 0.0
			PER = 0
			AcumDPd = 0
			AcumDPu = 0
			AcumVad = 0
			AcumVau = 0
			MedDPd = 0
			MedDPu = 0
			DPd = 0
			DPu = 0
			PotMaxd = -200
			PotMind = 10
			PotMaxu = -200
			PotMinu = 10
		
			# Imprime na tela o menu de opções
			print ' '
			print 'Escolha um comandos abaixos e pressione enter: '
			print '1 - Realiza Medidas: '
			print 's - Para sair: '

			# Leitura da opção do menu escolhida
			Opcao = raw_input('Entre com a Opção = ')

			if Opcao == "1":
				num_medidas = raw_input('Entre com o número de medidas = ')

				for j in range(int(num_medidas)):    #Inicializa uma lista para gravar as potências e calcular o desvio padrão
					listaPotDesviod[j] = 0
					listaPotDesviou[j] = 0

				Log = strftime("Coleta_de_dados_%Y_%m_%d_%H-%M-%S.txt")
				print "Arquivo de log: %s" % Log
				S = open(Log, 'w')

				# Laço para realização das medidas
				for j in range(int(num_medidas)):
					# Limpa o buffer da serial
					ser.flushInput()

					# Coloca no pacote o ID_sensor e ID_base
					PacoteTX[8] = int(ID_sensor)
					PacoteTX[10] = int(ID_base)

					# TX pacote - envia pacote para a base transmitir
					for i in range(52):
						ser.write(chr(PacoteTX[i]))

					# Tempo de espera para que receba a resposta do sensor
					time.sleep(0.1)

					# RX Pacote - Recebe o pacote enviado pelo sensor
					PacoteRX = ser.read(52) # faz a leitura de 52 bytes do buffer que recebe da serial pela COM

					# Checa se recebeu 52 bytes 
					if len(PacoteRX) == 52:
						# Realiza as Medidas de RSSI
						rssid = ord(PacoteRX[0]) # RSSI_DownLink
						rssiu = ord(PacoteRX[2]) # RSSI_UpLink

						#RSSI Downlink
						if rssid > 128:
							RSSId=((rssid-256)/2.0)-81

						else:
							RSSId=(rssid/2.0)-81

						#RSSI Uplink
						if rssiu > 128:
								RSSIu=((rssiu-256)/2.0)-81

						else:
								RSSIu=(rssiu/2.0)-81
								 
						# Seta as variáveis que serão utilizadas na leitura
						
						# No pacote recebido estão as informações enviadas pelo sensor.
						# Para saber as informações do pacote consultar o mapa do pacote do Radiuino.
						# Nos Bytes "X" e "Y" estão a conversão do ADC"X" do Arduino, que vai ser um valor entre 0 e 1023,
						# pois o conversor analógico para digital tem 10 bits. Portanto são necessários dois Bytes.
						# No Byte "X" vem o inteiro e no Byte "Y" o resto.
						# Para encontrar o valor basta multiplicar o inteiro por 256 e somar com o resto.
						# Vai resultar em um numero como por exemplo 235, então dividimos por 10 para chegar ao valor correto de 23,5
						# Estes valores são armazenados em variáveis do script para serem utilizados.
						# Utilizando como exemplo os Bytes 17 e 18, respectivamente como "X" e "Y",
						# e as variáveis ad0h e ad0l, ficaria assim:
						# Retira do pacote os Bytes 17 e 18, que estão com o valor inteiro e o resto
						# ad0h = ord(PacoteRX[17]) # Inteiro
						# ad0l = ord(PacoteRX[18]) # Resto
						
						usdh = ord(PacoteRX[16]) # Ultrasson - Inteiro
						mqah = ord(PacoteRX[17]) # Média Qualidade do Ar - Inteiro
						mqal = ord(PacoteRX[18]) # Média Qualidade do Ar - Resto
						usdl = ord(PacoteRX[19]) # Ultrasson - Resto
						qash = ord(PacoteRX[20]) # Qualidade do Ar Standart - Inteiro
						qasl = ord(PacoteRX[21]) # Qualidade do Ar Standart - Resto
						mvsh = ord(PacoteRX[23]) # Média Volume do Som - Inteiro
						mvsl = ord(PacoteRX[24]) # Média Volume do Som - Resto
						mxsh = ord(PacoteRX[26]) # Máximo Volume do Som - Inteiro
						mxsl = ord(PacoteRX[27]) # Máximo Volume do Som - Resto
						mnsh = ord(PacoteRX[29]) # Mínimo Volume do Som - Inteiro
						mnsl = ord(PacoteRX[30]) # Mínimo Volume do Som - Resto
						lmsh = ord(PacoteRX[31]) # Luminosidade - Inteiro
						lmsl = ord(PacoteRX[32]) # Luminosidade - Resto
						tmps = ord(PacoteRX[34]) # Temperatura - Sinal de Positivo ou Negativo
						tmph = ord(PacoteRX[35]) # Temperatura - Inteiro
						tmpl = ord(PacoteRX[36]) # Temperatura - Resto
						umdh = ord(PacoteRX[38]) # Umidade - Inteiro
						umdl = ord(PacoteRX[39]) # Umidade - Resto
						
						# Converte o número recebido para um valor entre 0 e 1023
						# Depois divide por 10 para ter a representação correta
						Valor_USD = (usdh * 256 + usdl)
						Valor_MQA = (mqah * 256 + mqal)
						Valor_QAS = (qash * 256 + qasl)
						Valor_MVS = (mvsh * 256 + mvsl)
						Valor_MXS = (mxsh * 256 + mxsl)
						Valor_MNS = (mnsh * 256 + mnsl)
						Valor_LMS = (lmsh * 256 + lmsl)
						Valor_TMP = (tmph * 256 + tmpl)
						Valor_TMP = (Valor_TMP / 10.0)
						Valor_UMD = (umdh * 256 + umdl)
						Valor_UMD = (Valor_UMD/10.0)
						
						if RSSId > PotMaxd:
							PotMaxd = RSSId

						if RSSId < PotMind:   
							PotMind = RSSId

						if RSSIu > PotMaxu:
							PotMaxu = RSSIu

						if RSSIu < PotMinu:   
							PotMinu = RSSIu

						#Grava a potência de downlink para cálculo do desvio padrão
						listaPotDesviod[contador_pot]= RSSId
						#Grava a potência de uplink para cálculo do desvio padrão
						listaPotDesviou[contador_pot]= RSSIu
						#incrementa o contador utilizado para a média de potência e para o desvio padrão
						contador_pot=contador_pot+1

						# Imprime na tela as leituras
						print time.asctime(),'Medida : ', j + 1, 'Ultrasson: ', Valor_USD, 'Média Qualidade do Ar: ', Valor_MQA, 'Qualidade do Ar Standart: ', Valor_QAS, 'Média Volume do Som: ', Valor_MVS, 'Máximo Volume do Som: ', Valor_MXS, 'Mínimo Volume do Som: ', Valor_MNS, 'Luminosidade: ', Valor_LMS, '%', 'Temperatura: ', Valor_TMP, 'ºC', 'Umidade: ', Valor_UMD, '%', 'RSSIu = ', RSSIu, 'dBm', 'RSSId = ', RSSId, 'dBm'
						# Gera o log
						print >>S,time.asctime(),'Medida : ', j + 1, 'Ultrasson: ', Valor_USD, 'Média Qualidade do Ar: ', Valor_MQA, 'Qualidade do Ar Standart: ', Valor_QAS, 'Média Volume do Som: ', Valor_MVS, 'Máximo Volume do Som: ', Valor_MXS, 'Mínimo Volume do Som: ', Valor_MNS, 'Luminosidade: ', Valor_LMS, '%', 'Temperatura: ', Valor_TMP, 'ºC', 'Umidade: ', Valor_UMD, '%', 'RSSIu = ', RSSIu, 'dBm', 'RSSId = ', RSSId, 'dBm'

						# Define as chaves dos itens no Zabbix
						L1=["Valor_USD", "Valor_MQA", "Valor_QAS", "Valor_MVS", "Valor_MXS", "Valor_MNS", "Valor_LMS", "Valor_TMP", "Valor_UMD", "RSSIu", "RSSId"]

						# Define as variáveis do Script que alimentarão os itens
						L2=[Valor_USD, Valor_MQA, Valor_QAS, Valor_MVS, Valor_MXS, Valor_MNS, Valor_LMS, Valor_TMP, Valor_UMD, RSSIu, RSSId]

						# Faz um loop para enviar cada valor de métrica para cada item no Zabbix
						x = 0
						while x<len(L1):
							# Envia Temperatura para o Zabbix
							metrics = []
							m = ZabbixMetric('meduZa', L1[x], L2[x])
							metrics.append(m)
							zbx = ZabbixSender(zabbix_server='127.0.0.1', zabbix_port=10051, use_config=None)
							zbx.send(metrics)
							x+=1

						time.sleep(int(TEMPO1))


					else:
						contador_err = contador_err + 1
						print 'Erro'
						time.sleep(int(TEMPO1))
					
					contador_tot = contador_tot + 1
					
				if contador_pot == 0:
					contador_pot = 1

				for l in range(0,contador_pot):
					AcumVad =AcumVad+ listaPotDesviod[l]   #acumula o valor da lista para calcular a média
					AcumVau =AcumVau+ listaPotDesviou[l]   #acumula o valor da lista para calcular a média

				MedDPd = float (AcumVad)/float(contador_pot)
				MedDPu = float (AcumVau)/float(contador_pot)

				for m in range(0,contador_pot):
					AcumDPd =AcumDPd+ pow((listaPotDesviod[m]- MedDPd),2)   #acumula o valor da variancia
					AcumDPu =AcumDPu+ pow((listaPotDesviou[m]- MedDPu),2)  #acumula o valor da variancia

				DPd = float (AcumDPd)/float(contador_pot)   #termina o calculo da variancia
				DPu = float (AcumDPu)/float(contador_pot)   #termina o calculo da variancia

				potmediad = potacumulad /contador_pot

				if potmediad==0:
					potmediad=0
				else:
					PotMedDbd = 10*math.log10(potmediad)
				
				print 'A Potência Média de Downlink em dBm foi:', PotMedDbd,' dBm'
				print 'A Potência Máxima de Downlink em dBm foi:', PotMaxd,' dBm'
				print 'A Potência Mínima de Downlink em dBm foi:', PotMind,' dBm'
				print 'O Desvio Padrão do sinal de Downlink foi:', DPd

				print >>S,time.asctime(),'A Potência Média de Downlink em dBm foi:', PotMedDbd,' dBm'
				print >>S,time.asctime(),'A Potência Máxima de Downlink em dBm foi:', PotMaxd,' dBm'
				print >>S,time.asctime(),'A Potência Mínima de Downlink em dBm foi:', PotMind,' dBm'
				print >>S,time.asctime(),'O Desvio Padrão do sinal de Downlink foi:', DPd

				potmediau = potacumulau /contador_pot

				if potmediau==0:
					potmediau=0
				else:
					PotMedDbu = 10*math.log10(potmediau)
				
				print 'A Potência Média de Uplink em dBm foi:', PotMedDbu,' dBm'
				print 'A Potência Máxima de Uplink em dBm foi:', PotMaxu,' dBm'
				print 'A Potência Mínima de Uplink em dBm foi:', PotMinu,' dBm'
				print 'O Desvio Padrão do sinal de Uplink foi:', DPu


				print >>S,time.asctime(),'A Potência Média de Uplink em dBm foi:', PotMedDbu,' dBm'
				print >>S,time.asctime(),'A Potência Máxima de Uplink em dBm foi:', PotMaxu,' dBm'
				print >>S,time.asctime(),'A Potência Mínima de Uplink em dBm foi:', PotMinu,' dBm'
				print >>S,time.asctime(),'O Desvio Padrão do sinal de Uplink foi:', DPu

				PER = (float(contador_err)/float(contador_tot))* 100
				print 'A PER foi de:', float(PER),'%'
				print >>S,time.asctime(),'A PER foi de:', float(PER),'%'

				# Define as chaves dos itens no Zabbix
				L1=["PotMedDbd", "PotMaxd", "PotMind", "DPd", "PotMedDbu", "PotMaxu", "PotMinu", "DPu", "PER"]

				# Define as variáveis do Script que alimentarão os itens
				L2=[PotMedDbd, PotMaxd, PotMind, DPd, PotMedDbu, PotMaxu, PotMinu, DPu, PER]

				# Faz um loop para enviar cada valor de métrica para cada item no Zabbix
				x = 0
				while x<len(L1):
					# Envia Temperatura para o Zabbix
					metrics = []
					m = ZabbixMetric('meduZa', L1[x], L2[x])
					metrics.append(m)
					zbx = ZabbixSender(zabbix_server='127.0.0.1', zabbix_port=10051, use_config=None)
					zbx.send(metrics)
					x+=1

				time.sleep(int(TEMPO1))

				S.close()
				
			else:
				# Opção de saída
				# Fecha a porta COM
				ser.close() 
				print 'Fim da Execução'  # escreve na tela
				break 
				ser.flushInput()
		
		
		except KeyboardInterrupt:
			S.close()
			ser.close()
			break	

	ser.close()

	exit()
else:
	# Cria o Pacote de 52 bytes com valor zero em todas as posicoes
	Pacote1 = {}

	for i in range(0,52):
		Pacote1[i] = 0

	# Se o primeiro argumento informado for 48, significa que nao devemos pegar o estada anterior da lampada
	if int(sys.argv[1]) == 48:
		# Faz um loop para setar o valor no pacote
		x = 40
		while x<48:
			Pacote1[x] = int(sys.argv[2])
			x += 1
	else:
		if int(sys.argv[1]) == 49:
			Pacote1[49] = int(sys.argv[2])
		else:
			if int(sys.argv[1]) == 50:
				Pacote1[50] = int(sys.argv[2])
			else:
				# Recupera o estado atual das lampadas
				itens = zapi.item.get({"output":["itemid", "lastvalue"],"filter":{"itemid":["25442", "25448", "25457", "25459", "25465", "25466", "25468", "25470"]} })

				L=[]
				for x in itens:
					valor = x["lastvalue"]
					L.append(str(valor))
				
				# Cria o pacote com o estado atual das lampadas
				x = 0
				for  i in range(40,48):
					Pacote1[i] = L[x]
					x += 1

	#  Cria o pacote com o novo comando
	Pacote1[int(sys.argv[1])] = int(sys.argv[2])

	# Limpa o buffer da serial
	ser.flushInput() 

	# Envia o sinal de radio com a configuracao atual das lampadas

	# Execucao da comunicacao
	Pacote1[8] = int(ID_sensor1)  #endereco de destino do pacote
	Pacote1[10] = int(ID_base1)   #endereco de origem do pacote

	# Comunicacao da Base com o Sensor

	#Transmissao do pacote de leitura
	for i in range(0,52):
		TXbyte = chr(int(Pacote1[i]))
   		ser.write(TXbyte)

	# Aguarda a resposta do sensor
	time.sleep(int(TEMPO1))

	# Novas Interacoes do usuario

	# Envia o sinal de radio com a nova configuracao das lampadas

	# Comunicacao da Base com o Sensor

	line = ser.read(52) # faz a leitura de 52 bytes do buffer que recebe da serial pela COM
	if len(line) == 52:
		rssid = ord(line[0]) # RSSI_DownLink
		rssiu = ord(line[2]) # RSSI_UpLink

		#RSSI Downlink
		if rssid > 128:
			RSSId=((rssid-256)/2.0)-81

		else:
			RSSId=(rssid/2.0)-81

		#RSSI Uplink
		if rssiu > 128:
			RSSIu=((rssiu-256)/2.0)-81

		else:
		 	RSSIu=(rssiu/2.0)-81

		# Identificacao da posicao do pacote que representa cada lampada na placa
		A40 = ord(line[40])
		A41 = ord(line[41])
		A42 = ord(line[42])
		A43 = ord(line[43])
		A44 = ord(line[44])
		A45 = ord(line[45])
		A46 = ord(line[46])
		A47 = ord(line[47])
		A48 = ord(line[48]) # Realizar a operacao em todas as lampadas

		L1=[A40,A41,A42,A43,A44,A45,A46,A47,A48]

		# Limpa o Buffer da serial de entrada
		ser.flushInput()

		# Configuracoes do Zabbix na Biliblioteca pyzabbix

		# Cria um dicionario com as chaves dos itens
		valores = { "40": "lampcoz01",
			    "41": "lampquar01",
		   	    "42": "lampsala01",
			    "43": "lampban01",
			    "44": "lampquar02",
			    "45": "lampsuite",
			    "46": "lampban02",
			    "47": "lampsala02" }

		# Cria um dicionario com o nome dos hosts
		hosts = { "40": "Cozinha 01",
			  "41": "Quarto 01",
			  "42": "Sala 01",
			  "43": "Banheiro 01",
			  "44": "Quarto 02",
			  "45": "Suite",
			  "46": "Banheiro 02",
			  "47": "Sala 02" }
		# Faz um loop para enviar  a configuracao de cada lampada para o Zabbix
		x = 40
		y = 0
		while x<48:
			# Envia o comando para o Zabbix
			metrics = []
			m = ZabbixMetric(hosts[str(x)],valores[str(x)],str(L1[y]))
			metrics.append(m)
			zbx = ZabbixSender(zabbix_server='127.0.0.1', zabbix_port=10051, use_config=None)
			zbx.send(metrics)
			x+=1
			y+=1
		print "Comando Executado com sucesso!"

	else:
		# Limpa o Buffer da serial de entrada
		ser.flushInput()
		print "Por Favor envie o comando novamente!"

	# Fecha as portas seriais
	ser.close()
	time.sleep(0.5)
