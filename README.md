
## Overview

Z-Beam Generator is a modular Text generation system that creates high-quality, E-A-T compliant articles through a generation → optimization pipeline.

Articles are generated via api and prompts.
Article Components are: Text Sections, metadata, author data, and optional tables or charts.
The config decides what Article Components are generated and in what order.
The Article Component may or may not be optimized in a subsequent step.
The final output is a single article in markdown format.

## Article types
There are multiple types of articles with different focuses and different Section and Article component configurations.
The config will have presets for article types each with their own schema.

## Text Sections
"Text Sections" are subject paragraphs comprised of text only. They are generated in sequence from (prompts/text/sections.json) and then run through the optimization pipeline.  

## Voice and Tone
The author (prompts/authors/authors.json) decides voice and tone of the Text Sections, ex: (prompts/optimizations/writing_samples/style_english.md).
The author_id is in the user config.

## Optimization
The goal of the optimization pipeline is to make the Text Sections E-A-T compliant and to read as if it were human written.  It must score extremely low on an AI detection tool.
Currently two methods are used.  One or the other is selected in the config.
Both methods create a "Rewriting prompt" to submit to the api provider that includes both the generated section and the optimization prompt instructions.

## Iterative
The generated section is sent to the api in multiple prompt steps (prompts/optimizations/iterative.json).  Within the iterations, the previous result is then sent through the next step.

## Writing Sample
A "Rewriting prompt" that includes the generated section is run through a prompt with a "Target example" writing sample (prompts/optimizations/writing_samples/style_english.md).

## Metadata component
The metadata example and generator is in (prompts/metadata/metadata.json).

## Orchestration
After all optimization steps are complete, the Text Sections and Article Components are orchestrated into a single article.
The flow is Generate → Optimize → Orchestrate.  However only Text Sections are run through the optimization pipeline.  Other Article Components are passed through as is.

## File output
Name convention is (material)_laser_cleaning.md

## Build philosophy
Avoid bloat and unnecessary complexity.
Research the simplest methods first.
Prioritize reworking of existing code instead of adding new code.
The previous code from Claude has been overcomplex and very brittle.
**NEVER** hardcode configs anywhere but in run.py.
**NEVER** use fallbacks.  Always fail fast.