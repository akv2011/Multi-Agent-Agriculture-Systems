/**
 * Gemini API Service for Agricultural Query Analysis
 * 
 * Handles communication with Google's Gemini API for intelligent
 * agricultural query processing and analysis
 */

interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

interface QueryAnalysisRequest {
  query: string;
  vegetationData?: any;
  coordinates?: {
    lat: number;
    lng: number;
  };
  context?: string;
}

interface QueryAnalysisResponse {
  analysis: string;
  recommendations: string[];
  confidence: number;
  agentType: string;
  priority: 'low' | 'medium' | 'high';
  actionItems: string[];
}

class GeminiService {
  private apiKey: string;
  private modelName: string = 'gemini-2.0-flash-exp';
  private baseUrl: string = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent';

  constructor() {
    // Get API key from environment variables first, then localStorage as fallback
    this.apiKey = import.meta.env.VITE_GEMINI_API_KEY || localStorage.getItem('gemini_api_key') || '';

    if (this.apiKey) {
      console.log(`✅ Gemini API key loaded successfully - Using model: ${this.modelName}`);
    } else {
      console.warn('⚠️ Gemini API key not found. Please set VITE_GEMINI_API_KEY environment variable or store in localStorage as "gemini_api_key"');
    }
  }

  /**
   * Set API key dynamically
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
    localStorage.setItem('gemini_api_key', apiKey);
  }

  /**
   * Create agricultural context prompt for Gemini
   */
  private createAgriculturalPrompt(request: QueryAnalysisRequest): string {
    const { query, vegetationData, coordinates, context } = request;
    
    let prompt = `You are an expert agricultural AI assistant specializing in Indian farming practices. 
    
Analyze the following farmer's query and provide comprehensive agricultural advice:

**Query:** "${query}"

**Context:**`;

    if (coordinates) {
      prompt += `\n- Location: Latitude ${coordinates.lat}, Longitude ${coordinates.lng}`;
    }

    if (vegetationData) {
      prompt += `\n- Vegetation Analysis Available: ${JSON.stringify(vegetationData, null, 2)}`;
    }

    if (context) {
      prompt += `\n- Additional Context: ${context}`;
    }

    prompt += `

**Please provide a structured response with:**

1. **Analysis**: Detailed analysis of the query and situation
2. **Recommendations**: 3-5 specific, actionable recommendations
3. **Agent Type**: Which agricultural specialist should handle this (crop_selection, pest_management, irrigation, market_timing, finance_policy, weather_advisory)
4. **Priority**: Low, Medium, or High urgency
5. **Action Items**: Immediate steps the farmer should take

**Response Format:**
Use clear headings and bullet points. Be practical and specific to Indian agricultural conditions. Consider seasonal factors, local practices, and cost-effectiveness.

**Language**: Respond in English, but acknowledge if the query was in Hindi or mixed language.`;

    return prompt;
  }

