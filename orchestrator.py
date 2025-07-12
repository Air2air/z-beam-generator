import logging
from metadata.generator import MetadataGenerator
from tags.generator import TagsGenerator
from jsonld.generator import JSONLDGenerator
from utils.schema_validator import validate_output

logger = logging.getLogger("zbeam.orchestrator")


class ArticleOrchestrator:
    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
        self.metadata_generator = MetadataGenerator(context, schema)
        self.tags_generator = TagsGenerator(context, schema)
        self.jsonld_generator = JSONLDGenerator(context, schema)

    def run(self):
        logger.info("Orchestrating article generation...")

        metadata = self.metadata_generator.run()
        tags = self.tags_generator.run()
        jsonld = self.jsonld_generator.run()

        output = {
            "metadata": metadata,
            "tags": tags,
            "jsonld": jsonld,
        }

        logger.info("Validating generated output against schema...")
        valid = validate_output(output, self.schema)
        if not valid:
            logger.error("Article generation failed validation.")
            return None
        logger.info("Article generated and validated successfully.")
        return output