# Metadata Enhancement Pipeline

The Dublin Core Metadata Enhancer includes an automated pipeline for generating WCAG 2.2-compliant alternative text for images in Dublin Core metadata records.

## System Overview

```{mermaid}
graph TB
    subgraph "Input Sources"
        A[Dublin Core JSON URL]
        B[OpenAI API Key]
    end

    subgraph "Enhancement Pipeline"
        C[MetadataEnhancer Class]
        D[CLI Interface]
        E[Image Processing]
        F[AI Analysis GPT-4o-2024-11-20]
    end

    subgraph "Output"
        G[Enhanced JSON with Alt Text]
        H[Error Logs]
    end

    A --> C
    B --> C
    C --> D
    C --> E
    E --> F
    F --> G
    C --> H

    style A fill:#e1f5fe
    style G fill:#e8f5e8
    style F fill:#fff3e0
```

## Overview

This pipeline uses OpenAI's newest GPT-4o model (gpt-4o-2024-11-20) multimodal capabilities to analyze images within their metadata context and generate appropriate alternative text descriptions in German.

### Pipeline Architecture

```{mermaid}
graph TD
    A[Load Dublin Core Metadata] --> B[Extract Image URLs]
    B --> C[Download & Process Images]
    C --> D[Build Context Prompts]
    D --> E[OpenAI GPT-4o Analysis]
    E --> F[Generate Alt Text]
    F --> G[Validate WCAG 2.2 Compliance]
    G --> H[Save Enhanced Metadata]

    C --> I[Image Preprocessing]
    I --> J[Resize to 800x800 max]
    J --> K[Format Optimization]
    K --> D

    E --> L{Image Type Classification}
    L -->|Informative| M[Generate 1-2 sentences<br/>Max 120 chars]
    L -->|Complex/Maps/Diagrams| N[Generate description<br/>Max 200 chars + longdesc]
    L -->|Text Images| O[OCR-based alt text]

    M --> F
    N --> F
    O --> F
```

## Components

### Core Module (`src/metadata_enhancer.py`)

The main `MetadataEnhancer` class provides:

- **Metadata Loading**: Fetch Dublin Core metadata from JSON URLs
- **Image Processing**: Download and prepare images for AI analysis
- **Prompt Generation**: Create contextual prompts using metadata
- **AI Integration**: Generate alt text using OpenAI GPT-4o API
- **Output Generation**: Save enhanced metadata as JSON

### CLI Interface (`enhance_metadata.py`)

Command-line tool for running the enhancement pipeline:

```bash
python enhance_metadata.py [options]
```

### CLI Workflow

```{mermaid}
graph TD
    A[Start CLI] --> B[Parse Arguments]
    B --> C{API Key Set?}
    C -->|No| D[Error: Missing API Key]
    C -->|Yes| E[Initialize MetadataEnhancer]

    E --> F[Load Metadata from URL]
    F --> G{Valid Metadata?}
    G -->|No| H[Error: Invalid Metadata]
    G -->|Yes| I[Process Each Object]

    I --> J[Extract Image Information]
    J --> K[Generate Alt Text]
    K --> L[Collect Enhanced Objects]

    L --> M{More Objects?}
    M -->|Yes| I
    M -->|No| N[Save to Output File]

    N --> O[Success: Enhancement Complete]

    D --> P[Exit with Error]
    H --> P
    O --> Q[Exit Successfully]

    style A fill:#e3f2fd
    style O fill:#e8f5e8
    style D fill:#ffebee
    style H fill:#ffebee
```

Options:

- `--metadata-url`: Source URL for metadata JSON
- `--output`: Output file for enhanced metadata
- `--api-key`: OpenAI API key (or use environment variable)

### Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or copy `example.env` to `.env` and configure:

```bash
cp example.env .env
# Edit .env with your API key
```

## AI Prompt Design

The pipeline uses a carefully designed German prompt that follows a systematic decision process:

### Image Classification Decision Tree

