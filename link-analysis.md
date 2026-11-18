
# Python Practical Test – AI-Powered Website Link Analysis API

| Details | Information |
|---|---|
| **Technology** | Python 3.x, FastAPI |
| **AI Integration** | OpenAI / Gemini / Anthropic / Other LLM |
| **Duration** | Maximum 2 Hours |
| **Difficulty** | Intermediate |
| **Submission** | Public GitHub Repository |

## 1. Objective

Develop a Python application using FastAPI that analyzes a given website URL, understands its content using an LLM, and generates meaningful business, competitor, SEO, search query, and target audience insights.

The application should extract website information, process the content using an LLM, and return structured analysis in five main sections.

Additionally, applicants must research and recommend the most suitable LLM platform or model based on accuracy, response speed, and API cost.

Applicants are expected to understand the problem, select suitable technologies, and implement the solution independently.

## 2. API Requirement

Create one REST API endpoint:

**Endpoint:**

```http
POST http://localhost:4000/link-analysis
```

### Request Body

```json
{
  "url": "https://example.com"
}
```

### Input Requirements

- Accept a valid website URL.
- Fetch and understand the website content.
- Extract relevant business and brand information.
- Use an LLM to analyze the extracted content.
- Generate structured results in JSON format.
- Handle inaccessible websites and invalid URLs gracefully.

## 3. Functional Requirements

The API must generate the following five sections.

### Section 1: Competitor vs Your Brand Details

Understand the submitted website and identify relevant competitors.

Compare the submitted brand with its competitors.

**Expected Information:**

- Your brand name.
- Business overview.
- Main business category.
- Main products and services.
- Identified competitors (minimum 3 where reliable information is available).
- Competitor strengths.
- Competitor weaknesses or gaps.
- Your brand's competitive advantages.
- Opportunities to improve market positioning.

**Example:**

| Comparison | Your Brand | Competitor |
|---|---|---|
| Brand Name | ABC Technologies | XYZ Technologies |
| Main Service | Web Development | Web Development |
| Target Market | Small Businesses | Enterprise |
| Key Strength | Affordable Solutions | Established Brand |
| Opportunity | Improve Online Visibility | Improve Customer Engagement |

### Section 2: Top 5 Target Search Queries

Identify five relevant search queries that potential customers might use to find the business.

The queries should be relevant to the website's services, business category, and target audience.

Support the following platforms:

1. Google Search
2. Facebook
3. Instagram
4. LinkedIn
5. X (Twitter)

**Expected Information:**

- Search query.
- Relevant platform.
- Search intent.
- Business relevance.
- Target audience.

**Example:**

| Search Query | Platform | Search Intent |
|---|---|---|
| Best web development company | Google | Service Search |
| Website development services | Facebook | Business Discovery |
| Website design ideas | Instagram | Inspiration |
| Web development company for startups | LinkedIn | B2B Search |
| Affordable web development services | X | Service Discovery |

Generate five relevant queries and indicate the platforms where each query is suitable.

**Note:** Platform-specific search volume or ranking data should only be reported when supported by actual data sources or APIs. Do not invent search volumes.

### Section 3: SEO Improvement

Analyze the website content and suggest practical SEO improvements.

**A. Keyword Recommendations**

- Primary keyword.
- Secondary keywords.
- Long-tail keywords.
- Relevant business keywords.

**B. SEO Title**

- Recommended SEO title.
- Relevant primary keyword.
- Improved title structure.

**C. Meta Description**

- Recommended meta description.
- Short, human-friendly business summary.
- Relevant keywords.

**D. Additional Support Content**

Suggest additional website content that can improve search visibility.

Examples:

- Service landing pages.
- Industry-specific pages.
- Frequently Asked Questions.
- Blog topics.
- Location-based landing pages.
- Supporting business articles.

### Section 4: Top 5 Services

Understand the website and identify its five most important services.

**Expected Information:**

| Field | Description |
|---|---|
| Service Name | Name of the service |
| Description | Short service explanation |
| Target Industry | Relevant business industry |
| Target Customer | Potential customer type |
| Main Benefit | Why customers need this service |

Services must be identified from actual website content wherever possible. Clearly label any inferred recommendations.

### Section 5: Target Audience Identification

Identify the most relevant target audience based on the website content, products, services, and business category.

