# Test Data Setup for Frontend Development

This document explains how to set up comprehensive test data for frontend development and testing.

## Quick Setup

### Option 1: Comprehensive Setup (Recommended)
```bash
# Run the comprehensive test data script
python setup_comprehensive_test_data.py
```

### Option 2: Run All Existing Scripts
```bash
# Run all existing test data scripts in order
python run_all_test_data.py
```

### Option 3: Individual Scripts
```bash
# Run individual scripts as needed
python create_divisions_data.py
python populate_products.py
python enhance_products_data.py
python entities/create_test_data.py
python create_campaigns_data.py
python create_offers_data.py
```

## What Data Gets Created

### Users (4 test users)
- **admin** / password123 (Superuser)
- **manager** / password123 (Staff)
- **sales** / password123 (Regular user)
- **marketing** / password123 (Regular user)

### Products System
- **5 Divisions**: Technology, Consulting, Training, Marketing, HR
- **13 Categories**: Hierarchical categories with parent-child relationships
- **4 Modalities**: Online, In-Person, Hybrid, Self-Paced
- **3 Customization Levels**: Basic, Standard, Premium
- **8 Products**: Full-stack web development, data science, consulting, etc.

### Entities System
- **5 Organizations**: TechCorp, StartupXYZ, Global Finance, etc.
- **8 People**: With contact details, profiles, and positions
- **Contact Details**: Email and phone for each person
- **Individual Profiles**: Bio, experience, education level

### Interactions System
- **5 Channels**: Email, Phone, Website, Social Media, In-Person
- **4 Mediums**: Direct, Marketing, Sales, Support
- **5 Action Types**: Inquiry, Meeting, Proposal, Follow-up, Purchase
- **4 Agents**: Sales Team, Marketing Team, Support Team, System
- **20 Sample Interactions**: With various entities and outcomes

### Campaigns System
- **3 Campaigns**: Q1 Launch, Summer Training, Enterprise Solutions
- **Organizational Structure**: Marketing Division and Digital Marketing Team
- **Campaign Relationships**: With channels, industries, segments, functions, tags

### Offers System
- **3 Product Offerings**: Early Bird Discount, Corporate Package, Consulting Bundle
- **Linked to Products**: Each offer is linked to existing products
- **Validity Periods**: Different start/end dates for testing

### World/Reference Data
- **5 Countries**: US, Mexico, Canada, Spain, Colombia
- **7 Industries**: Technology, Finance, Healthcare, Manufacturing, etc.
- **8 Skills**: Python, JavaScript, Leadership, Data Analysis, etc.
- **5 Market Segments**: SMB, Enterprise, Startups, Government, Non-Profit
- **5 Tags**: Premium, Popular, New, Limited, Certified

## API Endpoints Available

After running the test data setup, you can access:

### Products
- `GET /api/products/divisions/` - List all divisions
- `GET /api/products/categories/` - List all categories
- `GET /api/products/products/` - List all products
- `GET /api/products/analytics/dashboard/` - Product analytics

### Entities
- `GET /api/entities/people/` - List all people
- `GET /api/entities/organizations/` - List all organizations
- `GET /api/entities/contacts/` - List all contact details
- `GET /api/entities/profiles/` - List all individual profiles

### Interactions
- `GET /api/interactions/interactions/` - List all interactions
- `GET /api/interactions/channels/` - List all channels
- `GET /api/interactions/actions/` - List all actions
- `GET /api/interactions/agents/` - List all agents

### Campaigns
- `GET /api/campaigns/campaigns/` - List all campaigns
- `GET /api/campaigns/campaigns/active_now/` - Active campaigns
- `GET /api/campaigns/campaigns/analytics/` - Campaign analytics

### Offers
- `GET /api/offers/offerings/` - List all offers
- `GET /api/offers/offerings/currently_valid/` - Valid offers
- `GET /api/offers/offerings/analytics/` - Offer analytics

### World/Reference Data
- `GET /api/world/countries/` - List all countries
- `GET /api/world/industries/` - List all industries
- `GET /api/world/skills/` - List all skills
- `GET /api/world/market-segments/` - List all market segments
- `GET /api/world/tags/` - List all tags

## Frontend Testing Scenarios

With this test data, you can test:

### Products Management
- ✅ List products with pagination
- ✅ Search and filter products
- ✅ Create new products
- ✅ Edit existing products
- ✅ Delete products
- ✅ View product analytics
- ✅ Manage divisions and categories

### Entities Management
- ✅ List people and organizations
- ✅ Search entities
- ✅ View contact details
- ✅ Manage individual profiles
- ✅ Filter by organization

### Interactions Management
- ✅ View interaction timeline
- ✅ Filter by channel, medium, action type
- ✅ Search interactions
- ✅ View interaction analytics

### Campaigns Management
- ✅ List campaigns
- ✅ View campaign details
- ✅ Filter active/scheduled/finished campaigns
- ✅ View campaign analytics

### Offers Management
- ✅ List product offerings
- ✅ Filter by validity period
- ✅ View offer analytics
- ✅ Manage offer relationships

### Analytics Dashboard
- ✅ Product performance metrics
- ✅ Campaign effectiveness
- ✅ Interaction trends
- ✅ Revenue analytics

## Data Relationships

The test data includes realistic relationships:

- **Products** are linked to categories, divisions, modalities, and customizations
- **People** belong to organizations and have contact details and profiles
- **Interactions** connect people with channels, mediums, and action types
- **Campaigns** target specific industries, segments, and functions
- **Offers** are linked to products and have validity periods
- **All entities** can have tags, skills, and other semantic relationships

## Troubleshooting

### Common Issues

1. **Database not found**: Make sure Django migrations are applied
   ```bash
   python manage.py migrate
   ```

2. **Permission errors**: Make sure you have write access to the database

3. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

4. **Script fails**: Check the error output and ensure all required models exist

### Reset Data

To reset all test data:
```bash
# Clear all data (be careful!)
python manage.py flush

# Then run the setup again
python setup_comprehensive_test_data.py
```

## Next Steps

After setting up test data:

1. **Start the backend server**:
   ```bash
   python manage.py runserver
   ```

2. **Test API endpoints** in your browser or Postman

3. **Begin frontend development** with the Products Management system

4. **Use the test credentials** to log in and test authentication

5. **Explore the data** through the Django admin at `/admin/`

---

**Happy coding! 🚀**
