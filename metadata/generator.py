import logging
from api_client import APIClient
from metadata.prompt import build_metadata_prompt

logger = logging.getLogger("zbeam.metadata.generator")

class MetadataGenerator:
    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
        self.api_client = APIClient()

    def run(self):
        prompt = build_metadata_prompt(self.context, self.schema)
        logger.info("Metadata prompt: %s", prompt)
        metadata = self.api_client.call_llm(prompt)
        logger.info("Metadata generated.")
        return metadata