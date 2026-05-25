# 🐱 Mestre de Verdade — Especificação do Produto

> Dashboard web de inteligência para o Cartola FC: análise histórica de atletas, recomendação de escalação, comparador por posição e alertas de valorização.

---

## 1. Visão Geral

**Nome do produto:** Mestre de Verdade  
**Tipo:** Web App (SPA — Single Page Application)  
**Fonte de dados:** API pública do Cartola FC (`https://api.cartola.globo.com`)  
**Objetivo central:** Ajudar o usuário a escalar o melhor time possível a cada rodada, com base em dados históricos e análise estatística dos atletas.

---

## 2. Problema que Resolve

O Cartola FC exige decisões rápidas com informações fragmentadas. O usuário precisa navegar entre múltiplas fontes para entender:
- Quem está em boa fase?
- Quem vai valorizar?
- Qual é o melhor custo-benefício por posição?

O **Mestre de Verdade** centraliza tudo isso em um único painel visual, inteligente e atualizado.

---

## 3. Funcionalidades Principais (MVP)

### 3.1 🎯 Recomendação de Escalação por Rodada
**Descrição:** O sistema sugere o time ideal para a rodada atual com base em critérios ponderados.

**Critérios de pontuação:**
- Média de pontos nas últimas 5 rodadas (peso 40%)
- Tendência de valorização (peso 25%)
- Status do atleta: disponível, dúvida, suspenso, contundido (peso 20%)
- Mando de campo (casa vs. visitante) nas últimas partidas (peso 15%)

**Comportamento:**
- Filtra atletas por posição respeitando esquema tático do usuário (ex: 4-3-3, 3-4-3)
- Respeita o orçamento disponível do usuário
- Destaca o capitão recomendado (atleta com maior pontuação esperada)
- Exibe score de confiança para cada sugestão (ex: ⭐⭐⭐⭐)

**Inputs do usuário:**
- Esquema tático (dropdown)
- Orçamento total em cartoletas
- Atletas que já possui no elenco (opcional)

---

### 3.2 📈 Análise de Valorização / Desvalorização
**Descrição:** Painel dedicado a identificar atletas que tendem a subir ou cair de preço.

**Conteúdo exibido:**
- Gráfico de linha: evolução de preço por rodada (últimas 10 rodadas)
- Variação percentual na rodada mais recente
- Classificação: 🟢 Valorizando forte / 🟡 Estável / 🔴 Desvalorizando
- Ranking dos top 10 atletas que mais valorizaram na rodada
- Ranking dos top 10 que mais desvalorizaram

**Filtros disponíveis:**
- Por posição
- Por clube
- Por faixa de preço

---

### 3.3 ⚖️ Comparador de Atletas por Posição
**Descrição:** Ferramenta para comparar dois ou mais atletas lado a lado na mesma posição.

**Métricas comparadas:**
| Métrica | Descrição |
|---|---|
| Média de pontos | Últimas 5 e 10 rodadas |
| Preço atual | Em cartoletas |
| Custo por ponto | Preço ÷ média de pontos |
| Scouts principais | Gols, assistências, desarmes, defesas difíceis, etc. |
| Consistência | % de rodadas acima da média |
| Tendência | Subindo, estável ou caindo |

**UX:** Cards side-by-side com highlight automático do melhor valor em cada linha.

---

### 3.4 🔔 Alertas de Atletas em Boa Fase
**Descrição:** Sistema de alertas visuais que notifica quando um atleta entra em "modo quente".

**Critério de boa fase (configurável pelo usuário):**
- Pontuou acima de X pontos nas últimas N rodadas consecutivas
- Valorizou em pelo menos X% nas últimas rodadas
- Status disponível e sem histórico recente de lesão

**Exibição:**
- Seção "Em Chamas 🔥" no topo do dashboard
- Badge de destaque nos cards dos atletas em boa fase
- Filtro rápido: "Mostrar só atletas em boa fase"

---

## 4. Arquitetura Técnica

### 4.1 Stack Recomendada

| Camada | Tecnologia sugerida |
|---|---|
| Frontend | React + Vite |
| Estilização | Tailwind CSS |
| Gráficos | Recharts ou Chart.js |
| Estado global | Zustand ou Context API |
| Persistência local | localStorage / IndexedDB |
| Backend/Coleta | Python (script cron + FastAPI) |
| Banco de dados histórico | Supabase (PostgreSQL cloud) |
| Deploy frontend | Vercel / Netlify |
| Deploy backend | Railway / Render |

