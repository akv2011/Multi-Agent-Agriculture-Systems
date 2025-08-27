import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MarketplacePage.css';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  unit: string;
  category: string;
  seller: {
    name: string;
    location: string;
    rating: number;
    verified: boolean;
  };
  images: string[];
  stock: number;
  isOrganic: boolean;
  harvestDate: string;
  location: {
    state: string;
    district: string;
  };
  specifications: {
    variety?: string;
    grade?: string;
    moisture?: number;
    purity?: number;
  };
}

interface MarketStats {
  totalProducts: number;
  activeSellers: number;
  todaysOrders: number;
  avgPrice: number;
}

const MarketplacePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'b2c' | 'b2b'>('b2c');
  const [products, setProducts] = useState<Product[]>([]);
  const [marketStats, setMarketStats] = useState<MarketStats | null>(null);
  const [filters, setFilters] = useState({
    category: '',
    location: '',
    priceRange: '',
    organic: false
  });
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data for demonstration
  const mockProducts: Product[] = [
    {
      id: '1',
      name: 'Premium Basmati Rice',
      description: 'High-quality aged Basmati rice from Punjab fields',
      price: 85,
      unit: 'kg',
      category: 'Grains',
      seller: {
        name: 'Rajesh Kumar',
        location: 'Ludhiana, Punjab',
        rating: 4.8,
        verified: true
      },
      images: ['/images/basmati-rice.jpg', '/images/rice-field.jpg'],
      stock: 500,
      isOrganic: false,
      harvestDate: '2024-11-15',
      location: {
        state: 'Punjab',
        district: 'Ludhiana'
      },
      specifications: {
        variety: 'Pusa Basmati 1121',
        grade: 'Grade A',
        moisture: 12,
        purity: 99
      }
    },
    {
      id: '2',
      name: 'Organic Wheat Flour',
      description: 'Freshly ground organic wheat flour, pesticide-free',
      price: 45,
      unit: 'kg',
      category: 'Processed',
      seller: {
        name: 'Sunita Farms',
        location: 'Meerut, UP',
        rating: 4.9,
        verified: true
      },
      images: ['/images/wheat-flour.jpg', '/images/wheat-field.jpg'],
      stock: 200,
      isOrganic: true,
      harvestDate: '2024-12-01',
      location: {
        state: 'Uttar Pradesh',
        district: 'Meerut'
      },
      specifications: {
        variety: 'Sharbati Wheat',
        grade: 'Premium',
        moisture: 10,
        purity: 98
      }
    },
    {
      id: '3',
      name: 'Fresh Tomatoes',
      description: 'Farm-fresh tomatoes, perfect for cooking and salads',
      price: 35,
      unit: 'kg',
      category: 'Vegetables',
      seller: {
        name: 'Green Valley Farm',
        location: 'Nashik, Maharashtra',
        rating: 4.6,
        verified: true
      },
      images: ['/images/tomatoes.jpg', '/images/tomato-farm.jpg'],
      stock: 150,
      isOrganic: false,
      harvestDate: '2024-12-20',
      location: {
        state: 'Maharashtra',
        district: 'Nashik'
      },
      specifications: {
        variety: 'Hybrid Tomato',
        grade: 'Grade A'
      }
    },
    {
      id: '4',
      name: 'Bulk Cotton (B2B)',
      description: 'Premium quality cotton for textile manufacturing',
      price: 65000,
      unit: 'tonne',
      category: 'Cash Crops',
      seller: {
        name: 'Maharashtra Cotton Co-op',
        location: 'Aurangabad, Maharashtra',
        rating: 4.7,
        verified: true
      },
      images: ['/images/cotton-bulk.jpg', '/images/cotton-field.jpg'],
      stock: 50,
      isOrganic: false,
      harvestDate: '2024-11-30',
      location: {
        state: 'Maharashtra',
        district: 'Aurangabad'
      },
      specifications: {
        variety: 'Bt Cotton',
        grade: 'Premium',
        moisture: 8,
        purity: 96
      }
    }
  ];

  const mockStats: MarketStats = {
    totalProducts: 1247,
    activeSellers: 356,
    todaysOrders: 89,
    avgPrice: 52.5
  };

  useEffect(() => {
    // Fetch real data from API
    const fetchMarketplaceData = async () => {
      try {
        // Fetch products
        const productsResponse = await fetch('http://localhost:8001/marketplace/products');
        const productsData = await productsResponse.json();
        
        // Fetch stats
        const statsResponse = await fetch('http://localhost:8001/marketplace/stats');
        const statsData = await statsResponse.json();
        
        if (productsData.status === 'success') {
          setProducts(productsData.products);
        }
        
        if (statsData.status === 'success') {
          setMarketStats(statsData.stats);
        }
      } catch (error) {
        console.error('Failed to fetch marketplace data:', error);
        // Fallback to mock data
        setProducts(mockProducts);
        setMarketStats(mockStats);
      }
    };
    
    fetchMarketplaceData();
  }, []);

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !filters.category || product.category === filters.category;
    const matchesOrganic = !filters.organic || product.isOrganic;
    const matchesTab = activeTab === 'b2c' ? product.unit !== 'tonne' : product.unit === 'tonne';
    
    return matchesSearch && matchesCategory && matchesOrganic && matchesTab;
  });

  const categories = ['Grains', 'Vegetables', 'Fruits', 'Processed', 'Cash Crops', 'Spices'];

  return (
    <div className="marketplace-page">
      <div className="marketplace-header">
        <div className="header-top">
          <div className="header-text">
            <h1>🌾 Agricultural Marketplace</h1>
            <p>Connect farmers with buyers - transparent, fair, and efficient</p>
          </div>
          <button 
            className="add-product-btn"
            onClick={() => navigate('/marketplace/add-product')}
          >
            ➕ Add Product
          </button>
        </div>
        
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'b2c' ? 'active' : ''}`}
            onClick={() => setActiveTab('b2c')}
          >
            🛒 B2C Marketplace
            <span className="tab-desc">Direct to Consumer</span>
          </button>
          <button 
            className={`tab-btn ${activeTab === 'b2b' ? 'active' : ''}`}
            onClick={() => setActiveTab('b2b')}
          >
            🏭 B2B Marketplace
            <span className="tab-desc">Bulk Trading</span>
          </button>
        </div>
      </div>

      {/* Market Statistics */}
      {marketStats && (
        <div className="market-stats">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-number">{marketStats.totalProducts}</div>
              <div className="stat-label">Products Available</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👨‍🌾</div>
            <div className="stat-content">
              <div className="stat-number">{marketStats.activeSellers}</div>
              <div className="stat-label">Active Sellers</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📦</div>
            <div className="stat-content">
              <div className="stat-number">{marketStats.todaysOrders}</div>
              <div className="stat-label">Today's Orders</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <div className="stat-number">₹{marketStats.avgPrice}</div>
              <div className="stat-label">Avg Price/kg</div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="search-filters">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button className="search-btn">🔍</button>
        </div>
        
        <div className="filters">
          <select 
            value={filters.category} 
            onChange={(e) => setFilters({...filters, category: e.target.value})}
            className="filter-select"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          
          <label className="organic-filter">
            <input
              type="checkbox"
              checked={filters.organic}
              onChange={(e) => setFilters({...filters, organic: e.target.checked})}
            />
            Organic Only
          </label>
        </div>
      </div>

      {/* Products Grid */}
      <div className="products-grid">
        {filteredProducts.map(product => (
          <div key={product.id} className="product-card">
            <div className="product-image">
              <img 
                src={product.images[0] || '/images/placeholder.jpg'} 
                alt={product.name}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/images/placeholder.jpg';
                }}
              />
              {product.isOrganic && <span className="organic-badge">🌱 Organic</span>}
              {product.seller.verified && <span className="verified-badge">✅ Verified</span>}
            </div>
            
            <div className="product-info">
              <h3 className="product-name">{product.name}</h3>
              <p className="product-description">{product.description}</p>
              
              <div className="product-details">
                <div className="price-info">
                  <span className="price">₹{product.price}</span>
                  <span className="unit">/{product.unit}</span>
                </div>
                <div className="stock-info">
                  <span className="stock">📦 {product.stock} {product.unit} available</span>
                </div>
              </div>
              
              <div className="seller-info">
                <div className="seller-details">
                  <span className="seller-name">👨‍🌾 {product.seller.name}</span>
                  <span className="seller-location">📍 {product.seller.location}</span>
                  <span className="seller-rating">⭐ {product.seller.rating}</span>
                </div>
              </div>
              
              {product.specifications && (
                <div className="specifications">
                  <h4>Specifications:</h4>
                  <div className="spec-grid">
                    {product.specifications.variety && (
                      <span className="spec">Variety: {product.specifications.variety}</span>
                    )}
                    {product.specifications.grade && (
                      <span className="spec">Grade: {product.specifications.grade}</span>
                    )}
                    {product.specifications.moisture && (
                      <span className="spec">Moisture: {product.specifications.moisture}%</span>
                    )}
                    {product.specifications.purity && (
                      <span className="spec">Purity: {product.specifications.purity}%</span>
                    )}
                  </div>
                </div>
              )}
              
              <div className="product-actions">
                <button className="btn-primary">
                  {activeTab === 'b2c' ? '🛒 Add to Cart' : '📋 Request Quote'}
                </button>
                <button className="btn-secondary">💬 Contact Seller</button>
                <button className="btn-secondary">❤️ Save</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="no-products">
          <h3>No products found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      )}

      {/* Floating Action Button for Sellers */}
      <button className="fab-sell">
        <span className="fab-icon">+</span>
        <span className="fab-text">Sell Your Products</span>
      </button>
    </div>
  );
};

export default MarketplacePage;
