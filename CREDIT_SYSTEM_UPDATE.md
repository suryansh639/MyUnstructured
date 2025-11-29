# Credit System Update

## Changes Made

### 1. Credit Deduction on Document Processing (app.py)

**Before:** Documents were processed locally without calling the API, so credits were never deducted.

**After:** 
- Added credit check before processing
- Integrated API call to deduct credits when processing documents
- Shows remaining credits after each processing
- Blocks processing when credits reach 0

**Key Changes:**
```python
# Check credits before processing
current_credits = st.session_state.get('credits', 0)

if current_credits <= 0:
    # Show error and subscribe message
    st.error("❌ No credits remaining!")
    st.warning("🔔 Please subscribe to get more credits...")
else:
    # Process document
    elements = process_document(uploaded_file, processing_options)
    
    # Deduct credit via API
    api_result, api_error = process_document_with_credit(token, file_content, filename)
    
    # Update credits in session
    if api_result and 'credits_remaining' in api_result:
        st.session_state.credits = api_result['credits_remaining']
        st.info(f"💳 Credit used! Remaining credits: {api_result['credits_remaining']}")
```

### 2. Enhanced User Profile Sidebar (auth.py)

**Added:**
- Color-coded credit display based on credit level:
  - Red gradient: 0 credits (no credits)
  - Orange gradient: 1-2 credits (low credits warning)
  - Purple gradient: 3+ credits (normal)
- Warning messages for low/no credits
- Subscribe prompt when credits reach 0

**Visual Indicators:**
- ⚠️ No Credits! - Red background
- ⚠️ Low Credits - Orange background
- Normal display - Purple background

### 3. Subscribe Message

When credits reach 0, users see:
- Error message on process button click
- Subscribe prompt in sidebar
- Attractive gradient card with call-to-action

## User Flow

1. **User logs in** → Credits displayed in sidebar
2. **User uploads document** → File info shown
3. **User clicks "Process Document"**:
   - If credits > 0: Document processes, credit deducted, remaining credits shown
   - If credits = 0: Error shown, subscribe message displayed
4. **Credits update** → Sidebar shows current credit count with color coding
5. **No credits** → User prompted to subscribe

## Testing

To test the credit system:

```bash
# 1. Start the app
streamlit run app.py

# 2. Login with test account
# 3. Check credits in sidebar
# 4. Upload and process a document
# 5. Verify credit decreases by 1
# 6. Repeat until credits reach 0
# 7. Try processing - should show subscribe message
```

## API Integration

The system now properly integrates with:
- `POST /v1/process` - Processes document and deducts credit
- Returns `credits_remaining` in response
- Updates session state with new credit count

## Benefits

✅ Credits properly deducted on each document processing
✅ Real-time credit tracking
✅ Clear visual feedback to users
✅ Prevents processing when credits exhausted
✅ Encourages subscription when credits run out
✅ Color-coded warnings for low credits
