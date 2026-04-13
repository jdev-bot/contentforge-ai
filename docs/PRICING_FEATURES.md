# ContentForge AI - Pricing & Feature-Tier Mapping

**Document:** Feature-Tier Mapping & Pricing Strategy  
**Version:** 1.0  
**Date:** April 13, 2026  
**Prepared by:** Business Analyst, Neo DevOrg  
**Status:** Draft for Review

---

## Executive Summary

This document defines the complete feature-to-tier mapping for ContentForge AI's pricing strategy. It provides clear boundaries for each pricing tier, usage limits, feature entitlements, and the business rationale behind tier structuring.

**Pricing Philosophy:**
- **Free:** Hook users, demonstrate value, drive viral growth
- **Creator:** Individual power users, full feature access with reasonable limits
- **Pro:** Serious creators and small teams, unlimited core features
- **Team:** Agencies and companies, collaboration and management features
- **Enterprise:** Large organizations, compliance, custom SLAs

---

## Pricing Overview

### Tier Comparison Matrix

| Feature | Free | Creator $29/mo | Pro $79/mo | Team $199/mo | Enterprise Custom |
|---------|------|------------------|------------|--------------|-------------------|
| **AI Generations** | 50/mo | 250/mo | Unlimited | Unlimited | Unlimited |
| **Projects** | 1 | 5 | 20 | Unlimited | Unlimited |
| **Team Members** | 1 | 1 | 1 | 5 included | Custom |
| **Connected Accounts** | 2 | Unlimited | Unlimited | Unlimited | Unlimited |
| **Content History** | 30 days | 1 year | Unlimited | Unlimited | Unlimited |
| **Priority AI** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **API Access** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **White-Label** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **SSO/SAML** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Support** | Community | Email (24h) | Chat (4h) | Priority (1h) | Dedicated |

---

## Detailed Tier Breakdown

### 1. Free Tier

**Price:** $0/month  
**Target:** Trial users, casual creators, viral growth

#### Core Limits
| Limit | Value | Notes |
|-------|-------|-------|
| AI Generations | 50/month | Reset monthly |
| Projects | 1 active | Archive to create new |
| Content History | 30 days | Auto-deleted after |
| Connected Platforms | 2 | Twitter, LinkedIn, etc. |
| Exports | 10/month | PDF, CSV, etc. |

#### Included Features
**Content Creation:**
- ✅ Basic AI repurposing (all formats)
- ✅ 3 brand voice presets
- ✅ Manual export (TXT, Markdown)
- ✅ Basic analytics (last 30 days)

**Platform Access:**
- ✅ Web application
- ✅ Mobile-responsive design
- ❌ Mobile app

**Support:**
- ✅ Help center access
- ✅ Community Discord
- ❌ Email support
- ❌ Live chat

**Integrations:**
- ✅ Manual download
- ❌ Direct publishing
- ❌ API access

#### Upgrade Triggers
- At 80% usage: Contextual upgrade prompt
- At 100% usage: Hard limit with upgrade CTA
- After 30 days: Email sequence if active

#### Business Rationale
- **Viral Coefficient:** Free users invite others for credits
- **Conversion Funnel:** 5-8% expected conversion to paid
- **Cost:** Near-zero marginal cost (Groq free tier covers ~14,000 generations)

---

### 2. Creator Tier

**Price:** $29/month or $290/year (17% discount)  
**Target:** Individual content creators, solopreneurs  
**Sweet Spot:** Users generating 50-250 pieces/month

#### Core Limits
| Limit | Value | Notes |
|-------|-------|-------|
| AI Generations | 250/month | Soft limit with overages |
| Projects | 5 active | Archive unlimited |
| Content History | 1 year | Export to keep longer |
| Connected Platforms | Unlimited | All supported platforms |
| Scheduled Posts | 10/month | Buffer-style queue |

