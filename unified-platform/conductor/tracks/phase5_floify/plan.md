# Phase 5: Floify Integration & Frontend

> **Goal**: Connect the "Apply Now" flow to Floify for lead capture and application processing. Build the Next.js frontend components.

---

## 📋 Task Breakdown

### Task 5.1: Implement Floify Lead Push

**Agent**: Pricing Engineer  
**Priority**: P0 - Critical  
**Estimated Time**: 2-3 hours

#### Context
When a borrower completes the quote wizard and wants to apply, we push their information to Floify via the Prospects API. Floify then sends them an email with a link to complete the full application.

#### Floify API Reference
- Endpoint: `POST https://api.floify.com/v1/prospects`
- Auth: API Key in header
- Docs: See `FLOIFY-API/` folder

#### Instructions

1. **Create Floify client**
   ```python
   # api/integrations/floify.py
   
   import httpx
   from django.conf import settings
   from typing import Optional
   import logging
   
   logger = logging.getLogger(__name__)
   
   class FloifyClient:
       """
       Client for Floify API integration.
       
       Handles:
       - Creating prospects (leads)
       - Fetching application data
       - Processing webhooks
       """
       
       BASE_URL = "https://api.floify.com/v1"
       
       def __init__(self):
           self.api_key = settings.FLOIFY_API_KEY
           self.client = httpx.Client(
               base_url=self.BASE_URL,
               headers={
                   'Authorization': f'Bearer {self.api_key}',
                   'Content-Type': 'application/json',
               },
               timeout=30.0
           )
       
       def create_prospect(
           self,
           first_name: str,
           last_name: str,
           email: str,
           phone: Optional[str] = None,
           loan_amount: Optional[int] = None,
           property_address: Optional[str] = None,
           loan_purpose: Optional[str] = None,
           **extra_fields
       ) -> dict:
           """
           Create a new prospect in Floify.
           
           Floify will send the prospect an email invitation to complete
           their loan application on custommortgage.floify.com.
           
           Args:
               first_name: Borrower's first name
               last_name: Borrower's last name
               email: Email address (required)
               phone: Mobile phone number
               loan_amount: Requested loan amount
               property_address: Subject property address
               loan_purpose: purchase, refinance, cash_out
           
           Returns:
               Floify prospect response with ID and status
           """
           payload = {
               'firstName': first_name,
               'lastName': last_name,
               'email': email,
           }
           
           if phone:
               payload['mobilePhoneNumber'] = phone
           if loan_amount:
               payload['loanAmount'] = loan_amount
           if property_address:
               payload['subjectPropertyAddress'] = property_address
           if loan_purpose:
               payload['loanPurpose'] = loan_purpose
           
           # Add any extra fields
           payload.update(extra_fields)
           
           try:
               response = self.client.post('/prospects', json=payload)
               response.raise_for_status()
               
               data = response.json()
               logger.info(f"Created Floify prospect: {data.get('id')}")
               return data
               
           except httpx.HTTPError as e:
               logger.error(f"Floify API error: {e}")
               raise FloifyAPIError(str(e))
       
       def get_application(self, loan_id: str) -> dict:
           """Fetch full application data (1003 JSON format)."""
           response = self.client.get(f'/loans/{loan_id}')
           response.raise_for_status()
           return response.json()
       
       def get_1003_json(self, loan_id: str) -> dict:
           """Fetch application in 1003 JSON schema format."""
           response = self.client.get(f'/loans/{loan_id}/1003')
           response.raise_for_status()
           return response.json()
   
   
   class FloifyAPIError(Exception):
       """Raised when Floify API call fails."""
       pass
   ```

