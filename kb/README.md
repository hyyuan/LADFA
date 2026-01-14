# Knowledge Base Files Documentation

## Overview

All knowledge base JSON files use a unified structure with `"Root"` as the top-level key. This allows `rag.py`'s `convert_json()` function to process all files uniformly.

## JSON Structure

```json
{
  "Root": [
    {
      "name": "category name",
      "description": "detailed description",
      "items": ["item1", "item2", ...]
    }
  ]
}
```

## File Descriptions

| File | Purpose | What "Root" Represents |
|------|---------|------------------------|
| `data_categories_kt.json` | Personal data type categories | Data Category |
| `data_consumer_type_kt.json` | Entities that collect/receive data | Data Consumer Type |
| `data_processing_method_kt.json` | Methods of data collection/processing | Data Processing Method |
| `data_processing_purpose_kt.json` | Reasons for data processing | Data Processing Purpose |

## Key Points

- `"Root"` is the top-level key in all files
- Each file contains an array of category objects under `"Root"`
- The meaning of `"Root"` varies by file (see table above)
- Consistent structure enables unified processing by `rag.convert_json()`