#### Included Features
**Content Creation:**
- ✅ All AI models (GPT-4, Claude, Groq)
- ✅ 10 custom brand voices
- ✅ All export formats (PDF, Word, HTML)
- ✅ Advanced analytics (full history)
- ✅ Content scheduling (10/month)

**Platform Access:**
- ✅ Web application
- ✅ Mobile-responsive design
- ✅ PWA install
- ❌ Native mobile apps

**Support:**
- ✅ Help center access
- ✅ Community Discord
- ✅ Email support (24h response)
- ❌ Live chat
- ❌ Phone support

**Integrations:**
- ✅ Direct publishing (Twitter, LinkedIn)
- ✅ Zapier integration (basic)
- ✅ Notion export
- ❌ API access
- ❌ Custom webhooks

#### Overage Pricing
| Overage | Price | Notes |
|---------|-------|-------|
| +50 generations | $5 | Auto-billed |
| +5 scheduled posts | $2 | One-time |
| Additional project | $2/month | Auto-billed |

#### Business Rationale
- **Pricing Psychology:** $29 is impulse-buy range for creators
- **Value Prop:** 5x Free limits for reasonable price
- **Upgrade Path:** Clear path to Pro for power users
- **Expected Churn:** 8-10% monthly

---

### 3. Pro Tier

**Price:** $79/month or $790/year (17% discount)  
**Target:** Power users, small teams (2-3 people), professional creators  
**Sweet Spot:** Users hitting Creator limits regularly

#### Core Limits
| Limit | Value | Notes |
|-------|-------|-------|
| AI Generations | Unlimited | Fair use policy (10,000/month soft) |
| Projects | 20 active | Archive unlimited |
| Content History | Unlimited | Never deleted |
| Connected Platforms | Unlimited | All platforms |
| Scheduled Posts | Unlimited | Full scheduling engine |
| Team Members | 1 | Share login (limited) |

#### Included Features
**Content Creation:**
- ✅ All AI models with priority access
- ✅ Unlimited custom brand voices
- ✅ All export formats
- ✅ Advanced analytics with trends
- ✅ Unlimited scheduling
- ✅ Content calendar view
- ✅ Bulk operations

**Platform Access:**
- ✅ Web application
- ✅ Mobile-responsive design
- ✅ PWA install
- ✅ Early access to new features

**Support:**
- ✅ Help center access
- ✅ Community Discord
- ✅ Email support (4h response)
- ✅ Live chat (business hours)
- ❌ Phone support
- ❌ Dedicated account manager

**Integrations:**
- ✅ Direct publishing (all platforms)
- ✅ Zapier integration (premium)
- ✅ Notion export (sync)
- ✅ API access (10,000 calls/month)
- ✅ Webhooks (5 endpoints)
- ✅ Buffer integration
- ✅ ConvertKit integration

#### API Limits
| Metric | Limit | Overage |
|--------|-------|---------|
| Requests | 10,000/month | $0.001/request |
| Rate Limit | 100/minute | - |
| Webhooks | 5 endpoints | $5/additional |

#### Business Rationale
- **Psychological Pricing:** $79 signals "professional tool"
- **Unlimited Hook:** Key differentiator from Creator
- **API Value:** API access justifies price for developers
- **Expected Churn:** 5-7% monthly
- **Net Revenue Retention:** >110% (upsells to Team)

---

### 4. Team Tier

**Price:** $199/month or $1990/year (17% discount)  
**Additional Seats:** $25/seat/month  
**Target:** Marketing teams, agencies, small businesses  
**Sweet Spot:** 3-5 person teams creating content collaboratively

#### Core Limits
| Limit | Value | Notes |
|-------|-------|-------|
| AI Generations | Unlimited | Fair use per seat |
| Projects | Unlimited | Organized by workspace |
| Content History | Unlimited | Team-wide retention |
| Connected Platforms | Unlimited | Per team member |
| Scheduled Posts | Unlimited | Team scheduling |
| Team Members | 5 included | +$25/seat |
| Workspaces | Unlimited | Client/project separation |

