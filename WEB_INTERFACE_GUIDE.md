# RunaGen AI - Web Interface Guide 🎯

## Overview
The RunaGen AI web interface allows you to upload your resume and get instant AI-powered analysis including skill gaps, career trajectory predictions, and salary insights.

---

## Quick Start

### Step 1: Start the Application

**Option 1: One-Click Start (Recommended)**
```bash
# macOS/Linux
./start_web_app.sh

# Windows
start_web_app.bat
```

**Option 2: Manual Start**
```bash
# Terminal 1: Start API server
python3 src/api/main.py

# Terminal 2: Open web interface
open web/index.html  # macOS
xdg-open web/index.html  # Linux
start web\index.html  # Windows
```

### Step 2: Upload Your Resume
1. The web interface will open in your browser
2. Drag and drop your PDF resume onto the upload area
3. Or click the upload area to browse for your file
4. Click "Analyze Resume" button

### Step 3: View Results
The analysis will show:
- ✅ Extracted skills from your resume
- ✅ Years of experience and education level
- ✅ Top 3 career trajectory predictions with probabilities
- ✅ Skill gaps prioritized by importance
- ✅ Predicted salary range
- ✅ Personalized recommendations

---

## What You'll See

### 1. 📋 Extracted Information
**Shows:**
- Years of experience
- Education level (Bachelor's, Master's, PhD, etc.)
- Total number of skills found
- All extracted skills displayed as tags

**Example:**
```
Experience: 5 years
Education: Master's
Skills Found: 12

Skills: Python, SQL, AWS, Docker, Kubernetes, Machine Learning, etc.
```

---

### 2. 🚀 Career Trajectory Predictions
**Shows:**
- Top 3 most likely career paths
- Probability percentage for each path
- Confidence level (High/Medium/Low)

**Example:**
```
1. Data Scientist - 72.3%
   High probability - This is a strong career match for your profile

2. ML Engineer - 65.1%
   Medium probability - Consider developing relevant skills

3. Data Engineer - 54.2%
   Medium probability - Consider developing relevant skills
```

**How to interpret:**
- **>70%**: Strong match - You're well-positioned for this role
- **50-70%**: Good match - Some skill development recommended
- **<50%**: Requires significant upskilling

---

### 3. 📊 Skill Gap Analysis
**Shows:**
- Missing skills for your target career path
- Priority level (High/Medium/Low)
- Priority score (0-1 scale)

**Example:**
```
Machine Learning - HIGH PRIORITY
Priority Score: 0.92

AWS - HIGH PRIORITY
Priority Score: 0.88

Docker - MEDIUM PRIORITY
Priority Score: 0.75
```

**Priority Levels:**
- **HIGH** (>0.8): Learn these skills first - highest impact
- **MEDIUM** (0.6-0.8): Important but not urgent
- **LOW** (<0.6): Nice to have

---

### 4. 💰 Salary Insights
**Shows:**
- Predicted salary based on your profile
- Salary range (min-max)
- Currency (USD)

**Example:**
```
Predicted Salary: $105,000
Range: $94,500 - $115,500
```

**Factors considered:**
- Your current role
- Number of skills
- Years of experience
- Location
- Market demand

---

### 5. 💡 Personalized Recommendations
**Shows:**
- Actionable advice based on your analysis
- Learning priorities
- Career path suggestions
- Salary expectations

**Example:**
```
✓ Focus on learning: Machine Learning, Deep Learning, Statistics
✓ Top career path: Data Scientist
✓ Expected salary range: $94,500 - $115,500
```

---

## Features

### Interactive Upload
- **Drag & Drop**: Simply drag your PDF onto the upload area
- **Click to Browse**: Click the upload area to select a file
- **File Validation**: Only PDF files are accepted
- **Visual Feedback**: Upload area highlights when dragging files

### Real-Time Analysis
- **Fast Processing**: Results in 2-5 seconds
- **Progress Indicator**: Loading spinner shows analysis in progress
- **Error Handling**: Clear error messages if something goes wrong

### Beautiful Visualizations
- **Color-Coded Priority**: Red (high), Orange (medium), Green (low)
- **Skill Tags**: Visual representation of your skills
- **Career Cards**: Easy-to-read career predictions
- **Salary Box**: Prominent salary display

### Responsive Design
- Works on desktop, tablet, and mobile
- Smooth animations and transitions
- Professional gradient design
- Easy-to-read typography

---

## Troubleshooting

### Issue: "API server is not running"
**Solution:**
```bash
# Start the API server
python3 src/api/main.py

# Or use the start script
./start_api.sh
```

### Issue: "Analysis failed: 500"
**Solution:**
1. Check if models are trained:
   ```bash
   ls -lh models/
   ```
2. If models are missing, train them:
   ```bash
   python3 src/ml/train_models.py
   ```

### Issue: "CORS error"
**Solution:**
- Make sure you're accessing the web interface via file:// protocol
- Or serve it via a local web server:
  ```bash
  cd web
  python3 -m http.server 8080
  # Then open: http://localhost:8080
  ```

### Issue: PDF not uploading
**Solution:**
- Ensure the file is a valid PDF
- Check file size (should be < 10MB)
- Try a different PDF file

### Issue: No results showing
**Solution:**
1. Check browser console for errors (F12)
2. Verify API is running: http://localhost:8000/health
3. Check if resume has extractable text (not scanned image)

---

## API Endpoints Used

The web interface uses these API endpoints:

1. **GET /health** - Check API status
2. **POST /api/analyze-resume** - Complete resume analysis

You can also use these endpoints directly:

```bash
# Check API health
curl http://localhost:8000/health

# Analyze resume
curl -X POST "http://localhost:8000/api/analyze-resume" \
  -F "file=@your_resume.pdf"
```

---

## Sample Resume Format

For best results, your resume should include:

### Required Information
- **Skills**: List of technical skills (Python, SQL, AWS, etc.)
- **Experience**: Years of experience or job dates
- **Education**: Degree level and field

### Recommended Format
```
EXPERIENCE
Senior Data Engineer | Company Name | 2020-Present
- Built ETL pipelines using Python and Spark
- Managed AWS infrastructure

SKILLS
Python, SQL, AWS, Docker, Kubernetes, Apache Spark

EDUCATION
Master of Science in Computer Science
Stanford University, 2019
```

### Tips for Better Results
- ✅ Use clear section headers (Experience, Skills, Education)
- ✅ List skills explicitly
- ✅ Include years or dates for experience
- ✅ Mention specific technologies and tools
- ❌ Avoid image-based PDFs (use text-based PDFs)
- ❌ Don't use complex formatting or tables

---

## Privacy & Security

### Data Handling
- ✅ Your resume is processed locally on your machine
- ✅ No data is stored permanently
- ✅ Analysis happens in real-time
- ✅ Resume is not saved to disk

### API Security
- Currently runs on localhost (not exposed to internet)
- For production, add authentication
- Use HTTPS for secure transmission

---

## Advanced Usage

### Using with Different API URL
If your API is running on a different port or server:

1. Open `web/index.html`
2. Find this line:
   ```javascript
   const API_BASE_URL = 'http://localhost:8000';
   ```
3. Change to your API URL:
   ```javascript
   const API_BASE_URL = 'http://your-server:port';
   ```

### Customizing the Interface
The web interface is a single HTML file with embedded CSS and JavaScript. You can customize:

- **Colors**: Change the gradient colors in the CSS
- **Layout**: Modify the HTML structure
- **Behavior**: Update the JavaScript logic

---

## Integration with Existing Project

If you have the main RunaGen AI project in the `project/` folder, you can integrate this:

### Option 1: Standalone
Keep this as a separate analysis tool

### Option 2: Integrate
Copy the web interface to your main project:
```bash
cp -r runagen-ml-etl/web project/public/analyzer
```

Then access it at: `http://your-app/analyzer`

---

## Performance

### Analysis Speed
- **Skill Extraction**: ~50ms
- **Career Prediction**: ~100ms
- **Skill Gap Analysis**: ~80ms
- **Salary Prediction**: ~90ms
- **Total**: ~300ms (< 1 second)

### File Size Limits
- **Recommended**: < 2MB
- **Maximum**: 10MB
- **Format**: PDF only

---

## Next Steps

### After Analysis
1. **Review Skill Gaps**: Focus on high-priority skills
2. **Plan Learning Path**: Use recommendations as a guide
3. **Update Resume**: Add new skills as you learn them
4. **Re-analyze**: Upload updated resume to track progress

### Career Development
1. **Target Role**: Choose from top predictions
2. **Skill Development**: Learn missing high-priority skills
3. **Networking**: Connect with people in target roles
4. **Apply**: Use insights for job applications

---

## Screenshots

### Upload Screen
```
┌─────────────────────────────────────┐
│     🎯 RunaGen AI                   │
│  AI-Powered Resume Analysis         │
├─────────────────────────────────────┤
│                                     │
│         📄                          │
│  Drop your resume here              │
│  or click to browse                 │
│  Supports PDF files                 │
│                                     │
│     [Analyze Resume]                │
└─────────────────────────────────────┘
```

### Results Screen
```
┌─────────────────────────────────────┐
│ 📋 Extracted Information            │
│ Experience: 5 years                 │
│ Education: Master's                 │
│ Skills: Python, SQL, AWS...         │
├─────────────────────────────────────┤
│ 🚀 Career Trajectory                │
│ 1. Data Scientist - 72.3%           │
│ 2. ML Engineer - 65.1%              │
├─────────────────────────────────────┤
│ 📊 Skill Gap Analysis               │
│ Machine Learning - HIGH             │
│ AWS - HIGH                          │
├─────────────────────────────────────┤
│ 💰 Salary: $105,000                 │
│ Range: $94,500 - $115,500           │
└─────────────────────────────────────┘
```

---

## Support

### Getting Help
1. Check this guide first
2. Review API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
3. Check project documentation: [README.md](README.md)

### Common Questions

**Q: Can I analyze multiple resumes?**
A: Yes, just upload a new resume after viewing results

**Q: How accurate are the predictions?**
A: Career prediction: ~60% top-3 accuracy, Salary: 88.69% R² score

**Q: Can I export the results?**
A: Currently no, but you can screenshot or print the page

**Q: Does it work offline?**
A: Yes, once the API server is running locally

**Q: What languages are supported?**
A: Currently English only

---

## Conclusion

The RunaGen AI web interface provides an easy way to:
- ✅ Upload and analyze your resume
- ✅ See skill gaps and career predictions
- ✅ Get salary insights
- ✅ Receive personalized recommendations

**Ready to start?**
```bash
./start_web_app.sh
```

Then upload your resume and get instant AI-powered insights!

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-01  
**Status**: ✅ Production Ready
