from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str = "gemini-3-flash-preview"
    temperature: float = 0.7
    thinking_level: str = "medium"
