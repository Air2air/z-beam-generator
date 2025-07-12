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
        prompt = self._build_metadata_prompt()
        metadata = self.api_client.call_llm(prompt)
        logger.info("Metadata generated.")
        return metadata

    def generate_tags(self):
        logger.info("Generating tags...")
        prompt = self._build_tags_prompt()
        tags = self.api_client.call_llm(prompt)
        logger.info("Tags generated.")
        return tags

    def generate_jsonld(self):
        logger.info("Generating JSON-LD...")
        prompt = self._build_jsonld_prompt()
        jsonld = self.api_client.call_llm(prompt)
        logger.info("JSON-LD generated.")
        return jsonld

    def _build_metadata_prompt(self):
        # Build prompt using context and schema['generatorConfig']['metadata']
        return f"Generate metadata for {self.context['subject']} using schema: {self.schema.get('generatorConfig', {}).get('metadata', {})}"

    def _build_tags_prompt(self):
        # Build prompt using context and schema['generatorConfig']['tags']
        return f"Generate tags for {self.context['subject']} using schema: {self.schema.get('generatorConfig', {}).get('tags', {})}"

    def _build_jsonld_prompt(self):
        # Build prompt using context and schema['generatorConfig']['jsonld']
        return f"Generate JSON-LD for {self.context['subject']} using schema: {self.schema.get('generatorConfig', {}).get('jsonld', {})}"