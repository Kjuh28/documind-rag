from langchain_ollama import OllamaLLM # Importação atualizada

class DocuMindBrain:
    def __init__(self):
        # Conecta no container que você acabou de testar no terminal
        self.llm = OllamaLLM(
            model="qwen2:1.5b",
            base_url="http://localhost:11434"
        )

    def ask(self, question: str):
        return self.llm.invoke(question)

# Instância para ser usada na API
brain = DocuMindBrain()