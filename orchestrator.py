import logging
from generator import ZBeamGenerator
from utils.schema_validator import validate_output

logger = logging.getLogger("zbeam.orchestrator")

class ArticleOrchestrator:
    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
        self.generator = ZBeamGenerator(context, schema)

    def run(self):
        logger.info("Orchestrating article generation...")
        metadata = self.generator.generate_metadata()
        tags = self.generator.generate_tags()
        jsonld = self.generator.generate_jsonld()

        output = {
            "metadata": metadata,
            "tags": tags,
            "jsonld": jsonld
        }

        valid = validate_output(output, self.schema)
        if not valid:
            logger.error("Article generation failed validation.")
            return None
        logger.info("Article generated and validated successfully.")
        return output