# City Data Researcher

Automated tool to research and populate comprehensive historical and demographic data for San Francisco Bay Area cities using Grok AI.

## Purpose

Generates `Cities.yaml` with detailed information about 93 Bay Area cities including:
- Population history (1900-2020)
- Historical context and founding
- Geographic features and landmarks
- Historical and current industries
- Transportation history
- Notable buildings and architecture
- Cultural significance
- Demographics

## Setup

### 1. Install Dependencies

```bash
pip install openai pyyaml
```

### 2. Get Grok API Key

1. Visit [https://console.x.ai/](https://console.x.ai/)
2. Create an account and get API key
3. Add to your `.env` file:

```bash
XAI_API_KEY=your_grok_api_key_here
```

Or export directly:
```bash
export XAI_API_KEY=your_grok_api_key_here
```

## Usage

### Research All Bay Area Cities

```bash
python3 regions/city_data_researcher.py
```

This will research all 93 cities across 9 counties and populate `Cities.yaml`.

### Research Specific County

```bash
python3 regions/city_data_researcher.py --county "Contra Costa"
```

### Research Specific City

```bash
python3 regions/city_data_researcher.py --city "Martinez"
```

### Test with Limited Cities

```bash
python3 regions/city_data_researcher.py --limit 5
```

### Custom Output Path

```bash
python3 regions/city_data_researcher.py --output /path/to/output.yaml
```

## Features

### Incremental Saves
- Saves after each city is researched
- Safe to interrupt and resume
- Won't re-research existing cities

### Error Handling
- Continues with next city if one fails
- Logs all errors clearly
- Preserves existing data

### Data Quality
- Uses Grok AI for accurate historical research
- Low temperature (0.3) for factual responses
- Includes US Census data when available
- Validates JSON format

## Output Format

```yaml
cities:
  martinez:
    name: Martinez
    county: Contra Costa County
    state: California
    region: San Francisco Bay Area
    incorporation_year: 1876
    historical_context: "Founded in 1849..."
    population_history:
      1900: 1200
      1910: 1500
      # ... through 2020
    geographic_features:
      elevation_feet: 20
      area_square_miles: 13.2
      terrain: "Rolling hills..."
      notable_landmarks:
        - Martinez Adobe
        - John Muir National Historic Site
    historical_industries:
      - Agriculture
      - Shipping
      - Oil refining
    # ... and more
```

## Integration

The generated `Cities.yaml` is used by:
- Image generation system for historical context
- Population researcher for accurate demographics
- Region-specific content generation

## Progress Tracking

The tool shows:
- ✅ Successfully researched cities
- ⏭️  Skipped cities (already in database)
- ❌ Failed cities (with error details)
- 📊 Final statistics

## Notes

- **Cost**: Uses Grok API (check pricing at x.ai)
- **Time**: ~5-10 seconds per city
- **Total**: ~93 cities = 10-15 minutes for full research
- **Resume**: Safe to stop and restart - won't duplicate research

## Example Session

```bash
$ python3 regions/city_data_researcher.py --county "Contra Costa" --limit 3

✅ City data researcher initialized with Grok AI

============================================================
📍 Researching Contra Costa County
============================================================
🔍 Researching: Concord, Contra Costa County
✅ Successfully researched Concord
💾 Saved cities data to regions/Cities.yaml
✅ 1. Concord - Complete

🔍 Researching: Richmond, Contra Costa County
✅ Successfully researched Richmond
💾 Saved cities data to regions/Cities.yaml
✅ 2. Richmond - Complete

🔍 Researching: Antioch, Contra Costa County
✅ Successfully researched Antioch
💾 Saved cities data to regions/Cities.yaml
✅ 3. Antioch - Complete

⚠️  Reached limit of 3 cities

============================================================
✅ Research complete!
📊 Total cities researched: 3
📊 Total cities in database: 3
💾 Saved to: regions/Cities.yaml
============================================================
```

## Troubleshooting

### "XAI_API_KEY not found"
- Make sure you've set the environment variable
- Check `.env` file has `XAI_API_KEY=your_key`

### "JSON parsing error"
- Usually transient - the tool will continue with next city
- Check Grok API status if persistent

### "Import error: openai"
- Install with: `pip install openai`

## Future Enhancements

- [ ] Add data validation and quality checks
- [ ] Support for updating existing entries
- [ ] Historical photo URL collection
- [ ] Notable people database
- [ ] Historical events timeline
- [ ] Architectural inventory
