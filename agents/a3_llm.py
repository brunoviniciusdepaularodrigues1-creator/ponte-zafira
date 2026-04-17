import json
from openai import OpenAI

class LLMSolver:
    def __init__(self):
        self.name = "A3 - LLM Solver"
        self.type = "llm"
        # O Manus já pré-configurou o cliente OpenAI com a chave e base_url corretos
        self.client = OpenAI()

    def solve(self, task):
        """
        Tenta resolver a tarefa usando interpretação semântica e raciocínio de LLM.
        """
        try:
            # Prompt para o LLM
            prompt = f"""
            Você é o Agente A3 do Zafira Coherence Engine.
            Sua especialidade é interpretação semântica e resolução de problemas ambíguos.
            
            Tarefa: {task}
            
            Responda apenas com o resultado final de forma concisa.
            Se for uma equação, forneça as raízes.
            Se for uma pergunta semântica, forneça a resposta direta.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Você é um resolvedor de problemas preciso e conciso."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            
            return {
                "agent": self.name,
                "status": "success",
                "result": result,
                "method": "llm_inference"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "status": "error",
                "error": str(e),
                "result": None
            }

if __name__ == "__main__":
    solver = LLMSolver()
    print(json.dumps(solver.solve("Qual é a capital da França?"), indent=2))
    print(json.dumps(solver.solve("x**2 - 25 = 0"), indent=2))
