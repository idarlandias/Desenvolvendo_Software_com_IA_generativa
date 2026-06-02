# 🧠 Desenvolvendo Software com IA Generativa (Mod4 / PPI)

Repositório dedicado aos laboratórios práticos e projetos desenvolvidos durante a disciplina ministrada pelo **Prof. Nicksson Freitas** no SiDi.

O foco da disciplina é o desenvolvimento de aplicações inteligentes utilizando LLMs como componentes de arquitetura, integrando pipelines de RAG (Retrieval-Augmented Generation), Function-Calling (Tool-Use), avaliações robustas com RAGAS e técnicas de otimização de custo/latência.

---

## 🛠️ Tecnologias Utilizadas

*   **Provedor de LLM:** Google Gemini API (`gemini-2.5-flash-lite`, `gemini-3.5-flash`)
*   **Orquestração & Clientes:** OpenAI SDK (endpoint compatível com Gemini)
*   **Validação de Dados:** Pydantic v2 (Structured Outputs)
*   **Interface Gráfica:** Streamlit
*   **Banco de Vetores:** ChromaDB
*   **Gerenciador de Dependências:** `uv` (ambiente virtual rápido)

---

## 📂 Laboratórios Desenvolvidos

### 🚀 [LAB-001 — Agent CLI Single-Turn com Tool-Use](labs/01-agent-cli-tool-use.ipynb)
Implementação de um agente inteligente executado via terminal capaz de tomar decisões autônomas e acionar ferramentas locais para resolver problemas complexos.

*   **Principais Implementações:**
    *   **Loop de Raciocínio (ReAct):** Loop robusto entre a LLM e execução física de código.
    *   **Ferramentas Seguras (Tool-Use):** Calculadora com Whitelist para prevenção de injeção de código (RCE) e buscador conceitual case-insensitive.
    *   **Schemas JSON (JSON Schema):** Estruturação das ferramentas no formato oficial compatível com OpenAI/Anthropic.
    *   **Debrief de Tradeoffs:** Estudo analítico das vantagens em exatidão matemática e ancoragem (Groundedness) contra custos e latência de rede.

---

## 🎨 Arquitetura do Loop do Agente (Fluxo Colorido)

Este fluxograma colorido ilustra como as requisições transitam entre o loop local de Python e a API de LLM durante o processamento das ferramentas:

```mermaid
flowchart TD
    USER([Usuário]) -->|1. Envia Query| AGENT[Agente CLI]
    AGENT -->|2. Prompt + Tools| GEMINI{Google Gemini}
    
    GEMINI -->|3a. Precisa de Tool?| CALLS[Lista de Tool Calls]
    GEMINI -->|3b. Não precisa| RESP[Resposta Final]
    
    CALLS -->|4. Roteamento| REGISTRY{TOOL_REGISTRY}
    REGISTRY -->|calculator| CALC[Calculadora local]
    REGISTRY -->|lookup_doc| DOC[Buscador de Docs]
    
    CALC -->|5. Retorno string| MERGE[Resultados das Tools]
    DOC -->|5. Retorno string| MERGE
    
    MERGE -->|6. Role: Tool| AGENT
    
    RESP -->|7. Resposta Completa| USER

    %% Estilos Coloridos Personalizados
    style USER fill:#f3e8ff,stroke:#a855f7,stroke-width:2px,color:#581c87
    style AGENT fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1
    style GEMINI fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#854d0e
    style CALLS fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#991b1b
    style REGISTRY fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#3730a3
    style CALC fill:#dcfce7,stroke:#22c55e,stroke-width:2px,color:#15803d
    style DOC fill:#dcfce7,stroke:#22c55e,stroke-width:2px,color:#15803d
    style MERGE fill:#ffedd5,stroke:#f97316,stroke-width:2px,color:#c2410c
    style RESP fill:#fce7f3,stroke:#ec4899,stroke-width:2px,color:#9d174d
```

---

## 🔄 Fluxo de Execução (Diagrama de Sequência)


Abaixo está representado o fluxo sequencial de execução do agente implementado no **LAB-001** ao responder a uma consulta de duas ferramentas combinadas:

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuário
    participant Agent as Agente (Python Loop)
    participant LLM as LLM (Gemini API)
    participant Tool as Ferramenta Local (Calculator / Doc)

    User->>Agent: "Calcule 25% de 480 e me explique pydantic"
    Agent->>LLM: Envia Mensagens + Schema das Tools
    Note over LLM: LLM decide chamar a calculadora
    LLM-->>Agent: Requisição de Tool Call: calculator(expression="0.25 * 480")
    Agent->>Tool: Executa calculator("0.25 * 480")
    Tool-->>Agent: Retorno da ferramenta: "120.0"
    Agent->>LLM: Envia histórico + Tool Result ("120.0")
    Note over LLM: LLM decide buscar a documentação
    LLM-->>Agent: Requisição de Tool Call: lookup_doc(term="pydantic")
    Agent->>Tool: Executa lookup_doc("pydantic")
    Tool-->>Agent: Retorno da ferramenta: "Pydantic valida payload..."
    Agent->>LLM: Envia histórico + Tool Result ("Pydantic valida...")
    Note over LLM: LLM conclui que tem todas as respostas
    LLM-->>Agent: Resposta final compilada (Texto livre)
    Agent-->>User: "25% de 480 é 120. Pydantic é uma biblioteca..."
```

---

## 🛡️ Organização do Repositório


Para manter o repositório limpo, focado e profissional para portfólio, apenas os arquivos essenciais de entrega são rastreados publicamente, enquanto o ambiente virtual (`.venv`), chaves de segurança (`.env`) e os PDFs brutos de slides e guias permanecem protegidos localmente.

---

*SiDi - Desenvolvimento de Software de IA @ 2026*
