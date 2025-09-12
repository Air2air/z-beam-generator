# 🎯 Text Component Blueprint

## **Purpose**
The Text Component is the most complex component in the Z-Beam system, responsible for generating comprehensive technical articles about laser cleaning materials. It implements the three-layer prompt architecture (Base + Persona + Formatting) and includes real-time AI detection with iterative improvement.

## 📋 Requirements

### **Dependencies**
- **APIs**: DeepSeek API for content generation
- **AI Detection**: Winston.ai for quality scoring
- **Configuration**: Three-layer prompt system (YAML files)
- **Data**: Material data from frontmatter
- **Performance**: Real-time status updates every 10 seconds

### **Prerequisites**
- Valid DeepSeek API key in environment
- Winston.ai API key configured
- Complete three-layer prompt files
- Material frontmatter data available

## 🏗️ Architecture

### **Component Structure**
```
components/text/
├── generator.py                 # Main component interface
├── generators/
│   └── fail_fast_generator.py   # Core generation logic
└── prompts/                     # Three-layer prompt system
    ├── base_content_prompt.yaml # Technical requirements
    ├── personas/                # Author characteristics
    │   ├── usa_persona.yaml
    │   ├── italy_persona.yaml
    │   ├── taiwan_persona.yaml
    │   └── indonesia_persona.yaml
    └── formatting/              # Cultural presentation
        ├── usa_formatting.yaml
        ├── italy_formatting.yaml
        ├── taiwan_formatting.yaml
        └── indonesia_formatting.yaml
```

### **Three-Layer Architecture**
1. **Base Layer**: Pure technical content requirements
2. **Persona Layer**: Author characteristics and writing style
3. **Formatting Layer**: Cultural presentation preferences

### **Generation Flow**
```
Input Validation → Prompt Construction → API Call → AI Detection → Iterative Improvement → Result
```

## 🔧 Implementation

### **Main Generator Interface**

```python
from components.base import ComponentGenerator, ComponentResult
from .generators.fail_fast_generator import FailFastGenerator
from utils.ai_detection import AIDetectionService
from utils.status_tracker import StatusTracker

class TextComponentGenerator(ComponentGenerator):
    """Text component generator with three-layer architecture and AI detection"""

    def __init__(self, material_name: str, **kwargs):
        super().__init__(material_name, **kwargs)

        # Initialize core services
        self.fail_fast_generator = FailFastGenerator()
        self.ai_detection = AIDetectionService()
        self.status_tracker = StatusTracker()

        # Load configuration
        self.config = self._load_ai_detection_config()

    def get_component_type(self) -> str:
        return "text"

    def validate_inputs(self, **kwargs) -> bool:
        """Validate text generation inputs"""
        required = ['material_data', 'author_info', 'frontmatter_data']
        return all(key in kwargs for key in required)

    def generate(self, **kwargs) -> ComponentResult:
        """Generate text content with AI detection and iterative improvement"""
        try:
            # Input validation
            if not self.validate_inputs(**kwargs):
                return self.handle_error(ValueError("Missing required inputs"))

            # Extract parameters
            material_data = kwargs['material_data']
            author_info = kwargs['author_info']
            frontmatter_data = kwargs['frontmatter_data']

            # Start status tracking
            self.status_tracker.start_generation(
                material_name=self.material_name,
                target_score=self.config.get('target_score', 85.0),
                max_iterations=self.config.get('max_iterations', 5)
            )

            # Generate initial content
            initial_content = self._generate_initial_content(
                material_data, author_info, frontmatter_data
            )

            # Iterative improvement with AI detection
            final_content = self._iterative_improvement(initial_content, material_data)

            # Create success result
            return self.create_success_result(
                content=final_content,
                word_count=len(final_content.split()),
                material=self.material_name,
                ai_detection_score=self.ai_detection.get_latest_score(),
                iterations_completed=self.status_tracker.iteration_count
            )

        except Exception as e:
            return self.handle_error(e)

    def _generate_initial_content(self, material_data: Dict,
                                author_info: Dict, frontmatter_data: Dict) -> str:
        """Generate initial content using three-layer prompt system"""
        return self.fail_fast_generator.generate_content(
            material_name=self.material_name,
            material_data=material_data,
            author_info=author_info,
            frontmatter_data=frontmatter_data
        )

    def _iterative_improvement(self, content: str, material_data: Dict) -> str:
        """Perform iterative improvement using AI detection"""
        best_content = content
        best_score = 0.0

        for iteration in range(self.config.get('max_iterations', 5)):
            # Update status
            self.status_tracker.update_iteration(iteration + 1)

            # Get AI detection score
            score = self.ai_detection.analyze_content(best_content)

            # Update best results
            if score > best_score:
                best_score = score
                # Only improve if score is below target
                if score < self.config.get('target_score', 85.0):
                    best_content = self._improve_content(best_content, score, material_data)

            # Check if target reached
            if score >= self.config.get('target_score', 85.0):
                break

        return best_content

    def _improve_content(self, content: str, current_score: float, material_data: Dict) -> str:
        """Improve content based on AI detection feedback"""
        improvement_prompt = self._create_improvement_prompt(content, current_score)

        # Use DeepSeek to improve content
        improved_content = self.fail_fast_generator.generate_improved_content(
            original_content=content,
            improvement_prompt=improvement_prompt,
            material_data=material_data
        )

        return improved_content

    def _create_improvement_prompt(self, content: str, score: float) -> str:
        """Create improvement prompt based on current score"""
        return f"""
        Current AI detection score: {score}
        Target: {self.config.get('target_score', 85.0)} (higher = more human-like)
        Please improve this technical content to achieve a higher AI detection score (less detectable as AI)
        while maintaining technical accuracy and professional tone.

        Focus areas for improvement:
        - Natural language patterns
        - Conversational style
        - Sentence variability
        - Cultural adaptation
        """

    def _load_ai_detection_config(self) -> Dict:
        """Load AI detection configuration"""
        # Implementation would load from config/ai_detection.yaml
        return {
            'target_score': 85.0,
            'max_iterations': 5,
            'improvement_threshold': 3.0
        }
```

