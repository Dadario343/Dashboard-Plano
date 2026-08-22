# Dashboard-Plano

# Integrantes

| Nome | RM |
|---|---|
| *(Olavo Dadario Vianna Barreto )* | *(569272)* |
| *(Mateus de Oliveira Fernandes Neves )* | *(572431)* |
| *(Angela Sousa Takezawa)* | *(570797)* |
| *(Paulo Henrique Lira Bilac de Araujo)* | *(569496)* |
| *(Pedro Soares de Souza)* | *(571285)* |

# ReCarga — Dashboard de Recarga Veicular

## 📌 Sobre o projeto

O **ReCarga** é um protótipo acadêmico de um sistema de gerenciamento de recarga de veículos elétricos.

O projeto simula um estacionamento com várias vagas de recarga e mostra, em tempo real, informações como:

- Corrente consumida por cada carregador;
- Potência de cada veículo;
- Energia consumida em kWh;
- Custo da recarga;
- Carga total do barramento;
- Limite máximo de corrente;
- Quantidade de vagas ativas;
- Eventos de sobrecarga evitados;
- Receita acumulada;
- Diferença entre os planos pré-pago e pós-pago.

A interface funciona diretamente no navegador e o servidor é feito apenas com a biblioteca padrão do Python. **Não é necessário instalar Flask ou outras bibliotecas Python.**

---

## 🎯 Objetivo

O principal objetivo do protótipo é demonstrar uma lógica de gerenciamento de carga.

O estacionamento possui uma capacidade máxima de **40 A**. Os carregadores são divididos em dois tipos:

### Pré-pago

O plano pré-pago possui prioridade na distribuição de energia.

- Corrente-alvo: **16 A**;
- Preço: **R$ 1,35/kWh**;
- Possui capacidade reservada;
- Não é reduzido pela falta de capacidade disponível para o pós-pago.

### Pós-pago

O plano pós-pago utiliza a capacidade que sobra depois do atendimento dos carregadores pré-pagos.

- Corrente-alvo: **10 A**;
- Preço: **R$ 0,98/kWh**;
- Pode ser limitado quando a carga do estacionamento fica alta;
- Pode entrar em fila quando não existe capacidade suficiente.

---

## 🧩 Tecnologias utilizadas

O projeto é dividido em três partes principais:

### Python

Responsável pelo servidor, pela simulação e pelos cálculos.

Tecnologias utilizadas:

- Python 3;
- `http.server`;
- `threading`;
- `random`;
- `time`;
- `webbrowser`;
- `json`;
- `pathlib`.

Todas essas bibliotecas fazem parte da biblioteca padrão do Python.

### HTML

Responsável pela estrutura da página e pelos elementos do dashboard.

Arquivo:

```text
templates/index.html
```

### CSS

Responsável pelo visual, organização, cores, responsividade e componentes da interface.

Arquivo:

```text
static/style.css
```

### JavaScript

Responsável por buscar os dados do Python, atualizar a interface e criar o gráfico de receita.

Arquivo:

```text
static/app.js
```

### Chart.js

O gráfico de receita utiliza a biblioteca **Chart.js**, carregada diretamente pelo HTML através de uma CDN.

Por isso, é necessário ter acesso à internet para carregar o gráfico.

---

# 📁 Estrutura do projeto

```text
recarga-vscode-split/
│
├── app.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── app.js
    └── style.css
```

## `app.py`

É o arquivo principal do projeto.

Ele possui duas funções principais:

1. Simular o funcionamento dos carregadores;
2. Criar o servidor HTTP que entrega a página ao navegador.

---

## `templates/index.html`

É a página principal do dashboard.

Ela contém:

- Cabeçalho do sistema;
- Indicador da carga do barramento;
- Barra de capacidade;
- Indicadores das vagas;
- Cards dos carregadores;
- Gráfico de receita;
- Fórmulas de potência e energia;
- Informações dos planos;
- Estatísticas do sistema.

O HTML também importa o CSS e o Chart.js.

---

## `static/style.css`

Controla toda a aparência do sistema.

Entre outras coisas, define:

- Cores;
- Tipografia;
- Cards;
- Barra de carga;
- Indicadores;
- Botões;
- Layout em duas colunas;
- Responsividade para telas menores;
- Estados visuais dos carregadores.

O projeto utiliza as fontes **Space Grotesk**, **Inter** e **IBM Plex Mono** através do Google Fonts.

---

## `static/app.js`

É responsável pela comunicação entre o navegador e o servidor Python.

A cada **1,5 segundo**, o JavaScript consulta:

```text
/api/state
```

Depois disso, atualiza os elementos da tela.

Também permite:

- Ativar/desativar uma vaga;
- Alterar o plano de uma vaga;
- Selecionar uma vaga para visualizar seus dados;
- Atualizar o gráfico;
- Atualizar a barra de carga.

---

# ⚙️ Como funciona a simulação

A simulação é atualizada a cada:

```text
1,5 segundos
```