> **Por que Supabase?** A API do Cartola não fornece histórico nativo. O backend Python coleta e persiste os dados rodada a rodada no Supabase, que expõe uma API REST automática consumida diretamente pelo frontend.

---

### 4.2 Fluxo de Dados

```
API Cartola FC
     │
     ▼
Coletor (cron job / script)
     │  Roda 1x por rodada após fechamento do mercado
     ▼
Supabase (PostgreSQL)
     │  Tabelas: atletas, pontuações, partidas, preços
     ▼
FastAPI (Python) — opcional para lógica complexa
     │
     ▼
Frontend React
     │  Consome Supabase diretamente + API ao vivo para parciais
     ▼
Usuário
```

---

### 4.3 Rotas da API Cartola utilizadas

| Rota | Uso no sistema |
|---|---|
| `/mercado/status` | Saber rodada atual e se mercado está aberto |
| `/atletas/mercado` | Lista de atletas com preço e status atual |
| `/atletas/pontuados` | Scouts e pontuação da rodada (coleta pós-rodada) |
| `/atletas/valorizados` | Alimentar painel de valorização |
| `/atletas/desvalorizados` | Alimentar painel de valorização |
| `/atletas/bushido` | Parciais em tempo real durante rodada |
| `/partidas/{rodada}` | Contexto das partidas (mando, adversário) |
| `/clubes` | Lookup de nomes e escudos |
| `/posicoes` | Lookup de posições |
| `/rodadas` | Total de rodadas para loop de coleta histórica |

---

### 4.4 Modelo de Dados (Banco Local)

```sql
-- Atletas
CREATE TABLE atletas (
  id BIGINT PRIMARY KEY,
  nome TEXT NOT NULL,
  apelido TEXT,
  clube_id BIGINT,
  posicao_id INT,
  foto_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Clubes
CREATE TABLE clubes (
  id BIGINT PRIMARY KEY,
  nome TEXT NOT NULL,
  abreviacao TEXT,
  escudo_url TEXT
);

-- Preços por rodada
CREATE TABLE precos (
  atleta_id BIGINT REFERENCES atletas(id),
  rodada INT NOT NULL,
  preco NUMERIC(10,2),
  variacao NUMERIC(10,2),
  PRIMARY KEY (atleta_id, rodada)
);

-- Pontuações por rodada
CREATE TABLE pontuacoes (
  atleta_id BIGINT REFERENCES atletas(id),
  rodada INT NOT NULL,
  pontuacao NUMERIC(10,2),
  jogou BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (atleta_id, rodada)
);

-- Scouts por rodada
CREATE TABLE scouts (
  atleta_id BIGINT REFERENCES atletas(id),
  rodada INT NOT NULL,
  gols INT DEFAULT 0,
  assistencias INT DEFAULT 0,
  desarmes INT DEFAULT 0,
  defesas_dificeis INT DEFAULT 0,
  gols_sofridos INT DEFAULT 0,
  cartao_amarelo INT DEFAULT 0,
  cartao_vermelho INT DEFAULT 0,
  falta_cometida INT DEFAULT 0,
  finalizacao_trave INT DEFAULT 0,
  PRIMARY KEY (atleta_id, rodada)
);

-- Partidas
CREATE TABLE partidas (
  id BIGSERIAL PRIMARY KEY,
  rodada INT NOT NULL,
  clube_casa_id BIGINT REFERENCES clubes(id),
  clube_visitante_id BIGINT REFERENCES clubes(id),
  placar_casa INT,
  placar_visitante INT,
  data TIMESTAMPTZ
);
```

---

## 5. Estrutura de Telas

### 5.1 Layout Geral
- **Header:** Logo + rodada atual + status do mercado (aberto/fechado)
- **Sidebar (ou top nav):** Navegação entre as 4 funcionalidades
- **Main area:** Conteúdo dinâmico por funcionalidade

### 5.2 Telas

| Tela | Rota | Descrição |
|---|---|---|
| Dashboard Home | `/` | Resumo: atletas em chamas, top valorizados, recomendação rápida |
| Escalação | `/escalacao` | Configuração e sugestão de time completo |
| Valorização | `/valorizacao` | Rankings e gráficos de preço |
| Comparador | `/comparador` | Ferramenta de comparação lado a lado |
| Atleta | `/atleta/:id` | Perfil detalhado de um atleta específico |

