import logging
from api_client import APIClient

logger = logging.getLogger("zbeam.generator")

class ZBeamGenerator:
    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
        self.api_client = APIClient()

    def generate_metadata(self):
        logger.info("Generating metadata...")
        prompt = "Metadata prompt based on schema and context"  # Build prompt from schema
        metadata = self.api_client.call_llm(prompt)
        logger.info("Metadata generated.")
        return metadata

    def generate_tags(self):
        logger.info("Generating tags...")
        prompt = "Tag prompt based on schema and context"  # Build prompt from schema
        tags = self.api_client.call_llm(prompt)
        logger.info("Tags generated.")
        return tags

    def generate_jsonld(self):
        logger.info("Generating JSON-LD...")
        prompt = "JSON-LD prompt based on schema and context"  # Build prompt from schema
        jsonld = self.api_client.call_llm(prompt)
        logger.info("JSON-LD generated.")
        return jsonld