2. **Create API endpoint for lead submission**
   ```python
   # api/views.py
   
   class LeadSubmitView(APIView):
       """
       POST /api/v1/leads/
       
       Submit a lead to Floify after quote wizard completion.
       """
       permission_classes = [AllowAny]
       
       def post(self, request):
           serializer = LeadSubmitSerializer(data=request.data)
           serializer.is_valid(raise_exception=True)
           
           data = serializer.validated_data
           
           # Push to Floify
           client = FloifyClient()
           try:
               result = client.create_prospect(
                   first_name=data['first_name'],
                   last_name=data['last_name'],
                   email=data['email'],
                   phone=data.get('phone'),
                   loan_amount=data.get('loan_amount'),
                   property_address=data.get('property_address'),
               )
               
               return Response({
                   'success': True,
                   'floify_id': result.get('id'),
                   'message': 'Application link sent to your email'
               })
               
           except FloifyAPIError as e:
               return Response(
                   {'success': False, 'error': str(e)},
                   status=500
               )
   ```

3. **Add settings**
   ```python
   # config/settings/base.py
   
   FLOIFY_API_KEY = env('FLOIFY_API_KEY')
   FLOIFY_WEBHOOK_SECRET = env('FLOIFY_WEBHOOK_SECRET', default='')
   ```

#### Success Criteria
- [ ] FloifyClient creates prospects successfully
- [ ] API endpoint accepts lead submissions
- [ ] Floify sends email to prospect
- [ ] Error handling for API failures

---

### Task 5.2: Handle Floify Webhooks

**Agent**: Pricing Engineer  
**Priority**: P1 - High  
**Estimated Time**: 2-3 hours

#### Context
When borrowers complete their application on Floify, we receive webhook events. We need to sync this data back to Django for the borrower dashboard.

#### Instructions

1. **Create Application model**
   ```python
   # applications/models.py
   
   class Application(TimestampedModel):
       """
       Loan application synced from Floify.
       
       Stores application status and key data for borrower dashboard.
       """
       
       STATUS_CHOICES = [
           ('created', 'Created'),
           ('in_progress', 'In Progress'),
           ('submitted', 'Submitted'),
           ('processing', 'Processing'),
           ('approved', 'Approved'),
           ('funded', 'Funded'),
           ('denied', 'Denied'),
       ]
       
       # Floify identifiers
       floify_id = models.CharField(max_length=100, unique=True)
       floify_loan_id = models.CharField(max_length=100, blank=True)
       
       # Borrower info
       borrower_email = models.EmailField()
       borrower_first_name = models.CharField(max_length=100)
       borrower_last_name = models.CharField(max_length=100)
       
       # Loan details
       loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
       property_address = models.TextField(blank=True)
       loan_purpose = models.CharField(max_length=50, blank=True)
       
       # Status
       status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
       status_updated_at = models.DateTimeField(auto_now=True)
       
       # Raw Floify data (for debugging)
       floify_data = models.JSONField(default=dict)
       
       class Meta:
           ordering = ['-created_at']
       
       def __str__(self):
           return f"{self.borrower_last_name} - {self.loan_amount}"
   ```