### **Fail-Fast Generator Implementation**

```python
class FailFastGenerator:
    """Core content generation with fail-fast behavior"""

    def __init__(self):
        self.prompt_loader = PromptLoader()
        self.api_client = DeepSeekAPIClient()

    def generate_content(self, material_name: str, material_data: Dict,
                        author_info: Dict, frontmatter_data: Dict) -> str:
        """Generate content using three-layer prompt system"""

        # Load three-layer prompts
        base_prompt = self.prompt_loader.load_base_prompt()
        persona_prompt = self.prompt_loader.load_persona_prompt(author_info['country'])
        formatting_prompt = self.prompt_loader.load_formatting_prompt(author_info['country'])

        # Construct final prompt
        final_prompt = self._construct_three_layer_prompt(
            base_prompt, persona_prompt, formatting_prompt,
            material_data, frontmatter_data
        )

        # Generate content
        return self.api_client.generate_content(final_prompt)

    def _construct_three_layer_prompt(self, base: str, persona: str,
                                    formatting: str, material_data: Dict,
                                    frontmatter_data: Dict) -> str:
        """Construct the three-layer prompt"""
        return f"""
        {base}

        AUTHOR PROFILE:
        {persona}

        FORMATTING REQUIREMENTS:
        {formatting}

        MATERIAL DATA:
        Name: {material_data.get('name', 'Unknown')}
        Category: {material_data.get('category', 'Unknown')}
        Properties: {frontmatter_data.get('properties', [])}

        Generate comprehensive technical content following all guidelines above.
        """
```

## 🧪 Testing

### **Unit Test Structure**

