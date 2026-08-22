# ⚡ ReCarga — Dashboard de Recarga Veicular

## 👥 Integrantes

| Nome                                | RM     |
| ----------------------------------- | ------ |
| Olavo Dadario Vianna Barreto        | 569272 |
| Mateus de Oliveira Fernandes Neves  | 572431 |
| Angela Sousa Takezawa               | 570797 |
| Paulo Henrique Lira Bilac de Araujo | 569496 |
| Pedro Soares de Souza               | 571285 |
| Jhon Cutile Titirico                | 571976 |

---

## 📌 Sobre o projeto

O **ReCarga** é um protótipo de um sistema inteligente para gerenciamento de recarga de veículos elétricos. A solução foi desenvolvida pensando em ambientes que possuem diversos pontos de recarga e precisam administrar uma capacidade elétrica limitada.

Com o crescimento do número de veículos elétricos, locais como estacionamentos, empresas e condomínios podem enfrentar problemas quando vários veículos são carregados ao mesmo tempo. Uma demanda elevada pode ultrapassar a capacidade disponível da instalação, causando sobrecargas ou exigindo investimentos maiores na infraestrutura elétrica.

O ReCarga busca solucionar esse problema por meio de um sistema que gerencia a demanda de potência, distribui a capacidade disponível entre os carregadores e permite o acompanhamento das recargas através de uma interface interativa.

Além do gerenciamento de energia, o sistema também simula a cobrança das recargas de acordo com o consumo de cada veículo. Dessa forma, o projeto reúne em uma única solução o **controle da demanda elétrica, o gerenciamento inteligente das recargas e o acompanhamento dos usuários e gestores através de um dashboard**.

---

## 🎯 A solução

O sistema simula um estacionamento com diversas vagas para veículos elétricos. Cada vaga possui um carregador que pode estar ativo ou desativado e utiliza uma determinada quantidade de energia.

O ReCarga monitora constantemente a demanda dos carregadores e verifica se a capacidade máxima do sistema está sendo respeitada. Quando a demanda aumenta, o sistema distribui a energia disponível de forma inteligente, evitando que o limite seja ultrapassado.

A interface permite acompanhar informações como:

* ⚡ Corrente utilizada por cada carregador;
* 🔋 Potência consumida;
* 📊 Energia acumulada em kWh;
* 💰 Custo individual das recargas;
* 🔌 Carga total do sistema;
* 🚨 Situações de sobrecarga evitadas;
* 🅿️ Status das vagas;
* 📈 Receita acumulada.

---

## ⚡ Gerenciamento inteligente da demanda

O protótipo trabalha com uma capacidade máxima simulada de **40 A**. Todos os carregadores ativos compartilham essa capacidade.

Para tornar a simulação mais próxima de um cenário comercial, o sistema trabalha com dois tipos de plano: **pré-pago** e **pós-pago**.

### 🟢 Pré-pago

Os carregadores do plano pré-pago possuem prioridade na distribuição da capacidade disponível.

* Corrente-alvo de **16 A**;
* Preço de **R$ 1,35 por kWh**;
* Capacidade priorizada no sistema.

### 🔵 Pós-pago

Os carregadores do plano pós-pago utilizam a capacidade restante após o atendimento das demandas prioritárias.

* Corrente-alvo de **10 A**;
* Preço de **R$ 0,98 por kWh**;
* Pode ter a corrente reduzida quando a demanda está elevada;
* Pode aguardar caso não exista capacidade suficiente.

Essa lógica permite demonstrar como uma infraestrutura com recursos limitados pode gerenciar diversos veículos simultaneamente sem ultrapassar sua capacidade máxima.

---

## 💰 Sistema de cobrança

Cada recarga possui seu consumo acompanhado durante o funcionamento da simulação.

O sistema calcula a energia consumida em **kWh** e utiliza o valor do plano selecionado para calcular o custo da recarga. Dessa forma, é possível acompanhar quanto cada veículo consumiu e qual foi o valor correspondente.

A solução também registra a receita acumulada do sistema, permitindo que gestores tenham uma visão geral da operação.

Essa funcionalidade demonstra como o gerenciamento da infraestrutura de recarga pode ser combinado com um modelo de cobrança para usuários.

---

## 🖥️ Dashboard e experiência do usuário

O ReCarga possui uma interface desenvolvida para apresentar as informações do sistema de forma visual e organizada.

Através do dashboard, é possível:

* Visualizar a carga atual do sistema;
* Acompanhar o consumo dos carregadores;
* Ativar ou desativar vagas;
* Alternar o plano de uma vaga;
* Consultar o consumo de energia;
* Acompanhar o custo das recargas;
* Visualizar o status de cada carregador;
* Acompanhar a receita acumulada.

Os carregadores podem assumir diferentes estados, como **carregando**, **reservado**, **limitado**, **em fila** ou **livre**, facilitando a identificação da situação de cada vaga.

---

## 🚀 Diferenciais da solução

O ReCarga não se limita a apresentar o consumo dos veículos. O projeto combina diferentes funcionalidades em um único protótipo:

* **Distribuição inteligente da capacidade elétrica disponível**;
* **Controle para evitar sobrecargas**;
* **Priorização de diferentes tipos de usuários ou planos**;
* **Sistema de cobrança baseado no consumo**;
* **Monitoramento em tempo real**;
* **Dashboard interativo para usuários e gestores**.

A proposta foi pensada para ser aplicável em cenários reais onde a quantidade de veículos elétricos pode ser maior do que a capacidade disponível para carregamento simultâneo.

---

## 🧪 Protótipo atual

O projeto já possui uma versão funcional que pode ser executada localmente.

Atualmente, o protótipo conta com:

* Simulação de múltiplos carregadores;
* Gerenciamento da capacidade máxima;
* Controle de prioridade entre os planos;
* Cálculo de potência e energia;
* Sistema de cobrança;
* Atualização dos dados em tempo real;
* Interface interativa no navegador.

Isso permite demonstrar na prática o funcionamento da solução, indo além da ideia ou conceito inicial.

---

## 🧩 Tecnologias utilizadas

O projeto foi desenvolvido utilizando:

* **Python 3** — responsável pelo servidor, simulação e cálculos;
* **HTML** — estrutura da interface;
* **CSS** — organização e responsividade do dashboard;
* **JavaScript** — comunicação com o servidor e atualização dos dados;
* **Chart.js** — visualização gráfica das informações.

O projeto utiliza principalmente recursos da biblioteca padrão do Python, evitando a necessidade de instalar frameworks complexos para executar o protótipo.

---

## 📁 Estrutura do projeto

```text
Dashboard-Plano-main/
│
├── Dashboard/
│   └── app.py
│
├── template/
│   └── index.html
│
└── Static/
    ├── app.js
    └── style.css
```

---

## ⚙️ Como executar

### 1. Abra o projeto no VS Code

Após extrair o projeto, abra a pasta principal no VS Code.

### 2. Execute o servidor

Abra o arquivo `app.py` e execute o programa utilizando o botão **Run Python File** ou pelo terminal.

```bash
python app.py
```

Caso necessário:

```bash
python3 app.py
```

### 3. Acesse o dashboard

Com o servidor em execução, abra o navegador no endereço:

```text
http://localhost:5000
```

---

## 🔮 Próximos passos

Apesar de o projeto atual ser uma simulação, a proposta pode evoluir para uma aplicação conectada a uma infraestrutura real.

Entre as possíveis evoluções estão:

* Integração com carregadores reais;
* Leitura de dados através de sensores;
* Integração com dispositivos como ESP32;
* Autenticação de usuários;
* Histórico de recargas;
* Banco de dados;
* Sistema de pagamentos;
* Aplicação mobile;
* Comunicação segura com os carregadores.

Uma possível evolução da arquitetura seria:

```text
Sensores / Carregadores
          ↓
       ESP32
          ↓
Comunicação com o servidor
          ↓
Gerenciamento da demanda
          ↓
Cálculo de consumo e cobrança
          ↓
Dashboard para usuários e gestores
```

---

## 💡 Conclusão

O **ReCarga** apresenta uma proposta para tornar o gerenciamento de recarga de veículos elétricos mais eficiente e organizado.

Por meio da distribuição inteligente da potência, do acompanhamento do consumo e de um sistema de cobrança integrado, o projeto demonstra como diferentes aspectos da infraestrutura de recarga podem ser administrados em conjunto.

O protótipo atual representa uma base funcional que pode ser evoluída para aplicações em ambientes comerciais, oferecendo benefícios tanto para os gestores da infraestrutura quanto para os usuários dos veículos elétricos.

**Frontend:** HTML + CSS + JavaScript  
**Gráficos:** Chart.js  
**Servidor:** `http.server`  
**Dependências Python externas:** Nenhuma