2. **Update webhook handler**
   ```python
   # api/views.py
   
   import hmac
   import hashlib
   
   @api_view(['POST'])
   @permission_classes([AllowAny])
   def floify_webhook(request):
       """
       Webhook handler for Floify application events.
       
       Events:
       - application.created: New application submitted
       - application.updated: Application status changed
       - application.submitted: Application submitted to lender
       - document.uploaded: New document received
       
       Security: Verify webhook signature if configured.
       """
       
       # Verify webhook signature
       if settings.FLOIFY_WEBHOOK_SECRET:
           signature = request.headers.get('X-Floify-Signature')
           expected = hmac.new(
               settings.FLOIFY_WEBHOOK_SECRET.encode(),
               request.body,
               hashlib.sha256
           ).hexdigest()
           
           if not hmac.compare_digest(signature or '', expected):
               logger.warning("Invalid Floify webhook signature")
               return Response({'error': 'Invalid signature'}, status=401)
       
       event_type = request.data.get('event')
       payload = request.data.get('payload', {})
       
       logger.info(f"Floify webhook: {event_type}")
       
       if event_type == 'application.created':
           return _handle_application_created(payload)
       
       elif event_type == 'application.updated':
           return _handle_application_updated(payload)
       
       elif event_type == 'application.submitted':
           return _handle_application_submitted(payload)
       
       return Response({'received': True})
   
   
   def _handle_application_created(payload):
       """Handle new application from Floify."""
       floify_id = payload.get('id')
       
       # Fetch full application data
       client = FloifyClient()
       app_data = client.get_application(floify_id)
       
       # Create or update local record
       Application.objects.update_or_create(
           floify_id=floify_id,
           defaults={
               'borrower_email': app_data.get('email'),
               'borrower_first_name': app_data.get('firstName'),
               'borrower_last_name': app_data.get('lastName'),
               'loan_amount': app_data.get('loanAmount'),
               'property_address': app_data.get('subjectPropertyAddress'),
               'status': 'in_progress',
               'floify_data': app_data,
           }
       )
       
       return Response({'processed': True})
   
   
   def _handle_application_updated(payload):
       """Handle application status update."""
       floify_id = payload.get('id')
       new_status = payload.get('status', '').lower()
       
       try:
           app = Application.objects.get(floify_id=floify_id)
           
           # Map Floify status to our status
           status_map = {
               'submitted': 'submitted',
               'processing': 'processing',
               'approved': 'approved',
               'funded': 'funded',
               'denied': 'denied',
           }
           
           if new_status in status_map:
               app.status = status_map[new_status]
               app.save()
               logger.info(f"Updated application {floify_id} to {new_status}")
       
       except Application.DoesNotExist:
           logger.warning(f"Application not found: {floify_id}")
       
       return Response({'processed': True})
   ```

3. **Wire up webhook URL**
   ```python
   # api/urls.py
   urlpatterns = [
       path('v1/webhooks/floify/', floify_webhook, name='floify-webhook'),
   ]
   ```

#### Success Criteria
- [ ] Webhook endpoint receives Floify events
- [ ] Application model stores synced data
- [ ] Status updates reflected in database
- [ ] Signature verification (if secret configured)

---

### Task 5.3: Build Quote Wizard Frontend

**Agent**: Frontend Architect  
**Priority**: P0 - Critical  
**Estimated Time**: 4-5 hours

#### Context
The quote wizard is the primary user-facing feature. It collects borrower information, calls the Django API, and displays matching loan programs.

#### Instructions

