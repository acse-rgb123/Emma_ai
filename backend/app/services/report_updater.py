import os
import json
import logging
from typing import Dict, Any

from app.config import settings

# AI Provider imports
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class ReportUpdater:
    def __init__(self):
        if not OpenAI:
            raise ImportError("OpenAI package is required but not installed")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def update_report(self, original_report: Dict[str, Any], update_info: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update incident report with new information using LLM"""
        try:
            prompt = f"""
You are a social care incident report specialist. You need to update an existing incident report with new information provided by the user.

CURRENT INCIDENT REPORT JSON:
{json.dumps(original_report, indent=2)}

NEW INFORMATION PROVIDED BY USER:
"{update_info}"

TASK: Analyze the new information and determine which specific JSON fields need to be updated.

FIELD MAPPING GUIDE - Map user input to these JSON fields:
- "date_time": Any time/date references
- "service_user_name": Person's name mentioned
- "location": Any location/place mentioned (bedroom, kitchen, etc.)
- "incident_type": Type of incident (Fall, Medical Emergency, etc.)
- "description": Details about what happened
- "immediate_actions": Actions taken immediately
- "first_aid_administered": true/false - if first aid was given or NOT given
- "emergency_services_contacted": true/false - if emergency services called
- "who_was_notified": List of people/roles notified
- "witnesses": Any witnesses mentioned
- "agreed_next_steps": Future actions planned
- "risk_assessment_needed": true/false - if assessment required
- "risk_assessment_type": Type of assessment needed

ANALYSIS PROCESS:
1. READ the user's new information: "{update_info}"
2. IDENTIFY which fields this information relates to
3. UPDATE those specific fields based on the new information
4. PRESERVE all other fields exactly as they are

SPECIFIC EXAMPLES FOR THIS UPDATE:
- If user says "first aid was not given" → set "first_aid_administered": false
- If user says "first aid was administered" → set "first_aid_administered": true
- If user says "no injuries" → update "description" to mention no injuries
- If user says "ambulance called" → set "emergency_services_contacted": true
- If user says "supervisor was notified" → update "who_was_notified" field
- If user mentions a new location → update "location" field
- If user adds injury details → update "description" and possibly "first_aid_administered"

CRITICAL REQUIREMENTS:
1. You MUST return the COMPLETE JSON with ALL original fields
2. You MUST update the relevant fields based on the user input
3. You MUST preserve exact field names and data types
4. Boolean fields (first_aid_administered, emergency_services_contacted, risk_assessment_needed) must be true or false
5. String fields must contain descriptive text
6. Do NOT add new fields or remove existing fields

ANALYZE THE INPUT "{update_info}" AND UPDATE THE RELEVANT FIELDS:

Return the complete updated incident report as a JSON object:
"""

            # Add explicit JSON instruction to prompt for models that don't support response_format
            json_prompt = prompt + "\n\nIMPORTANT: Return ONLY a valid JSON object, no additional text or markdown formatting."
            
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    max_tokens=settings.openai_max_tokens,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a social care incident report specialist. Update incident reports accurately and professionally based on new information. Always return valid JSON."
                        },
                        {"role": "user", "content": json_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
            except Exception as e:
                if "response_format" in str(e):
                    # Fallback for models that don't support response_format
                    response = self.client.chat.completions.create(
                        model=settings.openai_model,
                        max_tokens=settings.openai_max_tokens,
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a social care incident report specialist. Update incident reports accurately and professionally based on new information. Always return valid JSON only, no additional text."
                            },
                            {"role": "user", "content": json_prompt}
                        ],
                        temperature=0.3
                    )
                else:
                    raise e
            
            # Extract JSON from response
            json_str = response.choices[0].message.content.strip()
            logger.debug(f"Raw OpenAI response for report update: {json_str[:500]}...")
            
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            updated_report = json.loads(json_str.strip())
            
            # Validate that all original fields are present
            missing_fields = []
            for field in original_report.keys():
                if field not in updated_report:
                    updated_report[field] = original_report[field]
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"OpenAI response missing fields {missing_fields}, restored from original")
            
            # Validate structure integrity
            if not isinstance(updated_report, dict):
                logger.error("OpenAI returned non-dict response")
                return original_report
                
            # Detailed change detection and logging
            changed_fields = {}
            for field, new_value in updated_report.items():
                original_value = original_report.get(field)
                if new_value != original_value:
                    changed_fields[field] = {
                        "original": original_value,
                        "updated": new_value
                    }
            
            if changed_fields:
                logger.info(f"Report updated successfully using OpenAI. Changes detected:")
                for field, changes in changed_fields.items():
                    logger.info(f"  - {field}: '{changes['original']}' → '{changes['updated']}'")
            else:
                logger.warning(f"No changes detected in updated report. User input was: '{update_info}'")
                logger.warning("This might indicate OpenAI didn't understand which fields to update")
                
            return updated_report
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON returned from OpenAI: {e}")
            logger.info("Falling back to original report")
            return original_report
        except Exception as e:
            logger.error(f"Error updating report with OpenAI: {e}")
            logger.info("Falling back to original report")
            return original_report
    
    def _fallback_update(self, original_report: Dict[str, Any], update_info: str) -> Dict[str, Any]:
        """Fallback method for updating report if OpenAI fails"""
        logger.info("Using fallback report update method")
        
        # Simple fallback - just add update info to description
        updated_report = original_report.copy()
        
        if "description" in updated_report:
            updated_report["description"] += f" Additional information: {update_info}"
        else:
            updated_report["description"] = f"Additional information: {update_info}"
        
        return updated_report