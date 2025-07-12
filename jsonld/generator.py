import logging
from api_client import APIClient
from jsonld.prompt import build_jsonld_prompt

logger = logging.getLogger("zbeam.jsonld.generator")

class JSONLDGenerator:
    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
        self.api_client = APIClient()

    def run(self):
        prompt = build_jsonld_prompt(self.context, self.schema)
        logger.info("JSON-LD prompt: %s", prompt)
        jsonld = self.api_client.call_llm(prompt)
        logger.info("JSON-LD generated.")
        return jsonld