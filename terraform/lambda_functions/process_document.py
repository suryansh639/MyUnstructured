import json
import boto3
import os
import base64
import uuid
from datetime import datetime
import PyPDF2
import io

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

USERS_TABLE = os.environ['USERS_TABLE']
USAGE_TABLE = os.environ['USAGE_TABLE']
DOCUMENTS_TABLE = os.environ['DOCUMENTS_TABLE']
BUCKET_NAME = os.environ['BUCKET_NAME']

users_table = dynamodb.Table(USERS_TABLE)
usage_table = dynamodb.Table(USAGE_TABLE)
documents_table = dynamodb.Table(DOCUMENTS_TABLE)

def extract_text_from_pdf(file_content):
    """Extract text from PDF"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        all_text = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            all_text.append(text.strip())
        
        return '\n\n'.join(all_text)
    except Exception as e:
        return f'Error extracting PDF: {str(e)}'

def extract_text_from_txt(file_content):
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8')
    except:
        return 'Error reading text file'

def extract_structured_data_with_llm(text, filename):
    """Use AWS Bedrock Claude to extract meaningful structured data"""
    
    # Determine document type from content
    prompt = f"""Analyze this document and extract structured, meaningful data.

Document filename: {filename}

Document content:
{text[:4000]}

Based on the content, intelligently extract relevant structured information. 

If it's a RESUME/CV, extract:
- Personal info (name, email, phone, location)
- Professional summary
- Skills (categorized: technical, soft, languages, tools, cloud, etc.)
- Work experience (company, role, duration, achievements)
- Education (degree, institution, year)
- Certifications
- Projects

If it's a BUSINESS DOCUMENT, extract:
- Document type
- Key entities (people, companies, dates)
- Main topics/themes
- Action items
- Important numbers/metrics

If it's a RESEARCH PAPER, extract:
- Title, authors, abstract
- Key findings
- Methodology
- Conclusions

If it's OTHER, extract:
- Document type
- Main topics
- Key information
- Entities mentioned

Return ONLY valid JSON with the extracted structured data. Be intelligent about categorization."""

    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        llm_output = response_body['content'][0]['text']
        
        # Extract JSON from response
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            structured_data = json.loads(llm_output[json_start:json_end])
            return structured_data
        else:
            return {"raw_text": text[:1000], "note": "Could not extract structured data"}
            
    except Exception as e:
        print(f"LLM extraction error: {str(e)}")
        return {"error": str(e), "raw_text": text[:1000]}

def handler(event, context):
    try:
        # Get user from JWT
        claims = event['requestContext']['authorizer']['jwt']['claims']
        user_id = claims['sub']
        
        # Check credits
        user_response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' not in user_response:
            return {'statusCode': 404, 'body': json.dumps({'error': 'User not found'})}
        
        user = user_response['Item']
        credits = int(user.get('credits', 0))
        
        if credits <= 0:
            return {'statusCode': 429, 'body': json.dumps({'error': 'Insufficient credits'})}
        
        # Parse request
        body = json.loads(event.get('body', '{}'))
        file_content = base64.b64decode(body['file'])
        filename = body.get('filename', 'document.pdf')
        
        # Generate IDs
        doc_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Save to S3
        s3_key = f"uploads/{user_id}/{doc_id}/{filename}"
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_content)
        
        # Extract text based on file type
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            raw_text = extract_text_from_pdf(file_content)
        elif file_ext in ['txt', 'text']:
            raw_text = extract_text_from_txt(file_content)
        else:
            raw_text = 'Unsupported file type'
        
        # Use LLM to extract meaningful structured data
        structured_data = extract_structured_data_with_llm(raw_text, filename)
        
        # Build final output
        result = {
            'document_id': doc_id,
            'filename': filename,
            'file_type': file_ext,
            'processing_method': 'llm_semantic_extraction',
            'structured_data': structured_data,
            'metadata': {
                'processed_at': timestamp,
                'file_size_bytes': len(file_content),
                's3_location': s3_key,
                'text_length': len(raw_text),
                'model_used': 'claude-3-haiku'
            }
        }
        
        # Save document metadata
        documents_table.put_item(Item={
            'document_id': doc_id,
            'user_id': user_id,
            'filename': filename,
            's3_key': s3_key,
            'status': 'completed',
            'created_at': timestamp
        })
        
        # Track usage
        usage_table.put_item(Item={
            'user_id': user_id,
            'timestamp': timestamp,
            'document_id': doc_id,
            'credits_used': 1
        })
        
        # Deduct credits
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET credits = credits - :dec',
            ExpressionAttributeValues={':dec': 1}
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'status': 'success',
                'credits_remaining': credits - 1,
                'data': result
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
