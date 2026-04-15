import dspy
from typing import Literal, Optional

class ClassifyPost(dspy.Signature):
    """
    Classify an Arabic (or mixed) Facebook post as 'lost', 'found', or 'irrelevant'.
    Lost: person is searching for something/someone.
    Found: person found something/someone.
    Irrelevant: unrelated to lost/found, or ads/spam.
    """
    post_text: str = dspy.InputField(desc="Raw Facebook post text, may be in Arabic or mixed language")
    post_type: Literal["lost", "found", "irrelevant"] = dspy.OutputField(desc="Must be 'lost', 'found', or 'irrelevant'")
    confidence: float = dspy.OutputField(desc="Confidence score between 0.0 and 1.0")

class ExtractEntities(dspy.Signature):
    """
    Extract structured information from a lost/found Arabic Facebook post.
    Return null, empty string, or "Not mentioned" for fields not mentioned. Do not hallucinate.
    """
    post_text: str = dspy.InputField(desc="Arabic or mixed Facebook post text")
    item_type: Optional[str] = dspy.OutputField(desc="Type of item/person lost or found (e.g. wallet, phone, child, pet)")
    person_name: Optional[str] = dspy.OutputField(desc="Name of person mentioned (lost person or owner)")
    location: Optional[str] = dspy.OutputField(desc="Location where item was lost/found")
    contact_info: Optional[str] = dspy.OutputField(desc="Phone, WhatsApp, or social media contact mentioned in text")
