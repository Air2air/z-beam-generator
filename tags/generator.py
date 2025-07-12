import logging
from api_client import APIClient
from tags.prompt import build_tags_prompt

logger = logging.getLogger("zbeam.tags.generator")

class TagsGenerator:
    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
        self.api_client = APIClient()

    def run(self):
        prompt = build_tags_prompt(self.context, self.schema)
        logger.info("Tags prompt: %s", prompt)
        tags = self.api_client.call_llm(prompt)
        logger.info("Tags generated.")
        return tags