# Social Trends API - RapidAPI Pricing Plans Configuration

## 🆓 **BASIC Plan (Free)**

- **Price**: $0/month
- **Requests**: 1,000/month
- **Rate Limit**: 100/day
- **Features**:
  - ✅ Global trends endpoint
  - ✅ Basic country filtering
  - ✅ Standard support
  - ❌ Platform-specific trends
  - ❌ Historical data
  - ❌ Advanced analytics

**Target**: Developers testing the API, small projects

---

## 💎 **PRO Plan**

- **Price**: $19.99/month
- **Requests**: 10,000/month
- **Rate Limit**: 500/day
- **Features**:
  - ✅ All Basic features
  - ✅ Platform-specific trends (TikTok, Instagram)
  - ✅ Extended country support
  - ✅ Growth percentage metrics
  - ✅ Priority support
  - ❌ Historical data
  - ❌ Custom webhooks

**Target**: Marketing agencies, social media managers, content creators

---

## 🚀 **ENTERPRISE Plan**

- **Price**: $99.99/month
- **Requests**: 100,000/month
- **Rate Limit**: 2,000/day
- **Features**:
  - ✅ All PRO features
  - ✅ Historical trend data (30 days)
  - ✅ Advanced analytics & insights
  - ✅ Custom country analysis
  - ✅ Webhook notifications
  - ✅ Dedicated support
  - ✅ SLA guarantee
  - ✅ Custom integrations

**Target**: Large enterprises, data companies, research institutions

---

## 🔧 **API Key Mapping**

```json
{
  "BASIC": {
    "monthly_limit": 1000,
    "daily_limit": 100,
    "endpoints": ["/v1/trends/global"],
    "features": ["basic_filtering"]
  },
  "PRO": {
    "monthly_limit": 10000,
    "daily_limit": 500,
    "endpoints": ["/v1/trends/global", "/v1/trends/platform"],
    "features": ["platform_specific", "growth_metrics", "priority_support"]
  },
  "ENTERPRISE": {
    "monthly_limit": 100000,
    "daily_limit": 2000,
    "endpoints": [
      "/v1/trends/global",
      "/v1/trends/platform",
      "/v1/trends/country"
    ],
    "features": ["historical_data", "advanced_analytics", "webhooks", "sla"]
  }
}
```

## 📊 **Revenue Projections**

### Conservative Estimate (Month 1-3):

- 50 Free users → $0
- 10 Pro users → $199.90
- 2 Enterprise users → $199.98
- **Total**: ~$400/month

### Growth Estimate (Month 6-12):

- 200 Free users → $0
- 50 Pro users → $999.50
- 10 Enterprise users → $999.90
- **Total**: ~$2,000/month

### Optimistic Estimate (Year 2):

- 500 Free users → $0
- 150 Pro users → $2,998.50
- 25 Enterprise users → $2,499.75
- **Total**: ~$5,500/month
