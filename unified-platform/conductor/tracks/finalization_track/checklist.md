# Finalization Track Checklist

## F.1: Wagtail CMS Models
- [ ] Refactor `cms/models.py` to package structure
- [ ] `ProgramPage` implemented (64 fields, StreamField FAQ)
- [ ] `BlogPage` implemented (StreamField body)
- [ ] `FundedLoanPage` implemented
- [ ] `LegacyRecreatedPage` migrated
- [ ] `HomePage` / `StandardPage` migrated
- [ ] Migrations created and applied
- [ ] Admin interface verified

## F.2: WordPress Content Extraction
- [ ] Extractor script created
- [ ] Content exported to JSON

## F.3: Content Import
- [ ] Import command created
- [ ] Content imported successfully
- [ ] URLs verified

## F.4: Office Locations
- [ ] Office model created
- [ ] CSV import verified

## F.5: Programmatic SEO
- [ ] Proximity service implemented
- [ ] Routing logic implemented

## F.6: AI Content
- [ ] OpenRouter configured
- [ ] Content generator service created

## F.7: Frontend CMS
- [ ] Next.js API client configured
- [ ] Page templates built

## F.8: Floify
- [ ] Webhook handler finalized
- [ ] Lead push finalized

## F.9: Testing
- [ ] E2E tests pass
- [ ] Security check pass

## F.10: Deployment
- [ ] Production build success
- [ ] Live verification