#### Included Features
**Content Creation:**
- ✅ All Pro features
- ✅ Team workspaces
- ✅ Content approval workflows
- ✅ Role-based permissions
- ✅ Shared brand voice library
- ✅ Content templates (team)
- ✅ Bulk operations

**Collaboration:**
- ✅ Real-time collaboration (basic)
- ✅ Comments and annotations
- ✅ Activity feed
- ✅ Content assignment
- ✅ Approval queues
- ✅ Revision history

**Platform Access:**
- ✅ All Pro access methods
- ✅ Team administration
- ✅ Usage analytics per member
- ✅ Cost allocation reporting

**Support:**
- ✅ All Pro support
- ✅ Priority chat (1h response)
- ✅ Onboarding call
- ✅ Quarterly business reviews
- ❌ Dedicated account manager

**Integrations:**
- ✅ All Pro integrations
- ✅ API access (50,000 calls/month)
- ✅ Webhooks (20 endpoints)
- ✅ SSO (Google Workspace, Microsoft)
- ✅ SCIM provisioning (basic)

#### Team Administration
| Feature | Description |
|---------|-------------|
| Role Management | Admin, Editor, Viewer roles |
| Permission Controls | Workspace-level permissions |
| Usage Quotas | Per-member generation limits |
| Billing Consolidation | Single invoice for team |
| Seat Management | Add/remove, pending invites |

#### Business Rationale
- **Per-Seat Economics:** 5 seats × $40 = $200, justifies $199 price
- **Agency Play:** Workspaces = client separation
- **Collaboration Premium:** Workflow features justify price jump
- **Expected Churn:** 4-6% monthly
- **Expansion Revenue:** Additional seats drive NRR >120%

---

### 5. Enterprise Tier

**Price:** Custom ($500+/month)  
**Target:** Large organizations, regulated industries  
**Minimum:** 20+ seats or custom requirements

#### Core Limits
| Limit | Value | Notes |
|-------|-------|-------|
| AI Generations | Unlimited | Dedicated capacity available |
| Projects | Unlimited | Organized by department |
| Content History | Unlimited | Custom retention policies |
| Connected Platforms | Unlimited | Custom integrations |
| Scheduled Posts | Unlimited | Enterprise scheduling |
| Team Members | Custom | Volume pricing |
| SLA | 99.99% uptime | Financial penalties |

#### Included Features
**Content Creation:**
- ✅ All Team features
- ✅ Custom AI model training
- ✅ Advanced brand voice analysis
- ✅ Dedicated inference capacity
- ✅ Custom output formats

**Collaboration:**
- ✅ All Team features
- ✅ Advanced workflows
- ✅ Custom approval chains
- ✅ Department workspaces
- ✅ Cross-team analytics

**Security & Compliance:**
- ✅ SOC 2 Type II certified
- ✅ HIPAA compliance (optional)
- ✅ GDPR advanced features
- ✅ Data residency options
- ✅ Custom encryption keys
- ✅ Penetration testing
- ✅ Security reviews

**White-Label Options:**
- ✅ Custom domain
- ✅ Full theming
- ✅ Branded mobile app
- ✅ Custom email domain
- ✅ No "Powered by" branding

**Support:**
- ✅ Dedicated account manager
- ✅ Technical account manager
- ✅ 24/7 phone support
- ✅ Slack Connect channel
- ✅ Priority bug fixes
- ✅ Custom development

**Integrations:**
- ✅ Unlimited API calls
- ✅ Unlimited webhooks
- ✅ Custom integrations
- ✅ Dedicated integration engineer
- ✅ On-premise deployment option

**SSO & Identity:**
- ✅ SAML 2.0
- ✅ SCIM provisioning (advanced)
- ✅ Custom identity providers
- ✅ Multi-factor authentication
- ✅ Session management

