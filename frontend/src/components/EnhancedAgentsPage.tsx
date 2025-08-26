import React, { useState } from 'react';
import { 
  Droplets, 
  TrendingUp,
  Camera,
  Database,
  Activity,
  ArrowLeft,
  Zap,
  Loader2,
  Bot,
  Leaf,
  Shield,
  BarChart3,
  Brain,
  Sparkles,
  CheckCircle,
  Clock,
  Users,
  Target,
  Microscope
} from 'lucide-react';

// Added strong typing for results
type AgentId = 'disease_identification' | 'crop_recommendation' | 'irrigation_scheduling' | 'market_analysis' | 'pest_management' | 'finance_policy' | 'harvest_planning';

interface RecommendedCropResult {
  name: string;
  nameML: string;
  nameHI: string;
  suitability: number;
  expectedYield: string;
}

interface IrrigationScheduleItem {
  day: string;
  time: string;
  duration: string;
  amount: string;
}

interface DiseaseResult {
  type: 'disease_identification';
  disease: string;
  diseaseML: string;
  diseaseHI: string;
  confidence: number;
  severity: string;
  treatment: string;
  treatmentML: string;
  treatmentHI: string;
}

interface CropRecommendationResult {
  type: 'crop_recommendation';
  recommendedCrops: RecommendedCropResult[];
  reason: string;
  reasonML: string;
  reasonHI: string;
}

interface IrrigationResult {
  type: 'irrigation_scheduling';
  schedule: IrrigationScheduleItem[];
  weeklyTotal: string;
  efficiency: string;
  notes: string;
  notesML: string;
  notesHI: string;
}

interface MarketResult {
  type: 'market_analysis';
  marketPrice: string;
  priceChange: string;
  recommendation: string;
  demandForecast: string;
}

interface PestManagementResult {
  type: 'pest_management';
  riskLevel: string;
  pestType: string;
  treatment: string;
  preventiveMeasures: string[];
}

interface FinancePolicyResult {
  type: 'finance_policy';
  loanEligibility: string;
  interestRate: string;
  subsidies: string[];
  riskAssessment: string;
}

interface HarvestPlanningResult {
  type: 'harvest_planning';
  optimalDate: string;
  qualityPrediction: string;
  marketRecommendation: string;
  storageAdvice: string;
}

type AgentResults = DiseaseResult | CropRecommendationResult | IrrigationResult | MarketResult | PestManagementResult | FinancePolicyResult | HarvestPlanningResult | null;

// Type guards for safe narrowing
const isDiseaseResult = (r: AgentResults): r is DiseaseResult => !!r && r.type === 'disease_identification';
const isCropRecommendationResult = (r: AgentResults): r is CropRecommendationResult => !!r && r.type === 'crop_recommendation';
const isIrrigationResult = (r: AgentResults): r is IrrigationResult => !!r && r.type === 'irrigation_scheduling';
const isMarketResult = (r: AgentResults): r is MarketResult => !!r && r.type === 'market_analysis';
const isPestManagementResult = (r: AgentResults): r is PestManagementResult => !!r && r.type === 'pest_management';
const isFinancePolicyResult = (r: AgentResults): r is FinancePolicyResult => !!r && r.type === 'finance_policy';
const isHarvestPlanningResult = (r: AgentResults): r is HarvestPlanningResult => !!r && r.type === 'harvest_planning';

interface AgentConfig {
  id: AgentId; // tightened type
  name: string;
  nameML: string;
  nameHI: string;
  description: string;
  descriptionML: string;
  descriptionHI: string;
  icon: React.ReactNode;
  color: string;
  category: string;
  modelType: 'image' | 'data' | 'hybrid';
  parameters: Array<{
    id: string;
    name: string;
    nameML: string;
    nameHI: string;
    type: string;
    required: boolean;
    placeholder?: string;
    placeholderML?: string;
    placeholderHI?: string;
    options?: string[];
    min?: number;
    max?: number;
    unit?: string;
  }>;
}

const EnhancedAgentsPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<AgentId | null>(null);
  const [formData, setFormData] = useState<Record<string, string | number | undefined>>({});
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<AgentResults>(null);
  const [language, setLanguage] = useState<'english' | 'tamil' | 'hindi'>('english');

  const agentConfigs: AgentConfig[] = [
    {
      id: 'disease_identification',
      name: 'Plant Disease Detection',
      nameML: 'தாவர நோய் கண்டறிதல்',
      nameHI: 'पौधे की बीमारी की पहचान',
      description: 'Advanced AI-powered plant disease identification with precise treatment recommendations',
      descriptionML: 'துல்லியமான சிகிச்சை பரிந்துரைகளுடன் மேம்பட்ட AI-சக்தி தாவர நோய் கண்டறிதல்',
      descriptionHI: 'सटीक उपचार सिफारिशों के साथ उन्नत AI-संचालित पौधे की बीमारी की पहचान',
      icon: <div className="relative">
        <Microscope className="w-8 h-8" />
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-pulse"></div>
        <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-orange-400 rounded-full animate-ping"></div>
      </div>,
      color: 'bg-gradient-to-br from-red-500 via-pink-500 to-rose-600',
      category: '🔬 Health Analysis',
      modelType: 'image',
      parameters: [
        {
          id: 'plant_image',
          name: 'Plant Image',
          nameML: 'தாவர படம்',
          nameHI: 'पौधे की छवि',
          type: 'file',
          required: true,
          placeholder: 'Upload a clear image of the affected plant',
          placeholderML: 'பாதிக்கப்பட்ட தாவரத்தின் தெளிவான படத்தை பதிவேற்றவும்',
          placeholderHI: 'प्रभावित पौधे की स्पष्ट छवि अपलोड करें'
        },
        {
          id: 'plant_type',
          name: 'Plant Type',
          nameML: 'தாவர வகை',
          nameHI: 'पौधे का प्रकार',
          type: 'select',
          required: true,
          placeholder: 'Select plant type',
          placeholderML: 'தாவர வகையை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'पौधे का प्रकार चुनें',
          options: ['Rice', 'Wheat', 'Tomato', 'Potato', 'Corn', 'Cotton', 'Sugarcane']
        }
      ]
    },
    {
      id: 'crop_recommendation',
      name: 'Smart Crop Recommendation',
      nameML: 'ஸ்மார்ட் பயிர் பரிந்துரை',
      nameHI: 'स्मार्ट फसल सिफारिश',
      description: 'AI-driven optimal crop selection based on soil composition and environmental factors',
      descriptionML: 'மண் கலவை மற்றும் சுற்றுச்சூழல் காரணிகளின் அடிப்படையில் AI-உந்துதல் உகந்த பயிர் தேர்வு',
      descriptionHI: 'मिट्टी की संरचना और पर्यावरणीय कारकों के आधार पर AI-संचालित इष्टतम फसल चयन',
      icon: <div className="relative">
        <Leaf className="w-8 h-8" />
        <Sparkles className="w-4 h-4 absolute -top-1 -right-1 text-yellow-300 animate-bounce" />
        <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
      </div>,
      color: 'bg-gradient-to-br from-emerald-500 via-green-500 to-teal-600',
      category: '🌱 Crop Planning',
      modelType: 'data',
      parameters: [
        {
          id: 'nitrogen',
          name: 'Nitrogen Content',
          nameML: 'நைட்ரஜன் உள்ளடக்கம்',
          nameHI: 'नाइट्रोजन सामग्री',
          type: 'number',
          required: true,
          placeholder: 'Enter nitrogen level (mg/kg)',
          placeholderML: 'நைட்ரஜன் அளவை உள்ளிடவும் (mg/kg)',
          placeholderHI: 'नाइट्रोजन स्तर दर्ज करें (mg/kg)',
          min: 0,
          max: 300,
          unit: 'mg/kg'
        },
        {
          id: 'phosphorus',
          name: 'Phosphorus Content',
          nameML: 'பாஸ்பரஸ் உள்ளடக்கம்',
          nameHI: 'फास्फोरस सामग्री',
          type: 'number',
          required: true,
          placeholder: 'Enter phosphorus level (mg/kg)',
          placeholderML: 'பாஸ்பரஸ் அளவை உள்ளிடவும் (mg/kg)',
          placeholderHI: 'फास्फोरस स्तर दर्ज करें (mg/kg)',
          min: 0,
          max: 200,
          unit: 'mg/kg'
        },
        {
          id: 'potassium',
          name: 'Potassium Content',
          nameML: 'பொட்டாசியம் உள்ளடக்கம்',
          nameHI: 'पोटेशियम सामग्री',
          type: 'number',
          required: true,
          placeholder: 'Enter potassium level (mg/kg)',
          placeholderML: 'பொட்டாசியம் அளவை உள்ளிடவும் (mg/kg)',
          placeholderHI: 'पोटेशियम स्तर दर्ज करें (mg/kg)',
          min: 0,
          max: 400,
          unit: 'mg/kg'
        },
        {
          id: 'ph',
          name: 'Soil pH',
          nameML: 'மண் pH',
          nameHI: 'मिट्टी pH',
          type: 'range',
          required: true,
          min: 3.5,
          max: 9.5,
          unit: 'pH'
        },
        {
          id: 'rainfall',
          name: 'Annual Rainfall',
          nameML: 'வருடாந்த மழைப்பொழிவு',
          nameHI: 'वार्षिक वर्षा',
          type: 'number',
          required: true,
          placeholder: 'Enter annual rainfall (mm)',
          placeholderML: 'வருடாந்த மழைப்பொழிவை உள்ளிடவும் (mm)',
          placeholderHI: 'वार्षिक वर्षा दर्ज करें (mm)',
          min: 0,
          max: 3000,
          unit: 'mm'
        },
        {
          id: 'temperature',
          name: 'Average Temperature',
          nameML: 'சராசரி வெப்பநிலை',
          nameHI: 'औसत तापमान',
          type: 'number',
          required: true,
          placeholder: 'Enter average temperature (°C)',
          placeholderML: 'சராசரி வெப்பநிலையை உள்ளிடவும் (°C)',
          placeholderHI: 'औसत तापमान दर्ज करें (°C)',
          min: -10,
          max: 50,
          unit: '°C'
        }
      ]
    },
    {
      id: 'irrigation_scheduling',
      name: 'Intelligent Irrigation',
      nameML: 'அறிவுள்ள நீர்ப்பாசனம்',
      nameHI: 'बुद्धिमान सिंचाई',
      description: 'Water-efficient irrigation scheduling with weather prediction and soil analysis',
      descriptionML: 'வானிலை முன்னறிவிப்பு மற்றும் மண் பகுப்பாய்வுடன் நீர்-திறமையான நீர்ப்பாசன திட்டமிடல்',
      descriptionHI: 'मौसम पूर्वानुमान और मिट्टी विश्लेषण के साथ जल-कुशल सिंचाई निर्धारण',
      icon: <div className="relative">
        <Droplets className="w-8 h-8" />
        <Brain className="w-4 h-4 absolute -bottom-1 -right-1 text-blue-300 animate-pulse" />
        <div className="absolute -top-1 -left-1 w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
      </div>,
      color: 'bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-600',
      category: '💧 Water Management',
      modelType: 'hybrid',
      parameters: [
        {
          id: 'crop_type',
          name: 'Crop Type',
          nameML: 'பயிர் வகை',
          nameHI: 'फसल का प्रकार',
          type: 'select',
          required: true,
          placeholder: 'Select crop type',
          placeholderML: 'பயிர் வகையை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'फसल का प्रकार चुनें',
          options: ['Rice', 'Wheat', 'Corn', 'Tomato', 'Cotton', 'Sugarcane']
        },
        {
          id: 'field_size',
          name: 'Field Size',
          nameML: 'வயல் அளவு',
          nameHI: 'खेत का आकार',
          type: 'number',
          required: true,
          placeholder: 'Enter field size (hectares)',
          placeholderML: 'வயல் அளவை உள்ளிடவும் (ஹெக்டேர்)',
          placeholderHI: 'खेत का आकार दर्ज करें (हेक्टेयर)',
          min: 0.1,
          max: 1000,
          unit: 'hectares'
        },
        {
          id: 'soil_moisture',
          name: 'Current Soil Moisture',
          nameML: 'தற்போதைய மண் ஈரப்பதம்',
          nameHI: 'वर्तमान मिट्टी की नमी',
          type: 'range',
          required: true,
          min: 0,
          max: 100,
          unit: '%'
        },
        {
          id: 'weather_forecast',
          name: 'Rain Probability (7 days)',
          nameML: 'மழை நிகழ்தகவு (7 நாட்கள்)',
          nameHI: 'बारिश की संभावना (7 दिन)',
          type: 'range',
          required: true,
          min: 0,
          max: 100,
          unit: '%'
        }
      ]
    },
    {
      id: 'market_analysis',
      name: 'Market Intelligence',
      nameML: 'சந்தை புத்திசாலித்தனம்',
      nameHI: 'बाजार बुद्धिमत्ता',
      description: 'Real-time market analysis with price predictions and demand forecasting',
      descriptionML: 'விலை முன்னறிவிப்புகள் மற்றும் தேவை முன்னறிவிப்புடன் நிகழ்நேர சந்தை பகுப்பாய்வு',
      descriptionHI: 'मूल्य भविष्यवाणियों और मांग पूर्वानुमान के साथ वास्तविक समय बाजार विश्लेषण',
      icon: <div className="relative">
        <BarChart3 className="w-8 h-8" />
        <Target className="w-4 h-4 absolute -top-1 -right-1 text-purple-300 animate-bounce" />
        <TrendingUp className="w-3 h-3 absolute -bottom-1 -left-1 text-yellow-400 animate-ping" />
      </div>,
      color: 'bg-gradient-to-br from-purple-500 via-violet-500 to-indigo-600',
      category: '📈 Market Analytics',
      modelType: 'data',
      parameters: [
        {
          id: 'crop_name',
          name: 'Crop Name',
          nameML: 'பயிர் பெயர்',
          nameHI: 'फसल का नाम',
          type: 'select',
          required: true,
          placeholder: 'Select crop for analysis',
          placeholderML: 'பகுப்பாய்வுக்கு பயிரை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'विश्लेषण के लिए फसल चुनें',
          options: ['Rice', 'Wheat', 'Tomato', 'Onion', 'Potato', 'Cotton', 'Sugarcane']
        },
        {
          id: 'quantity',
          name: 'Expected Quantity',
          nameML: 'எதிர்பார்க்கப்படும் அளவு',
          nameHI: 'अपेक्षित मात्रा',
          type: 'number',
          required: true,
          placeholder: 'Enter quantity (tonnes)',
          placeholderML: 'அளவை உள்ளிடவும் (டன்கள்)',
          placeholderHI: 'मात्रा दर्ज करें (टन)',
          min: 0.1,
          max: 10000,
          unit: 'tonnes'
        },
        {
          id: 'location',
          name: 'Market Location',
          nameML: 'சந்தை இடம்',
          nameHI: 'बाजार स्थान',
          type: 'select',
          required: true,
          placeholder: 'Select market location',
          placeholderML: 'சந்தை இடத்தை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'बाजार स्थान चुनें',
          options: ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem', 'Tirunelveli']
        }
      ]
    },
    {
      id: 'pest_management',
      name: 'Pest Management',
      nameML: 'பூச்சி மேலாண்மை',
      nameHI: 'कीट प्रबंधन',
      description: 'Weather-based pest outbreak prediction with environmental risk assessment and treatment recommendations',
      descriptionML: 'சுற்றுச்சூழல் அபாய மதிப்பீடு மற்றும் சிகிச்சை பரிந்துரைகளுடன் வானிலை அடிப்படையிலான பூச்சி வெடிப்பு முன்னறிவிப்பு',
      descriptionHI: 'पर्यावरणीय जोखिम आकलन और उपचार सिफारिशों के साथ मौसम-आधारित कीट प्रकोप भविष्यवाणी',
      icon: <div className="relative">
        <Shield className="w-8 h-8" />
        <Activity className="w-4 h-4 absolute -top-1 -right-1 text-orange-300 animate-pulse" />
        <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-red-400 rounded-full animate-bounce"></div>
      </div>,
      color: 'bg-gradient-to-br from-orange-500 via-amber-500 to-yellow-600',
      category: '🛡️ Pest Control',
      modelType: 'hybrid',
      parameters: [
        {
          id: 'crop_type',
          name: 'Crop Type',
          nameML: 'பயிர் வகை',
          nameHI: 'फसल का प्रकार',
          type: 'select',
          required: true,
          placeholder: 'Select crop type',
          placeholderML: 'பயிர் வகையை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'फसल का प्रकार चुनें',
          options: ['Rice', 'Wheat', 'Cotton', 'Tomato', 'Corn', 'Sugarcane', 'Potato']
        },
        {
          id: 'temperature',
          name: 'Temperature',
          nameML: 'வெப்பநிலை',
          nameHI: 'तापमान',
          type: 'number',
          required: true,
          placeholder: 'Enter temperature (°C)',
          placeholderML: 'வெப்பநிலையை உள்ளிடவும் (°C)',
          placeholderHI: 'तापमान दर्ज करें (°C)',
          min: 0,
          max: 50,
          unit: '°C'
        },
        {
          id: 'humidity',
          name: 'Humidity',
          nameML: 'ஈரப்பதம்',
          nameHI: 'आर्द्रता',
          type: 'range',
          required: true,
          min: 0,
          max: 100,
          unit: '%'
        },
        {
          id: 'season',
          name: 'Season',
          nameML: 'பருவம்',
          nameHI: 'मौसम',
          type: 'select',
          required: true,
          placeholder: 'Select season',
          placeholderML: 'பருவத்தை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'मौसम चुनें',
          options: ['Kharif', 'Rabi', 'Zaid', 'Summer', 'Monsoon']
        }
      ]
    },
    {
      id: 'finance_policy',
      name: 'Finance & Policy',
      nameML: 'நிதி மற்றும் கொள்கை',
      nameHI: 'वित्त और नीति',
      description: 'Environmental risk assessment with weather-adjusted loans, subsidies, and insurance guidance',
      descriptionML: 'வானிலை-சரிசெய்யப்பட்ட கடன்கள், மானியங்கள் மற்றும் காப்பீட்டு வழிகாட்டுதலுடன் சுற்றுச்சூழல் அபாய மதிப்பீடு',
      descriptionHI: 'मौसम-समायोजित ऋण, सब्सिडी और बीमा मार्गदर्शन के साथ पर्यावरणीय जोखिम आकलन',
      icon: <div className="relative">
        <Database className="w-8 h-8" />
        <CheckCircle className="w-4 h-4 absolute -top-1 -right-1 text-green-300 animate-pulse" />
        <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
      </div>,
      color: 'bg-gradient-to-br from-indigo-500 via-blue-500 to-cyan-600',
      category: '💰 Financial Services',
      modelType: 'data',
      parameters: [
        {
          id: 'farm_size',
          name: 'Farm Size',
          nameML: 'பண்ணை அளவு',
          nameHI: 'खेत का आकार',
          type: 'number',
          required: true,
          placeholder: 'Enter farm size (acres)',
          placeholderML: 'பண்ணை அளவை உள்ளிடவும் (ஏக்கர்)',
          placeholderHI: 'खेत का आकार दर्ज करें (एकड़)',
          min: 0.1,
          max: 1000,
          unit: 'acres'
        },
        {
          id: 'annual_income',
          name: 'Annual Income',
          nameML: 'வருடாந்த வருமானம்',
          nameHI: 'वार्षिक आय',
          type: 'number',
          required: true,
          placeholder: 'Enter annual income (₹)',
          placeholderML: 'வருடாந்த வருமானத்தை உள்ளிடவும் (₹)',
          placeholderHI: 'वार्षिक आय दर्ज करें (₹)',
          min: 10000,
          max: 10000000,
          unit: '₹'
        },
        {
          id: 'loan_amount',
          name: 'Loan Amount Required',
          nameML: 'தேவையான கடன் தொகை',
          nameHI: 'आवश्यक ऋण राशि',
          type: 'number',
          required: true,
          placeholder: 'Enter loan amount (₹)',
          placeholderML: 'கடன் தொகையை உள்ளிடவும் (₹)',
          placeholderHI: 'ऋण राशि दर्ज करें (₹)',
          min: 10000,
          max: 5000000,
          unit: '₹'
        },
        {
          id: 'credit_score',
          name: 'Credit Score',
          nameML: 'கடன் மதிப்பெண்',
          nameHI: 'क्रेडिट स्कोर',
          type: 'range',
          required: true,
          min: 300,
          max: 900,
          unit: ''
        }
      ]
    },
    {
      id: 'harvest_planning',
      name: 'Harvest Planning',
      nameML: 'அறுவடை திட்டமிடல்',
      nameHI: 'फसल कटाई योजना',
      description: 'Crop maturity monitoring with harvest window optimization and quality forecasting',
      descriptionML: 'அறுவடை சாளர உகப்பாக்கம் மற்றும் தர முன்னறிவிப்புடன் பயிர் முதிர்ச்சி கண்காணிப்பு',
      descriptionHI: 'फसल कटाई विंडो अनुकूलन और गुणवत्ता पूर्वानुमान के साथ फसल परिपक्वता निगरानी',
      icon: <div className="relative">
        <Clock className="w-8 h-8" />
        <Bot className="w-4 h-4 absolute -top-1 -right-1 text-amber-300 animate-pulse" />
        <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
      </div>,
      color: 'bg-gradient-to-br from-amber-500 via-yellow-500 to-orange-600',
      category: '⏰ Harvest Timing',
      modelType: 'hybrid',
      parameters: [
        {
          id: 'crop_variety',
          name: 'Crop Variety',
          nameML: 'பயிர் வகை',
          nameHI: 'फसल की किस्म',
          type: 'select',
          required: true,
          placeholder: 'Select crop variety',
          placeholderML: 'பயிர் வகையை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'फसल की किस्म चुनें',
          options: ['Basmati Rice', 'IR-64 Rice', 'Wheat HD-2967', 'Cotton Bt', 'Sugarcane Co-86032']
        },
        {
          id: 'planting_date',
          name: 'Planting Date',
          nameML: 'நடவு தேதி',
          nameHI: 'रोपण तिथि',
          type: 'date',
          required: true,
          placeholder: 'Select planting date',
          placeholderML: 'நடவு தேதியை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'रोपण तिथि चुनें'
        },
        {
          id: 'crop_maturity',
          name: 'Current Maturity (%)',
          nameML: 'தற்போதைய முதிர்ச்சி (%)',
          nameHI: 'वर्तमान परिपक्वता (%)',
          type: 'range',
          required: true,
          min: 0,
          max: 100,
          unit: '%'
        },
        {
          id: 'weather_conditions',
          name: 'Weather Conditions',
          nameML: 'வானிலை நிலைமைகள்',
          nameHI: 'मौसम की स्थिति',
          type: 'select',
          required: true,
          placeholder: 'Select weather conditions',
          placeholderML: 'வானிலை நிலைமைகளை தேர்ந்தெடுக்கவும்',
          placeholderHI: 'मौसम की स्थिति चुनें',
          options: ['Clear Sky', 'Partly Cloudy', 'Cloudy', 'Light Rain Expected', 'Heavy Rain Expected']
        }
      ]
    }
  ];

  const selectedAgentConfig = agentConfigs.find(agent => agent.id === selectedAgent);

  const handleParameterChange = (paramId: string, value: string | number | undefined) => {
    setFormData(prev => ({
      ...prev,
      [paramId]: value
    }));
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const runAgent = async () => {
    setIsLoading(true);
    setResults(null);

    try {
      // Simulate API call with realistic delay
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Mock results based on agent type
      let mockResults;
      
      if (selectedAgent === 'disease_identification') {
        mockResults = {
          type: 'disease_identification',
          disease: 'Late Blight',
          diseaseML: 'தாமத கருகல்',
          diseaseHI: 'देर से झुलसा रोग',
          confidence: 0.87,
          severity: 'Moderate',
          treatment: 'Apply copper-based fungicide. Remove affected leaves. Ensure good air circulation.',
          treatmentML: 'தாமிர அடிப்படையிலான பூஞ்சைக் கொல்லியை பயன்படுத்தவும். பாதிக்கப்பட்ட இலைகளை அகற்றவும். நல்ல காற்று சுழற்சியை உறுதி செய்யவும்।',
          treatmentHI: 'कॉपर-आधारित फंगिसाइड लगाएं। प्रभावित पत्तियों को हटाएं। अच्छा हवा संचार सुनिश्चित करें।'
        } as DiseaseResult;
      } else if (selectedAgent === 'crop_recommendation') {
        mockResults = {
          type: 'crop_recommendation',
          recommendedCrops: [
            { name: 'Rice', nameML: 'அரிசி', nameHI: 'चावल', suitability: 0.92, expectedYield: '4.5 tonnes/hectare' },
            { name: 'Sugarcane', nameML: 'கரும்பு', nameHI: 'गन्ना', suitability: 0.85, expectedYield: '85 tonnes/hectare' },
            { name: 'Cotton', nameML: 'பருத்தி', nameHI: 'कपास', suitability: 0.78, expectedYield: '2.8 tonnes/hectare' }
          ],
          reason: 'Based on soil nutrient levels and climate conditions, rice shows highest compatibility.',
          reasonML: 'மண் ஊட்டச்சத்து நிலைகள் மற்றும் காலநிலை நிலைமைகளின் அடிப்படையில், அரிசி அதிக இணக்கத்தை காட்டுகிறது।',
          reasonHI: 'मिट्टी के पोषक तत्व स्तर और जलवायु परिस्थितियों के आधार पर, चावल सबसे अधिक संगतता दिखाता है।'
        } as CropRecommendationResult;
      } else if (selectedAgent === 'irrigation_scheduling') {
        mockResults = {
          type: 'irrigation_scheduling',
          schedule: [
            { day: 'Monday', time: '6:00 AM', duration: '45 min', amount: '2.5L/m²' },
            { day: 'Wednesday', time: '6:00 AM', duration: '45 min', amount: '2.5L/m²' },
            { day: 'Friday', time: '6:00 AM', duration: '30 min', amount: '1.8L/m²' }
          ],
          weeklyTotal: '6.8L/m²',
          efficiency: '92%',
          notes: 'Optimal schedule considering current soil moisture and weather forecast.',
          notesML: 'தற்போதைய மண் ஈரப்பதம் மற்றும் வானிலை முன்னறிவிப்பைக் கருத்தில் கொண்டு உகந்த அட்டவணை।',
          notesHI: 'वर्तमान मिट्टी की नमी और मौसम पूर्वानुमान को ध्यान में रखते हुए इष्टतम कार्यक्रम।'
        } as IrrigationResult;
      } else if (selectedAgent === 'market_analysis') {
        mockResults = {
          type: 'market_analysis',
          marketPrice: '₹2,850/tonne',
          priceChange: '+5.2%',
          recommendation: 'Favorable time to sell',
          demandForecast: 'High demand expected next week'
        } as MarketResult;
      } else if (selectedAgent === 'pest_management') {
        mockResults = {
          type: 'pest_management',
          riskLevel: 'Medium',
          pestType: 'Brown Plant Hopper',
          treatment: 'Apply neem-based insecticide during evening hours',
          preventiveMeasures: [
            'Maintain proper field hygiene',
            'Use resistant crop varieties',
            'Monitor regularly for early detection',
            'Ensure balanced fertilization'
          ]
        } as PestManagementResult;
      } else if (selectedAgent === 'finance_policy') {
        mockResults = {
          type: 'finance_policy',
          loanEligibility: 'Approved',
          interestRate: '7.2% p.a.',
          riskAssessment: 'Low Risk',
          subsidies: [
            'PM-KISAN: ₹6,000/year',
            'Crop Insurance: 50% premium subsidy',
            'Equipment Subsidy: Up to ₹50,000'
          ]
        } as FinancePolicyResult;
      } else if (selectedAgent === 'harvest_planning') {
        mockResults = {
          type: 'harvest_planning',
          optimalDate: 'March 15-20, 2025',
          qualityPrediction: 'Premium Grade',
          marketRecommendation: 'Wait for 2 weeks for better prices',
          storageAdvice: 'Use proper ventilation and moisture control'
        } as HarvestPlanningResult;
      } else {
        mockResults = {
          type: 'market_analysis',
          marketPrice: '₹2,850/tonne',
          priceChange: '+5.2%',
          recommendation: 'Favorable time to sell',
          demandForecast: 'High demand expected next week'
        } as MarketResult;
      }

      setResults(mockResults);
    } catch (error) {
      console.error('Error running agent:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({});
    setUploadedImage(null);
    setResults(null);
  };

  if (selectedAgent && selectedAgentConfig) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Header */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={() => setSelectedAgent(null)}
                className="flex items-center text-gray-600 hover:text-gray-800 transition-colors duration-200 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                <span className="font-medium">
                  {language === 'tamil' ? 'பின்செல்' : language === 'hindi' ? 'एजेंटों पर वापस जाएं' : 'Back to Agents'}
                </span>
              </button>
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium text-gray-700">
                  {language === 'tamil' ? 'மொழி:' : language === 'hindi' ? 'भाषा:' : 'Language:'}
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as 'english' | 'tamil' | 'hindi')}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm"
                >
                  <option value="english">English</option>
                  <option value="tamil">தமிழ்</option>
                  <option value="hindi">हिंदी</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className={`w-16 h-16 ${selectedAgentConfig.color} rounded-2xl flex items-center justify-center text-white text-3xl shadow-lg`}>
                {selectedAgentConfig.icon}
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {language === 'tamil' ? selectedAgentConfig.nameML : language === 'hindi' ? selectedAgentConfig.nameHI : selectedAgentConfig.name}
                </h1>
                <p className="text-gray-600 text-lg leading-relaxed">
                  {language === 'tamil' ? selectedAgentConfig.descriptionML : language === 'hindi' ? selectedAgentConfig.descriptionHI : selectedAgentConfig.description}
                </p>
                <div className="mt-3 flex items-center space-x-4">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                    {selectedAgentConfig.category}
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    {language === 'tamil' ? 'செயலில்' : language === 'hindi' ? 'सक्रिय' : 'Active'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Input Form */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
                <h2 className="text-xl font-bold text-white flex items-center">
                  <Database className="w-6 h-6 mr-3" />
                  {language === 'tamil' ? 'உள்ளீடு அளவுருக்கள்' : language === 'hindi' ? 'इनपुट पैरामीटर' : 'Input Parameters'}
                </h2>
                <p className="text-blue-100 mt-2">
                  {language === 'tamil' ? 'தேவையான தகவல்களை நிரப்பவும்' : language === 'hindi' ? 'आवश्यक जानकारी भरें' : 'Fill in the required information'}
                </p>
              </div>

              <div className="p-6 space-y-6 max-h-96 overflow-y-auto">
                {selectedAgentConfig.parameters.map((param) => (
                  <div key={param.id} className="space-y-3">
                    <label className="block text-sm font-semibold text-gray-800">
                      {language === 'tamil' ? param.nameML : language === 'hindi' ? param.nameHI : param.name}
                      {param.required && <span className="text-red-500 ml-1">*</span>}
                      {param.unit && <span className="text-gray-500 ml-2 font-normal">({param.unit})</span>}
                    </label>

                    {param.type === 'file' ? (
                      <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-400 transition-colors duration-200 bg-gray-50">
                        {uploadedImage ? (
                          <div className="space-y-4">
                            <img src={uploadedImage} alt="Uploaded" className="max-w-full h-48 object-cover rounded-lg mx-auto shadow-md" />
                            <button
                              onClick={() => setUploadedImage(null)}
                              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
                            >
                              {language === 'tamil' ? 'அகற்று' : language === 'hindi' ? 'हटाएं' : 'Remove'}
                            </button>
                          </div>
                        ) : (
                          <div className="py-4">
                            <Camera className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                            <label htmlFor={`upload-${param.id}`} className="cursor-pointer">
                              <span className="text-gray-600 hover:text-blue-600 transition-colors duration-200 font-medium">
                                {language === 'tamil' ? param.placeholderML : language === 'hindi' ? param.placeholderHI : param.placeholder}
                              </span>
                              <input
                                id={`upload-${param.id}`}
                                type="file"
                                accept="image/*"
                                onChange={handleImageUpload}
                                className="hidden"
                              />
                            </label>
                            <p className="text-xs text-gray-500 mt-2">
                              {language === 'tamil' ? 'JPG, PNG, WebP வரை 10MB' : language === 'hindi' ? 'JPG, PNG, WebP 10MB तक' : 'JPG, PNG, WebP up to 10MB'}
                            </p>
                          </div>
                        )}
                      </div>
                    ) : param.type === 'select' ? (
                      <select
                        value={formData[param.id] || ''}
                        onChange={(e) => handleParameterChange(param.id, e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm hover:border-gray-400 transition-colors duration-200"
                      >
                        <option value="" className="text-gray-500">
                          {language === 'tamil' ? param.placeholderML : language === 'hindi' ? param.placeholderHI : param.placeholder}
                        </option>
                        {param.options?.map((option) => (
                          <option key={option} value={option} className="text-gray-900">{option}</option>
                        ))}
                      </select>
                    ) : param.type === 'range' ? (
                      <div className="space-y-3">
                        <input
                          type="range"
                          min={param.min}
                          max={param.max}
                          step="0.1"
                          value={formData[param.id] || param.min}
                          onChange={(e) => handleParameterChange(param.id, parseFloat(e.target.value))}
                          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        />
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500 font-medium">{param.min}</span>
                          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-bold">
                            {formData[param.id] || param.min} {param.unit}
                          </span>
                          <span className="text-gray-500 font-medium">{param.max}</span>
                        </div>
                      </div>
                    ) : (
                      <input
                        type={param.type}
                        value={formData[param.id] || ''}
                        onChange={(e) => handleParameterChange(param.id, param.type === 'number' ? parseFloat(e.target.value) : e.target.value)}
                        placeholder={language === 'tamil' ? param.placeholderML : language === 'hindi' ? param.placeholderHI : param.placeholder}
                        min={param.min}
                        max={param.max}
                        className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm hover:border-gray-400 transition-colors duration-200 placeholder-gray-400"
                      />
                    )}
                  </div>
                ))}
              </div>

              <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
                <div className="flex space-x-4">
                  <button
                    onClick={runAgent}
                    disabled={isLoading}
                    className={`flex-1 ${selectedAgentConfig.color} text-white px-6 py-3 rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105`}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-6 h-6 animate-spin" />
                        <span>{language === 'tamil' ? 'செயலாக்கம்...' : language === 'hindi' ? 'प्रसंस्करण...' : 'Processing...'}</span>
                      </>
                    ) : (
                      <>
                        <Zap className="w-6 h-6" />
                        <span>{language === 'tamil' ? 'முன்னறிவிp்பு' : language === 'hindi' ? 'पूर्वानुमान' : 'Predict'}</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={resetForm}
                    className="px-6 py-3 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-colors duration-200 font-medium text-gray-700 hover:border-gray-400"
                  >
                    {language === 'tamil' ? 'மீட்டமை' : language === 'hindi' ? 'रीसेट' : 'Reset'}
                  </button>
                </div>
              </div>
            </div>

            {/* Results */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-green-600 to-blue-600 p-6">
                <h2 className="text-xl font-bold text-white flex items-center">
                  <Activity className="w-6 h-6 mr-3" />
                  {language === 'tamil' ? 'முடிவுகள்' : language === 'hindi' ? 'परिणाम' : 'Results'}
                </h2>
                <p className="text-green-100 mt-2">
                  {language === 'tamil' ? 'AI பகுப्பாய्বு முடிवுகळ्' : language === 'hindi' ? 'AI विश्लेषण परिणाम' : 'AI Analysis Results'}
                </p>
              </div>

              <div className="p-6 min-h-96">
                {!results && !isLoading && (
                  <div className="text-center py-12 text-gray-500">
                    <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      {language === 'tamil' ? 'முடிவுகळ्ுக்காக காத्थிருக்கிரदு' : language === 'hindi' ? 'परिणामों की प्रतीक्षा में' : 'Waiting for Results'}
                    </h3>
                    <p className="text-gray-500">
                      {language === 'tamil' ? 'முடிவுகळैप् पেत मुन्नरिविप्पु पॊत्तानை अळुत्तவும्' : language === 'hindi' ? 'AI-संचालित परिणाम देखने के लिए पूर्वानुमान पर क्लिक करें' : 'Click Predict to see AI-powered results'}
                    </p>
                  </div>
                )}

                {isLoading && (
                  <div className="text-center py-12">
                    <div className="relative">
                      <Loader2 className="w-16 h-16 mx-auto animate-spin text-blue-500 mb-4" />
                      <div className="absolute inset-0 w-16 h-16 mx-auto border-4 border-blue-200 rounded-full"></div>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      {language === 'tamil' ? 'AI முகவர் பணியில்' : language === 'hindi' ? 'AI एजेंट काम कर रहा है' : 'AI Agent Working'}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {language === 'tamil' ? 'உங்கள் தரவை பகுப்பாய்வு செய்கிறது...' : language === 'hindi' ? 'आपके डेटा का विश्लेषण कर रहा है...' : 'Analyzing your data...'}
                    </p>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                      <div className="flex items-center justify-center space-x-2">
                        <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce"></div>
                        <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                )}

                {results && (
                  <div className="space-y-6">
                    {/* Disease Identification Results */}
                    {selectedAgent === 'disease_identification' && isDiseaseResult(results) && (
                      <div className="space-y-4">
                        <div className="bg-red-50 border-l-4 border-red-400 rounded-lg p-5 shadow-sm">
                          <div className="flex items-center mb-3">
                            <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white text-sm font-bold">🦠</span>
                            </div>
                            <h3 className="font-bold text-red-800 text-lg">
                              {language === 'tamil' ? 'கண்டறியப்பட்ட நோய்' : language === 'hindi' ? 'पहचाना गया रोग' : 'Detected Disease'}
                            </h3>
                          </div>
                          <p className="text-red-700 font-semibold text-xl mb-2">
                            {language === 'tamil' ? results.diseaseML : language === 'hindi' ? results.diseaseHI : results.disease}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-red-600 font-medium">
                              {language === 'tamil' ? 'நம்பகத்தன்மை' : language === 'hindi' ? 'विश्वसनीयता' : 'Confidence'}: {(results.confidence * 100).toFixed(1)}%
                            </span>
                            <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium">
                              {results.severity}
                            </span>
                          </div>
                        </div>
                        <div className="bg-blue-50 border-l-4 border-blue-400 rounded-lg p-5 shadow-sm">
                          <div className="flex items-center mb-3">
                            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white text-sm font-bold">💊</span>
                            </div>
                            <h3 className="font-bold text-blue-800 text-lg">
                              {language === 'tamil' ? 'சிகிச்சை' : language === 'hindi' ? 'उपचार' : 'Treatment'}
                            </h3>
                          </div>
                          <p className="text-blue-700 leading-relaxed">
                            {language === 'tamil' ? results.treatmentML : language === 'hindi' ? results.treatmentHI : results.treatment}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Crop Recommendation Results */}
                    {selectedAgent === 'crop_recommendation' && isCropRecommendationResult(results) && (
                      <div className="space-y-3">
                        <h3 className="font-semibold text-green-800">
                          {language === 'tamil' ? 'பரிந்துரைக்கப்பட்ட பயிர்கள்' : language === 'hindi' ? 'सुझाई गई फसलें' : 'Recommended Crops'}
                        </h3>
                        {Array.isArray(results.recommendedCrops) && results.recommendedCrops.length > 0 ? (
                          results.recommendedCrops.map((crop: RecommendedCropResult, index: number) => (
                            <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                              <div className="flex justify-between items-center">
                                <span className="font-medium text-green-800">
                                  {language === 'tamil' ? crop.nameML : language === 'hindi' ? crop.nameHI : crop.name}
                                </span>
                                <span className="text-green-600">{(crop.suitability * 100).toFixed(0)}% {language === 'tamil' ? 'பொருத்தம்' : language === 'hindi' ? 'उपयुक्त' : 'suitable'}</span>
                              </div>
                              <p className="text-sm text-green-600">
                                {language === 'tamil' ? 'எதிர்பார்க்கப்படும் விளைச்சல்' : language === 'hindi' ? 'अपेक्षित उत्पादन' : 'Expected yield'}: {crop.expectedYield}
                              </p>
                            </div>
                          ))
                        ) : (
                          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-700">
                            {language === 'tamil' ? 'பரிந்துரைகள் கிடைக்கவில்லை' : language === 'hindi' ? 'कोई फसल सुझाव उपलब्ध नहीं' : 'No crop recommendations available.'}
                          </div>
                        )}
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                          <p className="text-gray-700 text-sm">
                            {language === 'tamil' ? results.reasonML : language === 'hindi' ? results.reasonHI : results.reason}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Irrigation Scheduling Results */}
                    {selectedAgent === 'irrigation_scheduling' && isIrrigationResult(results) && (
                      <div className="space-y-3">
                        <h3 className="font-semibold text-blue-800">
                          {language === 'tamil' ? 'நீர்ப்பாசன அட்டவணை' : language === 'hindi' ? 'सिंचाई कार्यक्रम' : 'Irrigation Schedule'}
                        </h3>
                        {results.schedule.map((item: IrrigationScheduleItem, index: number) => (
                          <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <div className="flex justify-between items-center">
                              <span className="font-medium text-blue-800">{item.day}</span>
                              <span className="text-blue-600">{item.amount}</span>
                            </div>
                            <p className="text-sm text-blue-600">
                              {item.time} - {item.duration}
                            </p>
                          </div>
                        ))}
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                          <p className="text-sm text-gray-700">
                            <strong>{language === 'tamil' ? 'வார மொத்தம்' : language === 'hindi' ? 'साप्ताहिक कुल' : 'Weekly Total'}:</strong> {results.weeklyTotal}
                          </p>
                          <p className="text-sm text-gray-700">
                            <strong>{language === 'tamil' ? 'திறன்' : language === 'hindi' ? 'दक्षता' : 'Efficiency'}:</strong> {results.efficiency}
                          </p>
                          <p className="text-sm text-gray-600 mt-2">
                            {language === 'tamil' ? results.notesML : language === 'hindi' ? results.notesHI : results.notes}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Market Analysis Results */}
                    {selectedAgent === 'market_analysis' && isMarketResult(results) && (
                      <div className="space-y-3">
                        <h3 className="font-semibold text-purple-800">
                          {language === 'tamil' ? 'சந்தை பகுப்பாய்வு' : language === 'hindi' ? 'बाजार विश्लेषण' : 'Market Analysis'}
                        </h3>
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-purple-600 font-medium">
                                {language === 'tamil' ? 'தற்போதைய விலை' : language === 'hindi' ? 'वर्तमान मूल्य' : 'Current Price'}
                              </p>
                              <p className="text-2xl font-bold text-purple-800">{results.marketPrice}</p>
                            </div>
                            <div>
                              <p className="text-sm text-purple-600 font-medium">
                                {language === 'tamil' ? 'விலை மாற்றम்' : language === 'hindi' ? 'मूल्य परिवर्तन' : 'Price Change'}
                              </p>
                              <p className="text-xl font-bold text-green-600">{results.priceChange}</p>
                            </div>
                          </div>
                          <div className="mt-4 pt-4 border-t border-purple-200">
                            <p className="text-purple-700 font-medium">{results.recommendation}</p>
                            <p className="text-sm text-purple-600 mt-1">{results.demandForecast}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Pest Management Results */}
                    {selectedAgent === 'pest_management' && isPestManagementResult(results) && (
                      <div className="space-y-4">
                        <div className="bg-orange-50 border-l-4 border-orange-400 rounded-lg p-5 shadow-sm">
                          <div className="flex items-center mb-3">
                            <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white text-sm font-bold">🛡️</span>
                            </div>
                            <h3 className="font-bold text-orange-800 text-lg">
                              {language === 'tamil' ? 'பூச்சி அபாய மதிப்பீடு' : language === 'hindi' ? 'कीट जोखिम आकलन' : 'Pest Risk Assessment'}
                            </h3>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-orange-600 font-medium">Risk Level</p>
                              <p className="text-xl font-bold text-orange-800">{results.riskLevel}</p>
                            </div>
                            <div>
                              <p className="text-sm text-orange-600 font-medium">Pest Type</p>
                              <p className="text-lg font-semibold text-orange-700">{results.pestType}</p>
                            </div>
                          </div>
                          <div className="mt-4 pt-4 border-t border-orange-200">
                            <p className="text-orange-700 font-medium mb-2">Treatment: {results.treatment}</p>
                            <div className="space-y-1">
                              {results.preventiveMeasures.map((measure, index) => (
                                <p key={index} className="text-sm text-orange-600">• {measure}</p>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Finance Policy Results */}
                    {selectedAgent === 'finance_policy' && isFinancePolicyResult(results) && (
                      <div className="space-y-4">
                        <div className="bg-blue-50 border-l-4 border-blue-400 rounded-lg p-5 shadow-sm">
                          <div className="flex items-center mb-3">
                            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white text-sm font-bold">💰</span>
                            </div>
                            <h3 className="font-bold text-blue-800 text-lg">
                              {language === 'tamil' ? 'நிதி மதிப்பீடு' : language === 'hindi' ? 'वित्तीय मूल्यांकन' : 'Financial Assessment'}
                            </h3>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-blue-600 font-medium">Loan Eligibility</p>
                              <p className="text-xl font-bold text-blue-800">{results.loanEligibility}</p>
                            </div>
                            <div>
                              <p className="text-sm text-blue-600 font-medium">Interest Rate</p>
                              <p className="text-lg font-semibold text-blue-700">{results.interestRate}</p>
                            </div>
                          </div>
                          <div className="mt-4 pt-4 border-t border-blue-200">
                            <p className="text-blue-700 font-medium mb-2">Risk Assessment: {results.riskAssessment}</p>
                            <div className="space-y-1">
                              <p className="text-sm text-blue-600 font-medium">Available Subsidies:</p>
                              {results.subsidies.map((subsidy, index) => (
                                <p key={index} className="text-sm text-blue-600">• {subsidy}</p>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Harvest Planning Results */}
                    {selectedAgent === 'harvest_planning' && isHarvestPlanningResult(results) && (
                      <div className="space-y-4">
                        <div className="bg-amber-50 border-l-4 border-amber-400 rounded-lg p-5 shadow-sm">
                          <div className="flex items-center mb-3">
                            <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white text-sm font-bold">⏰</span>
                            </div>
                            <h3 className="font-bold text-amber-800 text-lg">
                              {language === 'tamil' ? 'அறுவடை திட்டம்' : language === 'hindi' ? 'फसल कटाई योजना' : 'Harvest Plan'}
                            </h3>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-amber-600 font-medium">Optimal Date</p>
                              <p className="text-xl font-bold text-amber-800">{results.optimalDate}</p>
                            </div>
                            <div>
                              <p className="text-sm text-amber-600 font-medium">Quality Prediction</p>
                              <p className="text-lg font-semibold text-amber-700">{results.qualityPrediction}</p>
                            </div>
                          </div>
                          <div className="mt-4 pt-4 border-t border-amber-200">
                            <p className="text-amber-700 font-medium mb-2">Market Recommendation: {results.marketRecommendation}</p>
                            <p className="text-sm text-amber-600">Storage Advice: {results.storageAdvice}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Enhanced Header Section */}
        <div className="text-center mb-12">
          <div className="relative inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 via-blue-500 to-purple-600 rounded-2xl mb-6 shadow-2xl group">
            <div className="absolute inset-0 bg-gradient-to-br from-green-400 via-blue-400 to-purple-500 rounded-2xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
            <Bot className="relative w-10 h-10 text-white float-animation" />
            {/* Floating particles */}
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping"></div>
            <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          </div>
          
          <h1 className="text-5xl font-extrabold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-4 scale-in">
            {language === 'tamil' ? 'AI விவசாய முகவர்கள்' : language === 'hindi' ? 'AI कृषि एजेंट' : 'AI Agricultural Agents'}
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed slide-in-left">
            {language === 'tamil' 
              ? 'அதிநவீன AI தொழில்நுட்பத்துடன் உங்கள் விவசாய தேவைகளுக்கு சிறப்பு முகவர்களை தேர்ந்தெடுத்து இயக்கவும்'
              : language === 'hindi'
              ? 'अपनी कृषि आवश्यकताओं के लिए विशेष एजेंटों के साथ उन्नत AI तकनीक की शक्ति का उपयोग करें'
              : 'Harness the power of advanced AI technology with specialized agents tailored for your agricultural needs'
            }
          </p>
          
          {/* Enhanced Language Selector */}
          <div className="flex items-center justify-center mt-8 slide-in-right">
            <div className="flex items-center space-x-4 bg-white px-8 py-4 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"></div>
                <label className="text-sm font-semibold text-gray-700 group-hover:text-gray-900 transition-colors duration-300">
                  {language === 'tamil' ? 'மொழி:' : language === 'hindi' ? 'भाषा:' : 'Language:'}
                </label>
              </div>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as 'english' | 'tamil' | 'hindi')}
                className="border-0 bg-transparent text-sm font-medium focus:outline-none focus:ring-0 cursor-pointer text-gray-700 group-hover:text-gray-900 transition-colors duration-300"
              >
                <option value="english">🇬🇧 English</option>
                <option value="tamil">🇮🇳 தமிழ்</option>
                <option value="hindi">🇮🇳 हिंदी</option>
              </select>
            </div>
          </div>
          
          {/* Animated Feature Badges */}
          <div className="flex items-center justify-center space-x-4 mt-6 fade-in-up">
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors duration-300">
              <CheckCircle className="w-4 h-4 mr-2" />
              {language === 'tamil' ? 'சான்றளிக்கப்பட்ட AI' : language === 'hindi' ? 'प्रमाणित AI' : 'Certified AI'}
            </span>
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors duration-300">
              <Shield className="w-4 h-4 mr-2" />
              {language === 'tamil' ? 'பாதுகாப்பான' : language === 'hindi' ? 'सुरक्षित' : 'Secure'}
            </span>
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-purple-100 text-purple-800 hover:bg-purple-200 transition-colors duration-300">
              <Sparkles className="w-4 h-4 mr-2" />
              {language === 'tamil' ? '24/7 கிடைக்கும்' : language === 'hindi' ? '24/7 उपलब्ध' : '24/7 Available'}
            </span>
          </div>
        </div>

        {/* Enhanced Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group card-hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium mb-1">
                  {language === 'tamil' ? 'செயலில் முகவர்கள்' : language === 'hindi' ? 'सक्रिय एजेंट' : 'Active Agents'}
                </p>
                <p className="text-3xl font-bold text-gray-900 group-hover:text-green-600 transition-colors duration-300">
                  {agentConfigs.length}
                </p>
                <p className="text-xs text-green-600 font-medium mt-1">
                  ↗ {language === 'tamil' ? 'அனைத்தும் ஆன்லைன்' : language === 'hindi' ? 'सभी ऑनलाइन' : 'All Online'}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-200 transition-colors duration-300 group-hover:scale-110 group-hover:rotate-3">
                <CheckCircle className="w-6 h-6 text-green-600 group-hover:animate-pulse" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group card-hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium mb-1">
                  {language === 'tamil' ? 'வெற்றி விகிதம்' : language === 'hindi' ? 'सफलता दर' : 'Success Rate'}
                </p>
                <p className="text-3xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
                  98.5%
                </p>
                <p className="text-xs text-blue-600 font-medium mt-1">
                  ↗ +2.3% {language === 'tamil' ? 'இந்த மாதம்' : language === 'hindi' ? 'इस महीने' : 'this month'}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center group-hover:bg-blue-200 transition-colors duration-300 group-hover:scale-110 group-hover:rotate-3">
                <Target className="w-6 h-6 text-blue-600 group-hover:animate-pulse" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group card-hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium mb-1">
                  {language === 'tamil' ? 'பதில் நேரம்' : language === 'hindi' ? 'प्रतिक्रिया समय' : 'Response Time'}
                </p>
                <p className="text-3xl font-bold text-gray-900 group-hover:text-purple-600 transition-colors duration-300">
                  &lt; 3s
                </p>
                <p className="text-xs text-purple-600 font-medium mt-1">
                  ↗ {language === 'tamil' ? 'சராசரி' : language === 'hindi' ? 'औसत' : 'Average'}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center group-hover:bg-purple-200 transition-colors duration-300 group-hover:scale-110 group-hover:rotate-3">
                <Clock className="w-6 h-6 text-purple-600 group-hover:animate-pulse" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group card-hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium mb-1">
                  {language === 'tamil' ? 'பணியாளர்கள்' : language === 'hindi' ? 'सेवा प्राप्त उपयोगकर्ता' : 'Users Served'}
                </p>
                <p className="text-3xl font-bold text-gray-900 group-hover:text-orange-600 transition-colors duration-300">
                  10K+
                </p>
                <p className="text-xs text-orange-600 font-medium mt-1">
                  ↗ +1.2K {language === 'tamil' ? 'இந்த வாரம்' : language === 'hindi' ? 'इस सप्ताह' : 'this week'}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center group-hover:bg-orange-200 transition-colors duration-300 group-hover:scale-110 group-hover:rotate-3">
                <Users className="w-6 h-6 text-orange-600 group-hover:animate-pulse" />
              </div>
            </div>
          </div>
        </div>

        {/* Agent Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8 mb-12">
          {agentConfigs.map((agent, index) => (
            <div
              key={agent.id}
              onClick={() => { 
                setSelectedAgent(agent.id as AgentId); 
                // Reset results and form-specific state when switching agents to avoid stale shape mismatches
                setResults(null);
                setFormData({});
                setUploadedImage(null);
              }}
              className="group relative bg-white rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer border border-gray-100 overflow-hidden transform hover:scale-105 card-hover-lift"
              style={{
                animationDelay: `${index * 0.15}s`,
                animation: 'fadeInUp 0.8s ease-out forwards'
              }}
            >
              {/* Animated background gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-gray-100 opacity-60"></div>
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/20 to-indigo-50/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              {/* Header with Icon */}
              <div className={`relative ${agent.color} p-6 text-white overflow-hidden`}>
                {/* Animated background pattern */}
                <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"></div>
                
                <div className="relative flex items-center justify-between mb-4">
                  <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-white group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                    <div className="group-hover:animate-pulse">
                      {agent.icon}
                    </div>
                  </div>
                  <div className="text-right space-y-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/20 backdrop-blur-sm text-white group-hover:bg-white/30 transition-colors duration-300">
                      {agent.modelType === 'image' && <Camera className="w-3 h-3 mr-1" />}
                      {agent.modelType === 'data' && <Database className="w-3 h-3 mr-1" />}
                      {agent.modelType === 'hybrid' && <Activity className="w-3 h-3 mr-1" />}
                      {agent.modelType}
                    </span>
                    <div className="flex items-center justify-end">
                      <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse mr-2"></div>
                      <span className="text-xs font-medium text-white/80">
                        {language === 'tamil' ? 'செயலில்' : language === 'hindi' ? 'सक्रिय' : 'Active'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <h3 className="text-xl font-bold mb-2 leading-tight group-hover:text-white transition-colors duration-300">
                  {language === 'tamil' ? agent.nameML : language === 'hindi' ? agent.nameHI : agent.name}
                </h3>
                
                <p className="text-sm font-medium text-white/90 group-hover:text-white transition-colors duration-300">
                  {agent.category}
                </p>
              </div>

              {/* Content */}
              <div className="relative p-6">
                <p className="text-gray-600 text-sm leading-relaxed mb-6 line-clamp-3 group-hover:text-gray-700 transition-colors duration-300">
                  {language === 'tamil' ? agent.descriptionML : language === 'hindi' ? agent.descriptionHI : agent.description}
                </p>

                {/* Enhanced Features with icons */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-xs text-gray-500 group-hover:text-gray-600 transition-colors duration-300">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-3 animate-pulse"></div>
                    <CheckCircle className="w-3 h-3 mr-2 text-green-500" />
                    {language === 'tamil' ? 'உயர் துல்லியம் (98.5%)' : language === 'hindi' ? 'उच्च सटीकता (98.5%)' : 'High Accuracy (98.5%)'}
                  </div>
                  <div className="flex items-center text-xs text-gray-500 group-hover:text-gray-600 transition-colors duration-300">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse" style={{animationDelay: '0.2s'}}></div>
                    <Clock className="w-3 h-3 mr-2 text-blue-500" />
                    {language === 'tamil' ? 'வேகமான செயலாக்கம் (&lt; 3s)' : language === 'hindi' ? 'तेज़ प्रसंस्करण (< 3s)' : 'Fast Processing (&lt; 3s)'}
                  </div>
                  <div className="flex items-center text-xs text-gray-500 group-hover:text-gray-600 transition-colors duration-300">
                    <div className="w-2 h-2 bg-purple-400 rounded-full mr-3 animate-pulse" style={{animationDelay: '0.4s'}}></div>
                    <Brain className="w-3 h-3 mr-2 text-purple-500" />
                    {language === 'tamil' ? 'AI சக்தி' : language === 'hindi' ? 'AI संचालित' : 'AI Powered'}
                  </div>
                </div>

                {/* Enhanced Action Button */}
                <button className="w-full bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-900 hover:to-black text-white px-6 py-3 rounded-2xl font-semibold text-sm transition-all duration-300 group-hover:shadow-xl transform group-hover:translate-y-[-2px] flex items-center justify-center space-x-2 relative overflow-hidden">
                  {/* Shimmer effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 shimmer-effect"></div>
                  <Zap className="w-4 h-4 group-hover:text-yellow-300 transition-colors duration-300" />
                  <span>{language === 'tamil' ? 'இயக்கு' : language === 'hindi' ? 'एजेंट चलाएं' : 'Launch Agent'}</span>
                  <ArrowLeft className="w-4 h-4 rotate-180 group-hover:translate-x-1 transition-transform duration-300" />
                </button>
              </div>

              {/* Enhanced hover effect with gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
              
              {/* Subtle border highlight on hover */}
              <div className="absolute inset-0 rounded-3xl border-2 border-transparent group-hover:border-gradient transition-all duration-300"></div>
            </div>
          ))}
        </div>

        {/* Enhanced Info Section */}
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 rounded-3xl p-8 text-white shadow-2xl">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">
              {language === 'tamil' ? 'எப்படி பயன்படுத்துவது?' : language === 'hindi' ? 'यह कैसे काम करता है?' : 'How It Works'}
            </h2>
            <p className="text-blue-100 text-lg max-w-2xl mx-auto leading-relaxed">
              {language === 'tamil' 
                ? 'சில நிமிடங்களில் AI-சக்தி வேளாண் நுண்ணறிவுகளைப் பெறுங்கள்'
                : language === 'hindi'
                ? 'कुछ ही मिनटों में AI-संचालित कृषि अंतर्दृष्टि प्राप्त करें'
                : 'Get AI-powered agricultural insights in just a few minutes'
              }
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold">1</span>
              </div>
              <h3 className="text-xl font-bold mb-3">
                {language === 'tamil' ? 'முகவரை தேர்ந்தெடுக்கவும்' : language === 'hindi' ? 'अपना एजेंट चुनें' : 'Choose Your Agent'}
              </h3>
              <p className="text-blue-100 leading-relaxed">
                {language === 'tamil' 
                  ? 'உங்கள் குறிப்பிட்ட தேவைக்கு ஏற்ற AI முகவரை தேர்ந்தெடுக்கவும்'
                  : language === 'hindi'
                  ? 'अपनी विशिष्ट कृषि आवश्यकता के अनुरूप AI एजेंट का चयन करें'
                  : 'Select the AI agent that matches your specific agricultural need'
                }
              </p>
            </div>
            
            <div className="text-center group">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold">2</span>
              </div>
              <h3 className="text-xl font-bold mb-3">
                {language === 'tamil' ? 'தரவை உள்ளிடவும்' : language === 'hindi' ? 'अपना डेटा दर्ज करें' : 'Input Your Data'}
              </h3>
              <p className="text-blue-100 leading-relaxed">
                {language === 'tamil' 
                  ? 'படங்கள், மண் தரவுகள் அல்லது பயிர் தகவல்களை வழங்கவும்'
                  : language === 'hindi'
                  ? 'आवश्यकतानुसार चित्र, मिट्टी का डेटा या फसल की जानकारी प्रदान करें'
                  : 'Provide images, soil data, or crop information as required'
                }
              </p>
            </div>
            
            <div className="text-center group">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold">3</span>
              </div>
              <h3 className="text-xl font-bold mb-3">
                {language === 'tamil' ? 'நுண்ணறிவுகள் பெறுங்கள்' : language === 'hindi' ? 'अंतर्दृष्टि प्राप्त करें' : 'Get Insights'}
              </h3>
              <p className="text-blue-100 leading-relaxed">
                {language === 'tamil' 
                  ? 'உடனடியாக AI-இயங்கும் பரிந்துரைகள் மற்றும் தீர்வுகளைப் பெறுங்கள்'
                  : language === 'hindi'
                  ? 'तत्काल AI-संचालित सिफारिशें और समाधान प्राप्त करें'
                  : 'Receive instant AI-powered recommendations and solutions'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Floating Action Button */}
        <div className="fixed bottom-8 right-8 z-50">
          <div className="relative group">
            {/* Tooltip */}
            <div className="absolute bottom-16 right-0 bg-gray-900 text-white px-3 py-2 rounded-lg text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
              {language === 'tamil' ? 'உதவி தேவையா?' : language === 'hindi' ? 'मदद चाहिए?' : 'Need Help?'}
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
            
            <button className="w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center group-hover:scale-110 float-animation">
              <Bot className="w-6 h-6 group-hover:animate-pulse" />
            </button>
            
            {/* Ripple effect */}
            <div className="absolute inset-0 rounded-full bg-blue-400 opacity-75 animate-ping"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAgentsPage;
