'use client'

import { useState, useEffect } from 'react'
import { tokenRefreshTester } from '@/utils/tokenRefreshTester'

/**
 * Token Refresh Debugger Component
 * 
 * This component provides a UI for testing token refresh functionality in development.
 * Only renders in development mode.
 */
export function TokenRefreshDebugger() {
  const [tokenInfo, setTokenInfo] = useState<any>(null)
  const [refreshLog, setRefreshLog] = useState<any[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [expirationSeconds, setExpirationSeconds] = useState(30)

  // Only render in development
  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  const updateTokenInfo = () => {
    const info = tokenRefreshTester.getTokenInfo()
    setTokenInfo(info)
  }

  const updateRefreshLog = () => {
    const log = tokenRefreshTester.getRefreshLog()
    setRefreshLog(log)
  }

  useEffect(() => {
    updateTokenInfo()
    updateRefreshLog()
    
    // Update every 5 seconds
    const interval = setInterval(() => {
      updateTokenInfo()
      updateRefreshLog()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const handleManualRefresh = async () => {
    setIsRefreshing(true)
    try {
      const result = await tokenRefreshTester.manualRefresh()
      if (result.success) {
        console.log('✅ Manual refresh successful:', result.newTokens)
        // Update localStorage with new tokens
        if (result.newTokens) {
          const currentTokens = JSON.parse(localStorage.getItem('auth_tokens') || '{}')
          const newTokens = {
            access: result.newTokens.access,
            refresh: result.newTokens.refresh || currentTokens.refresh
          }
          localStorage.setItem('auth_tokens', JSON.stringify(newTokens))
        }
      } else {
        console.error('❌ Manual refresh failed:', result.error)
      }
    } catch (error) {
      console.error('❌ Manual refresh error:', error)
    } finally {
      setIsRefreshing(false)
      updateTokenInfo()
      updateRefreshLog()
    }
  }

  const handleSimulateExpiration = () => {
    tokenRefreshTester.simulateTokenExpiration(expirationSeconds)
    updateTokenInfo()
  }

  const handleClearLog = () => {
    tokenRefreshTester.clearRefreshLog()
    updateRefreshLog()
  }

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds} seconds`
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    } else {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    }
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-300 rounded-lg shadow-lg p-4 max-w-md z-50">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800">🔐 Token Refresh Debugger</h3>
        <button
          onClick={() => window.location.reload()}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          Refresh
        </button>
      </div>

      {/* Token Information */}
      <div className="mb-4">
        <h4 className="text-xs font-medium text-gray-600 mb-2">Token Status</h4>
        {tokenInfo?.hasTokens ? (
          <div className="text-xs space-y-1">
            <div className="flex justify-between">
              <span>User:</span>
              <span className="font-mono">{tokenInfo.accessPayload?.username}</span>
            </div>
            <div className="flex justify-between">
              <span>Expires in:</span>
              <span className={`font-mono ${tokenInfo.isExpiringSoon ? 'text-red-600' : 'text-green-600'}`}>
                {formatTime(tokenInfo.timeUntilExpiry || 0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={tokenInfo.isExpiringSoon ? 'text-red-600' : 'text-green-600'}>
                {tokenInfo.isExpiringSoon ? '⚠️ Expiring Soon' : '✅ Valid'}
              </span>
            </div>
          </div>
        ) : (
          <div className="text-xs text-gray-500">No tokens found</div>
        )}
      </div>

      {/* Actions */}
      <div className="space-y-2 mb-4">
        <button
          onClick={handleManualRefresh}
          disabled={isRefreshing || !tokenInfo?.hasTokens}
          className="w-full px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {isRefreshing ? 'Refreshing...' : '🔄 Manual Refresh'}
        </button>

        <div className="flex space-x-2">
          <input
            type="number"
            value={expirationSeconds}
            onChange={(e) => setExpirationSeconds(parseInt(e.target.value) || 30)}
            className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded"
            placeholder="Seconds"
            min="1"
            max="300"
          />
          <button
            onClick={handleSimulateExpiration}
            disabled={!tokenInfo?.hasTokens}
            className="px-3 py-1 text-xs bg-orange-500 text-white rounded hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            ⏰ Simulate
          </button>
        </div>
      </div>

      {/* Refresh Log */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-xs font-medium text-gray-600">Refresh Log</h4>
          <button
            onClick={handleClearLog}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
        <div className="max-h-32 overflow-y-auto">
          {refreshLog.length === 0 ? (
            <div className="text-xs text-gray-500">No refresh attempts</div>
          ) : (
            <div className="space-y-1">
              {refreshLog.slice(-5).reverse().map((entry, index) => (
                <div key={index} className="text-xs">
                  <span className="text-gray-500">
                    {entry.timestamp.toLocaleTimeString()}
                  </span>
                  <span className={`ml-2 ${entry.success ? 'text-green-600' : 'text-red-600'}`}>
                    {entry.success ? '✅' : '❌'}
                  </span>
                  {entry.error && (
                    <div className="text-red-600 text-xs ml-4 truncate">
                      {entry.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Console Commands */}
      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 mb-1">Console Commands:</div>
        <div className="text-xs font-mono text-gray-500 space-y-1">
          <div>window.tokenRefreshTester.printTokenInfo()</div>
          <div>window.tokenRefreshTester.startMonitoring()</div>
        </div>
      </div>
    </div>
  )
}
