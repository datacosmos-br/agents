## Pattern 1: Adding New Config Sections with Backward Compatibility

### Example: Adding `adapters` Section While Keeping `cli_tools`

**Problem**: You need to add a new config section (`adapters`) to replace an old one (`cli_tools`) without breaking existing configs.

**Solution Pattern** (from `models/config.py`):

```python
from typing import Optional
from pydantic import BaseModel
import warnings

class Config(BaseModel):
    """Root configuration model."""

    # New section (preferred)
    adapters: Optional[dict[str, AdapterConfig]] = None

    # Legacy section (deprecated)
    cli_tools: Optional[dict[str, CLIToolConfig]] = None

    def model_post_init(self, __context):
        """Post-initialization validation."""
        # Ensure at least one section exists
        if self.adapters is None and self.cli_tools is None:
            raise ValueError(
                "Configuration must include either 'adapters' or 'cli_tools' section"
            )

        # Emit deprecation warning for old section
        if self.cli_tools is not None and self.adapters is None:
            warnings.warn(
                "The 'cli_tools' configuration section is deprecated. "
                "Please migrate to 'adapters' section with explicit 'type' field. "
                "See migration guide: docs/migration/cli_tools_to_adapters.md",
                DeprecationWarning,
                stacklevel=2,
            )
```

**Key Techniques**:

- Use `Optional` for both old and new sections
- Validate in `model_post_init()` that at least one exists
- Emit `DeprecationWarning` when old section is used
- Reference migration documentation in warning message
- Allow both sections temporarily for gradual migration

## Pattern 2: Type Discrimination with Discriminated Unions
