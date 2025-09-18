# 🧪 Touchpoint Resolution System Tests

This directory contains comprehensive tests for the touchpoint resolution system, covering all the core components and their interactions.

## 📁 Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── test_protocols.py             # Tests for protocols and interfaces
├── test_resolvers.py             # Tests for touchpoint resolvers
├── test_mapping_providers.py     # Tests for mapping providers
├── test_models.py                # Tests for TouchpointMappingRule model
├── test_runner.py                # Test runner script
└── README.md                     # This documentation
```

## 🎯 Test Coverage

### 1. Protocol Tests (`test_protocols.py`)
- **TouchpointHint**: Dataclass creation, defaults, immutability
- **TouchpointInferenceProtocol**: Interface implementation and type checking
- **TouchpointResolverProtocol**: Resolver interface implementation
- **MappingProviderProtocol**: Mapping provider interface implementation
- **Integration Tests**: Full workflow simulation using all protocols

### 2. Resolver Tests (`test_resolvers.py`)
- **DefaultTouchpointResolver**: Core resolution logic
  - Resolution without mapping rules
  - Resolution with mapping rules
  - Touchpoint reuse and caching
  - Edge cases (no code, no channel, etc.)
  - Mapping rule application
  - Touchpoint creation and relationship handling
- **CachedTouchpointResolver**: Caching functionality
  - Cache initialization and configuration
  - Cache hit/miss scenarios
  - Custom cache timeouts

### 3. Mapping Provider Tests (`test_mapping_providers.py`)
- **DatabaseMappingProvider**: Database-backed rule lookup
  - Rule lookup with different priority levels
  - Specific source vs generic rules
  - Priority ordering and inactive rule filtering
  - Connector type extraction
  - Caching integration
- **CachedMappingProvider**: Enhanced caching features
  - Cache invalidation (specific and global)
  - Cache warming
  - Local cache management
- **FileMappingProvider**: File-based configuration
  - Configuration file loading
  - Rule lookup from file data
  - Error handling for missing files

### 4. Model Tests (`test_models.py`)
- **TouchpointMappingRule**: Model validation and behavior
  - Model creation (minimal and full)
  - String representation
  - Ordering and unique constraints
  - Validation logic (clean method)
  - Default values and custom fields
  - Metadata handling
  - Database indexes and verbose names

## 🚀 Running Tests

### Option 1: Using Django's Test Runner
```bash
cd /path/to/backend
python manage.py test connectors.tests
```

### Option 2: Using the Custom Test Runner
```bash
cd /path/to/backend/connectors/tests
python test_runner.py
```

### Option 3: Running Individual Test Modules
```bash
# Test protocols only
python manage.py test connectors.tests.test_protocols

# Test resolvers only
python manage.py test connectors.tests.test_resolvers

# Test mapping providers only
python manage.py test connectors.tests.test_mapping_providers

# Test models only
python manage.py test connectors.tests.test_models
```

### Option 4: Running Specific Test Classes
```bash
# Test TouchpointHint only
python manage.py test connectors.tests.test_protocols.TestTouchpointHint

# Test DefaultTouchpointResolver only
python manage.py test connectors.tests.test_resolvers.TestDefaultTouchpointResolver
```

## 📊 Test Statistics

The test suite includes:

- **Protocol Tests**: 15+ test methods
- **Resolver Tests**: 20+ test methods
- **Mapping Provider Tests**: 25+ test methods
- **Model Tests**: 20+ test methods

**Total**: 80+ test methods covering all major functionality and edge cases.

## 🔍 Test Quality Features

### 1. **Comprehensive Coverage**
- All public methods and properties are tested
- Edge cases and error conditions are covered
- Integration between components is tested

### 2. **Mock Objects**
- Mock connectors for testing protocols
- Mock mapping providers for testing resolvers
- Mock cache for testing caching functionality

### 3. **Database Testing**
- Uses Django's TestCase for database transactions
- Tests model creation, validation, and constraints
- Verifies database indexes and relationships

### 4. **Error Handling**
- Tests validation errors and exceptions
- Tests edge cases (empty data, missing fields)
- Tests constraint violations

### 5. **Performance Testing**
- Tests caching behavior and cache invalidation
- Tests database query optimization
- Tests batch operations

## 🛠️ Test Utilities

### Mock Classes
- **MockConnector**: Implements TouchpointInferenceProtocol for testing
- **MockMappingProvider**: Provides mock mapping rules
- **MockMappingRule**: Represents mapping rule data

### Test Data
- Consistent test data across all test modules
- Realistic touchpoint codes and channel types
- Various priority levels and metadata examples

## 📈 Continuous Integration

These tests are designed to run in CI/CD pipelines:

1. **Fast Execution**: Tests run quickly with minimal setup
2. **Isolated**: Each test is independent and can run in parallel
3. **Deterministic**: Tests produce consistent results
4. **Comprehensive**: High coverage ensures reliability

## 🔧 Debugging Tests

### Running Tests with Verbose Output
```bash
python manage.py test connectors.tests --verbosity=2
```

### Running Tests with Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test connectors.tests
coverage report
coverage html  # Generate HTML report
```

### Debugging Specific Test Failures
```bash
# Run with pdb debugger
python manage.py test connectors.tests.test_resolvers.TestDefaultTouchpointResolver.test_resolve_without_mapping_rule --pdb
```

## 📝 Adding New Tests

When adding new functionality to the touchpoint resolution system:

1. **Add tests for new protocols** in `test_protocols.py`
2. **Add tests for new resolvers** in `test_resolvers.py`
3. **Add tests for new mapping providers** in `test_mapping_providers.py`
4. **Add tests for new models** in `test_models.py`
5. **Update this README** with new test coverage information

### Test Naming Convention
- Test classes: `Test{ClassName}`
- Test methods: `test_{method_name}_{scenario}`
- Example: `test_resolve_with_mapping_rule`

### Test Documentation
- Each test method should have a docstring explaining what it tests
- Use descriptive test names that explain the scenario
- Include comments for complex test logic

## ✅ Test Checklist

Before committing changes to the touchpoint resolution system:

- [ ] All existing tests pass
- [ ] New functionality has corresponding tests
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] Integration between components is tested
- [ ] Performance implications are considered
- [ ] Documentation is updated

This comprehensive test suite ensures the reliability and maintainability of the touchpoint resolution system.
