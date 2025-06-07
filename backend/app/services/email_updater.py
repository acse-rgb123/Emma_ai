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

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class EmailUpdater:
    def __init__(self):
        self.ai_provider = settings.ai_provider
        self.api_key = settings.api_key
        self._setup_ai_client()
    
    def _setup_ai_client(self):
        """Setup AI client based on provider"""
        if self.ai_provider == "openai" and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        elif self.ai_provider == "claude" and anthropic:
            self.client = anthropic.Client(api_key=self.api_key)
        elif self.ai_provider == "gemini" and genai:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(settings.gemini_model)
        else:
            raise ImportError(f"AI provider {self.ai_provider} not available or not installed")
    
    async def update_email(self, original_email: Dict[str, Any], update_info: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update email draft with new information using LLM"""
        try:
            prompt = f"""
You are a social care coordinator responsible for drafting professional incident notification emails. You need to update an existing email draft with new information provided by the user.

CURRENT EMAIL DRAFT JSON:
{json.dumps(original_email, indent=2)}

NEW INFORMATION PROVIDED BY USER:
"{update_info}"

TASK: Analyze the new information and determine which specific JSON fields need to be updated.

FIELD MAPPING GUIDE - Map user input to these JSON fields:
- "to": Array of primary email recipients (e.g. ["supervisor@emmacare.com"])
- "cc": Array of CC email recipients (e.g. ["riskassessment@emmacare.com"])
- "subject": Email subject line - update if incident nature changes
- "body": Email content - update with new information
- "priority": "high", "medium", or "low" - change based on urgency
- "attachments": Array of attachment names (e.g. ["incident_report.pdf"])

ANALYSIS PROCESS:
1. READ the user's new information: "{update_info}"
2. IDENTIFY which email fields this information relates to
3. UPDATE those specific fields based on the new information
4. PRESERVE all other fields exactly as they are

SPECIFIC EXAMPLES FOR THIS UPDATE:
- If user mentions changing sender organization → update "body" to change signature/sender info
- If user says "send to different person" → update "to" array with new recipients
- If user says "mark as urgent" → set "priority": "high"
- If user says "add more details" → update "body" to include new information
- If user mentions copying someone → update "cc" array
- If user changes incident severity → update "subject" and "priority"
- If user mentions new attachments → update "attachments" array

CRITICAL REQUIREMENTS:
1. You MUST return the COMPLETE JSON with ALL original fields
2. You MUST update the relevant fields based on the user input
3. You MUST preserve exact field names and data types
4. "to", "cc", "attachments" MUST always be arrays (even if single item: ["item"])
5. "priority" must be exactly "high", "medium", or "low"
6. "subject" and "body" must be strings
7. Do NOT add new fields or remove existing fields
8. Maintain professional email tone and formatting

ANALYZE THE INPUT "{update_info}" AND UPDATE THE RELEVANT FIELDS:

EMAIL JSON STRUCTURE:
- to: Array of primary recipients
- cc: Array of CC recipients  
- subject: String subject line
- body: String email content
- priority: String priority level
- attachments: Array of attachment names

Return the complete updated email as a JSON object:
"""

            if self.ai_provider == "openai":
                # Add explicit JSON instruction to prompt for models that don't support response_format
                json_prompt = prompt + "\n\nIMPORTANT: Return ONLY a valid JSON object, no additional text or markdown formatting."
                
                try:
                    response = self.client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a social care coordinator drafting professional incident notification emails. Update emails accurately while maintaining professional standards and clear communication. Always return valid JSON."
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
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "You are a social care coordinator drafting professional incident notification emails. Update emails accurately while maintaining professional standards and clear communication. Always return valid JSON only, no additional text."
                                },
                                {"role": "user", "content": json_prompt}
                            ],
                            temperature=0.3
                        )
                    else:
                        raise e
                
                # Extract JSON from response
                json_str = response.choices[0].message.content.strip()
                logger.debug(f"Raw LLM response for email update: {json_str[:500]}...")
                
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                updated_email = json.loads(json_str.strip())
            
            elif self.ai_provider == "claude":
                system_msg = """You are a social care coordinator drafting professional incident notification emails. You must update emails by analyzing user input and mapping it to specific JSON fields. Always return the complete JSON with all original fields. Focus on identifying which email fields need updating based on the user's specific input."""
                
                response = self.client.messages.create(
                    model=settings.claude_model,
                    max_tokens=settings.claude_max_tokens,
                    temperature=0.3,
                    system=system_msg,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Extract JSON from response
                json_str = response.content[0].text.strip()
                logger.debug(f"Raw Claude response for email update: {json_str[:500]}...")
                
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                updated_email = json.loads(json_str.strip())
            
            elif self.ai_provider == "gemini":
                full_prompt = f"""You are a social care coordinator drafting professional incident notification emails.
                {prompt}
                
                Return only valid JSON, no additional text or markdown formatting.
                """
                response = self.client.generate_content(full_prompt)
                json_str = response.text.strip()
                logger.debug(f"Raw Gemini response for email update: {json_str[:500]}...")
                
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                updated_email = json.loads(json_str.strip())
            
            # Validate that all original fields are present
            required_fields = ["to", "cc", "subject", "body", "priority"]
            missing_fields = []
            for field in required_fields:
                if field not in updated_email:
                    updated_email[field] = original_email.get(field, [] if field in ["to", "cc"] else "")
                    missing_fields.append(field)
            
            # Ensure attachments field exists
            if "attachments" not in updated_email:
                updated_email["attachments"] = original_email.get("attachments", [])
                if "attachments" in original_email:
                    missing_fields.append("attachments")
            
            if missing_fields:
                logger.warning(f"LLM response missing fields {missing_fields}, restored from original")
            
            # Validate structure integrity
            if not isinstance(updated_email, dict):
                logger.error("LLM returned non-dict response")
                return original_email
                
            # Validate and normalize essential field types
            # Normalize 'to' field
            if not isinstance(updated_email.get("to", []), list):
                if isinstance(updated_email.get("to"), str):
                    # Convert string to array
                    updated_email["to"] = [updated_email["to"]]
                    logger.info("Converted 'to' field from string to array")
                else:
                    logger.warning("Invalid 'to' field type, restoring from original")
                    updated_email["to"] = original_email.get("to", [])
            
            # Normalize 'cc' field  
            if not isinstance(updated_email.get("cc", []), list):
                if isinstance(updated_email.get("cc"), str):
                    # Convert string to array
                    updated_email["cc"] = [updated_email["cc"]]
                    logger.info("Converted 'cc' field from string to array")
                else:
                    logger.warning("Invalid 'cc' field type, restoring from original")
                    updated_email["cc"] = original_email.get("cc", [])
            
            # Normalize 'attachments' field
            if not isinstance(updated_email.get("attachments", []), list):
                if isinstance(updated_email.get("attachments"), str):
                    # Convert string to array
                    updated_email["attachments"] = [updated_email["attachments"]]
                    logger.info("Converted 'attachments' field from string to array")
                else:
                    updated_email["attachments"] = original_email.get("attachments", [])
                
            # Detailed change detection and logging
            changed_fields = {}
            for field, new_value in updated_email.items():
                original_value = original_email.get(field)
                if new_value != original_value:
                    changed_fields[field] = {
                        "original": original_value,
                        "updated": new_value
                    }
            
            if changed_fields:
                logger.info(f"Email updated successfully using LLM. Changes detected:")
                for field, changes in changed_fields.items():
                    logger.info(f"  - {field}: '{str(changes['original'])[:100]}...' → '{str(changes['updated'])[:100]}...'")
            else:
                logger.warning(f"No changes detected in updated email. User input was: '{update_info}'")
                logger.warning("This might indicate the LLM didn't understand which fields to update")
                
            return updated_email
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON returned from LLM: {e}")
            logger.info("Falling back to original email")
            return original_email
        except Exception as e:
            logger.error(f"Error updating email with LLM: {e}")
            logger.info("Falling back to original email")
            return original_email
    
    def _fallback_update(self, original_email: Dict[str, Any], update_info: str) -> Dict[str, Any]:
        """Fallback method for updating email if LLM fails"""
        logger.info("Using fallback email update method")
        
        # Simple fallback - add update info to the email body
        updated_email = original_email.copy()
        
        if "body" in updated_email:
            # Add the new information before the closing
            closing_index = updated_email["body"].rfind("Best regards,")
            if closing_index != -1:
                updated_body = (
                    updated_email["body"][:closing_index] + 
                    f"\n**Additional Information:**\n{update_info}\n\n" +
                    updated_email["body"][closing_index:]
                )
                updated_email["body"] = updated_body
            else:
                updated_email["body"] += f"\n\nAdditional Information: {update_info}"
        else:
            updated_email["body"] = f"Additional Information: {update_info}"
        
        return updated_email