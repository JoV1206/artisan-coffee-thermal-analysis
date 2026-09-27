# Pipeline de Análise Térmica e Modelação Preditiva para Torrefação de Café

Este repositório contém o código-fonte em Python desenvolvido para o processamento de sinais, análise estatística e modelação preditiva de perfis térmicos de torrefação de café. Os algoritmos processam ficheiros de registo gerados pelo software Artisan (.alog) para extrair assinaturas termodinâmicas e avaliar a viabilidade de prever o instante do Primeiro Estalo (First Crack - FC) utilizando apenas os primeiros minutos do processo.

## 1. Conjunto de Dados (Dataset) Associado

Os algoritmos presentes neste repositório foram concebidos para consumir o banco de dados aberto de perfis térmicos e variáveis físicas. Para executar o código localmente, é necessário descarregar o dataset oficial e extrair os ficheiros .alog e .csv para dentro da pasta dados/ na raiz deste projeto.

**Referência e citação obrigatória dos dados:**
> [1] J. V. Almeida Teodoro, G. Ximenes Verdan Pontes, L. Moretz-Sohn David Vieira, and H. LOPES GALVAO, “Open Dataset of Coffee Roasting Profiles and Physical Variables”. Zenodo, Jul. 15, 2026. doi: 10.5281/zenodo.21383047.

## 2. Estrutura do Repositório

O projeto está organizado de forma modular, separando a ingestão de dados, a modelação de Machine Learning e a geração de gráficos académicos de alta resolução.

├── dados/                 # Pasta de destino para os ficheiros do Zenodo (metadados e .alog)
├── src/
│   ├── analyse.py         # Ingestão, filtragem cronológica e interpolação temporal
│   ├── baseline.py        # Engenharia de atributos (features) e avaliação de modelos preditivos
│   ├── make_fig.py        # Renderização do perfil termodinâmico de uma torra específica
│   └── make_figs23.py     # Renderização do envelope populacional e distribuição de metadados
├── requirements.txt       # Fixação das versões do ecossistema Python
└── README.md


## 3. Requisitos e Instalação

O ambiente de execução requer o Python 3.8 ou superior. Recomenda-se a criação de um ambiente virtual (ex: .venv) antes da instalação das dependências.

As bibliotecas utilizadas garantem a reprodutibilidade dos cálculos estatísticos e da grelha de interpolação:

pip install -r requirements.txt


O ficheiro requirements.txt inclui:
* numpy==1.26.4
* pandas==2.2.2
* scikit-learn==1.5.1
* matplotlib==3.9.1

## 4. Fluxo de Execução dos Algoritmos

O processamento deve seguir a ordem lógica do ciclo de dados, executando os scripts a partir do diretório raiz.

### Etapa 1: Sanitização e Grelha Comum
O script varre a pasta dados/, remove os registos inválidos (verificando a consistência cronológica dos eventos) e aplica uma interpolação linear nos dados de Temperatura do Grão (BT). Os perfis são transpostos para uma grelha de tempo comum (passos de 0,05 min) para permitir operações matriciais.

python src/analyse.py

* Saídas geradas: curves.npy, grid.npy e tabela agregada analise.csv.

### Etapa 2: Modelação Preditiva (Machine Learning)
O módulo avalia algoritmos (como Ridge Regression e Gradient Boosting Regressor) para prever o instante do FC com base apenas nos primeiros 4,0 minutos de torra. Implementa extração de atributos cinéticos (Taxa de Ascensão - RoR, Turning Point) e utiliza validação cruzada rigorosa Leave-One-Out (LOO).

python src/baseline.py

* Saídas geradas: Métricas no terminal (MAE, RMSE, R2) e a tabela de atributos baseline_features.csv.

### Etapa 3: Visualização e Gráficoss (600 DPI)
Scripts dedicados à exportação de figuras com tipografia Serif (Liberation/Times New Roman).

python src/make_fig.py
python src/make_figs23.py

* Saídas geradas: 
  * fig1_perfil.png: Curvas BT, ET e RoR com demarcação exata dos eventos.
  * fig2_overlay.png: Sobreposição de todos os perfis sobre o envelope estatístico populacional (Percentis 10, 50 e 90).
  * fig3_metadados.png: Distribuição física das amostras agrícolas (altitude, massa, temperatura/umidade).

## 5. Licenciamento

O código-fonte desenvolvido para esta análise está distribuído sob a Licença MIT. 

O conjunto de dados de perfis térmicos depositado no Zenodo é regido de forma independente e disponibilizado ao abrigo da licença Creative Commons Attribution 4.0 International (CC BY 4.0). Pode partilhar e adaptar o material para qualquer fim, desde que atribua o devido crédito aos autores originais e indique se foram feitas alterações.