#### Enterprise Add-Ons
| Add-On | Price | Description |
|--------|-------|-------------|
| HIPAA Compliance | +$500/mo | BAA, PHI handling |
| Data Residency | +$300/mo | EU, UK, AU region hosting |
| Custom AI Training | Custom | Fine-tuned models |
| On-Premise | Custom | Self-hosted option |
| Professional Services | $200/hr | Implementation, training |

#### Business Rationale
- **High ACV:** $10K+ annual contracts
- **Low Volume, High Touch:** Sales-led process
- **Compliance Premium:** Regulatory requirements justify price
- **Custom Development:** Additional revenue stream
- **Expected Churn:** <2% monthly
- **Logo Value:** Enterprise logos for credibility

---

## Feature Gating Matrix

### Content Creation Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| Basic repurposing | ✅ | ✅ | ✅ | ✅ | ✅ |
| GPT-4 access | ❌ | ✅ | ✅ | ✅ | ✅ |
| Claude access | ❌ | ✅ | ✅ | ✅ | ✅ |
| Priority AI queue | ❌ | ❌ | ✅ | ✅ | ✅ |
| Custom brand voices | 3 | 10 | Unlimited | Unlimited | Unlimited |
| Voice training | ❌ | ❌ | ❌ | ✅ | ✅ |
| Bulk generation | ❌ | ❌ | ✅ | ✅ | ✅ |
| Content templates | 5 | 20 | 50 | Unlimited | Unlimited |
| Custom templates | ❌ | ❌ | ❌ | ✅ | ✅ |
| AI image generation | ❌ | ❌ | ❌ | ✅ | ✅ |

### Platform & Distribution Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| Manual export | ✅ | ✅ | ✅ | ✅ | ✅ |
| Direct publishing | ❌ | ✅ | ✅ | ✅ | ✅ |
| Scheduling | ❌ | 10/mo | Unlimited | Unlimited | Unlimited |
| Content calendar | ❌ | Basic | Advanced | Advanced | Advanced |
| Auto-posting | ❌ | ❌ | ✅ | ✅ | ✅ |
| Multi-platform sync | ❌ | ❌ | ✅ | ✅ | ✅ |
| Platform analytics | ❌ | Basic | Advanced | Advanced | Advanced |
| Custom integrations | ❌ | ❌ | ❌ | ❌ | ✅ |

### Collaboration Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| User count | 1 | 1 | 1 | 5+ | Custom |
| Workspaces | 1 | 5 | 20 | Unlimited | Unlimited |
| Sharing | ❌ | ❌ | View only | Full | Full |
| Comments | ❌ | ❌ | ❌ | ✅ | ✅ |
| Approval workflow | ❌ | ❌ | ❌ | ✅ | ✅ |
| Activity feed | ❌ | ❌ | ❌ | ✅ | ✅ |
| Real-time collab | ❌ | ❌ | ❌ | Basic | Advanced |
| Role management | ❌ | ❌ | ❌ | 3 roles | Custom |
| Audit logs | ❌ | ❌ | ❌ | 30 days | 7 years |

### Analytics & Reporting Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| Basic analytics | 30 days | Full | Full | Full | Full |
| Export reports | ❌ | PDF | PDF/CSV | All formats | All formats |
| Scheduled reports | ❌ | ❌ | ❌ | Weekly | Custom |
| Team analytics | ❌ | ❌ | ❌ | ✅ | ✅ |
| Custom dashboards | ❌ | ❌ | ❌ | ❌ | ✅ |
| Data API | ❌ | ❌ | ✅ | ✅ | ✅ |
| Custom metrics | ❌ | ❌ | ❌ | ❌ | ✅ |

### API & Integration Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| API access | ❌ | ❌ | ✅ | ✅ | ✅ |
| API calls/month | 0 | 0 | 10,000 | 50,000 | Unlimited |
| Rate limit | N/A | N/A | 100/min | 500/min | Custom |
| Webhooks | ❌ | ❌ | 5 | 20 | Unlimited |
| Zapier | ❌ | Basic | Premium | Premium | Premium |
| Native integrations | ❌ | 3 | 10 | 20 | Custom |
| Custom integrations | ❌ | ❌ | ❌ | ❌ | ✅ |
| Webhook signing | ❌ | ❌ | ❌ | ✅ | ✅ |

