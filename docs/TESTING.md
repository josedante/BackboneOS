# Testing Infrastructure - BackboneOS

## Overview

The BackboneOS project uses a modern, comprehensive testing infrastructure to ensure code quality and prevent regressions. This document outlines the testing setup, best practices, and maintenance guidelines.

## Testing Stack

### Frontend Testing

**Core Testing Framework**:
- **Vitest**: Modern, fast test runner (replaces Jest)
- **@testing-library/react**: React component testing utilities
- **@testing-library/jest-dom**: Custom matchers for DOM testing
- **@testing-library/user-event**: User interaction simulation
- **jsdom**: DOM environment for testing

**Why Vitest over Jest?**:
- ✅ **Faster**: Up to 10x faster than Jest
- ✅ **Modern**: Native ES modules support
- ✅ **TypeScript**: First-class TypeScript support
- ✅ **Vite Integration**: Seamless integration with Vite
- ✅ **Active Development**: Actively maintained and updated
- ✅ **No Deprecated Dependencies**: Uses modern, non-deprecated packages

### Backend Testing

**Core Testing Framework**:
- **pytest**: Python testing framework
- **Django TestCase**: Django-specific testing utilities
- **Factory Boy**: Test data generation
- **Coverage.py**: Code coverage analysis

## Configuration Files

### Frontend Configuration

**vitest.config.ts**:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**vitest.setup.ts**:
- Global test setup and mocks
- Next.js router mocking
- Sonner toast mocking
- localStorage mocking
- fetch API mocking

### Backend Configuration

**pytest.ini**:
- Test discovery patterns
- Coverage configuration
- Test output formatting

## Test Structure

### Frontend Test Organization

```
frontend/src/
├── __tests__/
│   ├── auth/                    # Authentication tests
│   │   └── AuthContext.test.tsx
│   ├── api/                     # API tests
│   │   └── interceptors.test.ts
│   ├── components/              # Component tests
│   │   ├── auth/
│   │   │   └── TokenRefreshManager.test.tsx
│   │   ├── ui/                  # UI component tests
│   │   └── layout/              # Layout component tests
│   ├── hooks/                   # Custom hook tests
│   └── utils/                   # Utility function tests
```

### Backend Test Organization

```
backend/
├── users/tests.py               # User app tests
├── products/tests.py            # Product app tests
├── entities/tests.py            # Entity app tests
├── world/tests.py               # World app tests
├── interactions/tests.py        # Interaction app tests
├── offers/tests.py              # Offer app tests
├── campaigns/tests.py           # Campaign app tests
└── test_*.py                    # Integration tests
```

## Running Tests

### Frontend Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI interface
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test AuthContext.test.tsx

# Run tests matching pattern
npm test -- --grep "authentication"
```

### Backend Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users

# Run specific test class
python manage.py test users.tests.UserModelTest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Test Categories

### 1. Unit Tests
- **Purpose**: Test individual functions, components, or methods
- **Scope**: Isolated functionality
- **Examples**: 
  - AuthContext login/logout functions
  - Token refresh logic
  - Utility functions

### 2. Integration Tests
- **Purpose**: Test interaction between multiple components
- **Scope**: Component integration, API integration
- **Examples**:
  - API interceptors with token refresh
  - Protected routes with authentication
  - Database model relationships

### 3. Component Tests
- **Purpose**: Test React components in isolation
- **Scope**: Component behavior, user interactions
- **Examples**:
  - Login form submission
  - Token refresh manager
  - Error boundary handling

### 4. End-to-End Tests (Planned)
- **Purpose**: Test complete user workflows
- **Scope**: Full application flow
- **Examples**:
  - Complete authentication flow
  - Product management workflow
  - User registration process

## Mocking Strategy

### Frontend Mocking

**Global Mocks** (vitest.setup.ts):
- `next/navigation`: Router and navigation
- `sonner`: Toast notifications
- `localStorage`: Browser storage
- `fetch`: HTTP requests
- `window.location`: Browser location

**Component-Specific Mocks**:
- API clients
- External services
- Complex dependencies

### Backend Mocking

**Django TestCase**:
- Database transactions
- User authentication
- File uploads
- External API calls

**Factory Boy**:
- Test data generation
- Model instances
- Related objects

## Test Data Management

### Frontend Test Data
- **Mock Data**: Static test data in test files
- **Fixtures**: Reusable test data sets
- **Factories**: Dynamic test data generation

### Backend Test Data
- **Fixtures**: JSON files with test data
- **Factory Boy**: Dynamic model instance creation
- **Database Seeding**: Initial test data setup

## Coverage Requirements

### Frontend Coverage
- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical Paths**: 100% coverage for authentication

### Backend Coverage
- **Minimum**: 85% line coverage
- **Target**: 95% line coverage
- **Critical Paths**: 100% coverage for security features

## Best Practices

### Writing Tests

1. **Arrange-Act-Assert Pattern**:
   ```typescript
   it('should login user successfully', async () => {
     // Arrange
     const mockUser = { username: 'test', password: 'password' }
     mockApi.login.mockResolvedValue({ success: true })
     
     // Act
     const result = await login(mockUser)
     
     // Assert
     expect(result.success).toBe(true)
   })
   ```

2. **Descriptive Test Names**:
   - Use "should" statements
   - Describe the expected behavior
   - Include context when relevant

3. **Test Isolation**:
   - Each test should be independent
   - Clean up after each test
   - Use beforeEach/afterEach appropriately

4. **Mock External Dependencies**:
   - Mock API calls
   - Mock browser APIs
   - Mock third-party libraries

### Test Maintenance

1. **Keep Tests Updated**:
   - Update tests when code changes
   - Remove obsolete tests
   - Refactor tests for clarity

2. **Monitor Test Performance**:
   - Keep test execution time low
   - Optimize slow tests
   - Use parallel execution

3. **Review Test Coverage**:
   - Regular coverage reports
   - Identify untested code paths
   - Prioritize critical path coverage

## Continuous Integration

### GitHub Actions (Planned)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test
      - run: npm run test:coverage
  
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v3
      - run: pip install -r requirements.txt
      - run: python manage.py test
      - run: coverage report
```

