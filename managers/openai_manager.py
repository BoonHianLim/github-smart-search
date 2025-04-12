from openai import AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Iterable

from loguru import logger


def chat_completion(endpoint: str, api_key: str, model: str, prompt: Iterable[ChatCompletionMessageParam], temperature: float = 0.7) -> str:
    """
    Function to send a chat request to OpenAI API.
    """

    logger.debug(
        f"Sending request to OpenAI API with endpoint: {endpoint}, model: {model}, temperature: {temperature}")
    logger.debug(f"Prompt: {prompt}")

    client: OpenAI = None
    if "openai.azure.com" in endpoint:
        logger.debug("Using Azure OpenAI API")
        client = AzureOpenAI(
            api_version='2024-10-21',
            azure_endpoint=endpoint,
            api_key=api_key
        )
    else:
        logger.debug("Using OpenAI API")
        client = OpenAI(
            api_key=api_key,
            base_url=endpoint,
        )
    response = client.chat.completions.create(
        model=model,
        messages=prompt,
        max_tokens=5000,
        stream=False,
    )

    output_texts = response.choices[0].message.content.strip()
    return output_texts
