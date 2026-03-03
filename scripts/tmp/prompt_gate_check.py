from shared.text.utils.prompt_registry_service import PromptRegistryService

def main() -> None:
    for component in ["pageTitle", "pageDescription"]:
        prompt = PromptRegistryService.get_schema_prompt(
            domain="applications",
            component_type=component,
            include_descriptor=False,
        )
        if not prompt:
            raise ValueError(f"No prompt returned for {component}")
        has_optimizer = "Optimize the draft" in prompt
        word_count = len(prompt.split())
        print(f"{component}: words={word_count}, optimizer={has_optimizer}")

if __name__ == "__main__":
    main()