### Support Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| Help center | ✅ | ✅ | ✅ | ✅ | ✅ |
| Community | ✅ | ✅ | ✅ | ✅ | ✅ |
| Email support | ❌ | 24h | 4h | 1h | 30min |
| Live chat | ❌ | ❌ | Business | Priority | 24/7 |
| Phone support | ❌ | ❌ | ❌ | ❌ | ✅ |
| Dedicated manager | ❌ | ❌ | ❌ | ❌ | ✅ |
| Onboarding | ❌ | ❌ | ❌ | Call | Custom |
| SLA | None | None | 99.5% | 99.9% | 99.99% |

### Security & Compliance Features

| Feature | Free | Creator | Pro | Team | Enterprise |
|---------|------|---------|-----|------|------------|
| 2FA | ✅ | ✅ | ✅ | ✅ | ✅ |
| SSO | ❌ | ❌ | ❌ | Google/O365 | SAML |
| SCIM | ❌ | ❌ | ❌ | Basic | Full |
| Audit logs | ❌ | ❌ | ❌ | 30 days | 7 years |
| SOC 2 | ❌ | ❌ | ❌ | Shared | Certified |
| HIPAA | ❌ | ❌ | ❌ | ❌ | Optional |
| Data residency | ❌ | ❌ | ❌ | ❌ | Optional |
| Custom encryption | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Usage Quotas & Overages

### Quota Structure

| Quota Type | Free | Creator | Pro | Team | Enterprise |
|------------|------|---------|-----|------|------------|
| AI Generations | 50/mo | 250/mo | 10,000* | 50,000* | Unlimited |
| Scheduled Posts | 0 | 10/mo | Unlimited | Unlimited | Unlimited |
| API Calls | 0 | 0 | 10,000/mo | 50,000/mo | Unlimited |
| Webhooks | 0 | 0 | 5 | 20 | Unlimited |
| Projects | 1 | 5 | 20 | Unlimited | Unlimited |
| Team Members | 1 | 1 | 1 | 5 | Custom |
| Content History | 30 days | 1 year | Unlimited | Unlimited | Unlimited |

\* Soft limit; overages available

### Overage Pricing

| Overage | Price | Applies To |
|---------|-------|------------|
| +50 AI generations | $5 | Free, Creator |
| +1,000 API calls | $1 | Pro, Team |
| +5 scheduled posts | $2 | Creator |
| +1 team member | $25/mo | Team, Enterprise |
| +1 webhook endpoint | $5/mo | Pro, Team |
| +1 project (over limit) | $2/mo | Creator, Pro |

### Soft vs Hard Limits

**Soft Limits (Pro+):**
- Allow overages with auto-billing
- Warn at 80% usage
- Grace period for overages
- Monthly billing reconciliation

**Hard Limits (Free, Creator):**
- Hard stop at 100%
- Upgrade prompt displayed
- No automatic overages
- Manual upgrade required

---

## Annual Plan Benefits

### Pricing Structure

| Tier | Monthly | Annual | Savings |
|------|---------|--------|---------|
| Creator | $29/mo | $290/yr | $58 (17%) |
| Pro | $79/mo | $790/yr | $158 (17%) |
| Team | $199/mo | $1990/yr | $398 (17%) |

### Additional Annual Benefits

| Benefit | Creator | Pro | Team | Enterprise |
|---------|---------|-----|------|------------|
| Months free | 2 | 2 | 2 | Custom |
| Priority support | ❌ | ❌ | ✅ | ✅ |
| Annual review call | ❌ | ❌ | ✅ | ✅ |
| Early access | ❌ | ❌ | ✅ | ✅ |
| Price lock | 1 year | 1 year | 1 year | Contract |

