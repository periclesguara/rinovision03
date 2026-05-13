from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
import os

# 🔑 Modelo de linguagem
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key="REDACTED_OPENAI_KEY"
)

# 🤖 Agente principal
refatorador = Agent(
    role="Refatorador Python",
    goal="Refatorar código de forma limpa, modular e funcional, corrigindo bugs e respeitando o briefing",
    backstory=(
        "Você é um engenheiro de software sênior focado em código limpo e sustentável. "
        "Seu trabalho é transformar sistemas legados em projetos estáveis e escaláveis, preservando a lógica central."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 📄 Leitura do briefing
with open("briefing_assistente_gpt.md", "r") as f:
    briefing = f.read()

# 📋 Tarefa de refatoração real
tarefa = Task(
    description=(
        f"{briefing}\n\nAgora, com base nesse briefing, refatore os arquivos diretamente. "
        "Aplique melhorias nos arquivos Python referenciados no briefing e retorne o conteúdo atualizado de cada um, pronto para ser salvo no disco."
    ),
    expected_output="Conteúdo dos arquivos Python refatorados, prontos para sobrescrever os originais.",
    agent=refatorador
)

# 🧑‍💻 Criar a crew
equipe = Crew(
    agents=[refatorador],
    tasks=[tarefa],
    verbose=True
)

# 🚀 Executar
resultado = equipe.kickoff()

# 💾 Salvar em arquivos novos (para revisão)
output_path = "refatorados"
os.makedirs(output_path, exist_ok=True)

with open(os.path.join(output_path, "resultado.txt"), "w") as f:
    f.write(resultado)

print("✅ Refatoração finalizada e salva em refatorados/resultado.txt")
