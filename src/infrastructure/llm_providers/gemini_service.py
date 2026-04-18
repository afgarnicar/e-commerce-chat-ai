import asyncio
import os
from typing import List

from google import genai

from src.domain.entities import ChatContext, Product


class GeminiService:
    """
    Service responsible for generating AI responses using Google Gemini.
    """

    def __init__(self) -> None:
        """
        Initialize the Gemini client and model configuration.

        Raises:
            ValueError: If GEMINI_API_KEY is not configured.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

    def format_products_info(self, products: List[Product]) -> str:
        """
        Convert the list of products into a readable text block.

        Format:
        - Name | Brand | Price | Stock

        Args:
            products (List[Product]): Available products.

        Returns:
            str: Formatted product information.
        """
        if not products:
            return "No products are currently available."

        lines = []
        for product in products:
            lines.append(
                f"- {product.name} | {product.brand} | "
                f"${product.price:.2f} | Stock: {product.stock} | "
                f"Category: {product.category} | Size: {product.size} | Color: {product.color}"
            )

        return "\n".join(lines)

    def _build_prompt(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Build the full prompt to send to Gemini.

        Args:
            user_message (str): Current user message.
            products (List[Product]): Available products.
            context (ChatContext): Conversation context.

        Returns:
            str: Full prompt.
        """
        products_info = self.format_products_info(products)
        conversation_history = context.format_for_prompt()

        if not conversation_history.strip():
            conversation_history = "No previous conversation history."

        prompt = f"""
You are a virtual assistant specialized in shoe sales for an e-commerce store.
Your goal is to help customers find the best shoes for their needs.

AVAILABLE PRODUCTS:
{products_info}

INSTRUCTIONS:
- Be friendly and professional.
- Use the previous conversation context when relevant.
- Recommend specific products when appropriate.
- Mention price, size, color, category, and availability.
- If you do not have enough information, be honest.
- Do not invent products that are not listed.
- Keep your answers clear, useful, and focused on helping the customer.

CONVERSATION HISTORY:
{conversation_history}

CURRENT USER MESSAGE:
User: {user_message}

Assistant:
""".strip()

        return prompt

    async def generate_response(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Generate a response using Gemini.

        This method wraps the synchronous SDK call using asyncio.to_thread()
        so it can be awaited safely from async application services.

        Args:
            user_message (str): Current user message.
            products (List[Product]): Available products.
            context (ChatContext): Conversation context.

        Returns:
            str: Generated assistant response.

        Raises:
            RuntimeError: If Gemini fails or returns an empty response.
        """
        prompt = self._build_prompt(user_message, products, context)

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
            )

            response_text = getattr(response, "text", None)

            if not response_text or not response_text.strip():
                raise RuntimeError("Gemini returned an empty response.")

            return response_text.strip()

        except Exception as exc:
            raise RuntimeError(f"Error while generating Gemini response: {exc}") from exc