1. **Create quote wizard component**
   ```typescript
   // components/QuoteWizard/QuoteWizard.tsx
   
   'use client';
   
   import { useState } from 'react';
   import { StepIndicator } from './StepIndicator';
   import { PurposeStep } from './steps/PurposeStep';
   import { PropertyStep } from './steps/PropertyStep';
   import { LoanInfoStep } from './steps/LoanInfoStep';
   import { ContactStep } from './steps/ContactStep';
   import { ResultsStep } from './steps/ResultsStep';
   
   interface QuoteData {
     purpose: string;
     propertyType: string;
     propertyState: string;
     propertyValue: number;
     loanAmount: number;
     creditScore: number;
     occupancy: string;
     firstName?: string;
     lastName?: string;
     email?: string;
     phone?: string;
   }
   
   const STEPS = [
     { id: 'purpose', title: 'Loan Purpose' },
     { id: 'property', title: 'Property Info' },
     { id: 'loan', title: 'Loan Details' },
     { id: 'contact', title: 'Contact Info' },
     { id: 'results', title: 'Your Quotes' },
   ];
   
   export function QuoteWizard() {
     const [currentStep, setCurrentStep] = useState(0);
     const [data, setData] = useState<Partial<QuoteData>>({});
     const [results, setResults] = useState<any[]>([]);
     const [loading, setLoading] = useState(false);
     
     const updateData = (updates: Partial<QuoteData>) => {
       setData(prev => ({ ...prev, ...updates }));
     };
     
     const nextStep = () => {
       if (currentStep < STEPS.length - 1) {
         setCurrentStep(prev => prev + 1);
       }
     };
     
     const prevStep = () => {
       if (currentStep > 0) {
         setCurrentStep(prev => prev - 1);
       }
     };
     
     const submitQuote = async () => {
       setLoading(true);
       
       try {
         const response = await fetch('/api/v1/quote/', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
             property_state: data.propertyState,
             loan_amount: data.loanAmount,
             credit_score: data.creditScore,
             property_value: data.propertyValue,
             property_type: data.propertyType,
             loan_purpose: data.purpose,
             occupancy: data.occupancy,
           }),
         });
         
         const result = await response.json();
         setResults(result.quotes || []);
         nextStep();
       } catch (error) {
         console.error('Quote error:', error);
       } finally {
         setLoading(false);
       }
     };
     
     return (
       <div className="max-w-2xl mx-auto p-6">
         <StepIndicator 
           steps={STEPS} 
           currentStep={currentStep} 
         />
         
         <div className="mt-8">
           {currentStep === 0 && (
             <PurposeStep 
               data={data} 
               updateData={updateData} 
               onNext={nextStep} 
             />
           )}
           
           {currentStep === 1 && (
             <PropertyStep 
               data={data} 
               updateData={updateData} 
               onNext={nextStep}
               onBack={prevStep}
             />
           )}
           
           {currentStep === 2 && (
             <LoanInfoStep 
               data={data} 
               updateData={updateData} 
               onNext={nextStep}
               onBack={prevStep}
             />
           )}
           
           {currentStep === 3 && (
             <ContactStep 
               data={data} 
               updateData={updateData} 
               onSubmit={submitQuote}
               onBack={prevStep}
               loading={loading}
             />
           )}
           
           {currentStep === 4 && (
             <ResultsStep 
               quotes={results}
               borrowerData={data}
             />
           )}
         </div>
       </div>
     );
   }
   ```