---

## 6. Tela: Dashboard Home (`/`)

**Componentes:**
- 🔥 **Em Chamas agora** — cards horizontais dos atletas em boa fase
- 📈 **Top 5 Valorizados da rodada** — mini ranking com variação
- 🎯 **Sugestão Rápida** — 1 atleta recomendado por posição
- 📅 **Próximas partidas** — jogos da rodada atual com data/hora

---

## 7. Tela: Escalação (`/escalacao`)

**Passo 1 — Configuração:**
- Selecionar esquema tático
- Informar orçamento disponível
- (Opcional) Marcar atletas já no elenco

**Passo 2 — Sugestão:**
- Campo visual de futebol com posições marcadas
- Card de cada atleta sugerido com: nome, clube, preço, média, score
- Botão "Gerar nova sugestão" para variações
- Botão "Trocar atleta" por posição

**Passo 3 — Análise do time:**
- Custo total do time
- Pontuação esperada total
- Alertas: atletas com dúvida ou contundidos

---

## 8. Tela: Valorização (`/valorizacao`)

**Seções:**
- Filtros (posição, clube, faixa de preço, número de rodadas)
- Gráfico de linha interativo para até 5 atletas
- Tabela completa com colunas ordenáveis
- Heatmap por rodada (bonus — fase 2)

---

## 9. Tela: Comparador (`/comparador`)

**UX:**
- Busca por nome + autocomplete
- Adicionar até 4 atletas para comparar
- Tabela de métricas side-by-side
- Gráfico radar de desempenho por categoria de scout
- Recomendação final: "Melhor custo-benefício: [Nome]"

---

## 10. Roadmap de Desenvolvimento

### Fase 1 — MVP (4–6 semanas)
- [ ] Script de coleta histórica (varrer rodadas passadas)
- [ ] Banco de dados local com modelo definido
- [ ] Cron job de coleta pós-rodada
- [ ] Tela de Dashboard Home
- [ ] Tela de Valorização (ranking + gráfico básico)

### Fase 2 — Core (2–4 semanas)
- [ ] Tela de Escalação com sugestão por algoritmo
- [ ] Tela de Comparador de atletas
- [ ] Sistema de alertas "Em Chamas"
- [ ] Tela de perfil do atleta

### Fase 3 — Polimento (2–3 semanas)
- [ ] Filtros avançados em todas as telas
- [ ] Gráfico radar no comparador
- [ ] Heatmap de valorização
- [ ] Responsividade mobile
- [ ] Modo escuro

### Fase 4 — Inteligência (futuro)
- [ ] Integração com IA para sugestão semântica ("me recomenda um meia barato que joga em casa")
- [ ] Análise de mando de campo histórico por adversário
- [ ] Simulador de pontuação ("e se eu escalar X em vez de Y?")

---

## 11. Regras de Negócio

- Atletas com status `contundido` ou `suspenso` nunca são recomendados
- Atletas com status `dúvida` são recomendados com badge de aviso
- Mínimo de 3 rodadas jogadas para entrar nas recomendações
- Capitão sugerido = atleta com maior score da rodada atual
- Custo-benefício = média de pontos das últimas 5 rodadas ÷ preço atual

---

## 12. Considerações de UX/UI

- **Paleta:** Verde Cartola (#00b300) + tons escuros (dashboard estilo "modo noturno" por padrão)
- **Identidade visual:** Nome "Mestre de Verdade" com logo de gato com chapéu de mestre/topete
- **Linguagem:** Informal, brasileira, com emojis nas interfaces de alerta
- **Performance:** Dados históricos vêm do banco local (rápido); dados ao vivo vêm da API com loading state

---

## 13. Definição de Pronto (DoD)

Uma funcionalidade está pronta quando:
1. Os dados exibidos estão corretos e validados com a API real
2. Funciona em Chrome, Firefox e mobile (viewport 375px+)
3. Estados de loading, erro e vazio estão implementados
4. Nenhum dado hardcoded — tudo vem do Supabase ou da API Cartola

---

*Documento gerado em: Maio 2026 | Versão 1.1 — Backend: Python + FastAPI | Banco: Supabase*