```{mermaid}
graph TD
    A[Image Analysis Start] --> B{Contains readable text?}
    B -->|Yes| C[Text Image Type]
    C --> D[OCR-based alt text<br/>Transcribe visible text]

    B -->|No| E{Complex visual content?}
    E -->|Yes - Maps/Diagrams| F[Complex Content Type]
    F --> G[Generate descriptive alt text<br/>Max 200 chars + optional longdesc]

    E -->|No - Simple image| H[Informative Image Type]
    H --> I[Generate concise description<br/>1-2 sentences, max 120 chars]

    D --> J[Apply WCAG 2.2 Guidelines]
    G --> J
    I --> J

    J --> K[German language output<br/>No "Image of..." prefixes<br/>Contextual and descriptive]
```

### Prompt Context Integration

```{mermaid}
graph LR
    A[Dublin Core Metadata] --> B[Extract Context]
    B --> C[Title]
    B --> D[Description]
    B --> E[Subject Terms]
    B --> F[Historical Era]
    B --> G[Creator Info]
    B --> H[Date Information]

    C --> I[Build Contextual Prompt]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J[Send to OpenAI GPT-4o]
    J --> K[Generate Contextual Alt Text]
```

The prompt design follows these principles:

1. **Identifies image types**:
   - Informative images (1-2 sentences, max 120 characters)
   - Complex content like diagrams/maps (max 200 characters, optional long description)
   - Text images (OCR-based alt text)

2. **Incorporates metadata context**:
   - Title, description, subject terms
   - Historical era, creator, dates
   - Collection and relationship information

3. **Follows WCAG 2.2 guidelines**:
   - Concise and descriptive
   - No redundant "Image of..." prefixes
   - German language output
   - Structured JSON response

## Output Format

Enhanced metadata objects include:

```json
{
	"objectid": "unique-identifier",
	"alt_text": "Descriptive alternative text in German",
	"longdesc": "Optional detailed description for complex content"
}
```

### Data Transformation Flow

```{mermaid}
graph LR
    A[Input: Dublin Core JSON] --> B[Extract Object Data]
    B --> C[Object Metadata]

    C --> D[objectid]
    C --> E[title]
    C --> F[description]
    C --> G[subject]
    C --> H[format/image URL]

    H --> I[Image Download & Analysis]
    D --> J[Context Building]
    E --> J
    F --> J
    G --> J

    I --> K[OpenAI GPT-4o Processing]
    J --> K

    K --> L[Generated Alt Text]
    K --> M[Optional Long Description]

    D --> N[Enhanced Object]
    L --> N
    M --> N

    N --> O[Output: Enhanced JSON]

    style A fill:#e1f5fe
    style O fill:#e8f5e8
    style K fill:#fff3e0
```

## Error Handling

The pipeline includes robust error handling for network, API, and processing issues:

### Error Handling Flow

```{mermaid}
graph TD
    A[Process Object] --> B{Valid image URL?}
    B -->|No| C[Log Warning & Skip]
    B -->|Yes| D[Download Image]

    D --> E{Download Success?}
    E -->|No| F[Network Error<br/>Log & Skip]
    E -->|Yes| G[Process Image]

    G --> H{Valid Image Format?}
    H -->|No| I[Format Error<br/>Log & Skip]
    H -->|Yes| J[Send to OpenAI]

    J --> K{API Success?}
    K -->|No| L[API Error<br/>Log & Skip]
    K -->|Yes| M{Valid JSON Response?}

    M -->|No| N[Parse Error<br/>Log & Skip]
    M -->|Yes| O[Save Enhanced Object]

    C --> P[Continue Next Object]
    F --> P
    I --> P
    L --> P
    N --> P
    O --> P
```

The pipeline handles various error scenarios:

- Network connectivity issues
- Invalid image formats
- API rate limits and errors
- Malformed metadata
- Missing required fields

Failed objects are logged and skipped, allowing the pipeline to continue processing other objects.

## Testing

Unit tests cover all major components:

```bash
python test/test_metadata_enhancer.py
```

Tests use mocking to avoid API calls during development and validate:

- Metadata extraction and prompt building
- Image processing logic
- Error handling scenarios
- CLI argument parsing

## Performance Considerations

- **Batch Processing**: Process multiple objects in sequence
- **Rate Limiting**: Respect OpenAI API limits
- **Image Optimization**: Resize images to 800x800 maximum
- **Caching**: Consider implementing caching for repeated images

## Security

- API keys are handled securely through environment variables
- No sensitive data is logged or stored in outputs
- Image data is processed in memory only
