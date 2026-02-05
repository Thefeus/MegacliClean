import unittest
import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class TestGeminiAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Carrega as variáveis de ambiente uma única vez para todos os testes."""
        dotenv.load_dotenv(dotenv_path='d:/MegaAmigos/.env')

    def setUp(self):
        """Configuração executada antes de cada método de teste individual."""
        self.api_key = os.getenv("GOOGLE_API_KEY", "").strip().strip('"').strip("'")

        api_key = os.getenv("GOOGLE_API_KEY", "")
        print(f"Repr da chave: {repr(api_key[:15])}")  # Mostra a representação exata
        print(f"Primeiro char: {repr(api_key[0])}")
        print(f"Último char: {repr(api_key[-1])}")

        if api_key:
            # Limpa a API Key de aspas e re-define no ambiente
            api_key = api_key.strip('"').strip("'")
            os.environ["GOOGLE_API_KEY"] = api_key
        
        self.api_key = api_key

    def test_api_key_is_set(self):
        """Verifica se a GOOGLE_API_KEY está configurada no ambiente."""
        self.assertIsNotNone(self.api_key, "A variável de ambiente GOOGLE_API_KEY não está definida.")
        self.assertTrue(len(self.api_key) > 0, "A variável de ambiente GOOGLE_API_KEY está vazia.")

    def test_gemini_api_call(self):
        """Testa uma chamada simples para a API do Gemini para validar a chave."""
        if not self.api_key:
            self.skipTest("Pulei o teste da API pois a GOOGLE_API_KEY não está definida ou está vazia.")

        try:
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
            message = HumanMessage(content="Olá! Isso é um teste.")
            response = llm.invoke([message])
            
            self.assertIsNotNone(response)
            self.assertIsInstance(response.content, str)
            self.assertTrue(len(response.content) > 0)
            print("\nTeste de API do Gemini bem-sucedido! Resposta recebida.")

        except Exception as e:
            self.fail(f"A chamada para a API do Gemini falhou com o erro: {e}")

if __name__ == '__main__':
    unittest.main()
