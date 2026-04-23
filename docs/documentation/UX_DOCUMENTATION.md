# 📱 UX Folder - Complete Documentation

## 📋 Mục Lục
1. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
2. [Cấu Hình & Setup](#cấu-hình--setup)
3. [Thư Mục Chính](#thư-mục-chính)
4. [Thư Mục Phụ](#thư-mục-phụ)
5. [Hệ Thống Phân Cấp Component](#hệ-thống-phân-cấp-component)

---

## Cấu Trúc Thư Mục

```
UX/
├── 📄 Tệp Cấu Hình
│   ├── package.json              # Dependencies & scripts
│   ├── tsconfig.json             # TypeScript configuration
│   ├── next.config.mjs           # Next.js configuration
│   ├── postcss.config.mjs        # PostCSS configuration
│   ├── components.json           # Shadcn/ui configuration
│   ├── project_spec.json         # Project specifications
│   ├── pnpm-lock.yaml            # Dependency lock file
│   └── next-env.d.ts             # Next.js type definitions
│
├── 📁 app/                       # Next.js App Router
│   ├── layout.tsx                # Root layout wrapper
│   ├── page.tsx                  # Main application entry point
│   └── globals.css               # Global styles
│
├── 📁 components/                # React Components (Reusable)
│   ├── app-sidebar.tsx           # Main navigation sidebar
│   ├── doctor-header.tsx         # Doctor profile header
│   ├── new-patient-modal.tsx     # Patient creation modal
│   ├── theme-provider.tsx        # Theme provider wrapper
│   │
│   ├── 📁 patients/              # Patient Management Components
│   │   ├── patients-dashboard.tsx     # Main patient list view
│   │   ├── patient-list.tsx          # Patient list table
│   │   ├── patient-profile.tsx       # Detailed patient view
│   │   └── compare-modal.tsx         # Compare multiple patients
│   │
│   ├── 📁 scanner/               # OCT Image Scanning Components
│   │   ├── scanner-dashboard.tsx      # Main scanner interface
│   │   ├── image-uploader.tsx        # File upload handler
│   │   ├── analysis-viewer.tsx       # Analysis results display
│   │   ├── inference-metrics.tsx     # Performance metrics
│   │   ├── validation-panel.tsx      # Doctor validation UI
│   │   ├── patient-context-panel.tsx # Patient info context
│   │   ├── patient-assignment.tsx    # Link image to patient
│   │   ├── export-pdf.tsx            # PDF export functionality
│   │   └── processing-overlay.tsx    # Loading/processing state
│   │
│   └── 📁 ui/                    # Shadcn/ui Components (45+ UI Components)
│       ├── accordion.tsx              # Collapsible sections
│       ├── alert.tsx                  # Alert messages
│       ├── alert-dialog.tsx           # Confirmation dialogs
│       ├── badge.tsx                  # Label badges
│       ├── breadcrumb.tsx             # Navigation breadcrumb
│       ├── button.tsx                 # Buttons
│       ├── button-group.tsx           # Button groups
│       ├── calendar.tsx               # Date picker calendar
│       ├── card.tsx                   # Card containers
│       ├── carousel.tsx               # Image carousel
│       ├── chart.tsx                  # Chart components
│       ├── collapsible.tsx            # Toggle sections
│       ├── command.tsx                # Command palette
│       ├── context-menu.tsx           # Right-click menu
│       ├── dialog.tsx                 # Modal dialogs
│       ├── drawer.tsx                 # Slide-out drawer
│       ├── dropdown-menu.tsx          # Dropdown menus
│       ├── empty.tsx                  # Empty state
│       ├── field.tsx                  # Form field
│       ├── form.tsx                   # Form wrapper
│       ├── hover-card.tsx             # Hover tooltip card
│       ├── input.tsx                  # Text input
│       ├── input-group.tsx            # Input with prefix/suffix
│       ├── input-otp.tsx              # OTP input
│       ├── kbd.tsx                    # Keyboard key display
│       ├── label.tsx                  # Form labels
│       ├── menubar.tsx                # Top menu bar
│       ├── navigation-menu.tsx        # Navigation menu
│       ├── pagination.tsx             # Page navigation
│       ├── popover.tsx                # Floating popover
│       ├── progress.tsx               # Progress bars
│       ├── radio-group.tsx            # Radio button groups
│       ├── resizable.tsx              # Resizable panels
│       ├── scroll-area.tsx            # Custom scrollable area
│       ├── select.tsx                 # Dropdown select
│       ├── separator.tsx              # Divider line
│       ├── sheet.tsx                  # Side sheet panel
│       ├── sidebar.tsx                # Sidebar layout
│       ├── skeleton.tsx               # Loading skeleton
│       ├── slider.tsx                 # Slider input
│       ├── sonner.tsx                 # Toast notifications
│       ├── spinner.tsx                # Loading spinner
│       ├── table.tsx                  # Data table
│       ├── tabs.tsx                   # Tab navigation
│       ├── textarea.tsx               # Multi-line text input
│       ├── toast.tsx                  # Toast notifications
│       ├── toaster.tsx                # Toast container
│       ├── toggle.tsx                 # Toggle switch
│       ├── toggle-group.tsx           # Toggle button group
│       ├── tooltip.tsx                # Tooltip overlay
│       ├── use-mobile.ts              # Mobile detection hook
│       └── use-toast.ts               # Toast notification hook
│
├── 📁 hooks/                     # React Custom Hooks
│   ├── use-mobile.ts             # Mobile responsiveness detection
│   └── use-toast.ts              # Toast notification management
│
├── 📁 lib/                       # Utilities & Helpers
│   ├── store.tsx                 # Global state management (React Context)
│   ├── api.ts                    # Backend API client
│   └── utils.ts                  # Utility functions
│
├── 📁 public/                    # Static assets
│   └── (images, icons, etc.)
│
├── 📁 styles/                    # CSS Styles
│   └── globals.css               # Global stylesheet
│
└── 📁 components.json            # Shadcn/ui config
```

---

## Cấu Hình & Setup

### Package.json - Dependencies

| Package | Version | Mục Đích |
|---------|---------|---------|
| **next** | 16.1.6 | React framework with App Router |
| **react** | 19.x+ | UI library |
| **typescript** | Latest | Type safety |
| **tailwindcss** | ^3.x | Utility-first CSS |
| **shadcn/ui** | Latest | Pre-built UI components |
| **@radix-ui/** | Various | Accessible component primitives |
| **lucide-react** | ^0.564.0 | Icon library |
| **next-themes** | ^0.4.6 | Theme switching (dark/light mode) |
| **zod** | Latest | Data validation |
| **react-hook-form** | ^7.x | Form state management |
| **@hookform/resolvers** | ^3.9.1 | Form validation resolvers |
| **sonner** | Latest | Toast notification library |
| **embla-carousel-react** | 8.6.0 | Image carousel |
| **date-fns** | 4.1.0 | Date utilities |
| **cmdk** | 1.1.1 | Command palette |
| **@vercel/analytics** | 1.6.1 | Vercel analytics |

### Scripts

```json
{
  "dev": "next dev",           // Start development server (port 3000)
  "build": "next build",       // Production build
  "start": "next start",       // Start production server
  "lint": "eslint ."           // Run ESLint
}
```

### Các File Cấu Hình Quan Trọng

| File | Mục Đích | Chi Tiết |
|------|---------|---------|
| **tsconfig.json** | TypeScript config | Path aliases (@/), strict mode |
| **next.config.mjs** | Next.js config | `ignoreBuildErrors: true`, image optimization disabled |
| **postcss.config.mjs** | CSS processing | TailwindCSS integration |
| **components.json** | Shadcn/ui config | Component style: "new-york", icons from lucide |
| **project_spec.json** | Project metadata | App name, description, version |

---

## Thư Mục Chính

### 1. 📁 `app/` - Next.js Application Root

#### `layout.tsx` - Root Layout Wrapper
**Chức năng:** Bao bọc toàn bộ ứng dụng
- Cấu hình metadata (title, favicon)
- Cài đặt viewport
- Integrate analytics
- Provide theme wrapper
- Render Toaster (toast notifications)

**Cách hoạt động:**
1. Render `<html>` tag
2. Inject `<body>` with global CSS
3. Include `<Analytics />` component
4. Wrap children with theme provider

#### `page.tsx` - Main Application Entry Point
**Chức năng:** Trang chính ứng dụng
- Khởi tạo `AppProvider` (state management)
- Render sidebar navigation
- Render current page content (Scanner hoặc Patients)

**Cách hoạt động:**
1. Initialize Redux/Context state (`AppProvider`)
2. Read `currentPage` from state
3. Conditionally render `<ScannerDashboard />` hoặc `<PatientsDashboard />`
4. Layout: Sidebar (trái) + Main content (phải)

#### `globals.css` - Global Styles
**Chức năng:** CSS toàn cục cho ứng dụng
- TailwindCSS directives
- CSS variables cho theme
- Global resets
- Custom utility classes

**Cấu trúc:**
```css
@tailwind base;         /* Tailwind base styles */
@tailwind components;   /* Tailwind component classes */
@tailwind utilities;    /* Tailwind utility classes */

:root {
  --background: ...     /* CSS variables cho theme */
  --foreground: ...
  --sidebar: ...
  /* Hơn 40 CSS variables cho màu sắc */
}
```

---

### 2. 📁 `components/` - Business Logic Components

#### Core Components

##### `app-sidebar.tsx` - Main Navigation
**Chức năng:** Sidebar navigation giữa Scanner và Patients pages
**Props:** None (uses global state)
**State:**
- `collapsed` - sidebar collapse/expand state

**Cách hoạt động:**
1. Display RetinaAI logo at top
2. Navigation buttons (Scanner, Patients)
3. User profile section
4. Collapse/expand animation
5. Active page highlighting

**Key Features:**
- Responsive (collapses on mobile)
- Animation transition
- Active state styling
- Keyboard navigation

---

##### `doctor-header.tsx` - Doctor Profile Header
**Chức năng:** Hiển thị thông tin bác sĩ và cài đặt
**Props:** None (uses global state)
**State:** Doctor profile info từ state

**Cách hoạt động:**
1. Show doctor name, title, avatar initials
2. Display notification bell icon
3. Settings gear icon
4. Dropdown menu for actions

**UI Elements:**
- Avatar with initials
- Name + Title
- Bell icon (notifications)
- Settings dropdown

---

##### `new-patient-modal.tsx` - Patient Creation Modal
**Chức năng:** Form tạo bệnh nhân mới
**Props:** `onClose()` callback
**State:** Form inputs (name, DOB, gender, contact, medical notes)

**Cách hoạt động:**
1. Modal appears when "New Patient" clicked
2. Form inputs: name, date of birth, gender, contact, medical notes
3. Calculate age from DOB automatically
4. Submit to backend: API call to `POST /api/v1/patients`
5. Close modal on success

**Form Fields:**
```typescript
- name: string (required)          // Patient name
- dob: string (ISO date, optional) // Date of birth for age calculation
- gender: string (optional)        // "Male" | "Female" | "Other"
- contact: string (optional)       // Phone/email
- medical_notes: string (optional) // Additional notes
```

---

##### `theme-provider.tsx` - Theme Management
**Chức năng:** Cung cấp dark/light theme switching
**Props:** `{ children, ... }`
**Integration:** Wraps entire app with `next-themes`

**Cách hoạt động:**
1. Wrap app with `ThemeProvider`
2. Detect system theme preference
3. Allow manual theme toggle
4. Persist theme in localStorage
5. Apply CSS variables based on theme

**Themes:**
- Light mode (default)
- Dark mode
- System mode (follows OS setting)

---

#### 3. 📁 `components/patients/` - Patient Management

##### `patients-dashboard.tsx` - Patient Management Main View
**Chức năng:** Trang quản lý bệnh nhân
**State:**
- `patients: Patient[]` - List of patients
- `selectedPatientId: number | null` - Currently selected patient
- `sortOrder: "asc" | "desc"` - Sort order

**Cách hoạt động:**
1. Load patients from backend on mount
2. Display patient list in table format
3. Click patient row → show patient profile
4. "New Patient" button → open modal
5. Compare patients feature
6. Sort by name, age, last visit

**Key Features:**
- Patient search/filter
- Sort by multiple columns
- Pagination
- Bulk actions (delete, reassign)
- Patient profile expandable view

**Data Displayed:**
- Name, Age, Gender
- Contact, Medical notes
- Last visit date
- Total scans count
- Actions (view, edit, delete)

---

##### `patient-list.tsx` - Patient List Table
**Chức năng:** Hiển thị danh sách bệnh nhân ở dạng bảng
**Props:**
```typescript
{
  patients: Patient[]
  selectedId?: number
  onSelectPatient: (id: number) => void
  onDeletePatient: (id: number) => void
}
```

**Cách hoạt động:**
1. Render table with patient rows
2. Highlight selected row
3. Show edit/delete action buttons
4. Support sorting by clicking column headers
5. Show pagination controls

**Columns:**
- Name | Age | Gender | Contact | Last Visit | Total Scans | Actions

---

##### `patient-profile.tsx` - Patient Detail View
**Chức năng:** Hiển thị chi tiết bệnh nhân và lịch sử scan
**Props:**
```typescript
{
  patientId: number
  onBack: () => void
}
```

**Cách hoạt động:**
1. Fetch patient data from backend
2. Display personal info (editable)
3. Show all scans associated with patient
4. Display scan details (image, lesion type, confidence)
5. Edit button for patient info
6. Download scan images as PDF

**Sections:**
- Personal Information
- Scan History
- Medical Notes
- Action Buttons

---

##### `compare-modal.tsx` - Compare Multiple Patients
**Chức năng:** So sánh kết quả quét giữa các bệnh nhân
**Props:**
```typescript
{
  patientIds: number[]
  onClose: () => void
}
```

**Cách hoạt động:**
1. Select 2-3 patients
2. Open comparison modal
3. Display side-by-side scan results
4. Show analysis metrics for each patient
5. Highlight differences

---

#### 4. 📁 `components/scanner/` - OCT Image Analysis

##### `scanner-dashboard.tsx` - Main Scanner Interface
**Chức năng:** Giao diện quét ảnh OCT chính
**Pages:**
1. Upload page (select image)
2. Processing page (waiting for inference)
3. Result page (show analysis results)

**State:**
```typescript
scannerMode: "upload" | "processing" | "result"
currentScan: ScanResult | null
selectedPatientId: number | null
uploadedFile: File | null
```

**Cách hoạt động:**
1. Show upload area or current page based on mode
2. Handle file upload
3. Send to backend for analysis
4. Polling or WebSocket for results
5. Display results when ready
6. Option to link scan to patient
7. Save/export scan

---

##### `image-uploader.tsx` - File Upload Handler
**Chức năng:** Xử lý upload ảnh OCT
**Props:**
```typescript
{
  onFileSelected: (file: File) => void
  onUpload: (file: File) => Promise<void>
  isLoading?: boolean
}
```

**Cách hoạt động:**
1. Drag & drop zone or file picker
2. Validate file type (PNG, JPEG, TIFF)
3. Validate file size (max 10MB)
4. Preview image before upload
5. Upload file to backend
6. Show progress indicator
7. Handle errors

**Validations:**
- File type: image/png, image/jpeg, image/tiff
- Max size: 10MB
- Min size: 100KB

---

##### `analysis-viewer.tsx` - Show Analysis Results
**Chức năng:** Hiển thị kết quả phân tích ảnh
**Props:**
```typescript
{
  scanResult: ScanResult
  onExport: () => void
  onSaveToPatient: (patientId: number) => void
}
```

**Cách hoạt động:**
1. Display original OCT image
2. Overlay segmentation mask
3. Show lesion type classification
4. Display confidence percentage
5. Show inference time
6. Export buttons (PDF, PNG)
7. Save to patient record

**Displays:**
- Original image (left)
- Segmentation mask overlay (right)
- Analysis results (bottom)
  - Lesion type
  - Confidence %
  - Processing time
  - Lesion metrics (area, severity)

---

##### `inference-metrics.tsx` - Performance Metrics
**Chức năng:** Hiển thị thông tin hiệu năng
**Props:**
```typescript
{
  scanResult: ScanResult
}
```

**Data:**
- Inference time (ms)
- Image resolution
- Model name & version
- GPU/CPU status
- Processing device

---

##### `validation-panel.tsx` - Doctor Validation UI
**Chức năng:** Bác sĩ dùng để xác nhận/sửa kết quả AI
**Props:**
```typescript
{
  scanId: number
  currentLabel: string
  confidence: number
  onValidate: (label: string, notes: string) => void
}
```

**Cách hoạt động:**
1. Show current AI prediction
2. Buttons for approve/reject/edit
3. Dropdown to change label if needed
4. Text area for validation notes
5. Submit validation

**Features:**
- Approve AI prediction
- Override with manual label
- Add validation notes
- Mark as "pending" → "approved" or "edited"

---

##### `patient-context-panel.tsx` - Patient Info Context
**Chức năng:** Hiển thị thông tin bệnh nhân liên quan
**Props:**
```typescript
{
  patientId?: number | null
}
```

**Displays:**
- Patient name, age, gender
- Medical history (last 5 scans)
- Previous diagnoses
- "Link to patient" button (if not assigned)

---

##### `patient-assignment.tsx` - Link Image to Patient
**Chức năng:** Gán ảnh quét vào hồ sơ bệnh nhân
**Props:**
```typescript
{
  scanId: number
  onAssign: (patientId: number) => void
}
```

**Cách hoạt động:**
1. Show dropdown with patient list
2. Or "New patient" option
3. Click to assign scan
4. API call to backend
5. Close on success

---

##### `export-pdf.tsx` - PDF Export
**Chức năng:** Xuất kết quả quét thành PDF
**Props:**
```typescript
{
  scanResult: ScanResult
  patientInfo?: Patient
  onExport: (pdf: Blob) => void
}
```

**PDF Content:**
- Header (clinic logo, date)
- Patient info
- Original OCT image
- Segmentation mask
- Analysis results (lesion type, confidence)
- Doctor validation notes
- Footer (signature line)

**Libraries Used:**
- jsPDF or html2pdf

---

##### `processing-overlay.tsx` - Loading State
**Chức năng:** Hiển thị loading animation trong khi xử lý
**Props:**
```typescript
{
  isProcessing: boolean
  message?: string
  progress?: number (0-100)
}
```

**Displays:**
- Spinner animation
- Processing message
- Progress bar (if available)
- Estimated time remaining

---

### 3. 📁 `components/ui/` - Shadcn/ui Components Library

**45+ Pre-built Accessible UI Components** từ shadcn/ui

Các component này là low-level building blocks dùng để xây dựng những component phức tạp hơn.

**Danh sách chính:**

| Component | Mục Đích | Ví Dụ Sử Dụng |
|-----------|---------|---|
| `button.tsx` | Button element | "Submit", "Cancel" |
| `input.tsx` | Text input field | Form inputs |
| `select.tsx` | Dropdown select | Gender selection |
| `checkbox.tsx` | Checkbox | Accept terms |
| `radio-group.tsx` | Radio buttons | Choose one option |
| `textarea.tsx` | Multi-line text | Notes field |
| `label.tsx` | Form labels | Field labels |
| `card.tsx` | Card container | Content wrapper |
| `table.tsx` | Data table | Patient list table |
| `tabs.tsx` | Tab navigation | Scanner/Patients tabs |
| `dialog.tsx` | Modal dialog | Confirmation dialogs |
| `sheet.tsx` | Side panel | Sidebar drawer |
| `popover.tsx` | Floating overlay | Info tooltip |
| `tooltip.tsx` | Hover tooltip | Help text on hover |
| `slider.tsx` | Range slider | Confidence threshold |
| `progress.tsx` | Progress bar | Upload progress |
| `badge.tsx` | Status label | "Approved", "Pending" |
| `alert.tsx` | Alert message | Error/success messages |
| `skeleton.tsx` | Loading placeholder | Skeleton screens |
| `carousel.tsx` | Image carousel | Scan history carousel |
| `calendar.tsx` | Date picker | Birth date picker |
| `pagination.tsx` | Page navigation | Patient list pagination |
| `breadcrumb.tsx` | Navigation path | Page breadcrumb |
| `command.tsx` | Command palette | Search |
| `sonner.tsx` | Toast notification | Quick notifications |
| `spinner.tsx` | Loading spinner | Processing state |

---

### 4. 📁 `lib/` - Utility Libraries

#### `store.tsx` - Global State Management
**Chức năng:** Centralized state management dùng React Context

**State Structure:**
```typescript
// Doctor Profile
doctor: DoctorProfile {
  name: string
  title: string
  avatarInitials: string
}

// Navigation
currentPage: "scanner" | "patients"
setCurrentPage: (page) => void

// Patient Management
patients: Patient[]
patientsLoading: boolean
patientsError: string | null
loadPatients: () => Promise<void>
selectedPatientId: number | null
setSelectedPatientId: (id) => void
addNewPatient: (patient) => Promise<Patient>
updatePatient: (id, updates) => Promise<void>
deletePatient: (id) => Promise<void>

// Scanner State
scannerMode: "upload" | "processing" | "result"
setScannerMode: (mode) => void
currentScan: ScanResult | null
setCurrentScan: (scan) => void
uploadedFile: File | null
setUploadedFile: (file) => void
saveScanToPatient: (patientId, scan) => void

// History
scanHistory: ScanResult[]
loadScanHistory: (patientId?) => Promise<void>
```

**Cách hoạt động:**
1. Create context with initial state
2. Provide `AppProvider` component to wrap app
3. Components use `useAppState()` hook to access state
4. Dispatch actions to update state
5. Auto-fetch data on component mount

**Usage:**
```typescript
const { currentPage, setCurrentPage } = useAppState()
```

---

#### `api.ts` - Backend API Client
**Chức năng:** Tất cả API calls tới backend

**Key Functions:**

```typescript
// Analysis API
async analyzeOCTImage(file: File): Promise<BackendAnalysisResponse>
  - POST /api/v1/analyze
  - Sends image file to backend
  - Returns analysis results

async getScanHistory(limit?: number, skip?: number): Promise<BackendHistoryRecord[]>
  - GET /api/v1/scans
  - Retrieves all previous scans

async getScanById(id: number): Promise<BackendAnalysisResponse>
  - GET /api/v1/scans/{id}
  - Gets specific scan

async healthCheck(): Promise<HealthStatus>
  - GET /api/v1/health
  - Checks backend availability

// Patient API
async createPatient(patient: PatientCreate): Promise<PatientResponse>
  - POST /api/v1/patients
  - Creates new patient

async listPatients(skip?: number, limit?: number): Promise<PatientListResponse>
  - GET /api/v1/patients
  - Lists all patients

async getPatient(id: number): Promise<PatientResponse>
  - GET /api/v1/patients/{id}
  - Gets patient details

async updatePatient(id: number, updates: PatientUpdate): Promise<PatientResponse>
  - PUT /api/v1/patients/{id}
  - Updates patient info

async deletePatient(id: number): Promise<void>
  - DELETE /api/v1/patients/{id}
  - Deletes patient
```

**Error Handling:**
```typescript
try {
  const result = await analyzeOCTImage(file)
} catch (error) {
  // Handle network errors
  // Handle API errors (422, 500)
  // Show user-friendly error message
}
```

---

#### `utils.ts` - Utility Functions
**Chức năng:** Helper functions dùng trong app

**Common Utilities:**
```typescript
cn(...classes) // Merge Tailwind classes
formatDate(date: string) // Format ISO date
formatConfidence(value: number) // Format confidence to %
calculateAge(dob: string) // Calculate age from DOB
truncateText(text: string, length: number) // Truncate long text
getInitials(name: string) // Get name initials
validateEmail(email: string) // Email validation
formatFileSize(bytes: number) // Format file size
```

---

### 5. 📁 `hooks/` - Custom React Hooks

#### `use-mobile.ts` - Mobile Detection
**Chức năng:** Detect nếu app running on mobile device
```typescript
const isMobile = useMobile()

if (isMobile) {
  // Show mobile layout
} else {
  // Show desktop layout
}
```

**Logic:**
- Listen to window resize
- Check viewport width < 768px
- Return boolean

---

#### `use-toast.ts` - Toast Notifications
**Chức năng:** Show toast notifications
```typescript
const { toast } = useToast()

toast({
  title: "Success",
  description: "Patient created successfully",
  variant: "default" // or "destructive", "success"
})
```

**Toast Types:**
- `default` - Neutral notification
- `success` - Success message
- `destructive` - Error message
- `warning` - Warning alert

---

## Hệ Thống Phân Cấp Component

### Data Flow (Redux-like)

```
┌─────────────────────────────────────────────────────────┐
│         User Interactions (Click, Type, etc)             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│    Components (page.tsx, patients-dashboard.tsx, etc)   │
│    - Dispatch actions via hooks                         │
│    - Read state via useAppState()                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│    Global State (lib/store.tsx)                          │
│    - Update state in Context                            │
│    - Side effects (data loading)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│    API Client (lib/api.ts)                               │
│    - Make HTTP requests to backend                      │
│    - Handle responses & errors                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         Backend (FastAPI Port 8000)
```

### Component Hierarchy

```
<root layout.tsx>
  └── <AppProvider> [store.tsx]
      └── <AppSidebar>
      └── <page.tsx>
          ├── <ScannerDashboard> (if currentPage === "scanner")
          │   ├── <ImageUploader>
          │   ├── <ProcessingOverlay>
          │   ├── <AnalysisViewer>
          │   │   ├── <InferenceMetrics>
          │   │   ├── <ValidationPanel>
          │   │   └── <ExportPdf>
          │   ├── <PatientAssignment>
          │   └── <PatientContextPanel>
          │
          └── <PatientsDashboard> (if currentPage === "patients")
              ├── <DoctorHeader>
              ├── <PatientList>
              │   └── [Patient rows...]
              ├── <PatientProfile> (when patient selected)
              │   ├── Patient Info
              │   ├── Scan History
              │   └── Actions
              └── <NewPatientModal> (when "New Patient" clicked)
```

---

## Luồng Hoạt Động Chính

### 1. 📸 Quét Ảnh OCT (Scanner Flow)

```
1. User clicks "Scanner" in sidebar
2. Component mounts: <ScannerDashboard>
3. Show: <ImageUploader> with drag-drop zone
4. User selects/drags image file
5. Validation: Check file type & size
6. Frontend preview image
7. User clicks "Analyze"
8. POST request to backend /api/v1/analyze with file
9. Backend returns ScanResult
   - lesion_type: "Drusen" | "CNV" | "Normal"
   - confidence: 0.92
   - segmentation_mask_base64: "data:image/png;base64,..."
   - image_url: "http://localhost:8000/images/uuid.png"
10. Frontend shows: <AnalysisViewer>
    - Original image on left
    - Segmentation mask overlay on right
    - Metrics below
11. Doctor validates result: <ValidationPanel>
    - Approve or edit label
    - Add notes
    - Mark as "approved" or "edited"
12. Optional: Link to patient: <PatientAssignment>
    - Select patient or create new
    - Save scan to patient record
13. Export result: <ExportPdf>
    - Generate PDF with analysis
    - Download to computer
```

### 2. 👥 Quản Lý Bệnh Nhân (Patient Flow)

```
1. User clicks "Patients" in sidebar
2. Component mounts: <PatientsDashboard>
3. useAppState() → loadPatients()
   - Fetch: GET /api/v1/patients
4. Display: <PatientList> with all patients
5. User searches/filters patient
6. User clicks patient row
7. Show: <PatientProfile>
   - Display patient info
   - List all scans for patient
   - Show scan thumbnails
8. Optional: Create new patient
   - Click "New Patient" → <NewPatientModal>
   - Fill form (name, DOB, gender, contact, notes)
   - POST /api/v1/patients with data
   - New patient appears in list
9. Optional: Compare patients
   - Select 2 patients
   - Click "Compare"
   - Show <CompareModal>
10. Optional: Delete patient
    - Click delete action
    - Confirm dialog
    - DELETE /api/v1/patients/{id}
```

---

## Các Công Nghệ Chính

| Công Nghệ | Phiên Bản | Mục Đích |
|-----------|----------|---------|
| **Next.js** | 16.1.6 | React framework with SSR, SSG |
| **React** | 19.x | UI library |
| **TypeScript** | Latest | Type safety |
| **TailwindCSS** | ^3.x | CSS framework |
| **Shadcn/ui** | Latest | UI component library |
| **Radix UI** | Various | Accessible component primitives |
| **React Hook Form** | ^7.x | Form state management |
| **Zod** | Latest | Schema validation |
| **next-themes** | ^0.4.6 | Theme switching |
| **Lucide React** | ^0.564.0 | 500+ icons |
| **Sonner** | Latest | Toast notifications |
| **Embla Carousel** | 8.6.0 | Image carousel |

---

## Development Tips

### Thêm New Component

```bash
# Method 1: Manual creation
touch components/my-component.tsx

# Method 2: Using shadcn/ui
npx shadcn-ui@latest add button

# Then import and use in other components
import { MyComponent } from "@/components/my-component"
```

### Add CSS Styles

```typescript
// Use Tailwind classes
<div className="flex gap-3 p-4 rounded-lg bg-card text-foreground">

// Or create CSS files in styles/
// Then import in layout.tsx
import "@/styles/custom.css"
```

### Make API Calls

```typescript
// In any component
import * as api from "@/lib/api"

// Wrap in useEffect for data fetching
useEffect(() => {
  api.listPatients().then(setPatients)
}, [])

// Or in event handlers
const handleAnalyze = async (file: File) => {
  const result = await api.analyzeOCTImage(file)
  setCurrentScan(result)
}
```

### Access Global State

```typescript
import { useAppState } from "@/lib/store"

export function MyComponent() {
  const { currentPage, setCurrentPage } = useAppState()
  
  return (
    <button onClick={() => setCurrentPage("scanner")}>
      Go to Scanner
    </button>
  )
}
```

---

## Environment Variables

**File:** `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=RetinaAI
NEXT_PUBLIC_VERSION=1.0.0
```

- `NEXT_PUBLIC_*` sind im Browser sichtbar
- Cần `.local` für local development secrets

---

## Build & Deployment

```bash
# Development
npm run dev              # http://localhost:3000

# Production
npm run build           # Build optimized bundle
npm run start           # Start production server
npm run lint            # Check for errors
```

**Build Output:**
```
.next/
├── server/             # Server-side code
├── static/             # Static assets
└── cache/              # Next.js cache
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Components not updating | Check useAppState() is called |
| API errors | Check backend is running on port 8000 |
| Styling not applied | Ensure Tailwind classes are correct |
| Type errors | Run `tsc --noEmit` to check types |
| Build fails | Clear `.next` and rebuild |

---

**Tài liệu này được cập nhật lần cuối: Tháng 4, 2026**