**Expected Information:**

- Primary target audience.
- Secondary target audience.
- Industry segments.
- Business types.
- Customer profiles.
- Location or geographical focus, if available.
- Customer needs and challenges.
- Potential customer interests.
- Recommended audience segments for marketing.

**Example:**

| Audience | Business Type | Requirement |
|---|---|---|
| Audience 1 | Small Businesses | Website Development |
| Audience 2 | Startups | Digital Solutions |
| Audience 3 | Enterprise Companies | Custom Software |
| Audience 4 | Retail Businesses | E-commerce Solutions |
| Audience 5 | Professional Services | Online Presence |

## 4. Expected API Response

Return all five website analysis sections in a structured JSON response.

### Example Response

```json
{
  "success": true,
  "website": "https://example.com",
  "brand": {
    "name": "ABC Technologies",
    "category": "Technology Services",
    "summary": "A technology company providing digital solutions."
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "Your brand overview",
      "competitors": [],
      "strengths": [],
      "opportunities": []
    },
    "target_search_queries": [
      {
        "query": "Best technology services company",
        "platforms": [
          "Google",
          "LinkedIn"
        ],
        "intent": "Service Discovery"
      }
    ],
    "seo_improvements": {
      "primary_keyword": "Technology Services",
      "secondary_keywords": [],
      "recommended_title": "Recommended SEO Title",
      "meta_description": "Recommended SEO description",
      "supporting_content": []
    },
    "top_services": [],
    "target_audience": {
      "primary_audience": [],
      "secondary_audience": [],
      "industries": [],
      "customer_needs": []
    }
  }
}
```

*This is an illustrative response structure. Your implementation should return meaningful analysis based on the submitted website.*

## 5. Technical Requirements

Use the following technologies:

- Python 3.x
- FastAPI
- Uvicorn
- Pydantic
- HTTPX or Requests
- BeautifulSoup or equivalent HTML parser
- OpenAI, Gemini, Anthropic, or another LLM API
- Environment variables for API credentials

### Suggested Processing Flow

1. Receive website URL.
2. Validate the URL.
3. Fetch website HTML content.
4. Extract relevant website content.
5. Clean and structure extracted information.
6. Send relevant content to the LLM.
7. Generate all five analysis sections.
8. Validate the LLM response.
9. Return structured JSON through FastAPI.

### Local Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

### API Documentation

http://localhost:4000/docs

## 6. LLM Platform & Model Research – Cost, Speed and Accuracy

Identify and recommend the best LLM platform or model for this website link analysis application.

The objective is to achieve:

- Maximum accuracy.
- Fast response time.
- Minimum API cost.
- Reliable structured JSON output.
- Efficient processing of website content.

Applicants should independently research and compare available LLM providers and models.

### A. LLM Platform Comparison

Research and compare at least 3 LLM models or providers.

Examples:

- OpenAI
- Google Gemini
- Anthropic Claude
- Other suitable LLM providers

Compare the following:

| Criteria | Description |
|---|---|
| Provider | LLM platform/provider |
| Model Name | Recommended model |
| API Cost | Input and output token pricing |
| Response Speed | Expected or measured response time |
| Accuracy | Quality of website content understanding |
| Context Window | Maximum supported input context |
| JSON Support | Ability to generate structured JSON |
| Recommendation | Suitability for this application |

### B. Best Model Selection

Recommend the most suitable model based on:

1. Accuracy in understanding website content.
2. Fast response time.
3. Low API cost.
4. Reliable structured JSON generation.
5. Ability to generate relevant competitor and SEO insights.
6. Ability to process large website content efficiently.

### C. Cost Optimization

Suggest ways to reduce LLM API costs without compromising output quality.

Consider:

- Cleaning website content before sending it to the LLM.
- Removing unnecessary HTML and duplicate content.
- Optimizing prompt length.
- Selecting the appropriate model for each task.
- Using smaller models for simple extraction tasks.
- Avoiding unnecessary repeated API calls.
- Caching previously analyzed website content where appropriate.
- Optimizing token usage.

### D. Final LLM Recommendation

Provide the following information:

- Recommended LLM provider.
- Recommended model name.
- Estimated input token usage.
- Estimated output token usage.
- Estimated API cost per website analysis.
- Expected response time.
- Reason for selecting the model.
- Alternative model for fallback.
- Recommended approach for balancing accuracy, speed, and cost.

