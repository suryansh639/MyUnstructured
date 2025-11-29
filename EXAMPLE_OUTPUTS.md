# 🎯 Example Outputs - Semantic Structured Data

## ✅ What You NOW Get (LLM-Powered Extraction)

### Example 1: Resume/CV

**Input:** PDF resume

**Output:**
```json
{
  "status": "success",
  "credits_remaining": 99,
  "data": {
    "document_id": "abc-123",
    "filename": "resume.pdf",
    "file_type": "pdf",
    "processing_method": "llm_semantic_extraction",
    "structured_data": {
      "document_type": "resume",
      "personal_info": {
        "name": "Suryansh Gupta",
        "email": "suryanshg.jiit@gmail.com",
        "phone": "+91 7668080592",
        "location": "India"
      },
      "professional_summary": "DevOps and Cloud Engineer with expertise in AWS, Azure, Docker, Kubernetes...",
      "skills": {
        "cloud_platforms": ["AWS", "Azure", "GCP"],
        "containers": ["Docker", "Kubernetes"],
        "iac": ["Terraform", "CloudFormation"],
        "ci_cd": ["Jenkins", "GitLab CI", "GitHub Actions"],
        "programming": ["Python", "Bash", "Go"],
        "databases": ["PostgreSQL", "MongoDB", "Redis"]
      },
      "experience": [
        {
          "company": "TCS",
          "role": "DevOps & Data Engineer",
          "duration": "2022 - Present",
          "achievements": [
            "Reduced deployment time by 60%",
            "Implemented CI/CD pipelines",
            "Managed AWS infrastructure"
          ]
        }
      ],
      "education": [
        {
          "degree": "B.Tech Computer Science",
          "institution": "JIIT",
          "year": "2022"
        }
      ],
      "certifications": [
        "AWS Solutions Architect",
        "Kubernetes Administrator"
      ]
    },
    "metadata": {
      "processed_at": "2025-11-29T17:50:00",
      "model_used": "claude-3-haiku",
      "s3_location": "uploads/user-id/doc-id/resume.pdf"
    }
  }
}
```

### Example 2: Business Contract

**Input:** PDF contract

**Output:**
```json
{
  "structured_data": {
    "document_type": "business_contract",
    "parties": [
      {
        "name": "ABC Corp",
        "role": "Service Provider",
        "address": "123 Main St"
      },
      {
        "name": "XYZ Inc",
        "role": "Client",
        "address": "456 Oak Ave"
      }
    ],
    "contract_details": {
      "effective_date": "2025-01-01",
      "expiration_date": "2026-01-01",
      "value": "$50,000",
      "payment_terms": "Net 30 days"
    },
    "key_terms": [
      "Service Level Agreement: 99.9% uptime",
      "Confidentiality clause included",
      "Termination: 30 days notice"
    ],
    "obligations": {
      "provider": [
        "Deliver services as specified",
        "Maintain confidentiality"
      ],
      "client": [
        "Pay invoices on time",
        "Provide necessary access"
      ]
    }
  }
}
```

### Example 3: Research Paper

**Input:** PDF research paper

**Output:**
```json
{
  "structured_data": {
    "document_type": "research_paper",
    "title": "Machine Learning for Document Classification",
    "authors": [
      "Dr. John Smith",
      "Dr. Jane Doe"
    ],
    "abstract": "This paper presents a novel approach to document classification using transformer models...",
    "keywords": ["machine learning", "NLP", "transformers", "classification"],
    "methodology": {
      "approach": "Supervised learning with BERT",
      "dataset": "10,000 labeled documents",
      "metrics": ["Accuracy", "F1-Score", "Precision", "Recall"]
    },
    "key_findings": [
      "Achieved 95% accuracy on test set",
      "Outperformed baseline by 12%",
      "Model generalizes well to unseen data"
    ],
    "conclusions": "The proposed method demonstrates significant improvements...",
    "references_count": 45
  }
}
```

### Example 4: Invoice

**Input:** PDF invoice

**Output:**
```json
{
  "structured_data": {
    "document_type": "invoice",
    "invoice_number": "INV-2025-001",
    "date": "2025-11-29",
    "due_date": "2025-12-29",
    "vendor": {
      "name": "Tech Solutions Inc",
      "address": "789 Tech Blvd",
      "tax_id": "12-3456789"
    },
    "customer": {
      "name": "Client Corp",
      "address": "321 Business St"
    },
    "line_items": [
      {
        "description": "Cloud Services",
        "quantity": 1,
        "unit_price": 5000,
        "total": 5000
      },
      {
        "description": "Support Hours",
        "quantity": 20,
        "unit_price": 150,
        "total": 3000
      }
    ],
    "subtotal": 8000,
    "tax": 800,
    "total": 8800,
    "payment_terms": "Net 30"
  }
}
```

## 🆚 Comparison

### Before (Raw Text Extraction):
```json
{
  "pages": [
    {"page": 1, "text": "Suryansh Gupta suryanshg.jiit@gmail.com +91 7668080592..."}
  ],
  "chunks": [
    {"chunk_id": 1, "text": "Suryansh Gupta suryanshg.jiit@gmail.com..."}
  ]
}
```

### After (LLM Semantic Extraction):
```json
{
  "structured_data": {
    "personal_info": {
      "name": "Suryansh Gupta",
      "email": "suryanshg.jiit@gmail.com",
      "phone": "+91 7668080592"
    },
    "skills": {
      "cloud": ["AWS", "Azure"],
      "containers": ["Docker", "Kubernetes"]
    }
  }
}
```

## 🎯 Key Differences

| Feature | Before | After (LLM) |
|---------|--------|-------------|
| **Understanding** | ❌ No semantic understanding | ✅ Understands meaning |
| **Structure** | Raw text blocks | Categorized fields |
| **Usability** | Need post-processing | Ready to use |
| **Intelligence** | Rule-based | AI-powered |
| **Output** | Generic | Domain-specific |

## 🚀 How to Use

1. **Upload any document** (PDF, TXT)
2. **Click "Process Document"**
3. **Get intelligent structured data** based on document type
4. **Use directly** in your application

The system automatically detects document type and extracts relevant structured information!

## 💰 Cost

- **1 credit per document**
- Uses AWS Bedrock Claude 3 Haiku (~$0.00025 per request)
- Total cost: ~$0.001 per document processed

---

**Your API now produces LlamaIndex-quality structured data!** 🎉
