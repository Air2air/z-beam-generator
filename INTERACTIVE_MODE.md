# Interactive Mode Guide

The Z-Beam Generator now includes a powerful **Interactive Mode** that allows you to generate content with fine-grained control, prompting you to proceed to each next material in the list.

## Key Features

### 🎮 Interactive Generation
- **Step-by-step processing**: Generate content for one material at a time
- **User prompts**: Choose whether to continue, skip, pause, or quit after each material
- **Progress tracking**: See completion progress and remaining materials
- **Resume capability**: Start from any specific material in the list

### 📊 Progress Monitoring
- Real-time progress display (`[5/122] Processing: Aluminum (metal)`)
- Component generation results per material
- Session summaries with completion and skip counts
- Material category information

### 🎯 User Controls

#### Available Commands at Each Prompt:
- **Y/Yes** (default): Continue to next material
- **N/No**: Pause generation (can resume later)
- **S/Skip**: Skip the next material and continue
- **Q/Quit**: Exit interactive mode
- **List**: Show next 10 remaining materials

## Usage Examples

### Basic Interactive Mode
```bash
python3 z_beam_generator.py --interactive
```

### Start from Specific Material
```bash
python3 z_beam_generator.py --interactive --start-from "Copper"
```

### Combined with Verbose Logging
```bash
python3 z_beam_generator.py --interactive --verbose
```

## Sample Session Flow

```
📋 Interactive Material Generation
   Total materials available: 122
   Press Ctrl+C at any time to exit

🎯 [1/122] Processing: Porcelain (ceramic)
   ✅ Generated: caption
   ✅ Generated: propertiestable
   ✅ Generated: bullets
   ✅ Generated: content
   ❌ Failed: frontmatter
   ✅ Generated: metatags
   ✅ Generated: jsonld
   📊 Results: 6/7 components generated

⏭️  Next material: Stoneware (ceramic)
   Progress: 1/122 completed, 121 remaining
Continue to next material? [Y/n/s/q/list]: y

🎯 [2/122] Processing: Stoneware (ceramic)
   [... generation continues ...]
```

## Interactive Commands Detail

### Continue (Y/Yes)
- Proceeds to generate the next material
- Default action (just press Enter)
- Maintains full generation workflow

### Pause (N/No)
- Stops generation but preserves session state
- Shows completion summary
- Safe exit that allows resuming later

### Skip (S/Skip)
- Removes the next material from the current session
- Useful for problematic materials or materials you want to handle separately
- Continues with the material after the skipped one

### List (List/L)
- Shows the next 10 remaining materials
- Displays material names and categories
- Helps you plan your generation strategy

### Quit (Q/Quit)
- Immediately exits interactive mode
- Shows session summary with completed and skipped counts
- Safe termination

## Resuming Generation

To resume from where you left off, use the `--start-from` option:

```bash
# If you paused at "Aluminum", resume with:
python3 z_beam_generator.py --interactive --start-from "Aluminum"
```

## Benefits Over Batch Mode

### 1. **Quality Control**
- Review results after each material
- Identify and skip problematic materials
- Immediate feedback on generation success

### 2. **Resource Management**
- Pause when API limits are reached
- Control generation timing
- Manage computational resources

### 3. **Flexible Workflow**
- Skip materials you've already processed
- Focus on specific material categories
- Interrupt and resume as needed

### 4. **Error Recovery**
- Continue generation even if individual materials fail
- Skip problematic materials without losing progress
- Monitor component success rates in real-time

## Best Practices

### 1. **Start Small**
```bash
# Test with first few materials
python3 z_beam_generator.py --interactive --start-from "Porcelain"
```

### 2. **Use Progress Tracking**
- Pay attention to component success rates
- Note materials that consistently fail
- Use the list command to plan ahead

### 3. **Strategic Skipping**
- Skip materials with known issues
- Process similar materials together
- Save complex materials for focused sessions

### 4. **Resume Smartly**
- Note where you stopped for easy resumption
- Use material names exactly as they appear in `--list-materials`

## Keyboard Shortcuts

- **Ctrl+C**: Emergency exit (shows summary)
- **Enter**: Accept default (continue)
- **ESC**: Not applicable (use 'q' instead)

## Error Handling

The interactive mode gracefully handles:
- API connection failures (pre-flight check)
- Individual material generation failures
- Keyboard interrupts (Ctrl+C)
- Invalid user input (reprompts)
- EOF conditions (safe exit)

## Comparison with Other Modes

| Feature | Batch (`--all`) | Single (`--material`) | Interactive |
|---------|-----------------|----------------------|-------------|
| Progress Control | ❌ | ❌ | ✅ |
| Skip Materials | ❌ | ❌ | ✅ |
| Resume Capability | ❌ | ❌ | ✅ |
| Real-time Monitoring | ❌ | ✅ | ✅ |
| Quality Control | ❌ | ✅ | ✅ |
| Bulk Processing | ✅ | ❌ | ✅ |

The interactive mode combines the best of both worlds: bulk processing capability with fine-grained control.
