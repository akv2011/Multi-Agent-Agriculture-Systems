import React, { useState, useEffect } from 'react';
import './AddProductPage.css';

interface Seller {
  seller_id: string;
  name: string;
  location: string;
  verified: boolean;
}

interface Category {
  name: string;
  icon: string;
  examples: string[];
}

const AddProductPage: React.FC<{ isModal?: boolean; onClose?: () => void }> = (props) => {
  const { isModal = false, onClose } = props; // reference props to avoid unused lint error

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'grains',
    price: '',
    unit: 'kg',
    stock: '',
    seller_id: '',
    is_organic: false,
    harvest_date: '',
    marketplace_type: 'b2c',
    specifications: ''
  });

  const [images, setImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [sellers, setSellers] = useState<Seller[]>([]);
  const [categories, setCategories] = useState<Record<string, Category>>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Default categories as fallback
    const defaultCategories: Record<string, Category> = {
      grains: {
        name: 'Grains & Cereals',
        icon: '🌾',
        examples: ['Rice', 'Wheat', 'Corn', 'Barley']
      },
      vegetables: {
        name: 'Vegetables',
        icon: '🥕',
        examples: ['Tomatoes', 'Onions', 'Potatoes', 'Carrots']
      },
      fruits: {
        name: 'Fruits',
        icon: '🍎',
        examples: ['Apples', 'Bananas', 'Oranges', 'Mangoes']
      },
      pulses: {
        name: 'Pulses & Legumes',
        icon: '🌰',
        examples: ['Lentils', 'Chickpeas', 'Black Beans', 'Kidney Beans']
      },
      spices: {
        name: 'Spices & Herbs',
        icon: '🌶️',
        examples: ['Turmeric', 'Coriander', 'Cumin', 'Cardamom']
      },
      dairy: {
        name: 'Dairy Products',
        icon: '🥛',
        examples: ['Milk', 'Cheese', 'Butter', 'Yogurt']
      }
    };

    // Default sellers as fallback
    const defaultSellers: Seller[] = [
      {
        seller_id: 'seller_001',
        name: 'Green Valley Farms',
        location: 'Punjab, India',
        verified: true
      },
      {
        seller_id: 'seller_002',
        name: 'Organic Harvest Co.',
        location: 'Maharashtra, India',
        verified: true
      },
      {
        seller_id: 'seller_003',
        name: 'Fresh Fields Agriculture',
        location: 'Gujarat, India',
        verified: false
      },
      {
        seller_id: 'seller_004',
        name: 'Sunrise Produce',
        location: 'Haryana, India',
        verified: true
      },
      {
        seller_id: 'seller_005',
        name: 'Natural Farms India',
        location: 'Uttar Pradesh, India',
        verified: false
      }
    ];

    // Initialize with default data first
    setCategories(defaultCategories);
    setSellers(defaultSellers);
    
    // Then try to fetch from API (will override defaults if successful)
    fetchSellers();
    fetchCategories();
  }, []);

  const fetchSellers = async () => {
    try {
      const response = await fetch('http://localhost:8001/marketplace/sellers');
      if (response.ok) {
        const data = await response.json();
        if (data.sellers && data.sellers.length > 0) {
          setSellers(data.sellers);
        }
        // If no sellers from API, keep the default ones
      }
    } catch (error) {
      console.error('Error fetching sellers:', error);
      // Keep default sellers on error
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8001/marketplace/categories');
      if (response.ok) {
        const data = await response.json();
        if (data.categories && Object.keys(data.categories).length > 0) {
          setCategories(data.categories);
        }
        // If no categories from API, keep the default ones
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Keep default categories on error
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      setImages(fileList);

      // Create previews
      const previews: string[] = [];
      fileList.forEach(file => {
        const reader = new FileReader();
        reader.onload = (event) => {
          if (event.target?.result) {
            previews.push(event.target.result as string);
            if (previews.length === fileList.length) {
              setImagePreviews(previews);
            }
          }
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const formDataToSend = new FormData();
      
      // Add form fields
      Object.entries(formData).forEach(([key, value]) => {
        if (key === 'specifications') {
          // Convert specifications to JSON
          const specs = (typeof value === 'string' && value) ? JSON.parse(value) : {};
          formDataToSend.append(key, JSON.stringify(specs));
        } else {
          formDataToSend.append(key, value.toString());
        }
      });

      // Add images
      images.forEach((image) => {
        formDataToSend.append('images', image);
      });

      const response = await fetch('http://localhost:8001/marketplace/products', {
        method: 'POST',
        body: formDataToSend,
      });

      if (!response.ok) {
        throw new Error('Failed to create product');
      }

      await response.json(); // Process the response
      setSuccess(true);
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        category: 'grains',
        price: '',
        unit: 'kg',
        stock: '',
        seller_id: '',
        is_organic: false,
        harvest_date: '',
        marketplace_type: 'b2c',
        specifications: ''
      });
      setImages([]);
      setImagePreviews([]);

      // If in modal mode, close after successful submission
      if (isModal && onClose) {
        setTimeout(() => {
          setSuccess(false);
          onClose();
        }, 1500); // Show success message briefly before closing
      } else {
        // Hide success message after 3 seconds for non-modal
        setTimeout(() => setSuccess(false), 3000);
      }

    } catch {
      setError('An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const addSpecification = () => {
    try {
      const specs = formData.specifications ? JSON.parse(formData.specifications) : {};
      const key = prompt('Enter specification key (e.g., "variety", "grade"):');
      const value = prompt('Enter specification value:');
      
      if (key && value) {
        specs[key] = value;
        setFormData(prev => ({ ...prev, specifications: JSON.stringify(specs, null, 2) }));
      }
    } catch {
      alert('Invalid JSON in specifications. Please check the format.');
    }
  };

  return (
    <div className={isModal ? 'add-product-modal-overlay' : 'add-product-page'}>
      <div className={isModal ? 'add-product-modal' : 'add-product-container'}>
        {isModal && (
          <div className="modal-header">
            <h2>➕ Add Product</h2>
            <button className="modal-close-btn" onClick={onClose} aria-label="Close">✕</button>
          </div>
        )}
        {!isModal && (
          <>
            <h1>🌾 Add New Product</h1>
            <p className="subtitle">List your agricultural products in the marketplace</p>
          </>
        )}

        {success && (
          <div className="success-message">
            ✅ Product created successfully!
          </div>
        )}

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="product-form">
          <div className="form-grid">
            {/* Basic Information */}
            <div className="form-section">
              <h3>📋 Basic Information</h3>
              
              <div className="form-group">
                <label htmlFor="name">Product Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., Premium Basmati Rice"
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description *</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                  rows={3}
                  placeholder="Describe your product quality, origin, and key features..."
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="category">Category *</label>
                  <select
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Select a category</option>
                    {Object.entries(categories).map(([key, category]) => (
                      <option key={key} value={key}>
                        {category.icon} {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="marketplace_type">Marketplace Type *</label>
                  <select
                    id="marketplace_type"
                    name="marketplace_type"
                    value={formData.marketplace_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="b2c">🛒 B2C (Direct to Consumer)</option>
                    <option value="b2b">🏢 B2B (Business to Business)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Pricing & Stock */}
            <div className="form-section">
              <h3>💰 Pricing & Stock</h3>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="price">Price *</label>
                  <input
                    type="number"
                    id="price"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="unit">Unit *</label>
                  <select
                    id="unit"
                    name="unit"
                    value={formData.unit}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="kg">Kilogram (kg)</option>
                    <option value="tonne">Tonne</option>
                    <option value="quintal">Quintal</option>
                    <option value="bag">Bag</option>
                    <option value="piece">Piece</option>
                    <option value="litre">Litre</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="stock">Stock Quantity *</label>
                  <input
                    type="number"
                    id="stock"
                    name="stock"
                    value={formData.stock}
                    onChange={handleInputChange}
                    required
                    min="1"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            {/* Seller & Quality */}
            <div className="form-section">
              <h3>👨‍🌾 Seller & Quality Information</h3>
              
              <div className="form-group">
                <label htmlFor="seller_id">Seller *</label>
                <select
                  id="seller_id"
                  name="seller_id"
                  value={formData.seller_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select a seller</option>
                  {sellers.map(seller => (
                    <option key={seller.seller_id} value={seller.seller_id}>
                      {seller.name} - {seller.location} {seller.verified ? '✅' : '⏳'}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="harvest_date">Harvest Date</label>
                  <input
                    type="date"
                    id="harvest_date"
                    name="harvest_date"
                    value={formData.harvest_date}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group checkbox-group">
                  <label htmlFor="is_organic" className="checkbox-label">
                    <input
                      type="checkbox"
                      id="is_organic"
                      name="is_organic"
                      checked={formData.is_organic}
                      onChange={handleInputChange}
                    />
                    🌱 Organic Product
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Product Images */}
          <div className="form-section">
            <h3>📸 Product Images</h3>
            <div className="form-group">
              <label htmlFor="images">Upload Product Images (Max 5)</label>
              <input
                type="file"
                id="images"
                name="images"
                multiple
                accept="image/*"
                onChange={handleImageChange}
                className="file-input"
              />
              <p className="help-text">Accepted formats: JPG, PNG, WEBP. Max size: 5MB each</p>
            </div>

            {imagePreviews.length > 0 && (
              <div className="image-previews">
                <h4>Image Previews:</h4>
                <div className="preview-grid">
                  {imagePreviews.map((preview, index) => (
                    <div key={index} className="preview-item">
                      <img src={preview} alt={`Preview ${index + 1}`} />
                      <span className="image-name">{images[index]?.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Specifications */}
          <div className="form-section">
            <h3>📊 Product Specifications</h3>
            <div className="form-group">
              <label htmlFor="specifications">Specifications (JSON format)</label>
              <textarea
                id="specifications"
                name="specifications"
                value={formData.specifications}
                onChange={handleInputChange}
                rows={4}
                placeholder='{"variety": "Basmati 1121", "grade": "Grade A", "moisture": 12, "purity": 99}'
              />
              <div className="specification-buttons">
                <button type="button" onClick={addSpecification} className="add-spec-btn">
                  ➕ Add Specification
                </button>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="form-actions">
            <button 
              type="submit" 
              disabled={loading || !formData.seller_id} 
              className="submit-btn"
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Creating Product...
                </>
              ) : (
                <>
                  🚀 Create Product
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProductPage;
