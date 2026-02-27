import google.generativeai as genai
import threading

class GeminiService:
    @staticmethod
    def configure(api_key):
        genai.configure(api_key=api_key)

    @staticmethod
    def list_models():
        try:
            return [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except:
            return ["gemini-1.5-flash"]

    @staticmethod
    def get_best_model(models):
        priority_list = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash-001',
            'gemini-pro',
            'gemini-1.0-pro'
        ]
        for p in priority_list:
            if p in models:
                return p
        return models[0] if models else "gemini-1.5-flash"

    @staticmethod
    def call_gemini(prompt, model_name, api_key, contexto=""):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(contexto + prompt)
            return response.text
        except Exception as e:
            return f"Erro na conexão ({model_name}): {str(e)}"
