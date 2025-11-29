from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import boto3
from datetime import datetime
import uuid
import json
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from unstructured.staging.base import convert_to_isd
import stripe
import os

app = FastAPI(title="AI-Ready Data API", version="1.0.0")

# Initialize services
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
usage_table = dynamodb.Table(os.getenv('USAGE_TABLE', 'api-usage'))
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class ProcessRequest(BaseModel):
    output_format: str = "json"  # json, embeddings, chunks
    chunk_strategy: Optional[str] = "by_title"
    max_chunk_size: Optional[int] = 500
    include_metadata: bool = True

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key and check usage limits"""
    try:
        response = usage_table.get_item(Key={'api_key': x_api_key})
        if 'Item' not in response:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        user = response['Item']
        if user.get('usage', 0) >= user.get('limit', 1000):
            raise HTTPException(status_code=429, detail="Usage limit exceeded")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/v1/process")
async def process_document(
    file: UploadFile = File(...),
    request: ProcessRequest = Depends(),
    user: dict = Depends(verify_api_key)
):
    """Process document and return AI-ready structured data"""
    try:
        doc_id = str(uuid.uuid4())
        content = await file.read()
        
        # Save to S3
        s3_key = f"uploads/{user['user_id']}/{doc_id}/{file.filename}"
        s3_client.put_object(
            Bucket=os.getenv('BUCKET_NAME'),
            Key=s3_key,
            Body=content
        )
        
        # Process with unstructured
        with open(f"/tmp/{file.filename}", "wb") as f:
            f.write(content)
        
        elements = partition(filename=f"/tmp/{file.filename}")
        
        # Apply chunking
        if request.chunk_strategy == "by_title":
            chunks = chunk_by_title(elements, max_characters=request.max_chunk_size)
        else:
            chunks = elements
        
        # Convert to structured format
        if request.output_format == "json":
            result = convert_to_isd(chunks)
        elif request.output_format == "chunks":
            result = [{"text": str(c), "metadata": c.metadata.to_dict()} for c in chunks]
        else:
            result = [{"text": str(e)} for e in elements]
        
        # Track usage
        usage_table.update_item(
            Key={'api_key': user['api_key']},
            UpdateExpression='SET usage = usage + :inc, last_used = :time',
            ExpressionAttributeValues={':inc': 1, ':time': datetime.utcnow().isoformat()}
        )
        
        return {
            "document_id": doc_id,
            "status": "success",
            "data": result,
            "usage": {"documents_processed": 1}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/usage")
async def get_usage(user: dict = Depends(verify_api_key)):
    """Get current usage statistics"""
    return {
        "user_id": user['user_id'],
        "usage": user.get('usage', 0),
        "limit": user.get('limit', 1000),
        "plan": user.get('plan', 'free')
    }