```python
class TestTextComponentGenerator:

    @pytest.fixture
    def generator(self):
        return TextComponentGenerator("aluminum")

    @pytest.fixture
    def mock_services(self, mocker):
        """Mock external services for testing"""
        mocker.patch('utils.ai_detection.AIDetectionService')
        mocker.patch('api.deepseek.DeepSeekAPIClient')

    def test_successful_generation(self, generator, mock_services):
        """Test successful text generation"""
        result = generator.generate(
            material_data={"name": "Aluminum", "category": "metal"},
            author_info={"name": "Todd", "country": "usa"},
            frontmatter_data={"properties": ["ductile", "lightweight"]}
        )

        assert result.success is True
        assert result.component_type == "text"
        assert "aluminum" in result.content.lower()

    def test_input_validation(self, generator):
        """Test input validation"""
        result = generator.generate()  # Missing inputs

        assert result.success is False
        assert "Missing required inputs" in result.error_message

    def test_iterative_improvement(self, generator, mocker):
        """Test iterative improvement process"""
        mock_ai = mocker.patch('utils.ai_detection.AIDetectionService')
        mock_ai.return_value.analyze_content.return_value = 75.0

        result = generator.generate(
            material_data={"name": "Aluminum"},
            author_info={"name": "Todd", "country": "usa"},
            frontmatter_data={"properties": []}
        )

        assert result.success is True
        assert result.metadata.get('ai_detection_score') == 75.0
```

### **Integration Test Pattern**

```python
class TestTextComponentIntegration:

    def test_end_to_end_generation(self):
        """Test complete generation pipeline"""
        generator = TextComponentGenerator("copper")

        # This would test with real API calls (use with caution)
        result = generator.generate(
            material_data=load_material_data("copper"),
            author_info=load_author_info("usa"),
            frontmatter_data=load_frontmatter_data("copper")
        )

        assert result.success is True
        assert len(result.content) > 1000  # Substantial content
        assert result.generation_time < 120  # Reasonable time limit
```

## 📊 Monitoring

### **Key Metrics**
- **Generation Time**: Total time for content generation
- **AI Detection Score**: Final quality score achieved
- **Iterations Required**: Number of improvement cycles
- **API Call Count**: Number of DeepSeek API calls made
- **Success Rate**: Percentage of successful generations

### **Status Updates**
```python
def log_generation_status(self, material: str, iteration: int,
                         score: float, elapsed: float):
    """Log detailed generation status"""
    status = {
        "material": material,
        "iteration": iteration,
        "current_score": score,
        "elapsed_time": elapsed,
        "target_score": self.config.get('target_score', 85.0),
        "timestamp": time.time()
    }

    print(f"📊 [ITERATION STATUS] {status}")
```

### **Performance Monitoring**
```python
def monitor_performance(self) -> Dict[str, Any]:
    """Monitor text component performance"""
    return {
        "average_generation_time": self._calculate_avg_generation_time(),
        "average_ai_score": self._calculate_avg_ai_score(),
        "success_rate": self._calculate_success_rate(),
        "api_call_efficiency": self._calculate_api_efficiency(),
        "memory_usage": self._get_memory_usage()
    }
```

## 🔄 Maintenance

### **Regular Updates**
- **Daily**: Monitor AI detection scores and generation times
- **Weekly**: Review prompt effectiveness and update if needed
- **Monthly**: Update persona and formatting files based on performance
- **Quarterly**: Major prompt architecture updates

### **Optimization Opportunities**
1. **Prompt Caching**: Cache constructed prompts for repeated materials
2. **Parallel Processing**: Process multiple improvement iterations in parallel
3. **Smart Iteration**: Stop early if improvement plateau is detected
4. **Content Chunking**: Break large content into smaller chunks for processing

### **Scaling Considerations**
- **API Rate Limiting**: Implement intelligent rate limiting for API calls
- **Content Batching**: Process multiple materials in batches
- **Caching Strategy**: Cache successful generations to reduce API calls
- **Load Balancing**: Distribute generation across multiple API keys

## 📚 Related Documentation

- **[Three-Layer Architecture](../CLEAN_ARCHITECTURE_SUMMARY.md)** - Prompt system design
- **[AI Detection Integration](../WINSTON_AI_INTEGRATION.md)** - Quality scoring system
- **[API Client Architecture](../API_SETUP.md)** - DeepSeek integration patterns
- **[Error Handling Patterns](../development/error_handling.md)** - Error management
- **[Performance Optimization](../development/performance_guide.md)** - Optimization techniques</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/components/text/README.md
