    def _fallback_generate(self, transcript: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report using rule-based approach"""
        logger.info("Using fallback report generation")
        
        # Import extraction functions
        from .analyzer_fix import extract_name_from_transcript, extract_location_from_transcript
        
        # Extract information from transcript
        service_user_name = extract_name_from_transcript(transcript) or "Unknown"
        location = extract_location_from_transcript(transcript) or "Not specified"
        
        # Determine incident type from analysis
        incident_types = []
        for violation in analysis.get("violations", []):
            if "fall" in violation.get("violation_type", "").lower():
                incident_types.append("Fall")
            if "mental" in violation.get("violation_type", "").lower():
                incident_types.append("Mental Health Concern")
        
        # Extract time if mentioned
        import re
        time_match = re.search(r'(\d+)\s*(?:minutes?|mins?|hours?)', transcript, re.IGNORECASE)
        time_on_floor = time_match.group(0) if time_match else "Unknown duration"
        
        report = {
            "date_time": datetime.now().isoformat(),
            "service_user_name": service_user_name,
            "location": location,
            "incident_type": ", ".join(incident_types) if incident_types else "Incident",
            "description": self._extract_description(transcript),
            "immediate_actions": "Support provided as per protocol" if not analysis.get("violations") else "Immediate support initiated. " + "; ".join([v.get("required_action", "") for v in analysis.get("violations", [])[:2]]),
            "first_aid_administered": "injury" in transcript.lower() or "hurt" in transcript.lower(),
            "emergency_services_contacted": "emergency" in transcript.lower() or "999" in transcript or "ambulance" in transcript.lower(),
            "who_was_notified": ", ".join(analysis.get("notifications_required", [])) or "To be determined",
            "witnesses": "None reported",
            "agreed_next_steps": self._generate_next_steps(analysis) or "To be determined following assessment",
            "risk_assessment_needed": len(analysis.get("risk_assessments", [])) > 0,
            "risk_assessment_type": ", ".join(analysis.get("risk_assessments", [])) or "N/A"
        }
        
        return report
    
    def _extract_description(self, transcript: str) -> str:
        """Extract incident description from transcript"""
        description_parts = []
        
        # Extract key facts
        if "fallen" in transcript.lower() or "fall" in transcript.lower():
            # Find context around fall
            import re
            fall_context = re.search(r'([^.]*(?:fallen|fall)[^.]*)', transcript, re.IGNORECASE)
            if fall_context:
                description_parts.append(fall_context.group(1).strip())
        
        if "confused" in transcript.lower() or "can't remember" in transcript.lower():
            description_parts.append("Service user exhibited signs of confusion or memory difficulties.")
        
        if "hurt" in transcript.lower() or "pain" in transcript.lower():
            pain_context = re.search(r'([^.]*(?:hurt|pain)[^.]*)', transcript, re.IGNORECASE)
            if pain_context:
                description_parts.append(pain_context.group(1).strip())
        
        # Count occurrences
        if "third time" in transcript.lower() or "multiple" in transcript.lower():
            description_parts.append("This is a recurring incident.")
        
        return " ".join(description_parts) if description_parts else "Service user contacted support. Details to be confirmed."