Esse valor está definido em:

```python
TICK_SECONDS = 1.5
```

O programa também converte esse intervalo para horas:

```python
TICK_HOURS = TICK_SECONDS / 3600
```

Isso é necessário para calcular a energia consumida.

---

# ⚡ Cálculo da potência

O sistema utiliza a fórmula:

```text
P = V × I
```

Onde:

- `P` = potência em watts;
- `V` = tensão;
- `I` = corrente.

No projeto, a tensão utilizada é:

```python
VOLTAGE = 230
```

Como o dashboard mostra a potência em kW, o resultado é dividido por 1000:

```python
power = cur * VOLTAGE / 1000
```

### Exemplo

Se um carregador estiver utilizando 10 A:

```text
P = 230 × 10
P = 2300 W
P = 2,3 kW
```

---

# 🔋 Cálculo da energia

A energia é calculada usando:

```text
E = P × Δt
```

Onde:

- `E` = energia em kWh;
- `P` = potência em kW;
- `Δt` = tempo em horas.

No código:

```python
dE = power * TICK_HOURS
```

O resultado é acumulado:

```python
s["energy_kwh"] += dE
```

Assim, quanto mais tempo o carregador permanece ativo, maior será o consumo acumulado.

---

# 💰 Cálculo do custo

O custo é calculado multiplicando a energia consumida pelo preço do plano.

Para o pré-pago:

```python
s["cost"] += dE * PRICE_PRE
```

Para o pós-pago:

```python
s["cost"] += dE * PRICE_POS
```

Os valores utilizados são:

```python
PRICE_PRE = 1.35
PRICE_POS = 0.98
```

Portanto:

```text
Pré-pago  → R$ 1,35/kWh
Pós-pago  → R$ 0,98/kWh
```

---

# 🔌 Controle de carga

O estacionamento possui:

```python
MAX_CAPACITY_A = 40
```

Ou seja, a capacidade máxima simulada é de **40 A**.

Primeiro o sistema calcula quanto os carregadores pré-pagos precisam:

```python
pre_target_total = sum(s["target_a"] for s in pre)
```

Se a demanda pré-paga ultrapassar o limite, ela é proporcionalmente ajustada.

Depois disso, o sistema calcula quanto sobrou:

```python
remaining = max(MAX_CAPACITY_A - reserved, 0)
```

Essa capacidade restante é destinada aos carregadores pós-pagos.

---

# 🚨 Controle de sobrecarga

O sistema verifica se a demanda do pós-pago é maior do que a capacidade restante:

```python
is_overloaded = pos_target_total > remaining + 0.01
```

Quando isso acontece, o sistema pode reduzir a corrente dos carregadores pós-pagos.

Os estados possíveis são:

### `carregando`

O carregador está funcionando normalmente.

### `reservado`

O carregador pré-pago está recebendo a capacidade reservada.

### `limitado`

O carregador pós-pago está funcionando com corrente reduzida.

### `em fila`

Não existe capacidade suficiente para o carregador pós-pago naquele momento.

### `livre`

A vaga está desativada.

---

# 🎲 Variação da corrente

A corrente possui uma pequena variação aleatória:

```python
jitter = random.uniform(0.9, 1.1)
```

Isso faz a simulação parecer mais próxima de uma leitura real de sensor.

Por exemplo, um carregador com alvo de 10 A pode apresentar valores próximos de:

```text
9,2 A
10,1 A
10,7 A
9,8 A
```

Essa variação é apenas uma simulação.

---

# 🚗 Vagas simuladas

O projeto começa com seis vagas:

```text
#1 — Onix EV
#2 — HB20 e
#3 — Kwid Volt
#4 — Compass e
#5 — Fastback e
#6 — Corolla e+
```

Inicialmente:

- Vagas 1 e 4 → pré-pago;
- Vagas 2 e 3 → pós-pago;
- Vagas 5 e 6 → desativadas.

Esses valores podem ser modificados diretamente no `app.py`.

---

# 🔄 API do servidor

O Python cria uma pequena API HTTP.

## GET `/`

Retorna a página principal:

```text
templates/index.html
```

## GET `/style.css`

Retorna:

```text
static/style.css
```

## GET `/app.js`

Retorna:

```text
static/app.js
```

## GET `/api/state`

Retorna os dados atuais da simulação em formato JSON.

Exemplo simplificado:

```json
{
  "stations": [],
  "history": [],
  "overload_events": 0,
  "total_load": 25.4,
  "total_revenue": 10.52,
  "total_energy": 8.21,
  "max_capacity": 40,
  "voltage": 230
}
```

## POST `/api/toggle_plug/<id>`

Ativa ou desativa um carregador.

Exemplo:

```text
/api/toggle_plug/1
```

## POST `/api/toggle_plan/<id>`

Troca o plano de uma vaga entre pré-pago e pós-pago.

Exemplo:

```text
/api/toggle_plan/1
```

---

# 🌐 Como rodar no VS Code

