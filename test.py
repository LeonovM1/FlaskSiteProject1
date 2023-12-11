import requests

api_key = "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"
api_url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Пример запроса POST к API OpenAI для создания нового чата с моделью GPT-3.5
data = {
    "model": "gpt-4-turbo",  # Замените на актуальное имя модели GPT-3.5
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    ]
}

response = requests.post(api_url, headers=headers, json=data)

# Вывести результат запроса
print(response.json())