## Current Status & Known Issues

### ✅ Working Components
- **Basic Test Infrastructure**: Vitest + React Testing Library configured and working
- **Test Configuration**: vitest.config.ts and vitest.setup.ts properly configured
- **Mocking Setup**: Global mocks for Next.js, localStorage, fetch, etc.
- **Basic Tests**: Core testing functionality verified

### 🔄 Partially Working Components
- **AuthContext Tests**: Tests written but localStorage mocking needs refinement
- **Token Refresh Logic Tests**: Tests written but timer mocking needs fixes
- **API Interceptor Tests**: Basic tests working, complex scenarios need work

### 📋 Pending Components
- **Component Tests**: TokenRefreshManager tests need refinement
- **Integration Tests**: End-to-end authentication flow tests
- **E2E Tests**: Complete user workflow tests

### Known Issues
1. **localStorage Mocking**: Complex interactions with React components need refinement
2. **Timer Mocking**: Fake timers with React components need proper setup
3. **Async Testing**: Some async operations in tests need better handling

## Troubleshooting

### Common Issues

1. **Test Environment Issues**:
   - Check vitest.config.ts configuration
   - Verify setup files are loaded
   - Ensure proper mocking

2. **Async Test Issues**:
   - Use proper async/await patterns
   - Wait for promises to resolve
   - Use waitFor for DOM updates

3. **Mock Issues**:
   - Verify mock implementations
   - Check mock call counts
   - Ensure proper cleanup

### Debugging Tests

1. **Verbose Output**:
   ```bash
   npm test -- --verbose
   ```

2. **Single Test Debugging**:
   ```bash
   npm test -- --grep "specific test name"
   ```

3. **Coverage Analysis**:
   ```bash
   npm run test:coverage
   open coverage/index.html
   ```

## Future Improvements

### Planned Enhancements
- **E2E Testing**: Playwright or Cypress integration
- **Visual Regression Testing**: Screenshot comparisons
- **Performance Testing**: Load and stress testing
- **Accessibility Testing**: Automated a11y checks

### Monitoring and Metrics
- **Test Execution Time**: Track and optimize
- **Coverage Trends**: Monitor over time
- **Flaky Test Detection**: Identify unstable tests
- **Test Quality Metrics**: Maintain high standards

## Maintenance Checklist

### Weekly
- [ ] Review test failures
- [ ] Update test data if needed
- [ ] Check coverage reports

### Monthly
- [ ] Review and update test dependencies
- [ ] Analyze test performance
- [ ] Update documentation

### Quarterly
- [ ] Major test infrastructure updates
- [ ] Test strategy review
- [ ] Coverage goal assessment

---

**Last Updated**: December 2024  
**Maintainer**: BackboneOS Development Team  
**Version**: 1.0.0
