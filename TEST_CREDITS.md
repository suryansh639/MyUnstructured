# Testing Credit System

## Quick Test Steps

### 1. Start the Application
```bash
cd /home/ubuntu/MyUnstructured
streamlit run app.py
```

### 2. Login/Register
- Register a new account (gets 5 free credits)
- Or login with existing account

### 3. Check Initial Credits
- Look at sidebar → Should show credit count
- New users: 5 credits
- Color: Purple gradient (normal)

### 4. Process First Document
1. Upload any document (PDF, DOCX, TXT, etc.)
2. Click "🚀 Process Document"
3. Watch for:
   - Processing animation
   - Success message
   - **"💳 Credit used! Remaining credits: X"** message
   - Sidebar credit count decreases by 1

### 5. Process More Documents
- Repeat step 4 until credits reach 2 or less
- Sidebar should turn **orange** with "⚠️ Low Credits" warning

### 6. Exhaust All Credits
- Continue processing until credits = 0
- Sidebar should turn **red** with "⚠️ No Credits!" warning
- Subscribe prompt appears in sidebar

### 7. Try Processing with 0 Credits
1. Upload a document
2. Click "🚀 Process Document"
3. Should see:
   - ❌ Error: "No credits remaining!"
   - ⚠️ Warning: "Please subscribe to get more credits..."
   - 💎 Subscribe card with gradient background
   - Document should NOT process

### 8. Refresh Credits
- Click "🔄 Refresh" button in sidebar
- Credits should update from API

## Expected Behavior

| Credits | Sidebar Color | Warning | Can Process? |
|---------|--------------|---------|--------------|
| 5-3     | Purple       | None    | ✅ Yes       |
| 2-1     | Orange       | Low     | ✅ Yes       |
| 0       | Red          | None    | ❌ No        |

## API Verification

Check if credits are actually deducted in DynamoDB:

```bash
# Check user credits in DynamoDB
aws dynamodb get-item \
  --table-name docuai-prod-users \
  --key '{"user_id": {"S": "YOUR_USER_ID"}}' \
  --region us-east-1
```

## Troubleshooting

### Credits not decreasing?
- Check browser console for errors
- Verify API endpoint is accessible
- Check Lambda logs: `aws logs tail /aws/lambda/docuai-prod-process-document --follow`

### Subscribe message not showing?
- Verify credits are actually 0
- Refresh the page
- Check session state

### API errors?
- Verify JWT token is valid
- Check API Gateway logs
- Verify Lambda has proper permissions

## Success Criteria

✅ Credits decrease by 1 after each document processing
✅ Sidebar shows correct credit count
✅ Color changes based on credit level
✅ Processing blocked when credits = 0
✅ Subscribe message appears when credits = 0
✅ Refresh button updates credits from API