---

## Add-Ons & Extras

### Individual Add-Ons

| Add-On | Price | Eligible Tiers |
|--------|-------|----------------|
| Additional AI generations (50) | $5 | Free, Creator |
| Priority AI queue | $10/mo | Creator |
| API access | $29/mo | Creator |
| Additional seat | $25/mo | Team+ |
| White-label domain | $49/mo | Pro+ |
| HIPAA compliance | $500/mo | Team+ |
| Data residency | $300/mo | Team+ |

### Bundle Add-Ons

| Bundle | Contents | Price | Savings |
|--------|----------|-------|---------|
| Power User | Priority AI + 100 extra generations | $15/mo | $5 |
| Developer | API + Webhooks + Priority | $49/mo | $10 |
| Agency Starter | White-label + 2 extra seats | $89/mo | $10 |

---

## Discount Programs

### Launch Promotions

| Program | Discount | Code | Eligibility |
|---------|----------|------|-------------|
| Early Bird | 50% off 3 months | EARLYBIRD50 | First 100 customers |
| Founding Member | 20% forever | FOUNDING20 | First 500 customers |
| Product Hunt | 30% off 1 year | PH30 | PH launch week |
| Waitlist | 25% forever | WAITLIST25 | Waitlist members |
| Beta Tester | 50% forever | BETA50 | Beta participants |

### Volume Discounts

| Seats | Monthly Discount | Annual Discount |
|-------|------------------|-----------------|
| 10-24 | 10% | 25% |
| 25-49 | 15% | 30% |
| 50-99 | 20% | 35% |
| 100+ | Custom | Custom |

### Non-Profit / Education

| Category | Discount | Verification |
|----------|----------|--------------|
| Non-profit | 50% | 501(c)(3) docs |
| Education | Free | .edu email |
| Students | 50% | Student ID |
| Open Source | Free | GitHub repo |

---

## Trial & Freemium Strategy

### Free Tier as Trial

**Strategy:** Permanent free tier with upgrade path

**Advantages:**
- No time pressure
- Builds habit
- Viral potential
- Zero friction signup

**Limitations:**
- Lower conversion urgency
- Support burden from free users
- Feature limitations may frustrate

**Conversion Tactics:**
- Usage milestone celebrations (40 generations: "Almost there!")
- Feature teasers ("Upgrade to unlock scheduling")
- Success stories ("See what Pro users create")
- Time-based offers ("Upgrade this week for 20% off")

### Optional: Time-Limited Trial

**Alternative:** 14-day full-featured trial

**Implementation:**
- No credit card required
- Full Pro access for 14 days
- Convert to paid or Free tier
- Email sequence during trial

**A/B Test:** Compare Free tier vs. time-limited trial conversion rates

---

## Pricing Psychology

### Anchoring Strategy

1. **Decoy Effect:** Pro ($79) positioned between Creator ($29) and Team ($199)
   - Pro appears "reasonable" vs. expensive Team
   - Creator seems "limited" vs. feature-rich Pro

2. **Annual Framing:** "2 months free" vs. "17% discount"
   - "Free" is more compelling than percentage

3. **Enterprise Unpriced:** "Custom" signals premium
   - Encourages contact (sales opportunity)
   - Avoids sticker shock

### Value Metrics

**Perception:**
- Creator: $0.12 per generation (at 250)
- Pro: Unlimited = "infinite value"
- Team: $40/seat with full features

**ROI Messaging:**
- "Save 10 hours/month = $300+ value"
- "One client project = tool pays for itself"
- "Agency: Billable hours saved = $1000s"

---

## Revenue Projections

### Mix Assumptions

| Tier | % of Customers | ARPU | Revenue Mix |
|------|----------------|------|-------------|
| Free | 70% | $0 | 0% |
| Creator | 20% | $29 | 20% |
| Pro | 7% | $79 | 35% |
| Team | 2.8% | $199 | 40% |
| Enterprise | 0.2% | $1000 | 5% |