  /**
   * Enhance AI response using Gemini API
   */
  async enhanceAIResponse(originalQuery: string, aiResponse: string, vegetationData?: any, coordinates?: any): Promise<string> {
    if (!this.apiKey) {
      throw new Error('Gemini API key is required. Please set it using setApiKey() method.');
    }

    try {
      const enhancementPrompt = this.createResponseEnhancementPrompt(originalQuery, aiResponse, vegetationData, coordinates);

      const response = await fetch(`${this.baseUrl}?key=${this.apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: enhancementPrompt
            }]
          }],
          generationConfig: {
            temperature: 0.8,
            topK: 64,
            topP: 0.95,
            maxOutputTokens: 8192,
          },
          safetySettings: [
            {
              category: "HARM_CATEGORY_HARASSMENT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_HATE_SPEECH",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            }
          ]
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Gemini API error: ${response.status} - ${errorData.error?.message || 'Unknown error'}`);
      }

      const data: GeminiResponse = await response.json();

      if (!data.candidates || data.candidates.length === 0) {
        throw new Error('No response generated from Gemini API');
      }

      return data.candidates[0].content.parts[0].text;

    } catch (error) {
      console.error('Gemini API request failed:', error);
      throw error;
    }
  }

  /**
   * Create enhancement prompt for AI response
   */
  private createResponseEnhancementPrompt(originalQuery: string, aiResponse: string, vegetationData?: any, coordinates?: any): string {
    let prompt = `You are an expert agricultural consultant specializing in Indian farming practices.

I have received an AI-generated response to a farmer's query, but I need you to enhance it to make it more comprehensive, practical, and farmer-friendly.

**Original Farmer Query:** "${originalQuery}"

**AI Response to Enhance:**
${aiResponse}

**Additional Context:**`;

    if (coordinates) {
      prompt += `\n- Location: Latitude ${coordinates.lat}, Longitude ${coordinates.lng}`;
    }

    if (vegetationData) {
      prompt += `\n- Vegetation Analysis: ${JSON.stringify(vegetationData, null, 2)}`;
    }

    prompt += `

**Please enhance this response by:**

1. **Making it more descriptive and comprehensive** - Add detailed explanations
2. **Adding practical implementation steps** - How exactly to do each recommendation
3. **Including cost estimates** - Approximate costs in Indian Rupees where relevant
4. **Adding timing considerations** - When to implement each suggestion
5. **Including preventive measures** - How to avoid similar issues in future
6. **Adding local context** - Considerations specific to Indian farming conditions
7. **Making it farmer-friendly** - Use simple, clear language that farmers can understand

**Response Format:**
- Use clear headings and bullet points
- Include specific quantities, measurements, and timeframes
- Add cost estimates in INR where applicable
- Mention local suppliers or resources when relevant
- Include seasonal considerations
- Add follow-up recommendations

**Language:** Respond in clear, simple English that can be easily understood by Indian farmers. Avoid technical jargon unless necessary, and explain any technical terms used.

**Focus on:** Practical, actionable, cost-effective solutions that are realistic for Indian farming conditions.`;

    return prompt;
  }

  /**
   * Analyze agricultural query using Gemini API
   */
  async analyzeQuery(request: QueryAnalysisRequest): Promise<QueryAnalysisResponse> {
    if (!this.apiKey) {
      throw new Error('Gemini API key is required. Please set it using setApiKey() method.');
    }

    try {
      const prompt = this.createAgriculturalPrompt(request);
      
      const response = await fetch(`${this.baseUrl}?key=${this.apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: prompt
            }]
          }],
          generationConfig: {
            temperature: 0.8,
            topK: 64,
            topP: 0.95,
            maxOutputTokens: 8192,
          },
          safetySettings: [
            {
              category: "HARM_CATEGORY_HARASSMENT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_HATE_SPEECH", 
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
              category: "HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold: "BLOCK_MEDIUM_AND_ABOVE"
            }
          ]
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Gemini API error: ${response.status} - ${errorData.error?.message || 'Unknown error'}`);
      }

      const data: GeminiResponse = await response.json();
      
      if (!data.candidates || data.candidates.length === 0) {
        throw new Error('No response generated from Gemini API');
      }

      const generatedText = data.candidates[0].content.parts[0].text;
      
      // Parse the structured response
      return this.parseGeminiResponse(generatedText);
      
    } catch (error) {
      console.error('Gemini API request failed:', error);
      throw error;
    }
  }

  /**
   * Parse Gemini's structured response into our format
   */
  private parseGeminiResponse(text: string): QueryAnalysisResponse {
    // Extract sections using regex patterns
    const analysisMatch = text.match(/\*\*Analysis\*\*:?\s*([\s\S]*?)(?=\*\*Recommendations\*\*|$)/i);
    const recommendationsMatch = text.match(/\*\*Recommendations\*\*:?\s*([\s\S]*?)(?=\*\*Agent Type\*\*|$)/i);
    const agentTypeMatch = text.match(/\*\*Agent Type\*\*:?\s*([\s\S]*?)(?=\*\*Priority\*\*|$)/i);
    const priorityMatch = text.match(/\*\*Priority\*\*:?\s*([\s\S]*?)(?=\*\*Action Items\*\*|$)/i);
    const actionItemsMatch = text.match(/\*\*Action Items\*\*:?\s*([\s\S]*?)$/i);

    // Extract and clean content
    const analysis = analysisMatch ? analysisMatch[1].trim() : text;
    
    const recommendations = recommendationsMatch 
      ? recommendationsMatch[1].split(/\n/).filter(line => line.trim()).map(line => line.replace(/^[-*•]\s*/, '').trim())
      : [];

    const agentType = agentTypeMatch 
      ? agentTypeMatch[1].trim().toLowerCase().replace(/[^a-z_]/g, '') 
      : 'general_advisory';

    const priorityText = priorityMatch ? priorityMatch[1].trim().toLowerCase() : 'medium';
    const priority = priorityText.includes('high') ? 'high' : 
                    priorityText.includes('low') ? 'low' : 'medium';

    const actionItems = actionItemsMatch 
      ? actionItemsMatch[1].split(/\n/).filter(line => line.trim()).map(line => line.replace(/^[-*•]\s*/, '').trim())
      : [];

    return {
      analysis,
      recommendations: recommendations.slice(0, 5), // Limit to 5 recommendations
      confidence: 0.85, // Default confidence score
      agentType,
      priority: priority as 'low' | 'medium' | 'high',
      actionItems: actionItems.slice(0, 5) // Limit to 5 action items
    };
  }

  /**
   * Test API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      const testRequest: QueryAnalysisRequest = {
        query: "Test connection to agricultural AI assistant"
      };
      
      await this.analyzeQuery(testRequest);
      return true;
    } catch (error) {
      console.error('Gemini API connection test failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const geminiService = new GeminiService();
export default geminiService;
