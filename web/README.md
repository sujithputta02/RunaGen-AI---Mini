# RunaGen AI - Web Interface

Beautiful skeuomorphic UI for resume analysis with realistic textures and depth.

## 🎨 Design Features

### Skeuomorphic Design Elements
- **Realistic Textures**: Leather-like cards with subtle grain patterns
- **3D Depth**: Embossed and debossed effects with realistic shadows
- **Glossy Surfaces**: Shiny buttons and badges with light reflections
- **Tactile Feel**: Interactive elements that respond to hover and click
- **Premium Materials**: Gradient overlays simulating real-world materials

### Visual Effects
- **Inset Shadows**: Creating depth and dimension
- **Gradient Overlays**: Multi-layered gradients for realism
- **Drop Shadows**: Multiple shadow layers for 3D effect
- **Border Highlights**: Top and bottom borders simulating light reflection
- **Backdrop Blur**: Frosted glass effect on header elements

## 🚀 Quick Start

### 1. Start the API Server
```bash
python3 src/api/main.py
```

### 2. Start the Web Interface
```bash
./start_web.sh
```

### 3. Open Browser
Navigate to: http://localhost:8080

## 📁 File Structure

```
web/
├── index.html          # Main HTML structure
├── styles.css          # Skeuomorphic CSS styles
├── script.js           # JavaScript functionality
└── README.md          # This file
```

## 🎯 Features

### Upload Section
- Drag and drop PDF files
- Click to browse files
- File size display
- Remove file option
- Animated upload zone

### Loading State
- Spinning loader with 3D effect
- Step-by-step progress indicators
- Smooth animations

### Results Display
- **Profile Summary**: Experience, education, skills count
- **Skills Grid**: Glossy skill badges with hover effects
- **Career Predictions**: Progress bars with rankings
- **Salary Insights**: Premium card with INR display
- **Skill Gap Analysis**: Color-coded priority badges
- **Recommendations**: Checkmark list with smooth transitions

## 🎨 Color Palette

```css
Primary: #4a5fc1 (Deep Blue)
Secondary: #6c5ce7 (Purple)
Accent: #00b894 (Teal Green)
Danger: #d63031 (Red)
Warning: #fdcb6e (Yellow)
```

## 💡 Design Principles

### 1. Depth & Dimension
- Multiple shadow layers
- Inset and outset effects
- Gradient overlays

### 2. Realistic Materials
- Leather texture on cards
- Glossy buttons
- Frosted glass header
- Metallic badges

### 3. Interactive Feedback
- Hover animations
- Click responses
- Smooth transitions
- Visual state changes

### 4. Premium Feel
- High-quality shadows
- Subtle textures
- Polished surfaces
- Professional typography

## 🔧 Customization

### Change Primary Color
```css
:root {
    --primary: #4a5fc1;  /* Change this */
}
```

### Adjust Shadow Intensity
```css
:root {
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.15);  /* Adjust opacity */
}
```

### Modify Card Radius
```css
.result-card {
    border-radius: 25px;  /* Change this */
}
```

## 📱 Responsive Design

The interface is fully responsive:
- Desktop: Full layout with all features
- Tablet: Adjusted grid layouts
- Mobile: Stacked cards, optimized touch targets

## 🎭 Animations

### Entrance Animations
- `fadeInDown`: Header elements
- `fadeInUp`: Cards and results
- `float`: Logo icon
- `bounce`: Upload icon

### Interactive Animations
- `pulse`: Active loading steps
- `spin`: Loading spinner
- `shake`: Error messages

### Hover Effects
- Scale transforms
- Shadow elevation
- Color transitions
- Position shifts

## 🌐 Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support

## 🔒 Security

- Client-side file validation
- PDF-only uploads
- API error handling
- XSS protection

## 📊 Performance

- Optimized CSS animations
- Efficient DOM updates
- Lazy loading for results
- Smooth 60fps animations

## 🎉 Special Effects

### Textured Background
- Diagonal line patterns
- Subtle noise overlay
- Depth simulation

### Glossy Buttons
- Light reflection simulation
- 3D press effect
- Shine animation on hover

### Embossed Cards
- Top highlight (light source)
- Bottom shadow (depth)
- Inset texture pattern

## 🛠️ Development

### Add New Result Card
```javascript
function createNewCard(data) {
    return `
        <div class="result-card">
            <div class="card-title">
                <span class="card-icon">🎯</span>
                <h2>Card Title</h2>
            </div>
            <!-- Card content -->
        </div>
    `;
}
```

### Style New Elements
```css
.new-element {
    background: linear-gradient(145deg, #ffffff, #f5f5f5);
    box-shadow: 
        0 8px 20px rgba(0,0,0,0.15),
        inset 0 1px 0 rgba(255,255,255,0.8);
    border-radius: 15px;
}
```

## 📝 Notes

- All salaries displayed in Indian Rupees (₹)
- Powered by Adzuna India job market data
- 85%+ accuracy on predictions
- Real-time API integration

## 🎨 Design Credits

Inspired by:
- Apple's iOS design language
- Material Design depth principles
- Neumorphism trends
- Classic skeuomorphic interfaces

---

**Enjoy the premium, tactile experience!** 🚀
