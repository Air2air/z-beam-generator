# Settings Domain Configuration

This directory contains configuration files for the settings domain text generation.

## Files

### `prompts.yaml`
Defines metadata for each text component in the settings domain:
- **settings_description**: Technical description of laser cleaning settings/requirements
- **component_summaries**: Per-component UI help text (11 components)

### `component_summaries.yaml`
Defines the 11 interactive UI components for per-component generation:
- machine_settings
- material_safety_heatmap
- energy_coupling_heatmap
- thermal_stress_heatmap
- process_effectiveness_heatmap
- heat_buildup_simulator
- diagnostic_center
- research_citations
- faq_settings
- dataset_download
- parameter_relationships

Each component gets its own API call for focused, high-quality output.

## Prompts Directory
Actual prompt templates are in `../prompts/`:
- `settings_description.txt` - Settings description prompt
- `component_summary_base.txt` - Base template for per-component generation
- `component_summaries.txt` - Legacy monolithic prompt (deprecated)

## Per-Component Generation
The `component_summaries` component uses a different architecture:
1. Load `component_summary_base.txt` template
2. For each component in `component_summaries.yaml`:
   - Inject component-specific context
   - Make individual API call
   - Save to `component_summaries.{component_id}` field
3. Result: 11 focused API calls instead of 1 monolithic call

This approach produces higher quality output by letting the model focus on one component at a time.
