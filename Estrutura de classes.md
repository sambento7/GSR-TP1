# Estrutura de Classes e Componentes do Projeto L-SNMPvS

Este documento resume os principais módulos, classes, atributos e métodos do projeto, com explicações claras para consulta rápida.

---

## Sensor – devices/sensor.py

**Objetivo:** Simular um sensor (ex: luz ou temperatura) que gera valores lidos pelo agente.

**Atributos:**
- id: identificador do sensor.
- tipo: tipo de sensor.
- min_valor, max_valor: intervalo de valores possíveis.
- valor_atual: último valor gerado.
- last_sampling_time: timestamp da última leitura.
- start_time: hora de arranque (para uptime).

**Métodos:**
- ler_valor(): gera novo valor aleatório e atualiza estado.
- obter_estado(): devolve dicionário com os dados atuais do sensor.

---

## Actuator – devices/actuator.py

**Objetivo:** Simular um atuador (ex: luz ou A/C) que pode ser controlado.

**Atributos:**
- id: identificador do atuador.
- tipo: tipo de atuador.
- min_valor, max_valor: intervalo permitido.
- estado: valor configurado.
- last_control_time: timestamp da última alteração.

**Métodos:**
- configurar(valor): altera estado se valor for válido.
- obter_estado(): devolve estado atual como dicionário.

---

## LMIBvS – l_mibvs.py

**Objetivo:** Simular a L-MIBvS que armazena sensores, atuadores e info do dispositivo.

**Atributos:**
- device_info: dicionário com ID, tipo, uptime, etc.
- sensors: lista de objetos Sensor.
- actuators: lista de objetos Actuator.

**Métodos:**
- get_value(iid): devolve valor baseado no IID.
- set_value(iid, valor): altera valor se permitido.

---

## ProtocolHandler – protocol.py

**Objetivo:** Processar e construir mensagens L-SNMPvS.

**Métodos:**
- construir_mensagem(...): cria mensagem codificada.
- parse_mensagem(msg): interpreta mensagem recebida.
- validar_mensagem(dados): verifica integridade e formato dos dados.

---

## Agent – agent.py

**Objetivo:** Agente que processa mensagens UDP, consulta a MIB e responde.

**Atributos:**
- porta: porta UDP usada.
- mib: instância de LMIBvS.
- protocol: instância de ProtocolHandler.
- msg_ids: IDs já processados.

**Métodos:**
- escutar(): laço principal de receção.
- processar_get(iids): lê valores da MIB.
- processar_set(iids, valores): tenta alterar valores.

---

## Manager – manager.py

**Objetivo:** Envia pedidos GET/SET ao agente e trata respostas.

**Atributos:**
- host, porta: IP e porta do agente.
- protocol: instância de ProtocolHandler.

**Métodos:**
- enviar_get(iids): envia pedido de leitura.
- enviar_set(iids, valores): envia pedido de escrita.

---

## timestamp_utils.py – utils/

**Objetivo:** Gerar timestamps no formato L-SNMPvS.

**Funções:**
- gerar_timestamp_data(): data/hora atual.
- gerar_timestamp_uptime(start): uptime formatado.

---

## iid_utils.py – utils/

**Objetivo:** Codificar/descodificar IIDs (identificadores de instância).

**Funções:**
- codificar_iid(iid): codifica IID como string.
- descodificar_iid(data): converte string em IID.