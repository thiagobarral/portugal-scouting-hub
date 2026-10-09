# Portugal Scouting Hub

[English](README.md) | [Português](README.pt-BR.md)

**Analytics aplicado ao scouting para identificação e avaliação de talentos SUB-23 no futebol português.**

O Portugal Scouting Hub é um projeto de portfólio que combina coleta de dados, processamento, football analytics e um produto de dados interativo desenvolvido em Streamlit. A aplicação permite analisar perfis de jogadores, comparar atletas da mesma posição e buscar talentos por meio de métricas específicas por posição.

> **Importante:** o Profile Score é um indicador configurável de aderência ao perfil definido pelas métricas e pesos selecionados. Ele não deve ser interpretado como uma medida objetiva da qualidade geral de um jogador.

## Objetivo do Projeto

O projeto foi desenvolvido a partir de uma pergunta prática de recrutamento: **Como dados de desempenho podem ajudar a identificar e contextualizar jogadores SUB-23 no futebol português?**

O objetivo não é automatizar decisões de scouting. A aplicação oferece uma camada analítica para explorar perfis individuais, comparar jogadores do mesmo grupo posicional, filtrar candidatos SUB-23, contextualizar desempenho por percentis e criar perfis de scouting personalizados alterando os pesos das métricas.

## Principais Funcionalidades

- **Perfil do Jogador:** informações do atleta, participação na temporada, indicadores específicos da posição e radar de percentis.
- **Comparação:** comparação de dois jogadores do mesmo grupo posicional usando o mesmo benchmark.
- **Buscar Talentos:** filtros por posição, idade, minutos e valor de mercado, com pesos configuráveis por posição.
- **Análise do Resultado:** cobertura das métricas e características com maiores e menores percentis do candidato selecionado.
- **Interface bilíngue:** português e inglês, com português como idioma padrão.

## Pipeline de Dados

```text
Fonte de dados
    ↓
Scripts de coleta
    ↓
Dados brutos em JSON
    ↓
Limpeza e processamento
    ↓
Dataset processado de scouting
    ↓
Métricas /90 + benchmarks posicionais + percentis
    ↓
Profile Score
    ↓
Aplicação Streamlit + Plotly
```

O arquivo `data/processed/scouting_dataset_2025_26.csv` é utilizado pela aplicação local, mas **não é distribuído neste repositório**. Os arquivos brutos em `data/raw/` também permanecem fora do controle de versão. A disponibilização pública dos dados e da aplicação depende da confirmação das condições de uso com o SofaScore.

## Dataset

A aplicação utiliza **574 jogadores únicos** da base da liga portuguesa de 2025/26 usada neste projeto. O dataset processado local possui **46 campos**, selecionados da base original para manter apenas as informações e estatísticas necessárias ao produto.

Ele inclui identificadores, nome, clube, data de nascimento, idade calculada, indicador SUB-23, posição, altura, pé preferencial, país, valor de mercado, minutos, jogos, titularidades e estatísticas ofensivas, de passe, defensivas e de goleiros utilizadas pelo motor analítico.

Métricas derivadas, como valores /90, percentis posicionais e Profile Score, são calculadas pelo código e não armazenadas como observações originais da fonte.

## Metodologia de Scouting

### Definição de SUB-23

A idade é calculada usando **1º de julho de 2025** como data de referência para a temporada 2025/26. O jogador é classificado como SUB-23 quando ainda não havia completado 23 anos nessa data.

### Mínimo de Minutos

É utilizado um limite de **450 minutos** para o benchmark estatístico, equivalente a cinco partidas completas. Jogadores abaixo desse limite não são excluídos da base; o limite é usado para construir uma referência estatística mais estável.

### Grupos Posicionais

| Grupo Posicional | Posições Detalhadas |
|---|---|
| Goleiro | GK |
| Zagueiro | DC |
| Lateral | DL, DR |
| Meio-Campo | DM, MC, AM |
| Ponta | ML, MR, LW, RW |
| Atacante | ST |

### Normalização por 90 Minutos

Estatísticas de volume são normalizadas para 90 minutos:

```text
metrica_por90 = metrica / minutos_jogados × 90
```

Métricas percentuais não são convertidas para /90.

### Benchmark Posicional

Os percentis são calculados em relação a **todos os jogadores elegíveis do mesmo grupo posicional com pelo menos 450 minutos**, e não apenas aos SUB-23. Assim, um candidato jovem é contextualizado em relação ao benchmark mais amplo de sua posição na liga.

### Percentis

Para a maioria das métricas, valores maiores geram percentis maiores. Em métricas nas quais valores menores são desejáveis, a direção é invertida; na metodologia atual, `goalsConceded_per90` é tratada dessa forma.

Um percentil próximo de 100 indica que o valor do jogador está próximo do topo do benchmark da mesma posição naquela métrica.

### Métricas por Posição

