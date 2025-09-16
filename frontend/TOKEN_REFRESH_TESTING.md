# Token Refresh Testing Guide

This guide provides comprehensive methods to test token refresh functionality in development.

## 🚀 Quick Start

### 1. Visual Debugger (Easiest)
- Start your development server: `npm run dev`
- Login to the application
- Look for the **Token Refresh Debugger** widget in the bottom-right corner
- Use the UI to monitor and test token refresh

### 2. Browser Console (Advanced)
- Open browser DevTools (F12)
- Use the global `window.tokenRefreshTester` object
- Run commands like `window.tokenRefreshTester.printTokenInfo()`

## 🔧 Testing Methods

### Method 1: Visual Debugger Widget

The `TokenRefreshDebugger` component provides a floating widget with:

- **Token Status**: Shows current token info, expiry time, and status
- **Manual Refresh**: Button to manually trigger token refresh
- **Simulate Expiration**: Set a token to expire in X seconds
- **Refresh Log**: History of refresh attempts
- **Console Commands**: Quick reference for console commands

#### Usage:
1. Login to the application
2. Look for the debugger widget in bottom-right corner
3. Click "Manual Refresh" to test refresh functionality
4. Use "Simulate" to create an expiring token for testing

### Method 2: Browser Console Commands

#### Basic Commands:
```javascript
// Print current token information
window.tokenRefreshTester.printTokenInfo()

// Start monitoring token refresh (logs to console every 10 seconds)
window.tokenRefreshTester.startMonitoring()

// Get detailed token information
const info = window.tokenRefreshTester.getTokenInfo()
console.log(info)
```

#### Manual Testing:
```javascript
// Manually trigger token refresh
const result = await window.tokenRefreshTester.manualRefresh()
console.log('Refresh result:', result)

// Simulate token expiration (expires in 30 seconds)
window.tokenRefreshTester.simulateTokenExpiration(30)

// Get refresh log
const log = window.tokenRefreshTester.getRefreshLog()
console.log('Refresh log:', log)

// Clear refresh log
window.tokenRefreshTester.clearRefreshLog()
```

### Method 3: Automated Testing

#### Test Token Refresh Flow:
```javascript
// 1. Login and get initial tokens
// 2. Simulate token expiration
window.tokenRefreshTester.simulateTokenExpiration(10) // Expires in 10 seconds

// 3. Wait for automatic refresh (TokenRefreshManager should handle this)
// 4. Or manually trigger refresh
const result = await window.tokenRefreshTester.manualRefresh()

// 5. Verify new tokens are stored
const newInfo = window.tokenRefreshTester.getTokenInfo()
console.log('New token info:', newInfo)
```

#### Test Error Scenarios:
```javascript
// 1. Set invalid refresh token
const tokens = JSON.parse(localStorage.getItem('auth_tokens'))
tokens.refresh = 'invalid-token'
localStorage.setItem('auth_tokens', JSON.stringify(tokens))

// 2. Try to refresh
const result = await window.tokenRefreshTester.manualRefresh()
console.log('Should fail:', result.success === false)

// 3. Verify user is logged out
// (AuthContext should clear tokens and redirect to login)
```

## 🧪 Test Scenarios

### Scenario 1: Normal Token Refresh
1. Login to the application
2. Wait for token to be close to expiry (or simulate)
3. Verify automatic refresh happens
4. Check that new tokens are stored
5. Verify user remains logged in

### Scenario 2: Manual Token Refresh
1. Login to the application
2. Use debugger widget or console to manually refresh
3. Verify refresh succeeds
4. Check that new tokens are stored

### Scenario 3: Token Refresh Failure
1. Login to the application
2. Manually corrupt the refresh token
3. Wait for automatic refresh attempt
4. Verify user is logged out and redirected to login

### Scenario 4: Network Error During Refresh
1. Login to the application
2. Disconnect from internet
3. Wait for token to expire
4. Verify graceful error handling
5. Reconnect and verify user can login again

### Scenario 5: Token Refresh Race Conditions
1. Login to the application
2. Simulate multiple rapid refresh attempts
3. Verify no duplicate requests
4. Check that only one refresh happens

## 🔍 Monitoring and Debugging

### Console Monitoring:
```javascript
// Start continuous monitoring
window.tokenRefreshTester.startMonitoring()

// This will log to console every 10 seconds:
// - Token expiry time
// - Whether token is expiring soon
// - Warnings when token is close to expiry
```

### Network Tab Monitoring:
1. Open DevTools → Network tab
2. Filter by "refresh" or the API endpoint
3. Monitor refresh requests and responses
4. Check for duplicate requests or errors

### LocalStorage Monitoring:
```javascript
// Monitor localStorage changes
const originalSetItem = localStorage.setItem
localStorage.setItem = function(key, value) {
  if (key === 'auth_tokens') {
    console.log('🔐 Tokens updated:', JSON.parse(value))
  }
  return originalSetItem.apply(this, arguments)
}
```

## 🐛 Common Issues and Solutions

### Issue: Token Refresh Not Happening
**Symptoms**: User gets logged out unexpectedly
**Debug Steps**:
1. Check if TokenRefreshManager is running: `window.tokenRefreshTester.printTokenInfo()`
2. Verify token expiry time
3. Check network requests for refresh calls
4. Look for JavaScript errors in console

### Issue: Multiple Refresh Requests
**Symptoms**: Multiple refresh API calls in network tab
**Debug Steps**:
1. Check refresh log: `window.tokenRefreshTester.getRefreshLog()`
2. Verify TokenRefreshManager cleanup
3. Check for component re-mounts

### Issue: Refresh Fails but User Stays Logged In
**Symptoms**: Network errors but no logout
**Debug Steps**:
1. Test manual refresh: `window.tokenRefreshTester.manualRefresh()`
2. Check error handling in AuthContext
3. Verify clearAuthData() is called on failure

## 📊 Performance Testing

### Test Refresh Frequency:
```javascript
// Monitor refresh frequency
let refreshCount = 0
const originalRefresh = window.tokenRefreshTester.manualRefresh
window.tokenRefreshTester.manualRefresh = async function() {
  refreshCount++
  console.log(`Refresh attempt #${refreshCount}`)
  return originalRefresh.apply(this, arguments)
}
```

### Test Memory Leaks:
1. Login and logout multiple times
2. Check for interval cleanup
3. Monitor memory usage in DevTools
4. Verify no lingering event listeners

## 🚨 Production Considerations

### Before Deploying:
1. Remove or disable debug components
2. Verify token refresh works without debug tools
3. Test with real token expiry times
4. Monitor refresh success rates

### Production Monitoring:
- Set up logging for refresh failures
- Monitor token refresh frequency
- Track user logout rates
- Set up alerts for refresh errors

## 📝 Testing Checklist

- [ ] Login works correctly
- [ ] Token refresh happens automatically
- [ ] Manual refresh works
- [ ] Refresh failure logs out user
- [ ] No duplicate refresh requests
- [ ] Proper error handling
- [ ] Memory cleanup on logout
- [ ] Works with network interruptions
- [ ] Handles corrupted tokens gracefully
- [ ] Performance is acceptable

## 🔗 Related Files

- `src/utils/tokenRefreshTester.ts` - Testing utilities
- `src/components/dev/TokenRefreshDebugger.tsx` - Visual debugger
- `src/contexts/AuthContext.tsx` - Main auth logic
- `src/components/auth/TokenRefreshManager.tsx` - Automatic refresh manager
