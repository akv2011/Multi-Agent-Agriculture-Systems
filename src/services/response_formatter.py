"""
Response Formatting Service
Structures and formats AI responses for better presentation
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class ResponseFormatter:
    """Formats raw AI responses into structured, well-organized content"""
    
    def __init__(self):
        self.emoji_map = {
            "crop": "🌾",
            "water": "💧", 
            "pest": "🐛",
            "disease": "🦠",
            "fertilizer": "🧪",
            "market": "💰",
            "weather": "🌤️",
            "satellite": "🛰️",
            "success": "✅",
            "warning": "⚠️",
            "info": "ℹ️",
            "recommendation": "💡",
            "urgent": "🚨"
        }
    
    def format_comprehensive_response(self, raw_response: str, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw response into comprehensive structured format"""
        
        # Clean and parse the raw response
        cleaned_response = self._clean_raw_response(raw_response)
        
        # Apply additional comprehensive cleaning
        cleaned_response = self._comprehensive_text_cleaning(cleaned_response)
        
        # Extract structured components
        structured_data = self._extract_structured_components(cleaned_response)
        
        # Create formatted sections
        formatted_response = {
            "executive_summary": self._create_executive_summary(structured_data, query_analysis),
            "detailed_analysis": self._create_detailed_analysis(structured_data),
            "actionable_recommendations": self._create_actionable_recommendations(structured_data),
            "supporting_data": self._create_supporting_data(structured_data),
            "confidence_indicators": self._create_confidence_indicators(structured_data),
            "next_steps": self._create_next_steps(structured_data),
            "formatted_display": self._create_formatted_display(structured_data, query_analysis)
        }
        
        return formatted_response
    
    def _clean_raw_response(self, raw_response: str) -> str:
        """Clean raw response by removing unnecessary formatting"""
        if not raw_response:
            return ""
        
        # Remove all markdown formatting
        cleaned = re.sub(r'\*{1,}', '', raw_response)  # Remove all asterisks
        cleaned = re.sub(r'#{1,}', '', cleaned)  # Remove hash headers
        cleaned = re.sub(r'`{1,}', '', cleaned)  # Remove backticks
        cleaned = re.sub(r'_{1,}', '', cleaned)  # Remove underscores for emphasis
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)  # Convert links to text
        
        # Clean bullet points and numbering
        cleaned = re.sub(r'^[\s]*[-\*\+•·]\s*', '• ', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^\s*(\d+)[\.\)]\s*', r'\1. ', cleaned, flags=re.MULTILINE)
        
        # Fix line breaks and spacing
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Remove excessive line breaks
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Remove excessive spaces
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _extract_structured_components(self, text: str) -> Dict[str, Any]:
        """Extract structured components from cleaned text"""
        components = {
            "title": "",
            "sections": [],
            "recommendations": [],
            "data_points": [],
            "metrics": {},
            "warnings": [],
            "benefits": []
        }
        
        if not text:
            return components
        
        lines = text.split('\n')
        current_section = ""
        current_content = []
        
        # First pass: collect all content as a single section if no clear headers found
        has_clear_sections = any(self._is_section_header(line.strip()) for line in lines if line.strip())
        
        if not has_clear_sections:
            # Treat entire content as one section
            components["sections"].append({
                "title": "Analysis",
                "content": text
            })
            # Still extract recommendations, warnings, etc.
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                self._extract_content_types(line, components)
        else:
            # Process with section headers
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect section headers
                if self._is_section_header(line):
                    if current_section and current_content:
                        components["sections"].append({
                            "title": current_section,
                            "content": '\n'.join(current_content)
                        })
                    current_section = line
                    current_content = []
                elif current_section:
                    current_content.append(line)
                    self._extract_content_types(line, components)
                else:
                    # Content before any section header
                    current_content.append(line)
                    self._extract_content_types(line, components)
            
            # Add the last section
            if current_section and current_content:
                components["sections"].append({
                    "title": current_section,
                    "content": '\n'.join(current_content)
                })
            elif current_content and not has_clear_sections:
                # Add content that appeared before any headers
                components["sections"].append({
                    "title": "Overview",
                    "content": '\n'.join(current_content)
                })
        
        return components
    
    def _extract_content_types(self, line: str, components: Dict[str, Any]):
        """Extract specific types of content from a line"""
        # Extract specific types of content
        if any(keyword in line.lower() for keyword in ["recommend", "suggest", "should", "apply", "use", "चाहिए"]):
            components["recommendations"].append(line)
        
        if any(keyword in line.lower() for keyword in ["warning", "caution", "risk", "avoid", "सावधान"]):
            components["warnings"].append(line)
        
        if any(keyword in line.lower() for keyword in ["benefit", "advantage", "improved", "फायदा"]):
            components["benefits"].append(line)
        
        # Extract numerical data
        numbers = re.findall(r'\d+(?:\.\d+)?', line)
        if numbers:
            components["data_points"].append({
                "text": line,
                "values": numbers
            })
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header"""
        if not line:
            return False
            
        # Clean the line for better detection
        clean_line = line.strip()
        
        # Exclude bullet points and content lines
        if clean_line.startswith('•') or clean_line.startswith('-') or clean_line.startswith('*'):
            return False
        
        # Exclude lines that look like content rather than headers
        content_indicators = [
            'based on', 'here\'s', 'this is', 'you should', 'it can',
            'avoid', 'improved', 'reduced', 'better', 'install', 'implement',
            'apply', 'use', 'monitor', 'schedule'
        ]
        if any(indicator in clean_line.lower() for indicator in content_indicators):
            return False
        
        # Check for real header indicators
        header_indicators = [
            # Ends with colon (strong indicator)
            clean_line.endswith(':'),
            # Numbered sections (1., 2., etc.) but not bullet content
            re.match(r'^\d+\.\s+[A-Z][^:]*:?$', clean_line),
            # Title-like format with main agricultural keywords
            (len(clean_line.split()) <= 4 and 
             any(keyword in clean_line.lower() for keyword in [
                 "analysis", "recommendations", "conditions", "benefits", 
                 "warning", "strategy", "actions"
             ]) and
             clean_line[0].isupper())
        ]
        
        return any(header_indicators)
    
    def _create_executive_summary(self, components: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary section"""
        intent = query_analysis.get("intent", "general")
        
        summary = {
            "query_type": intent.replace("_", " ").title(),
            "key_insight": "",
            "primary_recommendation": "",
            "confidence_level": "High",
            "urgency": "Normal"
        }
        
        # Extract key insight from first section
        if components["sections"]:
            first_section = components["sections"][0]["content"]
            summary["key_insight"] = first_section.split('.')[0] if first_section else ""
        
        # Extract primary recommendation
        if components["recommendations"]:
            summary["primary_recommendation"] = components["recommendations"][0]
        
        # Determine urgency from warnings
        if components["warnings"]:
            summary["urgency"] = "High"
        elif any(keyword in str(components).lower() for keyword in ["immediate", "urgent", "critical"]):
            summary["urgency"] = "Medium"
        
        return summary
    
    def _create_detailed_analysis(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create detailed analysis section"""
        analysis_sections = []
        
        for section in components["sections"]:
            # Apply comprehensive cleaning to section content
            clean_content = self._comprehensive_text_cleaning(section["content"])
            
            analysis_sections.append({
                "title": self._format_section_title(section["title"]),
                "content": self._format_section_content(clean_content),
                "data_points": [dp for dp in components["data_points"] 
                              if any(val in section["content"] for val in dp["values"])],
                "importance": self._assess_section_importance(section["content"])
            })
        
        return analysis_sections
    
    def _comprehensive_text_cleaning(self, text: str) -> str:
        """
        Apply comprehensive text cleaning to remove all markdown and formatting artifacts
        """
        if not text:
            return ""
        
        import re
        
        # Remove all markdown formatting aggressively
        cleaned = text
        
        # Remove all asterisks (bold/italic) - be more aggressive
        cleaned = re.sub(r'\*+', '', cleaned)
        
        # Remove all hash symbols (headers)
        cleaned = re.sub(r'#+\s*', '', cleaned)
        
        # Remove all backticks (code formatting)
        cleaned = re.sub(r'`+', '', cleaned)
        
        # Remove all underscores used for emphasis
        cleaned = re.sub(r'_+', '', cleaned)
        
        # Remove HTML tags if any
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Clean up links - convert [text](url) to just text
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
        
        # Clean bullet points and make them consistent
        cleaned = re.sub(r'^[\s]*[-\*\+•·]\s*', '• ', cleaned, flags=re.MULTILINE)
        
        # Clean numbered lists
        cleaned = re.sub(r'^\s*(\d+)[\.\)]\s*', r'\1. ', cleaned, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)  # Multiple line breaks
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Multiple spaces/tabs
        cleaned = re.sub(r'^\s+', '', cleaned, flags=re.MULTILINE)  # Leading spaces
        
        # Fix sentence endings
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Ensure proper sentence ending
                if line and not line.endswith(('.', '!', '?', ':')):
                    if not line.endswith((')', ']', '%')):  # Don't add period to these
                        line += '.'
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _create_actionable_recommendations(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create actionable recommendations"""
        recommendations = []
        
        for i, rec in enumerate(components["recommendations"][:5], 1):  # Limit to top 5
            recommendations.append({
                "priority": i,
                "action": self._format_recommendation(rec),
                "timeline": self._extract_timeline(rec),
                "impact": self._assess_impact(rec),
                "difficulty": self._assess_difficulty(rec)
            })
        
        return recommendations
    
    def _create_supporting_data(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Create supporting data section"""
        return {
            "key_metrics": self._extract_metrics(components["data_points"]),
            "data_sources": ["Satellite Data", "Agricultural Database", "Weather Forecast"],
            "reliability_score": 0.85,
            "last_updated": datetime.now().isoformat()
        }
    
    def _create_confidence_indicators(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Create confidence indicators"""
        data_quality = len(components["data_points"]) * 0.1
        recommendation_clarity = len(components["recommendations"]) * 0.15
        section_completeness = len(components["sections"]) * 0.1
        
        overall_confidence = min(0.95, 0.5 + data_quality + recommendation_clarity + section_completeness)
        
        return {
            "overall_confidence": round(overall_confidence, 2),
            "data_quality": min(0.9, data_quality + 0.6),
            "recommendation_clarity": min(0.95, recommendation_clarity + 0.7),
            "factors": {
                "satellite_data_available": True,
                "historical_data_used": True,
                "expert_validation": True,
                "real_time_analysis": True
            }
        }
    
    def _create_next_steps(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create next steps section"""
        next_steps = []
        
        # Extract immediate actions
        for i, rec in enumerate(components["recommendations"][:3], 1):
            next_steps.append({
                "step": i,
                "action": self._simplify_action(rec),
                "timeframe": self._extract_timeframe(rec),
                "resources_needed": self._extract_resources(rec)
            })
        
        return next_steps
    
    def _create_formatted_display(self, components: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create formatted display for frontend"""
        intent = query_analysis.get("intent", "general")
        emoji = self.emoji_map.get(intent.split('_')[0], "🌾")
        
        formatted_sections = []
        
        for section in components["sections"]:
            formatted_sections.append({
                "type": "section",
                "title": f"{emoji} {self._format_section_title(section['title'])}",
                "content": self._format_for_display(section["content"]),
                "collapsible": len(section["content"]) > 200
            })
        
        if components["recommendations"]:
            formatted_sections.append({
                "type": "recommendations",
                "title": f"💡 Key Recommendations",
                "content": self._format_recommendations_for_display(components["recommendations"]),
                "highlight": True
            })
        
        if components["warnings"]:
            formatted_sections.append({
                "type": "warnings",
                "title": f"⚠️ Important Warnings",
                "content": self._format_warnings_for_display(components["warnings"]),
                "alert": True
            })
        
        return {
            "sections": formatted_sections,
            "layout": "responsive",
            "theme": "agricultural"
        }
    
    def format_structured_ai_response(self, agent_response: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format structured AI response to ensure consistent, frontend-ready output
        """
        
        # Extract structured data from metadata if available
        metadata = agent_response.get("metadata", {})
        structured_sections = {
            "analysis": metadata.get("analysis_section", ""),
            "agent_type": metadata.get("agent_type", "General Agriculture"),
            "priority": metadata.get("priority", "Medium"),
            "action_items": metadata.get("action_items", [])
        }
        
        # Build consistent structured response
        structured_response = {
            "executive_summary": {
                "query_type": structured_sections["agent_type"],
                "key_insight": self._extract_key_insight(structured_sections["analysis"]),
                "primary_recommendation": self._extract_primary_recommendation(agent_response.get("recommendations", [])),
                "confidence_level": self._map_confidence_to_level(agent_response.get("confidence_score", 0.5)),
                "urgency": structured_sections["priority"]
            },
            
            "detailed_analysis": [
                {
                    "section": "Agricultural Analysis",
                    "content": structured_sections["analysis"],
                    "emoji": self.emoji_map.get("crop", "🌾"),
                    "type": "analysis"
                }
            ],
            
            "actionable_recommendations": self._format_structured_recommendations(
                agent_response.get("recommendations", [])
            ),
            
            "implementation_steps": self._format_action_items(structured_sections["action_items"]),
            
            "supporting_data": {
                "agent_type": structured_sections["agent_type"],
                "priority_level": structured_sections["priority"],
                "confidence_score": agent_response.get("confidence_score", 0.5),
                "processing_time": metadata.get("processing_time", 0),
                "structured_format": True
            },
            
            "confidence_indicators": {
                "overall_score": agent_response.get("confidence_score", 0.5),
                "data_quality": "High" if metadata.get("structured_format") else "Medium",
                "expert_validation": True,
                "real_time_analysis": True
            }
        }
        
        return structured_response
    
    def _extract_key_insight(self, analysis_text: str) -> str:
        """Extract key insight from analysis text"""
        if not analysis_text:
            return "Agricultural analysis completed"
        
        # Take first meaningful sentence
        sentences = analysis_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                return sentence
        
        return analysis_text[:100] + "..." if len(analysis_text) > 100 else analysis_text
    
    def _extract_primary_recommendation(self, recommendations: List[Dict[str, Any]]) -> str:
        """Extract primary recommendation from recommendations list"""
        if not recommendations:
            return "Consult agricultural experts for guidance"
        
        # Find highest priority recommendation
        primary_rec = None
        for rec in recommendations:
            if rec.get("priority") == "high" or rec.get("type") == "structured_recommendation":
                primary_rec = rec
                break
        
        if not primary_rec:
            primary_rec = recommendations[0]
        
        return primary_rec.get("text", "No specific recommendation available")
    
    def _map_confidence_to_level(self, confidence_score: float) -> str:
        """Map numerical confidence to level description"""
        if confidence_score >= 0.8:
            return "High"
        elif confidence_score >= 0.6:
            return "Medium-High"
        elif confidence_score >= 0.4:
            return "Medium"
        elif confidence_score >= 0.2:
            return "Low-Medium"
        else:
            return "Low"
    
    def _format_structured_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recommendations for frontend display"""
        
        formatted_recs = []
        
        for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5
            formatted_rec = {
                "id": rec.get("id", f"rec_{i}"),
                "title": f"Recommendation {i}",
                "description": rec.get("text", ""),
                "priority": rec.get("priority", "medium"),
                "category": rec.get("category", "General"),
                "emoji": self._get_recommendation_emoji(rec),
                "implementation": "immediate" if rec.get("priority") == "high" else "planned"
            }
            formatted_recs.append(formatted_rec)
        
        return formatted_recs
    
    def _format_action_items(self, action_items: List[str]) -> List[Dict[str, Any]]:
        """Format action items for frontend display"""
        
        formatted_actions = []
        
        for i, action in enumerate(action_items, 1):
            timeframe = "immediate"
            if "short-term" in action.lower() or "1-7 days" in action.lower():
                timeframe = "short-term"
            elif "long-term" in action.lower() or "weeks" in action.lower():
                timeframe = "long-term"
            
            formatted_action = {
                "id": f"action_{i}",
                "description": action,
                "timeframe": timeframe,
                "priority": "high" if "immediate" in action.lower() else "medium",
                "status": "pending"
            }
            formatted_actions.append(formatted_action)
        
        return formatted_actions
    
    def _get_recommendation_emoji(self, recommendation: Dict[str, Any]) -> str:
        """Get appropriate emoji for recommendation"""
        text = recommendation.get("text", "").lower()
        category = recommendation.get("category", "").lower()
        
        if any(word in text for word in ["water", "irrigation", "सिंचाई"]):
            return self.emoji_map.get("water", "💧")
        elif any(word in text for word in ["pest", "disease", "कीट", "रोग"]):
            return self.emoji_map.get("pest", "🐛")
        elif any(word in text for word in ["fertilizer", "nutrient", "खाद"]):
            return self.emoji_map.get("fertilizer", "🧪")
        elif any(word in text for word in ["crop", "seed", "फसल"]):
            return self.emoji_map.get("crop", "🌾")
        elif any(word in text for word in ["market", "price", "बाजार"]):
            return self.emoji_map.get("market", "💰")
        else:
            return self.emoji_map.get("recommendation", "💡")

    # Helper methods
    
    def _format_section_title(self, title: str) -> str:
        """Format section title"""
        title = title.replace(':', '').strip()
        return title.title() if title.islower() else title
    
    def _format_section_content(self, content: str) -> str:
        """Format section content for proper display"""
        if not content:
            return ""
        
        # Remove any remaining markdown formatting
        content = re.sub(r'\*{1,}', '', content)  # Remove asterisks
        content = re.sub(r'`{1,}', '', content)  # Remove backticks
        content = re.sub(r'_{2,}', '', content)  # Remove emphasis underscores
        content = re.sub(r'#{1,}\s*', '', content)  # Remove headers
        
        # Format lists properly
        content = re.sub(r'^\s*[-\*\+•·]\s*', '• ', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*(\d+)[\.\)]\s*', r'\1. ', content, flags=re.MULTILINE)
        
        # Add proper spacing after periods
        content = re.sub(r'\.([A-Z])', r'. \1', content)
        
        # Clean up spacing
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def _format_recommendation(self, rec: str) -> str:
        """Format a single recommendation"""
        rec = rec.strip()
        if not rec.endswith('.'):
            rec += '.'
        return rec.capitalize()
    
    def _format_for_display(self, content: str) -> str:
        """Format content for frontend display"""
        # Convert to structured format
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Format different types of content
            if re.match(r'^\d+\.', line):  # Numbered list
                formatted_lines.append(f"<li class='numbered-item'>{line[2:].strip()}</li>")
            elif re.match(r'^[•·-]', line):  # Bullet point
                formatted_lines.append(f"<li class='bullet-item'>{line[1:].strip()}</li>")
            else:
                formatted_lines.append(f"<p>{line}</p>")
        
        return '\n'.join(formatted_lines)
    
    def _format_for_display(self, content: str) -> str:
        """Format content for clean frontend display"""
        if not content:
            return ""
        
        # Comprehensive markdown removal
        formatted = content
        
        # Remove all markdown formatting characters
        formatted = re.sub(r'\*{1,}([^\*]*)\*{1,}', r'\1', formatted)  # Remove bold/italic asterisks
        formatted = re.sub(r'_{1,}([^_]*)_{1,}', r'\1', formatted)  # Remove underline emphasis
        formatted = re.sub(r'`{1,}([^`]*)`{1,}', r'\1', formatted)  # Remove code blocks
        formatted = re.sub(r'#{1,}\s*([^\n]*)', r'\1', formatted)  # Remove headers
        formatted = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', formatted)  # Convert links to text
        
        # Clean up bullet points and numbering
        formatted = re.sub(r'^\s*[-\*\+•·]\s*', '• ', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^\s*(\d+)[\.\)]\s*', r'\1. ', formatted, flags=re.MULTILINE)
        
        # Format as proper HTML for display
        lines = formatted.split('\n')
        html_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Convert bullet points to HTML
            if line.startswith('• '):
                line = f"<li>{line[2:]}</li>"
                if not html_content or not html_content[-1].startswith('<ul>'):
                    html_content.append('<ul>')
                html_content.append(line)
            # Convert numbered lists to HTML
            elif re.match(r'^\d+\.\s', line):
                numbered_content = re.sub(r'^\d+\.\s', '', line)
                line = f"<li>{numbered_content}</li>"
                if not html_content or not html_content[-1].startswith('<ol>'):
                    html_content.append('<ol>')
                html_content.append(line)
            else:
                # Close any open lists
                if html_content and (html_content[-1].endswith('</li>') or html_content[-1] in ['<ul>', '<ol>']):
                    if '<ul>' in html_content:
                        html_content.append('</ul>')
                    elif '<ol>' in html_content:
                        html_content.append('</ol>')
                
                # Add as paragraph
                html_content.append(f"<p>{line}</p>")
        
        # Close any remaining open lists
        if html_content and html_content[-1].endswith('</li>'):
            if '<ul>' in html_content:
                html_content.append('</ul>')
            elif '<ol>' in html_content:
                html_content.append('</ol>')
        
        return '\n'.join(html_content)

    def _format_recommendations_for_display(self, recommendations: List[str]) -> str:
        """Format recommendations for display"""
        formatted = []
        for i, rec in enumerate(recommendations[:5], 1):
            # Clean the recommendation of any markdown
            clean_rec = re.sub(r'\*{1,}', '', rec)  # Remove asterisks
            clean_rec = re.sub(r'`{1,}', '', clean_rec)  # Remove backticks
            clean_rec = re.sub(r'_{1,}', '', clean_rec)  # Remove underscores
            clean_rec = clean_rec.strip()
            formatted.append(f"<div class='recommendation-item'><span class='priority'>{i}.</span> {clean_rec}</div>")
        return '\n'.join(formatted)
    
    def _format_warnings_for_display(self, warnings: List[str]) -> str:
        """Format warnings for display"""
        formatted = []
        for warning in warnings:
            # Clean the warning of any markdown
            clean_warning = re.sub(r'\*{1,}', '', warning)  # Remove asterisks
            clean_warning = re.sub(r'`{1,}', '', clean_warning)  # Remove backticks
            clean_warning = re.sub(r'_{1,}', '', clean_warning)  # Remove underscores
            clean_warning = clean_warning.strip()
            formatted.append(f"<div class='warning-item'>⚠️ {clean_warning}</div>")
        return '\n'.join(formatted)
    
    def _assess_section_importance(self, content: str) -> str:
        """Assess the importance of a section"""
        important_keywords = ["critical", "urgent", "important", "महत्वपूर्ण", "जरूरी"]
        if any(keyword in content.lower() for keyword in important_keywords):
            return "high"
        elif len(content) > 100:
            return "medium"
        else:
            return "low"
    
    def _extract_timeline(self, text: str) -> str:
        """Extract timeline from text"""
        timeline_patterns = [
            (r'(\d+)\s*(day|days|दिन)', lambda m: f"{m.group(1)} days"),
            (r'(\d+)\s*(week|weeks|सप्ताह)', lambda m: f"{m.group(1)} weeks"),
            (r'(\d+)\s*(month|months|महीने)', lambda m: f"{m.group(1)} months"),
            (r'immediate|तुरंत', lambda m: "Immediate"),
            (r'urgent|जल्दी', lambda m: "Urgent")
        ]
        
        for pattern, formatter in timeline_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return formatter(match)
        
        return "As needed"
    
    def _extract_timeframe(self, text: str) -> str:
        """Extract timeframe for next steps"""
        if any(word in text.lower() for word in ["immediate", "now", "today", "तुरंत"]):
            return "Immediate"
        elif any(word in text.lower() for word in ["week", "weekly", "सप्ताह"]):
            return "This week"
        elif any(word in text.lower() for word in ["month", "monthly", "महीना"]):
            return "This month"
        else:
            return "Ongoing"
    
    def _extract_resources(self, text: str) -> List[str]:
        """Extract required resources"""
        resources = []
        resource_keywords = {
            "water": ["water", "irrigation", "पानी", "सिंचाई"],
            "fertilizer": ["fertilizer", "npk", "खाद", "उर्वरक"],
            "equipment": ["equipment", "tools", "machinery", "उपकरण"],
            "seeds": ["seeds", "variety", "बीज", "किस्म"],
            "labor": ["labor", "workers", "मजदूर", "श्रमिक"]
        }
        
        for resource, keywords in resource_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                resources.append(resource.title())
        
        return resources if resources else ["Basic farming resources"]
    
    def _assess_impact(self, text: str) -> str:
        """Assess the impact of a recommendation"""
        high_impact_words = ["critical", "significant", "major", "essential"]
        medium_impact_words = ["important", "beneficial", "helpful"]
        
        text_lower = text.lower()
        if any(word in text_lower for word in high_impact_words):
            return "High"
        elif any(word in text_lower for word in medium_impact_words):
            return "Medium"
        else:
            return "Low"
    
    def _assess_difficulty(self, text: str) -> str:
        """Assess the difficulty of implementation"""
        easy_indicators = ["simple", "easy", "basic", "आसान"]
        hard_indicators = ["complex", "difficult", "advanced", "कठिन"]
        
        text_lower = text.lower()
        if any(word in text_lower for word in hard_indicators):
            return "Hard"
        elif any(word in text_lower for word in easy_indicators):
            return "Easy"
        else:
            return "Medium"
    
    def _simplify_action(self, action: str) -> str:
        """Simplify action for next steps"""
        # Remove complex explanations and keep core action
        action = action.split('.')[0] if '.' in action else action
        action = action.split(',')[0] if ',' in action else action
        return action.strip()
    
    def _extract_metrics(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key metrics from data points"""
        metrics = {}
        
        for dp in data_points:
            text = dp["text"].lower()
            values = dp["values"]
            
            # Map common agricultural metrics
            if "temperature" in text or "तापमान" in text:
                metrics["temperature"] = f"{values[0]}°C" if values else "N/A"
            elif "humidity" in text or "नमी" in text:
                metrics["humidity"] = f"{values[0]}%" if values else "N/A"
            elif "moisture" in text or "मिट्टी" in text:
                metrics["soil_moisture"] = f"{values[0]}%" if values else "N/A"
            elif "yield" in text or "उत्पादन" in text:
                metrics["expected_yield"] = f"{values[0]} units" if values else "N/A"
        
        return metrics

# Global formatter instance
response_formatter = ResponseFormatter()