**Expected Result:** A practical recommendation for selecting an LLM that can support production-level website analysis efficiently.

**Important:** Use current provider pricing and model documentation wherever possible. Clearly distinguish measured response times and benchmarked accuracy from estimates. Do not claim maximum accuracy without testing.

## 7. Suggested Project Structure

```text
ai-link-analysis/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── services/
│   │   ├── website_extractor.py
│   │   ├── llm_service.py
│   │   ├── analysis_service.py
│   │   └── competitor_service.py
│   │
│   └── utils/
│       └── validators.py
│
├── tests/
│   └── test_link_analysis.py
│
├── .env.example
├── requirements.txt
└── README.md
```

## 8. Evaluation Criteria

| Criteria | Marks |
|---|---:|
| FastAPI implementation and API structure | 10 |
| Website extraction and content understanding | 15 |
| LLM integration and structured output | 15 |
| Competitor and search query analysis | 15 |
| SEO recommendations and keyword intelligence | 10 |
| Services and target audience identification | 10 |
| LLM model research and cost optimization | 15 |
| Error handling, code quality and documentation | 10 |
| **Total** | **100** |

## 9. Important Instructions

- Use actual website content for analysis.
- Do not generate generic results unrelated to the submitted website.
- Use an LLM to understand and analyze the extracted content.
- Competitor information should be based on credible research or clearly marked as an AI-generated suggestion.
- Do not invent Google or social media search volumes.
- Handle website access restrictions and API failures gracefully.
- Protect API keys and credentials.
- Validate website URLs and prevent access to private or internal network addresses (SSRF protection).
- Return valid, structured JSON responses.
- Use actual provider pricing for LLM cost comparisons.
- Clearly explain the reason for selecting the recommended LLM model.
- Distinguish actual benchmark results from estimated performance.

## 10. Submission Instructions

Once you complete the practical test:

1. Upload your complete Python source code to GitHub.
2. Make your GitHub repository **Public**.
3. Include a README.md with setup and execution instructions.
4. Include sample API requests and responses.
5. Add screenshots or logs demonstrating your implementation.
6. Include your LLM comparison and final model recommendation in the README.
7. Ensure no API keys, passwords, or private credentials are committed.

**Duration: Maximum 2 Hours.**

**Submission Deadline: 27nd November 2026.**

## 11. Application Verification & Deployment

As part of our recruitment process, following our official company social media accounts and sharing your profile links are mandatory verification steps.

**1. Follow Dxora Technologies on LinkedIn**

https://www.linkedin.com/company/dxora-technologies

**2. Follow CREST on Instagram**

https://www.instagram.com/crestspot/

### 3. Deploy Your Practical Test Application

- Deploy your completed FastAPI application on a publicly accessible server.
- Ensure the API is running and accessible.
- Provide a **Live Demo URL** for the deployed application.
- Share the API documentation link (`/docs`) for testing and validation.
- Ensure the API endpoint is working and returns the expected structured JSON response.

**Example:**

| Requirement | Example |
|---|---|
| Live Demo | `https://your-domain.com` |
| API Endpoint | `https://your-domain.com/link-analysis` |
| API Documentation | `https://your-domain.com/docs` |


**Important:** Please make sure to share your LinkedIn and Instagram profile links while submitting your application for verification.

## 12. Final Submission – Email Instructions

After completing the practical test, send an email to:

**To:** hr@chivoxai.com

**Subject:** Your Name - Python Practical Link Analysis test review

### Email Body

Please include:

1. Your Full Name.
2. Demo Link
3. Public GitHub Repository Link.
4. Contact Number.
5. Current Location.
6. Preferred Date and Time for Final Discussion.

## 13. Final Round – Dxora Panel Interview

Our technical team will review your GitHub repository and evaluate your implementation.

Shortlisted applicants will be contacted for the final technical discussion with the **Dxora Panel**.

We will evaluate:

- Python programming skills.
- FastAPI and REST API development.
- Website content extraction.
- LLM integration and prompt engineering.
- Competitor and SEO intelligence.
- LLM model selection and cost optimization.
- Problem-solving and code quality.

---

**All the best! We look forward to reviewing your work.**