## 1. Instale o Python

É necessário ter **Python 3** instalado.

Para verificar:

```bash
python --version
```

ou:

```bash
python3 --version
```

---

## 2. Abra o projeto

Extraia o arquivo `.zip`.

Depois abra a pasta:

```text
recarga-vscode-split
```

no VS Code.

É importante manter esta estrutura:

```text
app.py
templates/
static/
```

Não mova o `app.py` para outra pasta.

---

## 3. Execute o programa

Abra:

```text
app.py
```

No VS Code, clique em:

```text
▶ Run Python File
```

Também é possível utilizar o terminal:

```bash
python app.py
```

No Linux/macOS, caso necessário:

```bash
python3 app.py
```

---

## 4. Acesse o dashboard

O programa utiliza a porta:

```text
5000
```

O endereço será:

```text
http://localhost:5000
```

O navegador normalmente será aberto automaticamente pelo próprio programa.

Se não abrir, copie o endereço acima para o navegador.

---

# 🛑 Como parar o programa

No terminal onde o Python está rodando, pressione:

```text
Ctrl + C
```

Isso encerra o servidor.

---

# ❌ Problemas comuns

## `python` não é reconhecido

O Python provavelmente não está instalado ou não foi adicionado ao PATH.

Instale o Python 3 e tente novamente.

---

## O navegador não abriu

Isso não significa necessariamente que o programa deu erro.

Abra manualmente:

```text
http://localhost:5000
```

---

## Erro dizendo que a porta 5000 está em uso

Outro programa pode estar utilizando a porta.

No `app.py`, altere:

```python
PORT = 5000
```

para, por exemplo:

```python
PORT = 5001
```

Depois execute novamente e acesse:

```text
http://localhost:5001
```

---

## A página não encontra o CSS ou JavaScript

Verifique se a estrutura está exatamente assim:

```text
recarga-vscode-split/
├── app.py
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

O `app.py` precisa estar no mesmo nível das pastas `templates` e `static`.

---

## O gráfico não aparece

O gráfico utiliza o Chart.js através de uma CDN:

```html
https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js
```

Portanto, verifique se o computador está conectado à internet.

O restante do servidor Python não depende de instalar bibliotecas externas.

---

# 🧠 Resumo da execução

O funcionamento geral pode ser entendido assim:

```text
                 ┌─────────────────┐
                 │     app.py      │
                 │ Python + API    │
                 └────────┬────────┘
                          │
                          │ JSON
                          ▼
                 ┌─────────────────┐
                 │    app.js       │
                 │ Atualiza dados  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   index.html    │
                 │    Dashboard    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    style.css    │
                 │ Visual da página │
                 └─────────────────┘
```

O Python simula os carregadores e disponibiliza os dados.

O JavaScript consulta esses dados.

O HTML organiza as informações.

O CSS deixa o dashboard visualmente organizado.

---

# 🔧 Onde alterar as configurações

As principais configurações estão no começo do `app.py`:

```python
VOLTAGE = 230
MAX_CAPACITY_A = 40
PRICE_PRE = 1.35
PRICE_POS = 0.98
TICK_SECONDS = 1.5
PORT = 5000
```

### Tensão

```python
VOLTAGE = 230
```

Altera a tensão usada no cálculo da potência.

### Capacidade máxima

```python
MAX_CAPACITY_A = 40
```

Altera o limite total de corrente do estacionamento.

### Preço pré-pago

```python
PRICE_PRE = 1.35
```

Altera o preço do kWh do plano pré-pago.

### Preço pós-pago

```python
PRICE_POS = 0.98
```

Altera o preço do kWh do plano pós-pago.

### Velocidade da simulação

```python
TICK_SECONDS = 1.5
```

Define de quanto em quanto tempo a simulação é atualizada.

### Porta

```python
PORT = 5000
```

Define a porta utilizada pelo servidor local.

---

# 📚 Observação importante

Este projeto é uma **simulação acadêmica**.

Ele não controla carregadores elétricos reais e não recebe dados reais de um ESP32 ou sensor de efeito Hall.

A interface representa como esse sistema poderia funcionar futuramente.

Na proposta apresentada no dashboard, um sistema real poderia utilizar:

```text
Sensor de efeito Hall
        ↓
      ESP32
        ↓
 Comunicação Bluetooth
        ↓
Aplicação / servidor
        ↓
Cálculo de potência,
energia e custo
        ↓
     Dashboard
```

Para transformar o protótipo em um sistema real, seria necessário implementar a comunicação com o ESP32, aquisição das leituras do sensor, autenticação, armazenamento dos dados e comunicação segura com os carregadores.

---

# 👨‍💻 Projeto

**Nome:** ReCarga  
**Tipo:** Protótipo acadêmico  
**Versão da interface:** v0.3  
**Backend:** Python  
**Frontend:** HTML + CSS + JavaScript  
**Gráficos:** Chart.js  
**Servidor:** `http.server`  
**Dependências Python externas:** Nenhuma
