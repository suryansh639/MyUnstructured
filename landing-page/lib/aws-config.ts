// AWS Configuration - Update these after Terraform deployment
export const awsConfig = {
  region: process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1',
  userPoolId: process.env.NEXT_PUBLIC_USER_POOL_ID || '',
  userPoolClientId: process.env.NEXT_PUBLIC_USER_POOL_CLIENT_ID || '',
  apiEndpoint: process.env.NEXT_PUBLIC_API_ENDPOINT || '',
}

export const API_ENDPOINTS = {
  register: `${awsConfig.apiEndpoint}/v1/register`,
  process: `${awsConfig.apiEndpoint}/v1/process`,
  credits: `${awsConfig.apiEndpoint}/v1/credits`,
}