| Posição | Métricas |
|---|---|
| Atacante | Gols/90, xG/90, Finalizações/90, Finalizações no Alvo/90, Assistências/90, xA/90 |
| Ponta | Gols/90, xG/90, Assistências/90, xA/90, Passes-Chave/90, Dribles Bem-Sucedidos/90 |
| Meio-Campo | Assistências/90, xA/90, Passes-Chave/90, Passes Certos no Terço Final/90, Recuperações/90, Interceptações/90 |
| Lateral | Assistências/90, xA/90, Passes-Chave/90, Passes Certos no Terço Final/90, Dribles Bem-Sucedidos/90, Interceptações/90 |
| Zagueiro | Desarmes/90, Interceptações/90, Cortes/90, Recuperações/90, Duelos Aéreos Ganhos %, Passes Certos % |
| Goleiro | Defesas/90, Gols Evitados/90, Gols Sofridos/90, Saídas em Bolas Altas/90, Saídas Bem-Sucedidas/90, Passes Certos % |

Essas métricas representam os perfis analíticos escolhidos para o projeto, e não uma definição universal de desempenho para cada posição.

### Profile Score

O Profile Score é uma média ponderada dos percentis das métricas do jogador dentro de sua posição:

```text
Profile Score = Σ(percentil da métrica × peso da métrica) / Σ(pesos das métricas disponíveis)
```

O usuário pode alterar os pesos no Buscar Talentos. Métricas ausentes são retiradas do cálculo, em vez de receberem zero, e a aplicação informa a cobertura das métricas.

O score responde: **Quão aderente é o perfil estatístico deste jogador às métricas e pesos atualmente selecionados, em comparação com jogadores da mesma posição?** Ele não representa um ranking objetivo de qualidade geral ou potencial futuro.

## Estrutura do Projeto

```text
football-analytics/
├── app/
│   └── app.py
├── data/
│   ├── processed/
│   │   └── scouting_dataset_2025_26.csv  # local; não versionado
│   └── raw/                       # ignorado pelo Git
├── notebooks/
│   ├── 01_data_quality.ipynb
│   └── 02_player_analysis.ipynb
├── src/
│   ├── scouting.py
│   └── scripts de coleta / processamento
├── .gitignore
├── requirements.txt
├── README.md
└── README.pt-BR.md
```

`src/scouting.py` concentra a lógica analítica reutilizável utilizada pela aplicação, incluindo preparação dos dados, cálculos /90, pools posicionais, percentis e ranking do Buscar Talentos.

## Tecnologias

Python · Pandas · NumPy · Streamlit · Plotly · Matplotlib · curl-cffi · Jupyter Notebook

## Instalação

```bash
git clone https://github.com/thiagobarral/portugal-scouting-hub.git
cd portugal-scouting-hub
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Executando a Aplicação

Na raiz do projeto:

```bash
python -m streamlit run app/app.py
```

**Pré-requisito:** o arquivo `data/processed/scouting_dataset_2025_26.csv` deve estar disponível localmente. Ele não é fornecido no repositório. Sem esse arquivo, a aplicação não pode ser executada com os dados reais. Não há, neste momento, um dataset público para download nem uma instância pública hospedada.

## Fonte dos Dados e Condições de Uso

**Fonte consultada no desenvolvimento:** [SofaScore](https://www.sofascore.com/). O projeto foi desenvolvido com estatísticas de jogadores da Liga Portugal 2025/26, obtidas por meio de endpoints utilizados pelo site, internos/não documentados. O dataset local foi limpo, selecionado e transformado para análise de scouting; essas transformações não alteram a atribuição da fonte original.

A base local contém 574 jogadores e 46 campos. Os registros originais e processados **não são redistribuídos neste repositório**. A autorização para redistribuição dos dados e exibição pública das estatísticas no Streamlit ainda não foi confirmada. A referência à fonte não implica afiliação, endosso ou licença concedida pelo SofaScore.

Os scripts de coleta e processamento documentam o fluxo técnico do projeto, mas não representam uma API oficial ou uma autorização de uso. Os endpoints podem mudar, e a execução de novas coletas deve observar os termos e permissões aplicáveis. Imagens de jogadores e clubes podem depender de recursos externos.

## Limitações

Este projeto é uma ferramenta analítica de apoio ao scouting e não substitui análise contextual, observação ao vivo ou análise de vídeo. Dados estatísticos não capturam todos os aspectos táticos e qualitativos; a normalização /90 não elimina diferenças de função, força da equipe, contexto tático ou tamanho da amostra; valores de mercado são estimativas; o limite de 450 minutos é uma escolha metodológica; grupos posicionais simplificam funções mais específicas; e métricas e pesos influenciam diretamente o Profile Score. Métricas de goleiros também são fortemente influenciadas pelo contexto da equipe e dos adversários.

Um Profile Score alto representa aderência ao perfil estatístico selecionado, e não garantia de qualidade, potencial ou sucesso de contratação.

## Possíveis Evoluções

Possíveis extensões incluem outras temporadas e tendências históricas, seletores de liga/temporada, perfis mais específicos por função, métricas contextuais adicionais, exportação de relatórios e deploy público da aplicação Streamlit, sujeito às permissões de uso dos dados.

Modelos preditivos de Machine Learning e similaridade automática entre jogadores estão intencionalmente fora do escopo atual.

## Autor

Projeto de portfólio com foco em **Data Analytics, Data Engineering e Football Analytics**.
