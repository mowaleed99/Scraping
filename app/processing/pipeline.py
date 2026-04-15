import dspy
from typing import Dict, Any

from app.processing.signatures import ClassifyPost, ExtractEntities

class LostFoundPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(ClassifyPost)
        self.extract = dspy.ChainOfThought(ExtractEntities)

    def forward(self, post_text: str) -> Dict[str, Any]:
        """
        Processes a post:
        1. Classifies as lost/found/irrelevant
        2. Extends extraction if not irrelevant
        """
        classification = self.classify(post_text=post_text)
        
        # Guard against LLM output format issues
        post_type = str(classification.post_type).lower()
        if dict(post_type=post_type).get("post_type", "") not in ["lost", "found", "irrelevant"]:
            if "lost" in post_type:
                post_type = "lost"
            elif "found" in post_type:
                post_type = "found"
            else:
                post_type = "irrelevant"
            
        try:
            confidence = float(classification.confidence)
        except (ValueError, TypeError):
            confidence = 0.0

        if post_type == "irrelevant":
            return {
                "post_type": "irrelevant",
                "confidence": confidence,
                "item_type": None,
                "person_name": None,
                "location": None,
                "contact_info": None,
            }
            
        extraction = self.extract(post_text=post_text)
        
        return {
            "post_type": post_type,
            "confidence": confidence,
            "item_type": None if extraction.item_type in ["Not mentioned", "null", ""] else extraction.item_type,
            "person_name": None if extraction.person_name in ["Not mentioned", "null", ""] else extraction.person_name,
            "location": None if extraction.location in ["Not mentioned", "null", ""] else extraction.location,
            "contact_info": None if extraction.contact_info in ["Not mentioned", "null", ""] else extraction.contact_info,
        }
