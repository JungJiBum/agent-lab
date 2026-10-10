from openai import AsyncOpenAI

from app.config import settings
from app.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat(self, message: str) -> str:
        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "user", "content": message}
            ],
        )
        return response.choices[0].message.content or ""