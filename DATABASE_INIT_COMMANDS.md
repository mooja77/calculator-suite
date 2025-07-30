# 🗃️ Database Initialization Commands

## Post-Deployment Database Setup

Once your Calculator Suite deploys successfully, you'll need to initialize the database with essential data.

## 🎯 Required Database Operations

### 1. Initialize Database Tables
```bash
# This creates all database tables
flask init-db
```

### 2. Seed Global Infrastructure Data
```bash
# This populates currencies, countries, and system data
flask seed-global-data
```

### 3. Verify Seeding Status
```bash
# Check what data has been loaded
flask show-seed-status
```

### 4. Refresh Exchange Rates
```bash
# Update currency exchange rates
flask refresh-exchange-rates
```

## 🖥️ How to Run These Commands

### Method 1: Render Console (Recommended)
1. Go to your Render dashboard
2. Click on your Calculator Suite service
3. Go to "Shell" tab
4. Run each command above

### Method 2: Render CLI (If you have it installed)
```bash
# Install Render CLI
curl -fsSL https://render.com/install | sh

# Connect to your service
render shell your-service-name

# Run commands
flask init-db
flask seed-global-data
```

## 📊 Expected Outputs

### After `flask init-db`:
```
Database initialized.
```

### After `flask seed-global-data`:
```
Global infrastructure data seeded successfully.
```

### After `flask show-seed-status`:
```
Global Infrastructure Seeding Status:
  currencies: 20/20 seeded, 20 active
  countries: 195/195 seeded, 195 active
  regions: 7/7 seeded, 7 active
```

## 🚨 Troubleshooting Database Issues

### Issue: "Database connection failed"
**Cause**: PostgreSQL not properly connected
**Solution**: Check environment variables in Render dashboard

### Issue: "Table already exists"
**Cause**: Database already initialized
**Solution**: This is normal, skip `init-db` command

### Issue: "Seeding failed"
**Cause**: Network issues or data conflicts
**Solution**: Run `flask show-seed-status` to see what succeeded

## 🎯 Database Requirements

Your Calculator Suite needs these data types:
- **20+ Currencies**: USD, EUR, GBP, CAD, AUD, etc.
- **195+ Countries**: All ISO countries for localization
- **Regional Data**: Time zones and regional settings
- **Exchange Rates**: Current currency conversion rates

## ✅ Verification Steps

After database initialization:
1. Visit any calculator (e.g., Mortgage Calculator)
2. Check currency dropdown has 20+ options
3. Verify calculations work without errors
4. Test different currencies and countries

---

**Note**: These commands only need to be run ONCE after initial deployment. The database will persist across deployments.

Your Calculator Suite will be fully functional after these database initialization steps! 🚀