### Revenue at Scale

| Customers | MRR | ARPU | Annual Run Rate |
|-------------|-----|------|-----------------|
| 1,000 | $35,000 | $35 | $420,000 |
| 5,000 | $175,000 | $35 | $2,100,000 |
| 10,000 | $350,000 | $35 | $4,200,000 |
| 25,000 | $875,000 | $35 | $10,500,000 |

### Expansion Revenue

**Expected Monthly Expansion:**
- Upgrades: 2% of base
- Seat adds: 5% of Team tier
- Overages: 10% of Pro+ users

**Target Net Revenue Retention:** 110%+

---

## Competitive Positioning

### Comparison Matrix

| Tool | Starting Price | Our Equivalent | Our Price | Value |
|------|---------------|----------------|-----------|-------|
| Jasper | $49/mo | Creator | $29 | 41% less |
| Copy.ai | $49/mo | Creator | $29 | 41% less |
| Buffer | $15/mo | Creator (scheduling) | $29 | More features |
| Hootsuite | $99/mo | Pro | $79 | 20% less |
| Repurpose.io | $15/mo | Creator | $29 | Better AI |

### Differentiation

**Unique Value:**
- AI + Scheduling + Distribution = one tool
- Groq = fastest/cheapest AI
- Distribution focus vs. just creation
- Affordable entry point

**Trade-offs:**
- Fewer templates than Jasper
- Less scheduling than Buffer
- Newer brand (less trust)

---

## Implementation Checklist

### Pre-Launch (Weeks 0-2)

- [ ] Stripe products/prices created
- [ ] Pricing page designed and built
- [ ] Tier enforcement implemented
- [ ] Upgrade flows tested
- [ ] Overage billing configured
- [ ] Coupon codes created
- [ ] Annual discount logic implemented

### Launch (Weeks 3-4)

- [ ] Pricing page live
- [ ] Upgrade CTAs in product
- [ ] Email sequences active
- [ ] Support team trained on tiers
- [ ] Analytics tracking configured

### Post-Launch (Weeks 5-8)

- [ ] Monitor conversion rates
- [ ] A/B test pricing page
- [ ] Analyze upgrade reasons
- [ ] Adjust overage pricing if needed
- [ ] Launch annual plan promotions

---

## Success Metrics

### Conversion Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Free → Paid | >5% | Within 30 days |
| Trial → Paid | >15% | If using trial model |
| Creator → Pro | >10% | Monthly upgrade rate |
| Pro → Team | >5% | Monthly upgrade rate |
| Annual adoption | >30% | Of paid customers |

### Revenue Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| MRR growth | >20%/mo | First 6 months |
| ARPU | >$40 | Month 6 |
| Net Revenue Retention | >110% | Month 6 |
| Gross Revenue Retention | >90% | Month 6 |

### Support Metrics

| Metric | Free | Creator | Pro | Team | Enterprise |
|--------|------|---------|-----|------|------------|
| Response time | N/A | 24h | 4h | 1h | 30min |
| CSAT target | N/A | >80% | >85% | >90% | >95% |
| First contact resolution | N/A | >60% | >70% | >80% | >90% |

---

## Conclusion

This pricing structure balances accessibility for individual creators with powerful features for teams and enterprises. The key principles:

1. **Free is generous** - 50 generations enough to demonstrate value
2. **Clear upgrade path** - Each tier adds significant value
3. **Annual incentives** - 17% discount drives cash flow
4. **Enterprise flexibility** - Custom pricing for complex needs
5. **Value-based pricing** - Price based on value delivered, not cost

**Next Steps:**
1. Implement Stripe products for each tier
2. Build tier enforcement middleware
3. Design pricing page with clear comparison
4. Set up analytics to track conversion
5. Prepare launch promotion codes

---

*Document prepared by Neo DevOrg Business Analyst*  
*Version 1.0 - April 13, 2026*  
*Next Review: Post-launch pricing optimization*