2. **Create step components**
   ```typescript
   // components/QuoteWizard/steps/PurposeStep.tsx
   
   interface PurposeStepProps {
     data: Partial<QuoteData>;
     updateData: (updates: Partial<QuoteData>) => void;
     onNext: () => void;
   }
   
   const PURPOSE_OPTIONS = [
     { value: 'purchase', label: 'Purchase', icon: '🏠' },
     { value: 'refinance', label: 'Refinance', icon: '🔄' },
     { value: 'cash_out', label: 'Cash-Out Refinance', icon: '💰' },
     { value: 'construction', label: 'Construction', icon: '🏗️' },
   ];
   
   export function PurposeStep({ data, updateData, onNext }: PurposeStepProps) {
     return (
       <div>
         <h2 className="text-2xl font-bold mb-6">
           What do you want to do?
         </h2>
         
         <div className="grid grid-cols-2 gap-4">
           {PURPOSE_OPTIONS.map(option => (
             <button
               key={option.value}
               onClick={() => {
                 updateData({ purpose: option.value });
                 onNext();
               }}
               className={`
                 p-6 border-2 rounded-lg text-left
                 hover:border-blue-500 hover:bg-blue-50
                 ${data.purpose === option.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
               `}
             >
               <span className="text-3xl">{option.icon}</span>
               <p className="mt-2 font-medium">{option.label}</p>
             </button>
           ))}
         </div>
       </div>
     );
   }
   ```

3. **Create results display**
   ```typescript
   // components/QuoteWizard/steps/ResultsStep.tsx
   
   interface Quote {
     lender: string;
     program: string;
     rate_range: string;
     total_adjustment: number;
   }
   
   export function ResultsStep({ quotes, borrowerData }: { quotes: Quote[], borrowerData: any }) {
     const [applying, setApplying] = useState(false);
     
     const handleApply = async (quote: Quote) => {
       setApplying(true);
       
       try {
         await fetch('/api/v1/leads/', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
             first_name: borrowerData.firstName,
             last_name: borrowerData.lastName,
             email: borrowerData.email,
             phone: borrowerData.phone,
             loan_amount: borrowerData.loanAmount,
             selected_program: quote.program,
           }),
         });
         
         // Show success message
         alert('Check your email for the application link!');
       } catch (error) {
         console.error('Apply error:', error);
       } finally {
         setApplying(false);
       }
     };
     
     if (quotes.length === 0) {
       return (
         <div className="text-center py-12">
           <h2 className="text-2xl font-bold mb-4">No Matches Found</h2>
           <p className="text-gray-600">
             We couldn't find programs matching your criteria.
             Please call us at (877) 976-5663 for personalized assistance.
           </p>
         </div>
       );
     }
     
     return (
       <div>
         <h2 className="text-2xl font-bold mb-6">
           Your Loan Options ({quotes.length} matches)
         </h2>
         
         <div className="space-y-4">
           {quotes.map((quote, index) => (
             <div 
               key={index}
               className="border rounded-lg p-6 hover:shadow-md transition"
             >
               <div className="flex justify-between items-start">
                 <div>
                   <h3 className="font-bold text-lg">{quote.lender}</h3>
                   <p className="text-gray-600">{quote.program}</p>
                 </div>
                 <div className="text-right">
                   <p className="text-2xl font-bold text-blue-600">
                     {quote.rate_range}
                   </p>
                   {quote.total_adjustment !== 0 && (
                     <p className="text-sm text-gray-500">
                       Adjustment: {quote.total_adjustment > 0 ? '+' : ''}{quote.total_adjustment} pts
                     </p>
                   )}
                 </div>
               </div>
               
               <button
                 onClick={() => handleApply(quote)}
                 disabled={applying}
                 className="mt-4 w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
               >
                 {applying ? 'Sending...' : 'Apply Now'}
               </button>
             </div>
           ))}
         </div>
       </div>
     );
   }
   ```

#### Success Criteria
- [ ] Quote wizard collects all required fields
- [ ] API call returns matching programs
- [ ] Results display rates and adjustments
- [ ] Apply button triggers Floify lead push

---

### Task 5.4: Build Borrower Dashboard

**Agent**: Frontend Architect  
**Priority**: P2 - Medium  
**Estimated Time**: 3-4 hours

#### Context
After applying, borrowers should be able to see their application status on the unified platform.

#### Instructions

1. **Create dashboard page**
   ```typescript
   // app/dashboard/page.tsx
   
   import { getServerSession } from 'next-auth';
   import { redirect } from 'next/navigation';
   import { ApplicationList } from '@/components/Dashboard/ApplicationList';
   
   export default async function DashboardPage() {
     const session = await getServerSession();
     
     if (!session) {
       redirect('/login');
     }
     
     // Fetch applications for this user
     const response = await fetch(
       `${process.env.API_URL}/api/v1/applications/`,
       {
         headers: {
           Authorization: `Bearer ${session.accessToken}`,
         },
       }
     );
     
     const applications = await response.json();
     
     return (
       <div className="max-w-4xl mx-auto p-6">
         <h1 className="text-3xl font-bold mb-8">Your Applications</h1>
         <ApplicationList applications={applications} />
       </div>
     );
   }
   ```

2. **Create application list component** (similar pattern)

#### Success Criteria
- [ ] Dashboard shows user's applications
- [ ] Status updates reflected in real-time
- [ ] Secure (requires authentication)

---

## 📊 Progress Tracking

| Task | Status | Blocker | Notes |
|------|--------|---------|-------|
| 5.1 Floify Lead Push | ⏳ | - | Needs API key |
| 5.2 Webhooks | ⏳ | 5.1 | - |
| 5.3 Quote Wizard | ⏳ | Phase 2 | - |
| 5.4 Dashboard | ⏳ | 5.2 | - |

---

*Last Updated: 2026-01-11*
