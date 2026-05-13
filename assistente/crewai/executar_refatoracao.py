from crewai import Crew, Task, Agent
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

# ✅ Coloque sua chave da OpenAI aqui
os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY"

briefing_path = "briefing_assistente_gpt.md"

# 🔍 Agente 1: Leitor de briefing
briefing_reader = Agent(
    role="Analista de Requisitos",
    goal="Ler e entender instruções de projeto",
    backstory="Você é um especialista em leitura técnica que transforma textos em ações de desenvolvimento.",
    verbose=True,
    allow_delegation=False,
    llm=ChatOpenAI(model="gpt-4o")
)

# 🔧 Agente 2: Refatorador de código
code_refactorer = Agent(
    role="Engenheiro de Software Python",
    goal="Modificar arquivos de sistema conforme briefing",
    backstory="Você é responsável por melhorar e implementar novas funcionalidades no código do sistema RinoVision03.",
    verbose=True,
    allow_delegation=False,
    llm=ChatOpenAI(model="gpt-4o")
)

# ✅ Tarefa 1: Extrair requisitos do briefing
task1 = Task(
    description=f"Leia o arquivo {briefing_path} e extraia os requisitos e instruções de implementação.",
    expected_output="Lista de funcionalidades e botões com comportamentos esperados descritos de forma clara.",
    agent=briefing_reader
)

# ✅ Tarefa 2: Refatorar o compositor_window.py
task2 = Task(
    description="Com base nos requisitos extraídos, implemente as modificações no arquivo `windows/compositor_window.py`. "
                "Inclua os novos botões, chamadas para webcam/base_window, lock, rec e fullscreen. Use as práticas do projeto atual.",
    expected_output="Código refatorado e funcional de compositor_window.py com os novos botões funcionando corretamente.",
    agent=code_refactorer,
    depends_on=[task1]
)

# 👥 Equipe
crew = Crew(
    agents=[briefing_reader, code_refactorer],
    tasks=[task1, task2],
    verbose=True
)

# 🚀 Rodar o processo
crew.kickoff()
