# Kith Platform - Comprehensive Project Brief
*A detailed technical specification for building the Kith Platform from scratch*

## Document Structure

This document is organized **by features** (not by pages) because:
- Features are the logical units of functionality
- Features often span multiple pages/views
- Implementation details naturally group by feature
- Easier to understand the system holistically
- Better for onboarding new developers

Each feature section includes:
- Overview & Purpose
- User-facing Pages/Views
- API Endpoints
- Database Models
- Services/Business Logic
- **High-Level Implementation** (step-by-step guide, decision points, code patterns)
- Frontend Implementation
- Testing Approach

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Setup & Development Environment](#setup--development-environment)
4. [Feature 1: Authentication & User Management](#feature-1-authentication--user-management)
5. [Feature 2: Contact Management](#feature-2-contact-management)
6. [Feature 3: Note Processing & AI Analysis](#feature-3-note-processing--ai-analysis)
7. [Feature 4: Tag & Category System](#feature-4-tag--category-system)
8. [Feature 5: Search Functionality](#feature-5-search-functionality)
9. [Feature 6: Relationship Graph](#feature-6-relationship-graph)
10. [Feature 7: Telegram Integration](#feature-7-telegram-integration)
11. [Feature 8: File Upload & Processing](#feature-8-file-upload--processing)
12. [Feature 9: Analytics & Insights](#feature-9-analytics--insights)
13. [Feature 10: Calendar Integration](#feature-10-calendar-integration)
14. [Feature 11: Admin Functions](#feature-11-admin-functions)
15. [Cross-Cutting Concerns](#cross-cutting-concerns)
16. [Deployment & Production](#deployment--production)
17. [Testing Strategy](#testing-strategy)

---

## Executive Summary

**Kith Platform** is a personal intelligence system that helps individuals manage and analyze their personal relationships. It combines contact management with AI-powered note processing, multi-source data integration, and relationship visualization.

### Core Value Proposition
- **Intelligent Contact Management**: Three-tier contact system with AI-powered categorization
- **Multi-Modal Data Integration**: Voice transcription, Telegram sync, file uploads, vCard imports
- **AI-Powered Analysis**: Automatic categorization of unstructured notes using OpenAI, Gemini, and Vision APIs
- **Relationship Intelligence**: Interactive graph visualization of personal network connections
- **Privacy-First**: Self-hosted with complete data ownership and export capabilities

### Technology Stack

**Backend:**
- Flask 2.3.3 (Web framework)
- SQLAlchemy 2.0.36 (ORM)
- PostgreSQL (Production database)
- SQLite (Development database)
- Celery 5.4.0 (Background tasks)
- Redis 5.0.4 (Task queue & caching)

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5/CSS3
- vis.js (Graph visualization)

**Frontend Asset Strategy:**
- ES Modules (`<script type="module">`) for organized code structure
- No bundler required (keeps it "Vanilla" but organized)
- Module-based architecture for maintainability

**AI & Integrations:**
- OpenAI API 0.28.1
- Google Generative AI 0.8.5
- Google Cloud Vision 3.10.2
- Telethon 1.34.0 (Telegram)
- ChromaDB 0.4.15 (Vector database)

**Authentication & Security:**
- Flask-Login 0.6.3
- PBKDF2-SHA256 password hashing

**Deployment:**
- Render.com
- Docker support
- Gunicorn 21.2.0 (WSGI server)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (SPA)                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │  UI Components  │ │ Cache Manager   │ │  Lazy Loader    │ │
│  │  (Vanilla JS)   │ │ (5min TTL)      │ │ (20 items/batch)│ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API
┌─────────────────────────▼───────────────────────────────────┐
│                   Flask Backend                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │  API Routes │ │  Services   │ │ Celery Tasks│ │ Utils   │ │
│  │ (Blueprints)│ │   Layer     │ │ (Async BG)  │ │& Utils  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQLAlchemy ORM
┌─────────────────────────▼───────────────────────────────────┐
│                 PostgreSQL Database                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   Contacts   │ │    Notes     │ │     Tags     │        │
│  │ (Multi-user) │ │ (Raw + Synth)│ │ (Hierarchical)        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────┬───────────────────────────────────┘
                          │ External Integrations
  ┌─────────────────┐     │     ┌─────────────────┐ ┌─────────┐
  │  AI Services    │─────┼─────│  Telegram API   │ │ Redis   │
  │ OpenAI/Gemini   │     │     │   (Telethon)    │ │ Cache   │
  │ Vision API      │     │     │                 │ │ & Queue │
  └─────────────────┘     │     └─────────────────┘ └─────────┘
                          │
            ┌─────────────▼─────────────┐
            │    Monitoring & Health    │
            │   Performance Analytics   │
            └───────────────────────────┘
```

### Directory Structure

```
kith-platform/
├── app/                      # Main application package
│   ├── __init__.py          # Flask app factory
│   ├── celery_app.py        # Celery configuration
│   │
│   ├── api/                 # API endpoints (Blueprints)
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── contacts.py      # Contact management
│   │   ├── notes.py         # Note processing
│   │   ├── tags.py          # Tag management
│   │   ├── categories.py    # Categories management API
│   │   ├── search.py        # Search functionality
│   │   ├── graph.py         # Relationship graph
│   │   ├── telegram_enhanced.py  # Telegram integration
│   │   ├── files.py         # File upload/processing
│   │   ├── analytics.py     # Analytics endpoints
│   │   ├── settings.py      # Settings & preferences
│   │   ├── calendar.py      # Calendar integration
│   │   ├── admin.py         # Admin functions
│   │   └── diagnostics.py   # System diagnostics
│   │
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── contact_service.py
│   │   ├── note_service.py
│   │   ├── tag_service.py
│   │   ├── search_service.py
│   │   ├── ai_service.py
│   │   ├── unified_ai_service.py  # Unified AI with smart selection
│   │   ├── smart_model_selector.py # Intelligent model selection
│   │   ├── gemini_service.py      # Gemini-specific service
│   │   ├── telegram_service.py
│   │   ├── enhanced_telegram_integration.py  # Telegram sync
│   │   ├── telegram_migration.py  # Telegram session migration
│   │   ├── hybrid_telegram_session.py  # Hybrid session management
│   │   ├── file_service.py
│   │   ├── analytics_service.py
│   │   ├── settings_service.py  # User settings & preferences
│   │   ├── export_service.py    # Data export (CSV)
│   │   └── import_service.py    # Data import (CSV)
│   │
│   ├── tasks/               # Celery background tasks
│   │   ├── ai_tasks.py      # AI processing tasks
│   │   ├── telegram_tasks.py
│   │   └── import_tasks.py
│   │
│   ├── models/              # Database models
│   │   ├── contact.py
│   │   └── note.py
│   │
│   └── utils/               # Shared utilities
│       ├── database.py      # Database connection manager
│       ├── dependencies.py  # Dependency injection
│       ├── logging_config.py
│       ├── monitoring.py
│       └── validators.py
│
├── models.py                # Main models file
├── templates/               # HTML templates
│   ├── index.html          # Main SPA template
│   └── login.html          # Login page
├── static/                  # Static assets
│   ├── style.css
│   └── js/
│       ├── main.js
│       ├── contacts.js
│       ├── relationship-graph.js
│       └── ...
├── tests/                   # Test suite
├── migrations/              # Alembic migrations
├── requirements.txt         # Python dependencies
├── main.py                  # Application entry point
└── wsgi.py                  # WSGI entry for production
```

---

## Frontend Asset Strategy

### Overview
The application uses **Vanilla JavaScript (ES6+)** with **ES Modules** for code organization. With 20+ JavaScript files (contacts.js, graph.js, search.js, etc.), a clear module strategy is essential for maintainability.

### ES Modules Architecture

**Strategy**: Use native ES Modules (`<script type="module">`) to keep the codebase "Vanilla" while maintaining organization. No bundler (Vite/Webpack) required.

**Module Structure:**
```
static/js/
├── main.js              # Entry point, initializes app
├── modules/
│   ├── contacts.js      # Contact management module
│   ├── graph.js         # Relationship graph module
│   ├── search.js        # Search functionality module
│   ├── notes.js         # Note processing module
│   ├── tags.js          # Tag management module
│   ├── telegram.js      # Telegram integration module
│   ├── files.js         # File upload module
│   ├── analytics.js     # Analytics dashboard module
│   ├── admin.js         # Admin functions module
│   └── utils/
│       ├── cache-manager.js    # Cache management
│       ├── api-client.js       # API request wrapper
│       └── debounce.js         # Utility functions
└── lib/                  # Third-party libraries (if needed)
    └── vis-network.min.js
```

**Entry Point** (`static/js/main.js`):
```javascript
// main.js - Application entry point
import { initializeContacts } from './modules/contacts.js';
import { initializeGraph } from './modules/graph.js';
import { initializeSearch } from './modules/search.js';
import { initializeNotes } from './modules/notes.js';
import { setupCacheManager } from './modules/utils/cache-manager.js';

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupCacheManager();
    initializeContacts();
    initializeGraph();
    initializeSearch();
    initializeNotes();
});
```

**Module Example** (`static/js/modules/contacts.js`):
```javascript
// modules/contacts.js - Contact management module
import { apiRequest } from '../modules/utils/api-client.js';
import { cacheGet, cacheSet } from '../modules/utils/cache-manager.js';

export function initializeContacts() {
    const contactsContainer = document.getElementById('contacts-list');
    if (!contactsContainer) return;
    
    loadContacts();
}

async function loadContacts() {
    // Check cache first
    const cached = cacheGet('contacts');
    if (cached) {
        renderContacts(cached);
        return;
    }
    
    // Fetch from API
    const contacts = await apiRequest('/api/contacts');
    cacheSet('contacts', contacts, 300); // 5 min TTL
    renderContacts(contacts);
}

function renderContacts(contacts) {
    // Render logic
}

// Export functions for use in other modules
export { loadContacts, renderContacts };
```

**HTML Integration** (`templates/index.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>Kith Platform</title>
</head>
<body>
    <!-- Application content -->
    
    <!-- Main entry point as ES Module -->
    <script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

**Key Benefits:**
- ✅ **No Build Step**: Direct browser execution, faster development
- ✅ **Native Module System**: Standard ES6 imports/exports
- ✅ **Code Organization**: Clear module boundaries
- ✅ **Tree Shaking**: Browsers only load used modules
- ✅ **Maintainability**: Easy to locate and modify code

**Module Communication:**
```javascript
// modules/search.js
import { loadContacts } from './contacts.js';

// When search updates, refresh contacts
export function handleSearch(query) {
    // ... search logic ...
    loadContacts(); // Imported from contacts module
}
```

**Browser Support:**
- ✅ Modern browsers (Chrome 61+, Firefox 60+, Safari 10.1+, Edge 16+)
- ⚠️ IE11 not supported (use polyfills if needed)

**Development Workflow:**
1. Edit modules in `static/js/modules/`
2. Import/export as needed
3. No compilation step required
4. Browser handles module resolution automatically

---

## Mobile & Responsive Design Requirements

### Overview
Personal CRMs are heavily used on mobile devices (adding notes after meetings, quick contact lookups). The application must be fully functional and optimized for mobile devices, with specific attention to touch interactions and responsive layouts.

### Responsive Breakpoints

**Mobile-First Approach:**
```css
/* Mobile (default): 320px - 767px */
/* Tablet: 768px - 1023px */
/* Desktop: 1024px+ */

/* Mobile styles (default) */
.contact-card {
    width: 100%;
    padding: 1rem;
    margin-bottom: 1rem;
}

/* Tablet styles */
@media (min-width: 768px) {
    .contact-card {
        width: calc(50% - 1rem);
        display: inline-block;
    }
}

/* Desktop styles */
@media (min-width: 1024px) {
    .contact-card {
        width: calc(33.33% - 1rem);
    }
}
```

### Touch Interaction Requirements

**Relationship Graph** (`static/js/modules/graph.js`):
The relationship graph is unusable on mobile without specific touch-interaction specifications.

**Touch Gestures:**
```javascript
// graph.js - Touch interaction handlers
export function initializeGraph() {
    const network = new vis.Network(container, data, options);
    
    // Pinch-to-zoom
    let lastPinchDistance = 0;
    network.on('touch', (params) => {
        if (params.touches.length === 2) {
            const touch1 = params.touches[0];
            const touch2 = params.touches[1];
            const distance = Math.hypot(
                touch2.x - touch1.x,
                touch2.y - touch1.y
            );
            
            if (lastPinchDistance > 0) {
                const scale = distance / lastPinchDistance;
                network.moveTo({
                    scale: network.getScale() * scale
                });
            }
            lastPinchDistance = distance;
        } else {
            lastPinchDistance = 0;
        }
    });
    
    // Pan with single finger
    let isPanning = false;
    let lastPanPosition = null;
    network.on('hold', (params) => {
        isPanning = true;
        lastPanPosition = { x: params.pointer.DOM.x, y: params.pointer.DOM.y };
    });
    
    network.on('dragStart', (params) => {
        if (params.nodes.length === 0) {
            isPanning = true;
        }
    });
    
    network.on('drag', (params) => {
        if (isPanning && lastPanPosition) {
            const deltaX = params.pointer.DOM.x - lastPanPosition.x;
            const deltaY = params.pointer.DOM.y - lastPanPosition.y;
            network.moveTo({
                position: {
                    x: network.getViewPosition().x + deltaX,
                    y: network.getViewPosition().y + deltaY
                }
            });
            lastPanPosition = { x: params.pointer.DOM.x, y: params.pointer.DOM.y };
        }
    });
    
    network.on('dragEnd', () => {
        isPanning = false;
        lastPanPosition = null;
    });
    
    // Tap to select (instead of click)
    network.on('click', (params) => {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            showContactDetails(nodeId);
        }
    });
}
```

**Graph Mobile Options:**
```javascript
const mobileOptions = {
    interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        selectConnectedEdges: false,
        hover: false, // Disable hover on touch devices
        keyboard: false, // Disable keyboard on mobile
        multiselect: false, // Single selection only
        tooltipDelay: 300, // Longer delay for touch
        navigationButtons: true, // Show zoom controls
        touch: true // Enable touch interactions
    },
    physics: {
        enabled: true,
        stabilization: {
            enabled: true,
            iterations: 100,
            fit: true
        }
    },
    layout: {
        improvedLayout: true,
        hierarchical: {
            enabled: false, // Disable hierarchical on mobile (too complex)
            direction: 'UD'
        }
    }
};
```

### Mobile-Specific UI Components

**Navigation:**
```html
<!-- Mobile navigation (hamburger menu) -->
<nav class="mobile-nav">
    <button class="hamburger" aria-label="Toggle menu">
        <span></span>
        <span></span>
        <span></span>
    </button>
    <ul class="nav-menu">
        <li><a href="#contacts">Contacts</a></li>
        <li><a href="#graph">Graph</a></li>
        <li><a href="#settings">Settings</a></li>
    </ul>
</nav>
```

**Note Input:**
```css
/* Mobile-optimized note input */
@media (max-width: 767px) {
    #note-input {
        font-size: 16px; /* Prevents zoom on iOS */
        padding: 1rem;
        min-height: 150px;
    }
    
    #analyze-btn {
        width: 100%;
        padding: 1rem;
        font-size: 1.1rem;
    }
}
```

**Contact Cards:**
```css
/* Stack contact cards on mobile */
@media (max-width: 767px) {
    .contacts-grid {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .contact-card {
        width: 100%;
        padding: 1rem;
    }
}
```

### Performance Optimizations

**Lazy Loading:**
```javascript
// Load graph only when needed on mobile
if (window.innerWidth < 768) {
    // Defer graph initialization
    document.addEventListener('scroll', () => {
        if (isGraphViewVisible()) {
            initializeGraph();
        }
    }, { once: true });
}
```

**Image Optimization:**
```html
<!-- Responsive images -->
<img src="contact-photo.jpg" 
     srcset="contact-photo-small.jpg 320w,
             contact-photo-medium.jpg 768w,
             contact-photo-large.jpg 1024w"
     sizes="(max-width: 767px) 100vw,
            (max-width: 1023px) 50vw,
            33vw"
     alt="Contact photo">
```

### Testing Requirements

**Mobile Testing Checklist:**
- ✅ Touch interactions work (tap, swipe, pinch)
- ✅ Graph is navigable on mobile
- ✅ Forms are usable (no zoom on input focus)
- ✅ Navigation is accessible (hamburger menu)
- ✅ Text is readable (minimum 16px font size)
- ✅ Buttons are tappable (minimum 44x44px touch target)
- ✅ Loading states are clear
- ✅ Error messages are visible

**Device Testing:**
- iOS Safari (iPhone 12+, iPad)
- Android Chrome (various screen sizes)
- Responsive design mode in browser dev tools

---

## Setup & Development Environment

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (for production)
- SQLite (for local development)
- Redis (for Celery tasks)
- Node.js (optional, for frontend tooling)

### Initial Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd kith-platform
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost/kith_platform
   # Or for SQLite: sqlite:///kith_platform.db
   
   # AI Services
   GEMINI_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
   
   # Telegram (optional)
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   
   # Redis (for Celery)
   REDIS_URL=redis://localhost:6379/0
   
   # Flask
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   ```

5. **Initialize Database**
   ```bash
   # Create database tables
   python -c "from app import create_app; from models import Base; from app.utils.database import DatabaseManager; app = create_app(); app.app_context().push(); Base.metadata.create_all(DatabaseManager().engine)"
   
   # Or use Alembic migrations
   alembic upgrade head
   ```

6. **Start Development Server**
   ```bash
   python main.py
   # Or
   flask run
   ```

7. **Start Celery Worker** (for background tasks)
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

8. **Start Redis** (required for Celery)
   ```bash
   redis-server
   ```

### Development Workflow

- Frontend: Edit files in `templates/` and `static/`
- Backend: Edit files in `app/`
- Database changes: Create Alembic migrations
- Testing: Run `pytest` from project root

---

## Feature 1: Authentication & User Management

### Overview
Multi-user authentication system with role-based access control (admin/user). Uses Flask-Login for session management and PBKDF2-SHA256 for password hashing.

### User-Facing Pages
- **Login Page** (`/login` or `/` when not authenticated)
  - Username/password form
  - Error message display
  - Redirects to main app after successful login

### API Endpoints

**`POST /api/auth/login`**
- Authenticate user and create session
- Request: `{ "username": "string", "password": "string" }`
- Response: `{ "success": true, "user": {...} }`
- Sets Flask-Login session cookie

**`POST /api/auth/logout`**
- End user session
- Response: `{ "success": true }`

**`GET /api/auth/me`**
- Get current authenticated user info
- Response: `{ "id": int, "username": "string", "role": "string" }`

**`POST /api/auth/register`** (Admin only)
- Create new user account
- Request: `{ "username": "string", "password": "string", "role": "user|admin" }`

### Database Models

**User Model** (`models.py`)
```python
class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_plaintext = Column(String(255), nullable=True)  # Admin viewing
    role = Column(String(50), nullable=False, default='user')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contacts = relationship("Contact", back_populates="user")
```

### Services

**AuthService** (`app/services/auth_service.py`)
- `authenticate_user(username, password)` - Verify credentials
- `create_user(username, password, role)` - Create new user
- `hash_password(password)` - PBKDF2-SHA256 hashing
- `verify_password(password_hash, password)` - Verify password
- `get_user_by_id(user_id)` - Static method for Flask-Login user loader
- `update_user_password(user_id, new_password)` - Change user password

### High-Level Implementation

#### Implementation Flow: User Login

**Step 1: Flask-Login Configuration** (`app/__init__.py`)
```python
from flask_login import LoginManager

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirect to this route if not authenticated

# Configure session cookies
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
```

**Key Decision Points:**
- ✅ **SESSION_COOKIE_HTTPONLY=True** - Prevents JavaScript access to cookies (XSS protection)
- ✅ **SESSION_COOKIE_SAMESITE='Lax'** - CSRF protection, allows GET requests from other sites
- ✅ **24-hour session lifetime** - Balance between security and UX
- ✅ **login_view='auth.login'** - Redirects unauthenticated users to login page

**Step 2: User Loader Function** (`app/__init__.py`)
```python
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login - called on every request"""
    try:
        from app.utils.database import DatabaseManager
        from app.models import User
        from app.api.auth import AuthUser  # Lightweight user class
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == int(user_id)).first()
            if user:
                # Create lightweight AuthUser to avoid SQLAlchemy session issues
                return AuthUser(user.id, user.username, getattr(user, 'role', 'user'))
            return None
    except Exception as e:
        logging.error(f"Error loading user {user_id}: {e}")
        return None
```

**Key Decision Points:**
- ✅ **Use lightweight AuthUser class** - Avoids SQLAlchemy DetachedInstanceError
- ✅ **Extract data while session active** - Get user.id, username, role before session closes
- ✅ **Return None on error** - Flask-Login treats None as unauthenticated
- ✅ **Called on every request** - Flask-Login automatically calls this

**Step 3: Lightweight User Class** (`app/api/auth.py`)
```python
from flask_login import UserMixin

class AuthUser(UserMixin):
    """Lightweight user class for Flask-Login (avoids SQLAlchemy session issues)"""
    def __init__(self, user_id, username, role='user'):
        self.id = user_id  # Required by UserMixin
        self.username = username
        self.role = role
    
    # UserMixin provides:
    # - is_authenticated property (returns True if user has id)
    # - is_active property (returns True by default)
    # - is_anonymous property (returns False)
    # - get_id() method (returns str(self.id))
```

**Key Decision Points:**
- ✅ **Inherit from UserMixin** - Provides required Flask-Login properties
- ✅ **Store only essential data** - id, username, role (no SQLAlchemy relationships)
- ✅ **Avoid session issues** - Can be used after database session closes

**Step 4: Login Endpoint** (`app/api/auth.py`)
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login - supports both GET (show form) and POST (authenticate)"""
    
    # GET request: Show login page
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('index'))  # Already logged in
        return render_template('login.html')
    
    # POST request: Authenticate
    try:
        # 1. Extract credentials (support both JSON and form data)
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        # 2. Validate input
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # 3. Query database for user
        from app.utils.database import DatabaseManager
        from app.models import User
        from werkzeug.security import check_password_hash
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            
            # 4. Verify password
            if user and check_password_hash(user.password_hash, password):
                # 5. Extract user data while session is active
                user_id = user.id
                user_username = user.username
                user_role = getattr(user, 'role', 'user')
                
                # 6. Create lightweight AuthUser
                auth_user = AuthUser(user_id, user_username, user_role)
                
                # 7. Log user in with Flask-Login
                login_user(auth_user)  # Sets session cookie
                
                # 8. Return response
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'user': {'id': user_id, 'username': user_username}
                    })
                return redirect(url_for('index'))
            else:
                # Invalid credentials
                if request.is_json:
                    return jsonify({'error': 'Invalid credentials'}), 401
                return render_template('login.html', error='Invalid credentials')
                
    except Exception as e:
        logger.error(f"Login error: {e}")
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('login.html', error='Login failed')
```

**Key Decision Points:**
- ✅ **Support both JSON and form data** - Flexible for API and web forms
- ✅ **Extract data before session closes** - Avoid DetachedInstanceError
- ✅ **Use check_password_hash()** - Werkzeug's secure password verification
- ✅ **Create AuthUser before login_user()** - Lightweight object for session
- ✅ **Different responses for JSON vs HTML** - Better UX for both

**Step 5: Password Hashing** (`app/services/auth_service.py`)
```python
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(self, username: str, password: str, role: str = 'user') -> Optional[User]:
    """Create a new user with hashed password"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Check if user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                return None  # Username taken
            
            # 2. Hash password using PBKDF2-SHA256
            password_hash = generate_password_hash(
                password,
                method='pbkdf2:sha256'  # Secure hashing algorithm
            )
            
            # 3. Create user (store plaintext for admin viewing - optional)
            user = User(
                username=username,
                password_hash=password_hash,
                password_plaintext=password,  # For admin dashboard viewing
                role=role
            )
            
            # 4. Save to database
            session.add(user)
            session.flush()  # Get ID without committing
            session.expunge(user)  # Detach to avoid session issues
            return user
            
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}")
        return None
```

**Key Decision Points:**
- ✅ **PBKDF2-SHA256 method** - Industry standard, secure hashing
- ✅ **Check for duplicates** - Username must be unique
- ✅ **Store plaintext password** - Optional, for admin viewing (security trade-off)
- ✅ **Use flush() not commit()** - Get ID without committing transaction
- ✅ **Expunge user** - Detach from session to avoid issues

**Step 6: Password Verification**
```python
def authenticate_user(self, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Find user by username
            user = session.query(User).filter(User.username == username).first()
            
            if user:
                # 2. Verify password hash
                password_valid = check_password_hash(user.password_hash, password)
                
                if password_valid:
                    # 3. Detach user from session
                    session.expunge(user)
                    return user
                else:
                    logger.warning(f"Invalid password for user: {username}")
            else:
                logger.warning(f"User not found: {username}")
            return None
            
    except Exception as e:
        logger.error(f"Error authenticating user {username}: {e}")
        return None
```

**Key Decision Points:**
- ✅ **check_password_hash()** - Secure comparison (timing-safe)
- ✅ **Don't reveal if user exists** - Same error for invalid user/password (security)
- ✅ **Expunge before returning** - Avoid session issues
- ✅ **Log authentication failures** - Security monitoring

#### Data Flow Diagram: Login

```
User submits login form
    ↓
POST /api/auth/login
    ↓
Extract username/password from request
    ↓
Query database for user by username
    ↓
check_password_hash(user.password_hash, password)
    ├─ Valid → Extract user data
    │   ↓
    │   Create AuthUser(user_id, username, role)
    │   ↓
    │   login_user(auth_user) → Sets session cookie
    │   ↓
    │   Return success response
    └─ Invalid → Return 401 error
```

#### Implementation Flow: User Registration

**Step 1: Registration Endpoint** (`app/api/auth.py`)
```python
@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        # 1. Extract registration data
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')  # Default to 'user', admin can set 'admin'
        
        # 2. Validate input
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # 3. Create user via AuthService
        from app.utils.database import DatabaseManager
        db_manager = DatabaseManager()
        auth_service = AuthService(db_manager)
        user = auth_service.create_user(username, password, role)
        
        if user:
            # 4. Auto-login after registration
            auth_user = AuthUser(user.id, user.username, user.role)
            login_user(auth_user)
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'user': {'id': user.id, 'username': user.username}
                })
            return redirect(url_for('index'))
        else:
            # Username already exists
            if request.is_json:
                return jsonify({'error': 'Username already exists'}), 400
            return render_template('login.html', error='Username already exists')
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('login.html', error='Registration failed')
```

**Key Decision Points:**
- ✅ **Auto-login after registration** - Better UX, user doesn't need to login again
- ✅ **Default role='user'** - Security: new users are not admins by default
- ✅ **Check for duplicate username** - AuthService returns None if exists
- ✅ **Same error handling pattern** - Consistent with login endpoint

#### Implementation Flow: Logout

**Step 1: Logout Endpoint**
```python
@auth_bp.route('/logout', methods=['POST'])
@login_required  # Must be authenticated to logout
def logout():
    """Handle user logout"""
    logout_user()  # Clears session cookie
    
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('auth.login'))
```

**Key Decision Points:**
- ✅ **@login_required decorator** - Only authenticated users can logout
- ✅ **logout_user()** - Flask-Login function that clears session
- ✅ **Redirect to login** - After logout, send user to login page

#### Implementation Flow: Protected Routes

**Step 1: Using @login_required Decorator**
```python
from flask_login import login_required, current_user

@app.route('/api/contacts')
@login_required  # Redirects to login if not authenticated
def get_contacts():
    # current_user is available (AuthUser instance)
    user_id = current_user.id
    username = current_user.username
    role = current_user.role
    
    # Use user_id to filter data
    contacts = session.query(Contact).filter(
        Contact.user_id == current_user.id
    ).all()
```

**Key Decision Points:**
- ✅ **@login_required** - Simplest way to protect routes
- ✅ **current_user** - Available in all protected routes
- ✅ **Always filter by user_id** - Multi-user data isolation

**Step 2: Manual Authentication Check**
```python
@app.route('/')
def index():
    """Main route with manual auth check"""
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        return render_template('index.html')
    else:
        return render_template('login.html')
```

**Key Decision Points:**
- ✅ **Check is_authenticated** - For routes that don't use @login_required
- ✅ **hasattr check** - Prevents errors if current_user is AnonymousUser

#### Security Considerations

**Password Security:**
- ✅ **PBKDF2-SHA256 hashing** - Industry standard, secure
- ✅ **Never store plaintext passwords** - Only hashes (plaintext is optional for admin)
- ✅ **Timing-safe comparison** - check_password_hash() prevents timing attacks
- ✅ **No password length requirements** - Currently no validation (could add)

**Session Security:**
- ✅ **HTTPOnly cookies** - Prevents XSS attacks
- ✅ **SameSite='Lax'** - CSRF protection
- ✅ **24-hour expiration** - Balance security and UX
- ✅ **Secure flag in production** - Set SESSION_COOKIE_SECURE=True with HTTPS

**Authentication Security:**
- ✅ **Don't reveal if user exists** - Same error for invalid user/password
- ✅ **Log authentication failures** - Monitor for brute force attacks
- ✅ **Role-based access control** - Admin vs user roles
- ✅ **User data isolation** - Always filter by user_id

#### Integration Points

1. **Flask-Login**: Session management, user loading, authentication decorators
2. **DatabaseManager**: Database access for user queries
3. **User Model**: SQLAlchemy model with password_hash field
4. **Werkzeug Security**: Password hashing and verification
5. **Session Cookies**: Flask's session management

#### Common Patterns

**Pattern 1: Protected Route**
```python
@route('/api/resource')
@login_required
def get_resource():
    # current_user.id available
    # Filter by user_id for data isolation
```

**Pattern 2: Admin-Only Route**
```python
@route('/api/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    # Admin logic here
```

**Pattern 3: Extract User Data Before Session Closes**
```python
with db_manager.get_session() as session:
    user = session.query(User).filter(...).first()
    user_id = user.id  # Extract while session active
    username = user.username
    # Session closes here
    # Use user_id, username (not user object)
```

### Frontend Implementation

**Login Flow** (`static/js/main.js` or similar)
```javascript
// Login form submission
async function handleLogin(username, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',  // Important: include cookies
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Session cookie automatically set by Flask-Login
            window.location.href = '/';  // Redirect to main app
        } else {
            // Show error message
            showError(data.error || 'Login failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

// Check if user is authenticated
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
    return null;
}
```

**Key Frontend Points:**
- ✅ **credentials: 'include'** - Required to send/receive cookies
- ✅ **Session cookie automatic** - Flask-Login sets it, no manual handling
- ✅ **Redirect on success** - Navigate to main app
- ✅ **Error handling** - Show user-friendly error messages

### Testing Approach
- Unit tests for password hashing/verification
- Integration tests for login/logout flows
- Test role-based access control
- Test session persistence
- Test invalid credentials (don't reveal if user exists)
- Test protected routes redirect to login

---

## Feature 2: Contact Management

### Overview
Three-tier contact classification system (Tier 1: close contacts, Tier 2: regular, Tier 3: distant). Full CRUD operations with vCard import, duplicate detection, and Telegram integration fields.

### User-Facing Pages
- **Main Contacts View** (default view in SPA)
  - Search bar with tier filter
  - Tier 1 contacts list (prominent)
  - All contacts list (searchable)
  - Contact creation/edit forms
  - Contact detail view with 360° profile

### API Endpoints

**`GET /api/contacts`**
- Get all contacts for current user
- Query params: `tier` (optional filter)
- Response: `[{ "id": int, "full_name": string, "tier": int, ... }]`

**`POST /api/contacts`**
- Create new contact
- Request: `{ "full_name": string, "tier": int, ... }`
- Response: `{ "id": int, ... }`

**`GET /api/contacts/<id>`**
- Get contact details with all related data
- Response: Full contact object with notes, tags, etc.

**`PUT /api/contacts/<id>`**
- Update contact
- Request: `{ "full_name": string, ... }`

**`DELETE /api/contacts/<id>`**
- Delete contact (cascades to notes)

**`POST /api/contacts/import-vcard`**
- Import contacts from vCard file
- Request: Multipart form with `.vcf` file
- Response: `{ "imported": int, "duplicates": int, "errors": [...] }`

### Database Models

**Contact Model** (`models.py`)
```python
class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    full_name = Column(String(255), nullable=False)
    tier = Column(Integer, default=2, nullable=False)  # 1, 2, or 3
    
    # Telegram fields
    telegram_id = Column(String(255))
    telegram_username = Column(String(255))
    telegram_phone = Column(String(255))
    telegram_handle = Column(String(255))
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    telegram_last_sync = Column(DateTime)
    telegram_metadata = Column(JSON)
    
    # Extensible fields
    custom_fields = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="contacts")
    raw_notes = relationship("RawNote", back_populates="contact")
    synthesized_entries = relationship("SynthesizedEntry", back_populates="contact")
    tags = relationship("Tag", secondary="contact_tags")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Services

**ContactService** (`app/services/contact_service.py`)
- `create_contact(user_id, data)` - Create with validation
- `update_contact(contact_id, user_id, data)` - Update with ownership check
- `delete_contact(contact_id, user_id)` - Delete with cascade
- `import_vcard(user_id, file)` - Parse vCard and import
- `detect_duplicates(user_id, contact_data)` - Check for existing contacts
- `get_contact_profile(contact_id, user_id)` - Get full 360° profile

### High-Level Implementation

#### Implementation Flow: Create Contact

**Step 1: API Endpoint Handler** (`app/api/contacts.py`)
```python
@contacts_bp.route('/', methods=['POST'])
@login_required
def create_contact():
    # 1. Extract and validate request data
    data = request.json
    if not data or not data.get('full_name'):
        return jsonify({'error': 'Full name is required'}), 400
    
    # 2. Get database session
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        # 3. Create Contact model instance
        contact = Contact(
            full_name=data.get('full_name').strip(),  # Always strip whitespace
            tier=data.get('tier', 2),  # Default to tier 2
            user_id=current_user.id,  # From Flask-Login
            vector_collection_id=f"contact_{uuid.uuid4().hex[:8]}"  # For ChromaDB
        )
        
        # 4. Add to session and commit
        session.add(contact)
        session.commit()  # This generates the ID
        
        # 5. Return JSON response
        return jsonify({
            'id': contact.id,
            'full_name': contact.full_name,
            'tier': contact.tier,
            'message': f"Contact '{contact.full_name}' created successfully"
        }), 201
```

**Key Decision Points:**
- ✅ **Use direct database access in API** (not service layer) - Current pattern for simplicity
- ✅ **Generate vector_collection_id immediately** - Needed for ChromaDB integration
- ✅ **Default tier to 2** - Most contacts are regular (not inner circle)
- ✅ **Strip whitespace** - Prevent accidental spaces in names
- ✅ **Return 201 status** - RESTful convention for resource creation

**Step 2: Database Transaction Pattern**
```python
# ALWAYS use context manager for sessions
with db_manager.get_session() as session:
    # Do database operations
    session.add(contact)
    session.commit()  # Explicit commit for writes
    # Session automatically closes after context
```

**Step 3: Error Handling Pattern**
```python
try:
    # Operation
    return jsonify({'success': True}), 201
except Exception as e:
    current_app.logger.error(f"Error: {e}")  # Log for debugging
    return jsonify({'error': str(e)}), 500  # Return generic error
```

**Step 4: User Ownership Check** (for GET/UPDATE/DELETE)
```python
contact = session.query(Contact).filter(
    Contact.id == contact_id,
    Contact.user_id == current_user.id  # CRITICAL: Always filter by user_id
).first()

if not contact:
    return jsonify({'error': 'Contact not found'}), 404
```

#### Implementation Flow: Get Contacts List

**Step 1: Query with User Filter**
```python
@contacts_bp.route('/', methods=['GET'])
@login_required
def get_contacts():
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        # ALWAYS filter by user_id for security
        contacts = session.query(Contact).filter(
            Contact.user_id == current_user.id
        ).all()
        
        # Convert to JSON-serializable format
        return jsonify([{
            'id': c.id,
            'full_name': c.full_name,
            'tier': c.tier,
            'telegram_username': c.telegram_username,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in contacts])
```

**Key Decision Points:**
- ✅ **Always filter by user_id** - Multi-user isolation is critical
- ✅ **Select only needed fields** - Don't return entire model (performance)
- ✅ **Handle None dates** - Use conditional for optional fields
- ✅ **Use list comprehension** - Clean, readable JSON serialization

#### Implementation Flow: Update Contact

**Step 1: Validate Ownership First**
```python
@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    data = request.json
    
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        # 1. Get contact AND verify ownership
        contact = session.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        ).first()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # 2. Update only provided fields
        if 'full_name' in data:
            contact.full_name = data['full_name'].strip()
        if 'tier' in data:
            contact.tier = data['tier']
        # ... other fields
        
        # 3. Commit changes
        session.commit()
        
        return jsonify(contact.to_dict())
```

**Key Decision Points:**
- ✅ **Check ownership BEFORE update** - Security first
- ✅ **Partial updates** - Only update fields provided in request
- ✅ **Use model's to_dict()** - Consistent serialization

#### Implementation Flow: Delete Contact

**Step 1: Cascade Delete Pattern**
```python
@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        # 1. Verify ownership
        contact = session.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        ).first()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # 2. Delete (cascade handled by SQLAlchemy relationships)
        session.delete(contact)
        session.commit()
        
        return jsonify({'message': 'Contact deleted successfully'}), 200
```

**Key Decision Points:**
- ✅ **Cascade deletes** - Configured in models.py with `cascade="all, delete-orphan"`
- ✅ **Verify ownership** - Even for delete operations
- ✅ **Return success message** - Confirm deletion

#### Data Flow Diagram

```
User Request (POST /api/contacts)
    ↓
Flask Route Handler (@login_required)
    ↓
Extract & Validate Data (full_name required)
    ↓
DatabaseManager.get_session() (context manager)
    ↓
Create Contact Model (user_id from current_user)
    ↓
session.add() → session.commit()
    ↓
Return JSON Response (201 Created)
```

#### Integration Points

1. **Authentication**: Uses `@login_required` decorator and `current_user.id`
2. **Database**: Uses `DatabaseManager` singleton pattern
3. **Models**: Uses SQLAlchemy `Contact` model with relationships
4. **Logging**: Uses Flask's `current_app.logger` for errors
5. **ChromaDB**: Vector collection ID generated for future RAG integration

#### Common Patterns to Follow

**Pattern 1: Request Validation**
```python
# Always validate required fields first
if not data or not data.get('required_field'):
    return jsonify({'error': 'Required field missing'}), 400
```

**Pattern 2: User Isolation**
```python
# ALWAYS filter by user_id
.filter(Contact.user_id == current_user.id)
```

**Pattern 3: Error Handling**
```python
try:
    # Operation
except Exception as e:
    current_app.logger.error(f"Error: {e}")
    return jsonify({'error': str(e)}), 500
```

**Pattern 4: Session Management**
```python
# ALWAYS use context manager
with db_manager.get_session() as session:
    # Operations
    session.commit()  # Explicit for writes
```

#### Implementation Flow: Get Contact Detail (360° Profile)

**Step 1: Contact Detail Endpoint** (`app/api/contacts.py`)
```python
@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@login_required
@inject
def get_contact(contact_id, contact_service: ContactService = Provide[Container.contact_service]):
    """Get a single contact by ID with categorized data (360° profile)"""
    try:
        # 1. Get contact via service
        contact = contact_service.get_contact_by_id(contact_id)
        
        # 2. Verify ownership
        if not contact or contact.user_id != current_user.id:
            return jsonify({'error': 'Contact not found'}), 404
        
        # 3. Get contact basic info
        contact_dict = contact.to_dict()
        
        # 4. Fetch categorized data (synthesized entries from AI analysis)
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            entries = session.query(SynthesizedEntry).filter(
                SynthesizedEntry.contact_id == contact_id
            ).order_by(
                SynthesizedEntry.category.asc(),  # Group by category
                SynthesizedEntry.created_at.desc()  # Newest first within category
            ).all()
            
            # 5. Group entries by category
            categorized_data = {}
            for entry in entries:
                if entry.category not in categorized_data:
                    categorized_data[entry.category] = []
                categorized_data[entry.category].append(entry.content)
        
        # 6. Return combined data
        return jsonify({
            'contact_info': contact_dict,
            'categorized_data': categorized_data  # Organized by AI categories
        })
    except Exception as e:
        current_app.logger.error(f"Error getting contact {contact_id}: {e}")
        return jsonify({'error': str(e)}), 500
```

**Key Decision Points:**
- ✅ **Use service layer** - ContactService for contact retrieval
- ✅ **Verify ownership** - Check user_id matches current_user.id
- ✅ **Separate query for entries** - Don't use relationship (better control)
- ✅ **Group by category** - Frontend expects organized structure
- ✅ **Order by category then date** - Logical grouping

#### Implementation Flow: Update Contact

**Step 1: Update Endpoint** (`app/api/contacts.py`)
```python
@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@login_required
@inject
def update_contact(contact_id, contact_service: ContactService = Provide[Container.contact_service]):
    """Update an existing contact"""
    data = request.json
    
    # 1. Update via service (service handles ownership check internally)
    contact = contact_service.update_contact(contact_id, **data)
    
    # 2. Verify ownership and return
    if contact and contact.user_id == current_user.id:
        return jsonify(contact.to_dict())
    return jsonify({'error': 'Contact not found'}), 404
```

**Step 2: Service Update Implementation** (`app/services/contact_service.py`)
```python
def update_contact(self, contact_id: int, **data) -> Optional[Contact]:
    """Update an existing contact"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Find contact
            contact = session.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return None
            
            # 2. Define allowed updatable fields (security: prevent updating user_id)
            updatable_fields = [
                'full_name', 'tier', 'telegram_id', 'telegram_username',
                'is_verified', 'is_premium', 'vector_collection_id'
            ]
            
            # 3. Update only provided fields
            updated_fields = []
            for key, value in data.items():
                if key in updatable_fields and hasattr(contact, key):
                    old_value = getattr(contact, key)
                    if old_value != value:
                        setattr(contact, key, value)
                        updated_fields.append(f"{key}: {old_value} -> {value}")
            
            # 4. Commit if changes made
            if updated_fields:
                session.flush()
                session.refresh(contact)
                logger.info(f"Updated contact {contact_id}: {', '.join(updated_fields)}")
            
            # 5. Return contact (still attached to session)
            return contact
            
    except Exception as e:
        logger.error(f"Error updating contact {contact_id}: {e}")
        return None
```

**Key Decision Points:**
- ✅ **Whitelist updatable fields** - Security: prevent updating user_id
- ✅ **Only update changed fields** - Efficient, logs what changed
- ✅ **Use flush() not commit()** - Get updated values without committing
- ✅ **Log updates** - Audit trail of changes

#### Implementation Flow: Delete Contact

**Step 1: Delete Endpoint**
```python
@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@login_required
@inject
def delete_contact(contact_id, contact_service: ContactService = Provide[Container.contact_service]):
    """Delete a contact"""
    # Service handles ownership check
    success = contact_service.delete_contact(contact_id)
    if success:
        return jsonify({'message': 'Contact deleted successfully'})
    return jsonify({'error': 'Contact not found'}), 404
```

**Step 2: Service Delete Implementation**
```python
def delete_contact(self, contact_id: int) -> bool:
    """Delete a contact (cascade handled by SQLAlchemy)"""
    try:
        with self.db_manager.get_session() as session:
            contact = session.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return False
            
            contact_name = contact.full_name
            session.delete(contact)  # Cascade deletes notes, entries, tags
            logger.info(f"Deleted contact {contact_id}: {contact_name}")
            return True
            
    except Exception as e:
        logger.error(f"Error deleting contact {contact_id}: {e}")
        return False
```

**Key Decision Points:**
- ✅ **Cascade delete** - Configured in models.py with `cascade="all, delete-orphan"`
- ✅ **Return boolean** - Simple success/failure indicator
- ✅ **Log deletion** - Audit trail

#### Implementation Flow: Get Raw Notes/Logs

**Step 1: Raw Logs Endpoint** (`app/api/contacts.py`)
```python
@contacts_bp.route('/<int:contact_id>/raw-logs', methods=['GET'])
@login_required
def get_raw_logs(contact_id):
    """Get raw notes (logs) for a contact"""
    try:
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            # 1. Verify contact ownership
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == current_user.id
            ).first()
            
            if not contact:
                return jsonify({"error": "Contact not found"}), 404
            
            # 2. Get all raw notes
            raw_notes = session.query(RawNote).filter(
                RawNote.contact_id == contact_id
            ).order_by(RawNote.created_at.desc()).all()
            
            # 3. Format with metadata
            formatted_logs = []
            for note in raw_notes:
                # Extract metadata (engine used for processing)
                details = None
                engine = None
                
                if note.metadata_tags:
                    if isinstance(note.metadata_tags, dict):
                        details = note.metadata_tags
                    else:
                        try:
                            import json
                            details = json.loads(note.metadata_tags) if isinstance(note.metadata_tags, str) else None
                        except:
                            details = None
                
                # Determine processing engine from metadata
                if details and isinstance(details, dict):
                    if details.get('used_google_ocr'):
                        engine = 'vision'
                    elif details.get('used_openai_mm'):
                        engine = 'openai'
                    elif details.get('used_gemini'):
                        engine = 'gemini'
                    else:
                        engine = 'local'
                
                formatted_logs.append({
                    "content": note.content,
                    "date": note.created_at.isoformat() if note.created_at else None,
                    "details": details,
                    "engine": engine
                })
            
            return jsonify(formatted_logs)
            
    except Exception as e:
        current_app.logger.error(f"Error getting raw logs for contact {contact_id}: {e}")
        return jsonify({"error": f"Failed to retrieve raw logs: {str(e)}"}), 500
```

**Key Decision Points:**
- ✅ **Verify ownership first** - Security check before querying notes
- ✅ **Order by date descending** - Most recent first
- ✅ **Extract metadata** - Show which AI engine processed the note
- ✅ **Handle JSON metadata** - Support both dict and string JSON

#### Implementation Flow: Contact Search

**Step 1: Search Endpoint** (`app/api/contacts.py`)
```python
@contacts_bp.route('/search', methods=['GET'])
@login_required
def search_contacts():
    """Semantic search placeholder using ChromaDB"""
    try:
        query = request.args.get('q', '').strip()
        results = []
        
        # Try ChromaDB semantic search (if available)
        try:
            from app.utils.chromadb_client import chroma_client
            _ = chroma_client.get_client()
            # TODO: Implement actual semantic search
        except Exception:
            pass
        
        return jsonify({'query': query, 'results': results}), 200
    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

**Step 2: Service Search Implementation** (`app/services/contact_service.py`)
```python
def search_contacts(self, user_id: int, search_term: str) -> List[Contact]:
    """Search contacts by name using case-insensitive LIKE"""
    try:
        if not search_term or not search_term.strip():
            return []
        
        # Use ILIKE for case-insensitive search (PostgreSQL) or LIKE (SQLite)
        search_pattern = f"%{search_term.strip()}%"
        with self.db_manager.get_session() as session:
            contacts = session.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.full_name.ilike(search_pattern)  # Case-insensitive
            ).all()
            return contacts
    except Exception as e:
        logger.error(f"Error searching contacts for user {user_id}: {e}")
        return []
```

**Key Decision Points:**
- ✅ **Case-insensitive search** - Use `ilike()` for better UX
- ✅ **Wildcard pattern** - `%term%` matches anywhere in name
- ✅ **Strip whitespace** - Clean user input
- ✅ **Filter by user_id** - Multi-user isolation

#### Implementation Flow: Get Contacts by Tier

**Step 1: Tier Filtering** (`app/services/contact_service.py`)
```python
def get_contacts_by_tier(self, user_id: int, tier: int) -> List[Contact]:
    """Get contacts filtered by tier"""
    try:
        with self.db_manager.get_session() as session:
            contacts = session.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.tier == tier
            ).all()
            return contacts
    except Exception as e:
        logger.error(f"Error retrieving tier-{tier} contacts for user {user_id}: {e}")
        return []
```

**Tier System:**
- **Tier 1**: Close contacts (family, best friends, romantic partners) - Priority 9-10
- **Tier 2**: Regular contacts (colleagues, acquaintances, friends) - Priority 5-8 (default)
- **Tier 3**: Distant contacts (professional network, occasional interactions) - Priority 1-4

**Key Decision Points:**
- ✅ **Default tier is 2** - Most contacts are regular
- ✅ **Filter in database** - More efficient than filtering in Python
- ✅ **User isolation** - Always filter by user_id

#### Implementation Flow: CSV Import

**Step 1: Import Service** (`app/services/import_service.py`)
```python
class ImportService:
    """Parse CSV and upsert contacts"""
    
    REQUIRED_COLUMNS = {'user_id', 'contact_name'}
    
    @classmethod
    def parse_and_validate(cls, csv_bytes: bytes) -> Tuple[List[Dict], List[str]]:
        """Parse CSV and validate structure"""
        errors = []
        rows = []
        
        # 1. Decode with BOM handling (Excel exports often have BOM)
        text = csv_bytes.decode('utf-8-sig')  # utf-8-sig handles BOM
        reader = csv.DictReader(io.StringIO(text))
        
        # 2. Check required columns
        missing = [c for c in cls.REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return [], errors
        
        # 3. Validate each row
        for idx, row in enumerate(reader, start=2):  # header is line 1
            if not row.get('user_id') or not row.get('contact_name'):
                errors.append(f"Row {idx}: user_id and contact_name are required")
                continue
            
            # Normalize JSON columns
            for key in ('categories', 'tags', 'sources', 'raw_logs_json', 'edits_json'):
                if row.get(key):
                    row[key] = cls._parse_json(row[key])
            
            rows.append(row)
        
        return rows, errors
    
    @classmethod
    def upsert_contacts(cls, session, rows: List[Dict]) -> ImportResult:
        """Upsert contacts (create or update)"""
        total = len(rows)
        created = 0
        updated = 0
        errors = []
        
        for row in rows:
            try:
                # 1. Verify user exists
                user = session.query(User).filter(User.id == int(row['user_id'])).first()
                if not user:
                    errors.append(f"User {row['user_id']} not found")
                    continue
                
                # 2. Check if contact exists (by contact_id if provided)
                contact = None
                if row.get('contact_id'):
                    contact = session.query(Contact).filter(
                        Contact.id == int(row['contact_id'])
                    ).first()
                
                # 3. Create or update
                if contact is None:
                    contact = Contact(user_id=user.id, full_name=row['contact_name'])
                    created += 1
                    session.add(contact)
                else:
                    updated += 1
                    contact.full_name = row['contact_name'] or contact.full_name
                
                # 4. Update optional fields
                if row.get('contact_phone'):
                    contact.telegram_phone = row['contact_phone']
                if row.get('contact_email'):
                    cf = contact.custom_fields or {}
                    cf['email'] = row['contact_email']
                    contact.custom_fields = cf
                
                # 5. Store complex data in custom_fields
                cf = contact.custom_fields or {}
                if row.get('categories') is not None:
                    cf['categories'] = row['categories']
                # ... other fields
                contact.custom_fields = cf
                
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
        
        return ImportResult(total, created, updated, errors)
```

**Step 2: Celery Task for Async Import** (`app/tasks/import_tasks.py`)
```python
@celery_app.task(bind=True, name='app.tasks.import_tasks.run_contacts_import', queue='import_queue')
def run_contacts_import(self: Task, csv_bytes: bytes, scope: str = 'admin'):
    """Background CSV import for contacts"""
    from app.services.import_service import ImportService
    from app.utils.database import DatabaseManager
    
    # 1. Parse and validate
    rows, parse_errors = ImportService.parse_and_validate(csv_bytes)
    result_dict = {
        'status': 'success' if not parse_errors else 'error',
        'parse_errors': parse_errors,
    }
    
    if parse_errors:
        return result_dict
    
    # 2. Upsert contacts
    dm = DatabaseManager()
    with dm.get_session() as session:
        result = ImportService.upsert_contacts(session, rows)
        result_dict.update({
            'total_rows': result.total_rows,
            'created': result.created,
            'updated': result.updated,
            'errors': result.errors,
        })
    
    return result_dict
```

**Key Decision Points:**
- ✅ **Handle BOM** - Use `utf-8-sig` for Excel exports
- ✅ **Upsert logic** - Create if new, update if exists (by contact_id)
- ✅ **Store complex data in custom_fields** - JSON field for flexibility
- ✅ **Async processing** - Use Celery for large imports
- ✅ **Error collection** - Continue processing, collect all errors

#### Performance Considerations

1. **Eager Loading**: Use `.options(joinedload(Contact.raw_notes))` if loading relationships
2. **Field Selection**: Only return needed fields in JSON responses
3. **Indexing**: Ensure `user_id` and `id` are indexed in database
4. **Batch Operations**: For bulk imports, use `session.bulk_insert_mappings()`
5. **Pagination**: For large contact lists, implement pagination (not currently done)
6. **Caching**: Cache contact lists with 5-minute TTL (frontend)

#### Error Scenarios to Handle

1. **Missing required field**: Return 400 with clear error message
2. **Contact not found**: Return 404 (after ownership check)
3. **Database error**: Log and return 500 with generic message
4. **Unauthorized access**: Flask-Login handles redirect (302)
5. **Duplicate name**: Allow (users may have multiple contacts with same name)
6. **Invalid tier value**: Validate tier is 1, 2, or 3 (currently no validation)
7. **Import errors**: Collect and return all errors, don't fail on first error

### Frontend Implementation

**Contacts View** (`static/js/contacts.js`)
- Lazy loading for contact lists
- Search with debouncing
- Tier filter toggle
- Contact creation modal
- Contact detail panel
- vCard import button

### Export & Import Services

**Overview:**
Services for exporting and importing contact data in CSV format. Provides round-trip data preservation with JSON field handling for complex data structures.

**Components:**

1. **ExportService** (`app/services/export_service.py`)
   - CSV generation for contacts
   - UTF-8 BOM encoding for Excel compatibility
   - JSON field stringification

2. **ImportService** (`app/services/import_service.py`)
   - CSV parsing and validation
   - Contact upsert logic
   - Error handling for malformed data

**Key Features:**

1. **Round-Trip Data Preservation**
   - Exports all contact data including categories, tags, sources, raw_logs, edits
   - Imports preserve JSON fields (categories, tags, raw_logs_json, edits_json)
   - Maintains data integrity across export/import cycles

2. **Excel Compatibility**
   - UTF-8 BOM encoding for proper Excel display
   - Proper CSV formatting with quoted fields

3. **Data Validation**
   - Required columns: `user_id`, `contact_name`
   - JSON field parsing with error handling
   - Row-level error reporting

**High-Level Implementation**

#### Implementation Flow: Export Contacts to CSV

**Step 1: ExportService.generate_contacts_csv()**
```python
class ExportService:
    """Generate single-CSV exports for contacts. JSON fields are stringified."""
    
    CSV_HEADER = [
        'user_id', 'user_username', 'user_email',
        'contact_id', 'contact_external_id',
        'contact_name', 'contact_phone', 'contact_email',
        'categories', 'tags', 'sources',
        'raw_logs_json', 'edits_json',
        'created_at', 'updated_at'
    ]
    
    @staticmethod
    def _stringify(value) -> str:
        """Convert value to string, handling JSON objects"""
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    
    @classmethod
    def generate_contacts_csv(cls, rows: Iterable[dict]) -> bytes:
        """
        Generate CSV from contact data.
        
        Args:
            rows: Iterable of dicts matching CSV_HEADER keys
            
        Returns:
            bytes of UTF-8 CSV with BOM for Excel compatibility
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=cls.CSV_HEADER, extrasaction='ignore')
        writer.writeheader()
        
        for row in rows:
            # Stringify all values (JSON fields become JSON strings)
            safe_row = {
                k: cls._stringify(row.get(k)) 
                for k in cls.CSV_HEADER
            }
            writer.writerow(safe_row)
        
        data = output.getvalue()
        # Prepend UTF-8 BOM for Excel compatibility
        return ('\ufeff' + data).encode('utf-8')
```

**Key Decision Points:**
- ✅ **UTF-8 BOM** - Excel requires BOM for proper UTF-8 display
- ✅ **JSON stringification** - Complex fields stored as JSON strings
- ✅ **Extrasaction='ignore'** - Ignore extra fields not in header
- ✅ **ensure_ascii=False** - Preserve Unicode characters

**Step 2: API Endpoint for Export**
```python
@settings_bp.route('/export/contacts-csv', methods=['GET'])
@login_required
def export_contacts_csv():
    """Export current user's contacts to CSV"""
    try:
        from app.services.export_service import ExportService
        from app.utils.database import DatabaseManager
        from app.models import Contact
        
        dm = DatabaseManager()
        with dm.get_session() as session:
            # Get all contacts for current user
            contacts = session.query(Contact).filter_by(
                user_id=current_user.id
            ).all()
            
            # Build rows matching CSV_HEADER
            rows = []
            for c in contacts:
                cf = c.custom_fields or {}
                rows.append({
                    'user_id': current_user.id,
                    'user_username': getattr(current_user, 'username', ''),
                    'user_email': getattr(current_user, 'email', ''),
                    'contact_id': c.id,
                    'contact_external_id': c.vector_collection_id,
                    'contact_name': c.full_name,
                    'contact_phone': c.telegram_phone,
                    'contact_email': (cf or {}).get('email'),
                    'categories': cf.get('categories'),
                    'tags': cf.get('tags'),
                    'sources': cf.get('sources'),
                    'raw_logs_json': cf.get('raw_logs'),
                    'edits_json': cf.get('edits'),
                    'created_at': c.created_at.isoformat() if c.created_at else '',
                    'updated_at': c.updated_at.isoformat() if c.updated_at else '',
                })
            
            # Generate CSV
            csv_bytes = ExportService.generate_contacts_csv(rows)
        
        # Return as downloadable file
        return Response(
            csv_bytes,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="my_contacts.csv"'
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting contacts: {e}")
        return jsonify({'error': 'Failed to export contacts'}), 500
```

**Step 3: ImportService.parse_and_validate()**
```python
class ImportService:
    """Parse single-CSV and upsert contacts and related data."""
    
    REQUIRED_COLUMNS = {'user_id', 'contact_name'}
    
    @staticmethod
    def _parse_json(maybe_json: str):
        """Parse JSON string, return None if invalid"""
        if not maybe_json:
            return None
        try:
            return json.loads(maybe_json)
        except Exception:
            return None
    
    @classmethod
    def parse_and_validate(cls, csv_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse and validate CSV file"""
        errors: List[str] = []
        rows: List[Dict[str, Any]] = []
        
        # Decode with BOM handling
        text = csv_bytes.decode('utf-8-sig')  # Handles UTF-8 BOM
        reader = csv.DictReader(io.StringIO(text))
        
        # Check required columns
        missing = [c for c in cls.REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return [], errors
        
        # Parse each row
        for idx, row in enumerate(reader, start=2):  # Header is line 1
            if not row.get('user_id') or not row.get('contact_name'):
                errors.append(f"Row {idx}: user_id and contact_name are required")
                continue
            
            # Parse JSON fields
            for key in ('categories', 'tags', 'sources', 'raw_logs_json', 'edits_json'):
                row[key] = cls._parse_json(row.get(key)) if row.get(key) else row.get(key)
            
            rows.append(row)
        
        return rows, errors
```

**Step 4: ImportService.upsert_contacts()**
```python
@dataclass
class ImportResult:
    total_rows: int
    created: int
    updated: int
    errors: List[str]

@classmethod
def upsert_contacts(cls, session, rows: List[Dict[str, Any]]) -> ImportResult:
    """Upsert contacts from parsed CSV rows"""
    from app.models import Contact, User
    
    total = len(rows)
    created = 0
    updated = 0
    errors: List[str] = []
    
    for row in rows:
        try:
            # Verify user exists
            user = session.query(User).filter(
                User.id == int(row['user_id'])
            ).first()
            
            if not user:
                errors.append(f"User {row['user_id']} not found")
                continue
            
            # Find or create contact
            contact = None
            if row.get('contact_id'):
                contact = session.query(Contact).filter(
                    Contact.id == int(row['contact_id'])
                ).first()
            
            if contact is None:
                contact = Contact(user_id=user.id, full_name=row['contact_name'])
                created += 1
                session.add(contact)
            else:
                updated += 1
                contact.full_name = row['contact_name'] or contact.full_name
            
            # Update fields
            if row.get('contact_phone'):
                contact.telegram_phone = row['contact_phone']
            
            # Store complex fields in custom_fields
            cf = contact.custom_fields or {}
            if row.get('categories') is not None:
                cf['categories'] = row['categories']
            if row.get('tags') is not None:
                cf['tags'] = row['tags']
            if row.get('raw_logs_json') is not None:
                cf['raw_logs'] = row['raw_logs_json']
            # ... other fields ...
            
            contact.custom_fields = cf
            
        except Exception as exc:
            errors.append(str(exc))
    
    session.commit()
    return ImportResult(total_rows=total, created=created, updated=updated, errors=errors)
```

**Data Flow Diagram: Export/Import**

```
Export: User → GET /api/settings/export/contacts-csv
    → Query contacts → Build rows → ExportService.generate_contacts_csv()
    → UTF-8 BOM CSV → Download

Import: User → POST /api/settings/import/contacts-csv
    → Read file → ImportService.parse_and_validate()
    → ImportService.upsert_contacts() → Return statistics
```

**Integration Points**

1. **Database**: Uses Contact and User models
2. **Custom Fields**: Stores complex data in `custom_fields` JSON column
3. **User Isolation**: Always restricts to current user
4. **File Handling**: Uses Flask's `request.files` for upload

**Security Considerations**

1. **User Isolation**: Always override `user_id` to current user on import
2. **File Validation**: Validate file type and size
3. **Input Sanitization**: Parse and validate all input data

**Testing Approach**

- Test CSV generation with various data types
- Test UTF-8 BOM handling
- Test JSON field round-trip (export → import)
- Test required column validation
- Test upsert logic (create vs update)
- Test user isolation (cannot import to other users)
- Test error collection (multiple errors reported)

### Testing Approach
- Test CRUD operations
- Test vCard import with various formats
- Test duplicate detection logic
- Test tier filtering
- Test user isolation (users can't see others' contacts)
- Test CSV export/import round-trip
- Test data preservation across export/import

---

## Feature 3: Note Processing & AI Analysis
**⚠️ CORE BUSINESS FEATURE - This is the heart of the application**

### Overview
AI-powered analysis of unstructured notes. Supports multiple AI providers (OpenAI, Gemini), automatic categorization into 15+ categories, RAG pipeline with ChromaDB for context, and background processing with Celery. This feature transforms raw conversational notes into structured, actionable intelligence about relationships.

### Business Value
- **Quality-First Analysis**: Prioritizes accuracy and depth over speed
- **Context-Aware**: Uses RAG pipeline to retrieve relevant history for better analysis
- **Multi-Provider**: Gemini (preferred) with OpenAI fallback for reliability
- **Structured Output**: 15 predefined categories for consistent organization
- **Confidence Scoring**: AI provides confidence levels for quality filtering
- **Background Processing**: Async processing for long operations without blocking UI

### User-Facing Pages
- **Note Input Area** (in main contacts view)
  - Textarea for note entry
  - Voice recording button (🎤)
  - Contact selection
  - "Analyze Note" button
  - Analysis results display with editable categories
  - Save/Approve button

### API Endpoints

**`POST /api/notes/process-note`**
- Process note synchronously (for small notes)
- Request: `{ "note": string, "contact_id": int }`
- Response: `{ "synthesis": {...categories...}, "contact_name": string }`

**`POST /api/notes/analyze-note`**
- Process note asynchronously (Celery task)
- Request: `{ "note": string, "contact_id": int }`
- Response: `{ "task_id": string, "status": "pending" }`

**`GET /api/notes/task-status/<task_id>`**
- Get status of async analysis task
- Response: `{ "status": "pending|processing|completed|failed", "result": {...} }`

**`POST /api/notes/save-synthesis`**
- Save approved analysis to database
- Request: `{ "contact_id": int, "synthesis": {...}, "raw_note": string }`
- Response: `{ "success": true, "synthesized_entry_id": int }`

**`GET /api/notes/<contact_id>`**
- Get all notes for a contact
- Response: `{ "raw_notes": [...], "synthesized_entries": [...] }`

### Database Models

**RawNote Model** (`models.py`)
```python
class RawNote(Base):
    __tablename__ = 'raw_notes'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    source = Column(String(50))  # 'manual', 'telegram', 'voice', 'file'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contact = relationship("Contact", back_populates="raw_notes")
```

**SynthesizedEntry Model** (`models.py`)
```python
class SynthesizedEntry(Base):
    __tablename__ = 'synthesized_entries'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'))
    raw_note_id = Column(Integer, ForeignKey('raw_notes.id'))
    categories = Column(JSON, nullable=False)  # Structured categories
    confidence_scores = Column(JSON)  # AI confidence per category
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contact = relationship("Contact", back_populates="synthesized_entries")
```

### Services

**NoteService** (`app/services/note_service.py`)
- `process_note(note_text, contact_id, user_id)` - Orchestrate analysis
- `save_synthesis(contact_id, synthesis, raw_note)` - Persist results
- `get_notes_for_contact(contact_id, user_id)` - Retrieve all notes

**AIService** (`app/services/ai_service.py`)
- `analyze_note(content, contact_name, context=None)` - Main analysis method
- `get_relevant_history(contact_name, query)` - RAG retrieval from ChromaDB
- `select_model()` - Smart model selection (OpenAI/Gemini)
- `categorize_content(content, context)` - Extract categories

### Celery Tasks

**AI Tasks** (`app/tasks/ai_tasks.py`)
```python
@celery_app.task(bind=True)
def process_note_async(self, note_text, contact_id, user_id):
    # Long-running AI analysis
    # Updates task status
    # Returns synthesis result
```

### High-Level Implementation

#### Implementation Flow: Synchronous Note Processing

**Step 1: API Endpoint - Validate Input** (`app/api/notes.py`)
```python
@notes_bp.route('/process-note', methods=['POST'])
@login_required
def process_note():
    # 1. Extract and validate request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    raw_note_text = data.get('note') or data.get('note_text') or ''  # Support both keys
    contact_id = data.get('contact_id')
    
    # 2. Validate required fields
    if not raw_note_text:
        return jsonify({"error": "Valid note text is required"}), 400
    if not contact_id:
        return jsonify({"error": "Valid contact_id is required"}), 400
```

**Key Decision Points:**
- ✅ **Support multiple key names** - `note` or `note_text` for flexibility
- ✅ **Validate early** - Check all required fields before database access
- ✅ **Return specific errors** - Help frontend show helpful messages

**Step 2: Verify Contact Ownership**
```python
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        # 3. Verify contact exists and belongs to user
        contact = session.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id  # CRITICAL: Ownership check
        ).first()
        
        if not contact:
            return jsonify({"error": "Contact not found"}), 404
```

**Key Decision Points:**
- ✅ **Check ownership in same query** - More efficient than separate check
- ✅ **Return 404, not 403** - Don't reveal contact exists for other users

**Step 3: Call AI Service**
```python
        # 4. Initialize AI service (no dependency injection in this endpoint)
        ai_service = AIService()
        
        try:
            # 5. Analyze note with AI
            analysis_result = ai_service.analyze_note(
                content=raw_note_text,
                contact_name=contact.full_name  # Provide context
            )
            
            # 6. Return analysis results
            return jsonify({
                'success': True,
                'synthesis': analysis_result.get('categories', {}),
                'contact_name': contact.full_name
            })
            
        except Exception as ai_error:
            logger.error(f"AI analysis failed for contact {contact_id}: {ai_error}")
            return jsonify({"error": f"AI analysis failed: {str(ai_error)}"}), 500
```

**Key Decision Points:**
- ✅ **Separate try/except for AI** - Different error handling than DB errors
- ✅ **Return categories dict** - Frontend expects this structure
- ✅ **Log errors with context** - Include contact_id for debugging

#### Implementation Flow: Asynchronous Note Processing

**Step 1: Try Celery, Fallback to Sync**
```python
@notes_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_note():
    data = request.get_json() or {}
    contact_id = data.get('contact_id')
    note_text = data.get('note') or data.get('note_text') or ''
    
    if not contact_id or not note_text:
        return jsonify({'error': 'contact_id and note_text required'}), 400
    
    # Try async first (preferred for long operations)
    try:
        task = process_note_async.delay(contact_id, note_text, current_user.id)
        return jsonify({'status': 'queued', 'task_id': task.id}), 202
    except Exception:
        # Fallback to synchronous if Celery unavailable
        ai_service = AIService()
        # ... sync processing ...
        return jsonify({'status': 'completed', ...}), 200
```

**Key Decision Points:**
- ✅ **Try async first** - Better UX for long-running operations
- ✅ **Graceful fallback** - Don't fail if Celery is down
- ✅ **Return 202 for async** - Standard status for queued operations
- ✅ **Return task_id** - Frontend needs this to poll status

**Step 2: Celery Task Implementation** (`app/tasks/ai_tasks.py`)
```python
@celery_app.task(bind=True)  # bind=True gives access to self (task instance)
def process_note_async(self, contact_id: int, content: str, user_id: int):
    try:
        # 1. Update task state (for progress tracking)
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Processing note...'}
        )
        
        # 2. Initialize services (create fresh instances in task context)
        db_manager = DatabaseManager()
        ai_service = AIService()
        note_service = NoteService(db_manager, ai_service)
        
        # 3. Process note (saves to DB and analyzes)
        result = note_service.process_note(contact_id, content, user_id)
        
        # 4. Update task state to success
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'Note processed successfully',
                'result': result
            }
        )
        
        return result
        
    except ValueError as e:
        # Handle specific errors gracefully
        if "Contact not found" in str(e):
            self.update_state(
                state='SUCCESS',
                meta={'status': 'Contact not found, skipped', 'result': None}
            )
            return None
        else:
            self.update_state(
                state='FAILURE',
                meta={'status': 'Failed to process note', 'error': str(e)}
            )
            raise
```

**Key Decision Points:**
- ✅ **Use `bind=True`** - Enables `self.update_state()` for progress
- ✅ **Create fresh service instances** - Don't reuse Flask app context
- ✅ **Update state at each step** - Frontend can poll for progress
- ✅ **Handle ValueError separately** - Business logic errors vs system errors
- ✅ **Return result in meta** - Makes it available via task.result

**Step 3: Task Status Endpoint**
```python
@notes_bp.route('/task/<task_id>/status', methods=['GET'])
@login_required
def get_task_status(task_id):
    from app.celery_app import celery_app
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting to be processed...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'progress': task.info.get('progress', 0)
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'status': 'Task completed successfully',
            'result': task.result  # Contains synthesis data
        }
    else:  # FAILURE
        response = {
            'state': task.state,
            'status': 'Task failed',
            'error': str(task.info)
        }
    
    return jsonify(response)
```

**Key Decision Points:**
- ✅ **Handle all task states** - PENDING, PROGRESS, SUCCESS, FAILURE
- ✅ **Extract info from task.info** - Contains custom metadata
- ✅ **Return result on SUCCESS** - Frontend needs synthesis data

#### Implementation Flow: AI Service Analysis

**Step 1: Service Initialization** (`app/services/ai_service.py`)
```python
class AIService:
    def __init__(self):
        # 1. Try secure credential storage first
        try:
            from secure_credentials import SecureCredentialManager
            manager = SecureCredentialManager('.gemini_credentials.enc')
            secure_gemini_key, model = manager.load_credentials()
            if secure_gemini_key:
                self.gemini_api_key = secure_gemini_key
        except Exception:
            pass
        
        # 2. Fallback to environment variables
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # 3. Configure clients if keys available
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self._available = True
        else:
            self._available = False
```

**Key Decision Points:**
- ✅ **Try secure storage first** - Better security for production
- ✅ **Fallback to env vars** - Easier for development
- ✅ **Mark as unavailable if no keys** - Graceful degradation
- ✅ **Don't raise exception** - Allow service creation, mark unavailable

**Step 2: Analysis with Fallback Chain**
```python
@log_performance("ai_analysis")  # Performance logging decorator
def analyze_note(self, content: str, contact_name: str) -> Dict[str, Any]:
    # 1. Check availability
    if not self._available:
        return self._fallback_analysis(content, contact_name)
    
    # 2. Try Gemini first (preferred)
    if self.gemini_api_key:
        try:
            return self._analyze_with_gemini(content, contact_name)
        except Exception as e:
            logger.warning(f"Gemini analysis failed: {e}")
            # 3. Fallback to OpenAI if Gemini fails
            if self.openai_api_key:
                return self._analyze_with_openai(content, contact_name)
            else:
                return self._fallback_analysis(content, contact_name)
    
    # 4. Try OpenAI if no Gemini
    elif self.openai_api_key:
        try:
            return self._analyze_with_openai(content, contact_name)
        except Exception as e:
            logger.warning(f"OpenAI analysis failed: {e}")
            return self._fallback_analysis(content, contact_name)
    
    # 5. Final fallback
    return self._fallback_analysis(content, contact_name)
```

**Key Decision Points:**
- ✅ **Gemini preferred** - Better quality/cost ratio
- ✅ **OpenAI as fallback** - Redundancy for reliability
- ✅ **Local fallback** - Always return something, never fail completely
- ✅ **Log each failure** - Helps diagnose API issues

**Step 3: Gemini Analysis Implementation**

**Full Gemini Prompt** (exact prompt used in production):
```python
def _analyze_with_gemini(self, content: str, contact_name: str) -> Dict[str, Any]:
    import time
    import json
    import re
    import google.api_core.exceptions
    
    # 1. Select model (configurable via env var, default: gemini-2.5-pro)
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
    model = genai.GenerativeModel(model_name)
    
    # 2. Build the complete prompt with all category definitions
    prompt = f"""
        Analyze this note about {contact_name} and extract structured information.
        
        Categorize the content into these categories (only include if relevant):
        
        CATEGORY_DEFINITIONS:
        - Actionable: Immediate tasks, follow-ups, reminders, requests, or discussion topics requiring attention within days or weeks.
        - Goals: Clearly defined aspirations and objectives across all life domains, including short-term targets (3-12 months), medium-term goals (1-5 years), and long-term visions (5+ years).
        - Relationship_Strategy: Structured approaches to nurturing, deepening, or improving your relationship with specific tactics for connection and support.
        - Social: Comprehensive mapping of their social ecosystem including family dynamics, friendship networks, romantic relationships, professional connections, community involvement.
        - Professional_Background: Detailed career history and occupational profile including employment timeline, educational credentials, skill inventory, achievement record.
        - Financial_Situation: Comprehensive portrait of their economic circumstances, money management approach, and financial outlook.
        - Wellbeing: Holistic health status encompassing physical, mental, emotional, and spiritual dimensions.
        - Avocation: Comprehensive inventory of non-professional interests, passions, and recreational activities.
        - Environment_And_Lifestyle: Detailed portrait of their daily living context and routine patterns.
        - Psychology_And_Values: In-depth profile of their mental frameworks, belief systems, and guiding principles.
        - Communication_Style: Comprehensive analysis of their interpersonal communication patterns and preferences across all contexts.
        - Challenges_And_Development: Nuanced exploration of their struggles, growth areas, and evolution across personal and professional domains.
        - Deeper_Insights: Profound observations about their core essence, philosophical outlook, and unique qualities that transcend conventional categorization.
        - Admin_matters: Administrative details including important dates, birthdays, anniversaries, and other key information to track.
        - Others: Any other important information that doesn't fit into the categories above.
        
        Note content: {content}
        
        Return a JSON response with this structure:
        {{
            "categories": {{
                "Actionable": {{"content": "specific factual information extracted", "confidence": 0.85}},
                "Goals": {{"content": "specific factual information extracted", "confidence": 0.80}},
                "Social": {{"content": "specific factual information extracted", "confidence": 0.90}}
            }}
        }}
        
        IMPORTANT:
        - Only include categories that have relevant content from the note
        - Extract specific, factual information - not interpretations
        - Confidence should be between 0.0 and 1.0 based on clarity of information
        - Be precise and concise in your extraction
        - Focus on actionable insights and meaningful categorization
        
        NEGATIVE CONSTRAINTS (What NOT to do):
        - Do NOT infer feelings, emotions, or internal states not explicitly stated in the note
        - Do NOT add information that is not present in the note text
        - Do NOT make assumptions about relationships beyond what is stated
        - Do NOT extrapolate future plans or intentions unless explicitly mentioned
        - Do NOT categorize information into multiple categories if it clearly belongs to one
        - Do NOT include generic or vague statements that don't add value
        - Do NOT infer negative implications (e.g., "they seem stressed" from "they have a deadline")
        - Do NOT create categories that don't exist in the category list
        - Do NOT include personal opinions or judgments about the contact
        - Do NOT infer causality or connections not explicitly stated
        """
    
    # 3. Call API with retry logic for rate limits
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            break
        except google.api_core.exceptions.ResourceExhausted as e:
            if "quota" in str(e).lower() or "429" in str(e):
                if attempt < max_retries - 1:
                    logger.warning(f"Gemini API rate limit hit, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"Gemini API rate limit exceeded after {max_retries} attempts")
                    raise Exception(f"Gemini API rate limit exceeded: {e}")
            else:
                raise
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    # 4. Parse JSON response - handle markdown code blocks
    response_text = response.text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    if response_text.startswith('```'):
        response_text = response_text[3:]   # Remove ```
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove trailing ```
    
    response_text = response_text.strip()
    
    return json.loads(response_text)
```

**Full OpenAI Prompt** (system + user messages):
```python
def _analyze_with_openai(self, content: str, contact_name: str) -> Dict[str, Any]:
    import json
    
    # System prompt (defines AI role and behavior)
    system_prompt = """You are an AI assistant that analyzes personal notes and extracts structured information into specific categories.

Available categories:
- Actionable: Immediate tasks, follow-ups, reminders, requests requiring attention
- Goals: Aspirations and objectives across all life domains (short/medium/long-term)
- Relationship_Strategy: Structured approaches to nurturing relationships
- Social: Social ecosystem including family, friends, romantic, professional connections
- Professional_Background: Career history, credentials, skills, achievements
- Financial_Situation: Economic circumstances, money management, financial outlook
- Wellbeing: Holistic health status (physical, mental, emotional, spiritual)
- Avocation: Non-professional interests, passions, recreational activities
- Environment_And_Lifestyle: Daily living context and routine patterns
- Psychology_And_Values: Mental frameworks, belief systems, guiding principles
- Communication_Style: Interpersonal communication patterns and preferences
- Challenges_And_Development: Struggles, growth areas, evolution
- Deeper_Insights: Core essence, philosophical outlook, unique qualities
- Admin_matters: Important dates, birthdays, anniversaries, key information
- Others: Information that doesn't fit other categories

Return ONLY a JSON object with this structure:
{
    "categories": {
        "category_name": {"content": "specific factual information", "confidence": 0.85}
    }
}

Only include categories with relevant content. Be factual and precise.

NEGATIVE CONSTRAINTS (What NOT to do):
- Do NOT infer feelings, emotions, or internal states not explicitly stated
- Do NOT add information that is not present in the note text
- Do NOT make assumptions about relationships beyond what is stated
- Do NOT extrapolate future plans or intentions unless explicitly mentioned
- Do NOT categorize information into multiple categories if it clearly belongs to one
- Do NOT include generic or vague statements that don't add value
- Do NOT infer negative implications without explicit evidence
- Do NOT create categories that don't exist in the category list
- Do NOT include personal opinions or judgments about the contact
- Do NOT infer causality or connections not explicitly stated"""

    # User prompt (the actual note to analyze)
    user_prompt = f"""Analyze this note about {contact_name} and extract structured information:

{content}

Return ONLY the JSON response."""

    # API call with temperature=0.3 for more deterministic results
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3  # Lower temperature = more consistent, factual responses
    )
    
    # Parse JSON response
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {"categories": {"other": {"content": response.choices[0].message.content, "confidence": 0.6}}}
```

**Fallback Analysis** (when AI services unavailable):
```python
def _fallback_analysis(self, content: str, contact_name: str) -> Dict[str, Any]:
    """Fallback analysis when AI services are unavailable"""
    logger.info("Using fallback analysis - AI services unavailable")
    
    # Simple keyword-based analysis as fallback
    content_lower = content.lower()
    categories = {}
    
    # Personal info keywords
    personal_keywords = ['age', 'birthday', 'born', 'phone', 'email', 'address', 'lives in', 'from']
    if any(keyword in content_lower for keyword in personal_keywords):
        categories['personal_info'] = {
            'content': content,
            'confidence': 0.6
        }
    
    # Work keywords
    work_keywords = ['work', 'job', 'company', 'office', 'career', 'profession', 'boss', 'colleague']
    if any(keyword in content_lower for keyword in work_keywords):
        categories['work'] = {
            'content': content,
            'confidence': 0.7
        }
    
    # Relationship keywords
    relationship_keywords = ['family', 'friend', 'spouse', 'partner', 'relationship', 'married', 'single']
    if any(keyword in content_lower for keyword in relationship_keywords):
        categories['relationships'] = {
            'content': content,
            'confidence': 0.8
        }
    
    # If no specific categories found, put in 'other'
    if not categories:
        categories['other'] = {
            'content': content,
            'confidence': 0.5
        }
    
    return {'categories': categories}
```

**Key Decision Points:**
- ✅ **Configurable model** - Allow switching models via `GEMINI_MODEL` env var (default: `gemini-2.5-pro`)
- ✅ **Detailed category definitions** - 15 categories with specific definitions for accuracy
- ✅ **Retry with exponential backoff** - Handle rate limits gracefully (2s, 4s, 8s delays)
- ✅ **Parse JSON carefully** - Handle markdown code blocks that models sometimes return
- ✅ **Extract confidence scores** - For quality filtering (0.0-1.0 scale)
- ✅ **Temperature=0.3 for OpenAI** - More deterministic, factual responses
- ✅ **Fallback keyword matching** - Always return something, even if AI unavailable
- ✅ **Only include relevant categories** - Don't create empty categories

**Environment Variables for AI Configuration:**
```env
# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-pro  # Optional, defaults to gemini-2.5-pro
# Alternative env var name also supported:
GOOGLE_API_KEY=your_gemini_api_key_here  # Falls back to this if GEMINI_API_KEY not set

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
# Model is hardcoded to gpt-3.5-turbo in current implementation
# Temperature is hardcoded to 0.3 for deterministic results

# Secure Credential Storage (optional, for production)
# Uses secure_credentials module to load encrypted keys from:
# - .gemini_credentials.enc (for Gemini)
# - SecureCredentialManager for encrypted storage
```

**API Configuration Details:**

**Gemini API Call:**
```python
# Model initialization
model = genai.GenerativeModel(model_name)  # Default: 'gemini-2.5-pro'

# API call (no explicit parameters, uses defaults)
response = model.generate_content(prompt)

# Response structure
response.text  # String containing JSON response
```

**OpenAI API Call:**
```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Hardcoded model
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.3  # Lower = more deterministic, factual responses
)

# Response structure
response.choices[0].message.content  # String containing JSON response
```

**Alternative Gemini Service Configuration** (if using `GeminiService` class):
```python
# Different model and generation config
self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

response = self.model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        max_output_tokens=1000000,  # Very high limit
        temperature=0.1,             # Very low for factual extraction
        top_p=0.8,                   # Nucleus sampling
        top_k=40                     # Top-k sampling
    )
)
```

**Prompt Engineering Notes:**
1. **Category Definitions**: Each category has a detailed definition to guide the AI
2. **Contact Name Context**: Included in prompt to help AI understand relationship context
3. **JSON Structure**: Explicitly defined to ensure consistent response format
4. **Confidence Scores**: Requested to help filter low-quality extractions (0.0-1.0 scale)
5. **Factual Extraction**: Emphasized "specific factual information" not interpretations
6. **Relevance Filtering**: "Only include if relevant" prevents empty categories
7. **IMPORTANT Section**: Explicit instructions at end of prompt for clarity

**Response Parsing Details:**

**Gemini Response Handling:**
```python
# Remove markdown code blocks that models sometimes add
response_text = response.text.strip()
if response_text.startswith('```json'):
    response_text = response_text[7:]  # Remove ```json
if response_text.startswith('```'):
    response_text = response_text[3:]   # Remove ```
if response_text.endswith('```'):
    response_text = response_text[:-3]  # Remove trailing ```
response_text = response_text.strip()
result = json.loads(response_text)
```

**OpenAI Response Handling:**
```python
try:
    result = json.loads(response.choices[0].message.content)
except json.JSONDecodeError:
    # Fallback: wrap entire response in "other" category
    return {
        "categories": {
            "other": {
                "content": response.choices[0].message.content,
                "confidence": 0.6
            }
        }
    }
```

**Error Handling & Retry Logic:**

**Gemini Rate Limiting:**
```python
max_retries = 3
retry_delay = 2  # seconds

for attempt in range(max_retries):
    try:
        response = model.generate_content(prompt)
        break
    except google.api_core.exceptions.ResourceExhausted as e:
        if "quota" in str(e).lower() or "429" in str(e):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff: 2s, 4s, 8s
                continue
            else:
                raise Exception(f"Gemini API rate limit exceeded: {e}")
```

**Service Initialization Priority:**
1. Try secure credential storage first (`.gemini_credentials.enc`)
2. Fallback to environment variables (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)
3. Mark service as unavailable if no keys found (don't raise exception)
4. Allow service creation but return fallback analysis

**Confidence Score Usage:**
```python
# Filter low-confidence extractions
for category, data in analysis_result['categories'].items():
    if data['content'] and len(data['content'].strip()) > 10:
        # Only save if content exists and is substantial
        # Confidence score stored but not used for filtering currently
        entry = SynthesizedEntry(
            confidence_score=data['confidence'],  # 0.0-1.0
            content=data['content']
        )
```

**Performance Logging:**
```python
@log_performance("ai_analysis")  # Decorator logs execution time
def analyze_note(self, content: str, contact_name: str):
    # Automatically logs:
    # - Function name
    # - Execution time
    # - Success/failure
    # - To structured log file
```

#### Implementation Flow: RAG Pipeline (Retrieval-Augmented Generation)

**Overview**: The RAG pipeline retrieves relevant historical notes from ChromaDB to provide context for AI analysis, improving accuracy and consistency.

**Step 1: ChromaDB Client Initialization** (`app/utils/chromadb_client.py`)
```python
class ChromaDBClient:
    """Singleton ChromaDB client for vector storage and semantic search"""
    
    _instance = None
    _client = None
    _db_path = None
    
    def __new__(cls):
        """Singleton pattern - only one instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize_client(self):
        """Initialize ChromaDB persistent client"""
        # 1. Disable telemetry
        os.environ.setdefault('ANONYMIZED_TELEMETRY', 'FALSE')
        
        # 2. Determine storage path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default_chroma_dir = os.path.join(project_root, 'chroma_db')
        self._db_path = os.getenv('CHROMA_DB_PATH', default_chroma_dir)
        
        # 3. Ensure directory exists
        os.makedirs(self._db_path, exist_ok=True)
        
        # 4. Create persistent client
        self._client = chromadb.PersistentClient(path=self._db_path)
        logger.info(f"✅ ChromaDB initialized at: {self._db_path}")
    
    def get_or_create_collection(self, name: str, **kwargs) -> Collection:
        """Get existing collection or create if doesn't exist"""
        client = self.get_client()
        collection = client.get_or_create_collection(name=name, **kwargs)
        return collection
```

**Key Decision Points:**
- ✅ **Singleton pattern** - One client instance across application
- ✅ **Persistent storage** - Data survives restarts
- ✅ **Per-contact collections** - Each contact has own collection (`contact_{id}`)
- ✅ **Automatic directory creation** - No manual setup needed

**Step 2: Store Notes in ChromaDB** (when saving notes)
```python
def store_note_in_chromadb(contact_id: int, note_content: str, note_id: int):
    """Store a note in ChromaDB for future RAG retrieval"""
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        # 1. Get or create collection for this contact
        collection = get_contact_collection(contact_id, prefix="contact_")
        
        # 2. Add note as document with metadata
        collection.add(
            documents=[note_content],
            ids=[f"note_{note_id}"],  # Unique ID: note_{raw_note_id}
            metadatas=[{
                "contact_id": contact_id,
                "note_id": note_id,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
        
        logger.debug(f"Stored note {note_id} in ChromaDB for contact {contact_id}")
        
    except Exception as e:
        # Don't fail note processing if ChromaDB fails
        logger.warning(f"Failed to store note in ChromaDB: {e}")
```

**Key Decision Points:**
- ✅ **Per-contact collections** - Isolated vector spaces per contact
- ✅ **Store after saving** - Only store successfully saved notes
- ✅ **Don't fail on ChromaDB error** - Graceful degradation
- ✅ **Include metadata** - Contact ID, note ID, timestamp for filtering

**Step 2.5: Vector Sync Strategy** (CRUD Operations for ChromaDB)

**CRITICAL**: When a RawNote is updated or deleted, the corresponding vector in ChromaDB MUST be synchronized to prevent RAG from returning outdated or conflicting information. Without proper sync, the RAG pipeline will hallucinate based on stale vectors.

**The Problem:**
- User edits note: "John loves golf" → "I actually hate golf"
- Old vector remains in ChromaDB with "loves golf"
- RAG retrieves old vector → AI sees conflicting information → Hallucinations

**The Solution:**
Maintain strict synchronization between database operations and ChromaDB vectors using a delete-then-add pattern for updates and cascade deletion for deletes.

---

### Vector Sync Strategy: Update Operation

**When**: RawNote content is edited (PUT `/api/notes/<note_id>` or similar)

**Process**:
1. **Calculate new embedding** (automatic when adding to ChromaDB)
2. **Delete old vector ID** (`note_{raw_note_id}`)
3. **Insert new vector** with updated content

**Implementation:**
```python
def update_note_in_chromadb(contact_id: int, note_id: int, new_content: str):
    """
    Update a note in ChromaDB when RawNote is edited.
    
    CRITICAL: This prevents RAG from returning outdated information.
    Process: Delete old vector → Add new vector with updated content.
    
    Args:
        contact_id: Contact ID for collection lookup
        note_id: RawNote ID (used as vector ID: note_{note_id})
        new_content: Updated note content (will be embedded automatically)
    """
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        collection = get_contact_collection(contact_id, prefix="contact_")
        note_id_str = f"note_{note_id}"  # Consistent ID format
        
        # STEP 1: Check if note exists in ChromaDB
        try:
            existing = collection.get(ids=[note_id_str])
            if existing['ids']:
                # STEP 2: Delete old vector (CRITICAL - prevents stale data)
                collection.delete(ids=[note_id_str])
                logger.info(f"✅ Deleted old vector for note {note_id} (preventing RAG hallucinations)")
            else:
                logger.warning(f"⚠️ Note {note_id} not found in ChromaDB, will create new vector")
        except Exception as e:
            logger.warning(f"⚠️ Could not check existing vector for note {note_id}: {e}")
        
        # STEP 3: Add updated note as new vector
        # ChromaDB automatically calculates embedding from document text
        collection.add(
            documents=[new_content],  # New content (embedding calculated automatically)
            ids=[note_id_str],  # Same ID format for consistency
            metadatas=[{
                "contact_id": contact_id,
                "note_id": note_id,
                "timestamp": datetime.utcnow().isoformat(),
                "updated": True,  # Flag to track modifications
                "sync_version": 1  # Increment on each update
            }]
        )
        
        logger.info(f"✅ Updated note {note_id} in ChromaDB for contact {contact_id} (new embedding calculated)")
        
    except Exception as e:
        # CRITICAL: Don't fail note update if ChromaDB fails
        # Log error but allow database operation to succeed
        logger.error(f"❌ Failed to update note {note_id} in ChromaDB: {e}")
        logger.warning(f"⚠️ Note updated in database but ChromaDB sync failed - RAG may return stale data")
        # Don't raise - allow operation to continue
```

**Integration in NoteService:**
```python
def update_note(self, note_id: int, new_content: str, user_id: int):
    """Update a note and sync to ChromaDB"""
    with self.db_manager.get_session() as session:
        # 1. Update database
        raw_note = session.query(RawNote).filter(
            RawNote.id == note_id,
            RawNote.contact.has(user_id=user_id)
        ).first()
        
        if not raw_note:
            raise ValueError("Note not found")
        
        old_content = raw_note.content
        raw_note.content = new_content
        raw_note.updated_at = datetime.utcnow()
        session.commit()
        
        # 2. Sync to ChromaDB (non-blocking)
        try:
            update_note_in_chromadb(
                contact_id=raw_note.contact_id,
                note_id=note_id,
                new_content=new_content
            )
        except Exception as e:
            logger.error(f"ChromaDB sync failed for note {note_id}: {e}")
            # Continue - database update succeeded
        
        return raw_note
```

---

### Vector Sync Strategy: Delete Operation

**When**: RawNote is deleted (DELETE `/api/notes/<note_id>`)

**Process**:
1. **Cascade delete the vector ID** (`note_{raw_note_id}`)
2. **Verify deletion** (optional, for logging)

**Implementation:**
```python
def delete_note_from_chromadb(contact_id: int, note_id: int):
    """
    Delete a note from ChromaDB when RawNote is deleted.
    
    CRITICAL: Cascade deletion prevents RAG from retrieving deleted notes.
    This is a hard delete - vector is permanently removed.
    
    Args:
        contact_id: Contact ID for collection lookup
        note_id: RawNote ID (used as vector ID: note_{note_id})
    """
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        collection = get_contact_collection(contact_id, prefix="contact_")
        note_id_str = f"note_{note_id}"
        
        # STEP 1: Delete vector by ID (cascade delete)
        collection.delete(ids=[note_id_str])
        
        # STEP 2: Verify deletion (optional, for logging)
        try:
            remaining = collection.get(ids=[note_id_str])
            if remaining['ids']:
                logger.warning(f"⚠️ Vector {note_id_str} still exists after deletion attempt")
            else:
                logger.info(f"✅ Verified deletion of vector {note_id_str}")
        except Exception:
            # Vector doesn't exist - deletion successful
            logger.info(f"✅ Vector {note_id_str} deleted (or never existed)")
        
        logger.info(f"✅ Deleted note {note_id} from ChromaDB for contact {contact_id}")
        
    except Exception as e:
        # CRITICAL: Don't fail note deletion if ChromaDB fails
        logger.error(f"❌ Failed to delete note {note_id} from ChromaDB: {e}")
        logger.warning(f"⚠️ Note deleted from database but ChromaDB sync failed - orphaned vector may remain")
        # Don't raise - allow operation to continue
```

**Integration in NoteService:**
```python
def delete_note(self, note_id: int, user_id: int):
    """Delete a note and cascade delete from ChromaDB"""
    with self.db_manager.get_session() as session:
        # 1. Get note before deletion (for ChromaDB sync)
        raw_note = session.query(RawNote).filter(
            RawNote.id == note_id,
            RawNote.contact.has(user_id=user_id)
        ).first()
        
        if not raw_note:
            raise ValueError("Note not found")
        
        contact_id = raw_note.contact_id
        
        # 2. Delete from database (cascade will handle SynthesizedEntry)
        session.delete(raw_note)
        session.commit()
        
        # 3. Cascade delete from ChromaDB (non-blocking)
        try:
            delete_note_from_chromadb(
                contact_id=contact_id,
                note_id=note_id
            )
        except Exception as e:
            logger.error(f"ChromaDB cascade delete failed for note {note_id}: {e}")
            # Continue - database deletion succeeded
        
        return True
```

**Database Cascade Configuration:**
```python
# In models.py - RawNote model
class RawNote(Base):
    # ... other fields ...
    
    # Cascade delete to ChromaDB is handled in application code
    # Database cascade only handles SynthesizedEntry
    synthesized_entries = relationship(
        "SynthesizedEntry", 
        back_populates="raw_note", 
        cascade="all, delete-orphan"  # Database cascade
    )
    
    # ChromaDB cascade is handled in NoteService.delete_note()
```

---

### Vector Sync Strategy: Complete CRUD Flow

**Create (C)**: Store new vector when note is created
```python
# On note creation
store_note_in_chromadb(contact_id, note_content, note_id)
```

**Read (R)**: Query vectors for RAG retrieval
```python
# On RAG retrieval
get_relevant_history(contact_id, query_text, n_results=3)
```

**Update (U)**: Delete old vector → Add new vector
```python
# On note update
update_note_in_chromadb(contact_id, note_id, new_content)
# Process: Delete old → Calculate new embedding → Insert new
```

**Delete (D)**: Cascade delete vector
```python
# On note deletion
delete_note_from_chromadb(contact_id, note_id)
# Process: Delete vector by ID → Verify deletion
```

---

### Integration Points & Error Handling

**Integration Points:**
- **On RawNote Update**: Call `update_note_in_chromadb()` immediately after database commit
- **On RawNote Delete**: Call `delete_note_from_chromadb()` immediately after database commit
- **On SynthesizedEntry Update**: If note content changes, update ChromaDB vector
- **On Batch Operations**: Update/delete vectors in batch for efficiency

**Error Handling Strategy:**
```python
# Pattern: Try ChromaDB sync, but don't block database operations
try:
    update_note_in_chromadb(contact_id, note_id, new_content)
except Exception as e:
    logger.error(f"ChromaDB sync failed: {e}")
    # Continue - database operation succeeded
    # Log warning for manual sync if needed
```

**Why Non-Blocking?**
- ChromaDB is an enhancement (RAG), not a requirement
- Database operations must succeed even if ChromaDB is unavailable
- Failed syncs can be retried later or logged for manual intervention

---

### Key Decision Points

- ✅ **Delete-then-Add Pattern** - ChromaDB doesn't support direct updates, so delete old vector and add new one
- ✅ **ID Consistency** - Use `note_{raw_note_id}` format consistently for reliable lookups
- ✅ **Non-Blocking** - ChromaDB sync failures don't prevent note edits/deletes
- ✅ **Metadata Tracking** - Include `updated` flag and `sync_version` in metadata
- ✅ **Cascade Deletion** - Always delete vector when note is deleted
- ✅ **Verification** - Optional verification step after deletion for logging
- ✅ **Automatic Embedding** - ChromaDB calculates embeddings automatically from document text
- ✅ **Error Recovery** - Log failures for manual sync or retry mechanisms

**Step 3: Retrieve Relevant History** (before AI analysis)
```python
def get_relevant_history(contact_id: int, query_text: str, n_results: int = 3) -> str:
    """Retrieve relevant historical notes from ChromaDB for context"""
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        # 1. Get contact's collection
        collection = get_contact_collection(contact_id, prefix="contact_")
        
        # 2. Create query from first 30 words of note (for semantic search)
        query_words = query_text.split()[:30]
        query_text_short = " ".join(query_words)
        
        # 3. Query ChromaDB for similar notes
        results = collection.query(
            query_texts=[query_text_short],
            n_results=n_results  # Get top 3 most relevant
        )
        
        # 4. Format retrieved history
        if results['documents'] and len(results['documents'][0]) > 0:
            retrieved_docs = results['documents'][0]
            retrieved_history = "\n---\n".join(retrieved_docs)
            logger.debug(f"Retrieved {len(retrieved_docs)} relevant notes for contact {contact_id}")
            return retrieved_history
        else:
            logger.debug(f"No relevant history found for contact {contact_id}")
            return "No relevant history found."
            
    except Exception as e:
        # Graceful fallback - proceed without context
        logger.warning(f"RAG pipeline unavailable, proceeding without context: {e}")
        return "No relevant history found."
```

**Key Decision Points:**
- ✅ **Use first 30 words** - Focus on key concepts, not entire note
- ✅ **Top 3 results** - Balance between context and prompt size
- ✅ **Separate with `---`** - Clear delimiter between historical notes
- ✅ **Graceful fallback** - Continue without context if ChromaDB fails
- ✅ **Log retrieval** - Monitor RAG effectiveness

**Step 4: Integrate RAG into AI Analysis**
```python
def analyze_note_with_rag(self, content: str, contact_id: int, contact_name: str) -> Dict[str, Any]:
    """Analyze note with RAG context retrieval"""
    
    # 1. Retrieve relevant history from ChromaDB
    retrieved_history = get_relevant_history(contact_id, content, n_results=3)
    
    # 2. Build enhanced prompt with context
    prompt = f"""
    Analyze this note about {contact_name} and extract structured information.
    
    **Retrieved Relevant History:**
    {retrieved_history}
    
    **New Note to Analyze:**
    {content}
    
    Use the retrieved history to:
    - Maintain consistency with previous information
    - Identify contradictions or updates
    - Build upon existing knowledge
    - Extract new information not in history
    
    Categorize into these categories:
    [Category definitions...]
    
    Return JSON with categories...
    """
    
    # 3. Call AI with enhanced prompt
    return self._analyze_with_gemini(prompt, contact_name)
```

**Key Decision Points:**
- ✅ **Retrieve before analysis** - Context improves accuracy
- ✅ **Include in prompt** - AI uses history for better understanding
- ✅ **Maintain consistency** - RAG helps avoid contradictions
- ✅ **Identify updates** - Detect when new info contradicts old

#### Implementation Flow: Complete Note Processing Pipeline

**Step 1: NoteService.process_note() - Full Implementation** (`app/services/note_service.py`)
```python
@log_performance("note_processing")
def process_note(self, contact_id: int, content: str, user_id: int) -> Dict[str, Any]:
    """Complete note processing pipeline: save → analyze → store → return"""
    
    with self.db_manager.get_session() as session:
        # 1. Verify contact ownership
        contact = self._get_user_contact(session, contact_id, user_id)
        if not contact:
            raise ValueError("Contact not found")
        
        # 2. Save raw note to database
        raw_note = RawNote(
            contact_id=contact_id,
            content=content.strip(),
            source='manual',  # 'manual', 'telegram', 'voice', 'file'
            created_at=datetime.utcnow(),
            metadata_tags={
                "type": "manual_note",
                "source": "ui_note_input",
                "user_id": user_id
            }
        )
        session.add(raw_note)
        session.flush()  # Get ID without committing
        
        # 3. Store in ChromaDB for future RAG (async, don't block)
        try:
            from app.utils.chromadb_client import get_contact_collection
            collection = get_contact_collection(contact_id)
            collection.add(
                documents=[content],
                ids=[f"note_{raw_note.id}"],
                metadatas=[{
                    "contact_id": contact_id,
                    "note_id": raw_note.id,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            )
        except Exception as e:
            logger.warning(f"Failed to store in ChromaDB: {e}")
            # Continue - ChromaDB is optional
        
        # 4. Retrieve relevant history for RAG context
        retrieved_history = "No relevant history found."
        try:
            from app.utils.chromadb_client import get_contact_collection
            collection = get_contact_collection(contact_id)
            query_text = " ".join(content.split()[:30])  # First 30 words
            results = collection.query(
                query_texts=[query_text],
                n_results=3
            )
            if results['documents'] and len(results['documents'][0]) > 0:
                retrieved_history = "\n---\n".join(results['documents'][0])
        except Exception as e:
            logger.debug(f"RAG retrieval failed: {e}")
        
        # 5. Analyze with AI (with RAG context)
        try:
            analysis_result = self.ai_service.analyze_note(
                content=content,
                contact_name=contact.full_name,
                context=retrieved_history  # Pass RAG context
            )
            
            # 6. Save synthesized entries to database
            synthesis_results = []
            for category, data in analysis_result['categories'].items():
                # Filter: only save meaningful content (min 10 chars)
                if data.get('content') and len(data['content'].strip()) > 10:
                    entry = SynthesizedEntry(
                        contact_id=contact_id,
                        raw_note_id=raw_note.id,  # Link to raw note
                        category=category,
                        content=data['content'].strip(),
                        confidence_score=data.get('confidence', 0.0),
                        created_at=datetime.utcnow()
                    )
                    session.add(entry)
                    synthesis_results.append({
                        'category': category,
                        'content': data['content'],
                        'confidence': data['confidence']
                    })
            
            # 7. Commit all changes (raw note + synthesized entries)
            session.commit()
            
            return {
                'success': True,
                'raw_note_id': raw_note.id,
                'synthesis': synthesis_results,
                'contact_name': contact.full_name,
                'categories_count': len(synthesis_results)
            }
            
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {ai_error}")
            # Still save the raw note even if AI fails
            session.commit()
            return {
                'success': True,
                'raw_note_id': raw_note.id,
                'synthesis': [],
                'ai_error': str(ai_error),
                'contact_name': contact.full_name
            }
```

**Key Decision Points:**
- ✅ **Save raw note first** - Always preserve original input
- ✅ **Store in ChromaDB** - For future RAG retrieval
- ✅ **Retrieve history** - Get context before analysis
- ✅ **Filter low-quality extractions** - Min 10 characters, confidence > 0
- ✅ **Link entries to raw note** - Maintain traceability
- ✅ **Save even if AI fails** - Never lose user input

#### Implementation Flow: Save Synthesis (User Approval)

**Step 1: Save Synthesis Endpoint** (`app/api/notes.py`)
```python
@notes_bp.route('/save-synthesis', methods=['POST'])
@login_required
def save_synthesis():
    """Save approved analysis to database (user reviews and approves before saving)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        contact_id = data.get('contact_id')
        raw_note_text = data.get('raw_note')
        synthesis_data = data.get('synthesis')
        
        # 1. Validate required fields
        if not contact_id or not synthesis_data:
            return jsonify({"error": "Missing required data: contact_id and synthesis"}), 400
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            # 2. Verify contact ownership
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == current_user.id
            ).first()
            
            if not contact:
                return jsonify({"error": "Contact not found"}), 404
            
            # 3. Save raw note if provided (may have been saved already)
            raw_note_id = None
            if isinstance(raw_note_text, str) and raw_note_text.strip():
                raw_note = RawNote(
                    contact_id=contact_id,
                    content=raw_note_text.strip(),
                    created_at=datetime.utcnow(),
                    metadata_tags={
                        "type": "manual_note",
                        "source": "ui_note_input",
                        "approved": True
                    }
                )
                session.add(raw_note)
                session.flush()
                raw_note_id = raw_note.id
            
            # 4. Handle multiple synthesis data formats
            categories_to_save = {}
            
            if isinstance(synthesis_data, dict):
                # Format 1: synthesis.synthesis (nested)
                if 'synthesis' in synthesis_data and isinstance(synthesis_data['synthesis'], dict):
                    categories_to_save = synthesis_data['synthesis']
                # Format 2: synthesis.categories (direct)
                elif 'categories' in synthesis_data:
                    categories_to_save = synthesis_data['categories']
                # Format 3: synthesis_data is categories dict
                else:
                    categories_to_save = synthesis_data
            
            # 5. Save each category entry
            saved_count = 0
            for category, category_data in categories_to_save.items():
                if isinstance(category_data, dict):
                    content = category_data.get('content', '')
                    confidence = category_data.get('confidence', 0.0)
                elif isinstance(category_data, str):
                    content = category_data
                    confidence = 0.0
                else:
                    continue
                
                # Only save meaningful content
                if content and len(content.strip()) > 10:
                    synthesized_entry = SynthesizedEntry(
                        contact_id=contact_id,
                        raw_note_id=raw_note_id,
                        category=category,
                        content=content.strip(),
                        confidence_score=confidence,
                        created_at=datetime.utcnow()
                    )
                    session.add(synthesized_entry)
                    saved_count += 1
            
            # 6. Commit all changes
            session.commit()
            logger.info(f"Saved {saved_count} synthesized entries for contact {contact_id}")
            
            return jsonify({
                "success": True,
                "message": "Note analyzed and saved successfully",
                "saved_entries": saved_count
            }), 200
            
    except Exception as e:
        logger.exception(f"Error saving synthesis: {e}")
        return jsonify({"error": f"Failed to save synthesis: {str(e)}"}), 500
```

**Key Decision Points:**
- ✅ **User approval step** - User reviews before saving (quality control)
- ✅ **Handle multiple formats** - Flexible input handling
- ✅ **Filter empty categories** - Only save meaningful content
- ✅ **Link to raw note** - Maintain relationship
- ✅ **Count saved entries** - Return useful feedback

#### Implementation Flow: Response Parsing & Normalization

**Step 1: Parse AI Response** (handle various formats)
```python
def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """Parse AI response, handling markdown, JSON, and edge cases"""
    import json
    import re
    
    # 1. Strip whitespace
    response_text = response_text.strip()
    
    # 2. Remove markdown code blocks (models sometimes add these)
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    if response_text.startswith('```'):
        response_text = response_text[3:]   # Remove ```
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove trailing ```
    response_text = response_text.strip()
    
    # 3. Try to parse JSON
    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError:
        # 4. Try to extract JSON from text (sometimes wrapped in explanation)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                return result
            except json.JSONDecodeError:
                pass
        
        # 5. Fallback: wrap entire response in "other" category
        logger.warning(f"Failed to parse AI response as JSON, using fallback")
        return {
            "categories": {
                "Others": {
                    "content": response_text,
                    "confidence": 0.5
                }
            }
        }
```

**Key Decision Points:**
- ✅ **Handle markdown blocks** - Models often wrap JSON in code blocks
- ✅ **Regex extraction** - Extract JSON from explanatory text
- ✅ **Fallback strategy** - Never return empty, always return something
- ✅ **Log parsing failures** - Monitor for prompt improvements

**Step 2: Normalize Category Names**
```python
def normalize_category_name(category: str) -> str:
    """Normalize category names to match database schema"""
    # Map variations to standard names
    category_map = {
        'actionable': 'Actionable',
        'goals': 'Goals',
        'relationship_strategy': 'Relationship_Strategy',
        'relationship strategy': 'Relationship_Strategy',
        'social': 'Social',
        'professional_background': 'Professional_Background',
        'professional background': 'Professional_Background',
        'financial_situation': 'Financial_Situation',
        'financial situation': 'Financial_Situation',
        'wellbeing': 'Wellbeing',
        'avocation': 'Avocation',
        'environment_and_lifestyle': 'Environment_And_Lifestyle',
        'environment and lifestyle': 'Environment_And_Lifestyle',
        'psychology_and_values': 'Psychology_And_Values',
        'psychology and values': 'Psychology_And_Values',
        'communication_style': 'Communication_Style',
        'communication style': 'Communication_Style',
        'challenges_and_development': 'Challenges_And_Development',
        'challenges and development': 'Challenges_And_Development',
        'deeper_insights': 'Deeper_Insights',
        'deeper insights': 'Deeper_Insights',
        'admin_matters': 'Admin_matters',
        'admin matters': 'Admin_matters',
        'others': 'Others',
        'other': 'Others'
    }
    
    # Normalize: lowercase, strip, map
    normalized = category.lower().strip()
    return category_map.get(normalized, category)  # Return mapped or original
```

**Key Decision Points:**
- ✅ **Handle variations** - AI may return different formats
- ✅ **Case-insensitive** - Normalize to lowercase first
- ✅ **Default to original** - If no mapping, use as-is
- ✅ **Consistent naming** - Match database schema exactly

**Step 3: Validate and Filter Categories**
```python
def validate_and_filter_categories(categories: Dict[str, Any]) -> Dict[str, Any]:
    """Validate category structure and filter invalid entries"""
    VALID_CATEGORIES = {
        'Actionable', 'Goals', 'Relationship_Strategy', 'Social',
        'Professional_Background', 'Financial_Situation', 'Wellbeing',
        'Avocation', 'Environment_And_Lifestyle', 'Psychology_And_Values',
        'Communication_Style', 'Challenges_And_Development', 'Deeper_Insights',
        'Admin_matters', 'Others'
    }
    
    filtered = {}
    for category, data in categories.items():
        # 1. Normalize category name
        normalized_category = normalize_category_name(category)
        
        # 2. Validate category is in allowed list
        if normalized_category not in VALID_CATEGORIES:
            logger.warning(f"Invalid category '{category}', mapping to 'Others'")
            normalized_category = 'Others'
        
        # 3. Extract content and confidence
        if isinstance(data, dict):
            content = data.get('content', '')
            confidence = data.get('confidence', 0.0)
        elif isinstance(data, str):
            content = data
            confidence = 0.0
        else:
            continue  # Skip invalid format
        
        # 4. Filter empty or too-short content
        if content and len(content.strip()) > 10:
            # 5. Clamp confidence to 0.0-1.0
            confidence = max(0.0, min(1.0, float(confidence)))
            
            # 6. Merge if category already exists (append content)
            if normalized_category in filtered:
                existing_content = filtered[normalized_category]['content']
                filtered[normalized_category]['content'] = f"{existing_content}\n{content}"
                # Use higher confidence
                filtered[normalized_category]['confidence'] = max(
                    filtered[normalized_category]['confidence'],
                    confidence
                )
            else:
                filtered[normalized_category] = {
                    'content': content.strip(),
                    'confidence': confidence
                }
    
    return filtered
```

**Key Decision Points:**
- ✅ **Validate category names** - Only allow predefined categories
- ✅ **Filter short content** - Minimum 10 characters
- ✅ **Clamp confidence** - Ensure 0.0-1.0 range
- ✅ **Merge duplicates** - Combine if same category appears twice
- ✅ **Use higher confidence** - When merging, keep best confidence

#### Implementation Flow: Batch Processing

**Step 1: Batch Process Notes** (`app/tasks/ai_tasks.py`)
```python
@celery_app.task(bind=True)
def batch_process_notes(self, note_data: list):
    """Process multiple notes in batch with progress tracking"""
    try:
        total_notes = len(note_data)
        processed = 0
        results = []
        errors = []
        
        # Initialize services once
        db_manager = DatabaseManager()
        ai_service = AIService()
        note_service = NoteService(db_manager, ai_service)
        
        for i, note_info in enumerate(note_data):
            try:
                # 1. Update progress
                progress = int((i / total_notes) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Processing note {i+1}/{total_notes}',
                        'progress': progress,
                        'processed': processed,
                        'total': total_notes
                    }
                )
                
                # 2. Process individual note
                contact_id = note_info['contact_id']
                content = note_info['content']
                user_id = note_info['user_id']
                
                result = note_service.process_note(contact_id, content, user_id)
                results.append({
                    'contact_id': contact_id,
                    'success': True,
                    'result': result
                })
                processed += 1
                
            except Exception as e:
                # Log error but continue processing
                logger.error(f"Error processing note {i+1}: {e}")
                errors.append({
                    'note_index': i,
                    'error': str(e)
                })
                results.append({
                    'contact_id': note_info.get('contact_id'),
                    'success': False,
                    'error': str(e)
                })
        
        # 3. Final state update
        self.update_state(
            state='SUCCESS',
            meta={
                'status': f'Processed {processed}/{total_notes} notes successfully',
                'processed': processed,
                'total': total_notes,
                'errors': len(errors),
                'results': results
            }
        )
        
        return {
            'processed': processed,
            'total': total_notes,
            'errors': errors,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        self.update_state(
            state='FAILURE',
            meta={'status': 'Batch processing failed', 'error': str(e)}
        )
        raise
```

**Key Decision Points:**
- ✅ **Progress tracking** - Update state for each note
- ✅ **Continue on error** - Don't stop batch on single failure
- ✅ **Collect all results** - Return success and failures
- ✅ **Initialize services once** - More efficient for batch

#### Implementation Flow: Quality Assurance & Validation

**Step 1: Content Quality Checks**
```python
def validate_extracted_content(content: str, confidence: float) -> bool:
    """Validate extracted content meets quality standards"""
    
    # 1. Minimum length check
    if not content or len(content.strip()) < 10:
        return False
    
    # 2. Confidence threshold (optional - currently not enforced)
    # if confidence < 0.5:
    #     return False
    
    # 3. Check for placeholder text
    placeholder_patterns = [
        'example', 'placeholder', 'test', 'lorem ipsum',
        'n/a', 'not applicable', 'none', 'no information'
    ]
    content_lower = content.lower()
    if any(pattern in content_lower for pattern in placeholder_patterns):
        logger.warning(f"Detected placeholder text: {content[:50]}")
        return False
    
    # 4. Check for meaningful content (not just punctuation)
    meaningful_chars = sum(1 for c in content if c.isalnum())
    if meaningful_chars < 5:
        return False
    
    return True
```

**Step 2: Confidence Score Normalization**
```python
def normalize_confidence_score(confidence: Any) -> float:
    """Normalize confidence score to 0.0-1.0 range"""
    try:
        # Handle string confidence (e.g., "0.85" or "85%")
        if isinstance(confidence, str):
            if '%' in confidence:
                return float(confidence.replace('%', '')) / 100.0
            else:
                return float(confidence)
        
        # Handle numeric confidence
        confidence_float = float(confidence)
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, confidence_float))
        
    except (ValueError, TypeError):
        # Default to 0.5 if can't parse
        logger.warning(f"Invalid confidence value: {confidence}, defaulting to 0.5")
        return 0.5
```

**Step 3: Category Content Deduplication**
```python
def deduplicate_category_content(categories: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicate content within and across categories"""
    seen_content = set()
    deduplicated = {}
    
    for category, data in categories.items():
        content = data.get('content', '') if isinstance(data, dict) else str(data)
        
        # Normalize content for comparison (lowercase, strip)
        normalized = content.lower().strip()
        
        # Skip if exact duplicate
        if normalized in seen_content:
            logger.debug(f"Skipping duplicate content in category {category}")
            continue
        
        # Skip if very similar (fuzzy match - optional)
        # Could use fuzzywuzzy or similar for advanced deduplication
        
        seen_content.add(normalized)
        deduplicated[category] = data
    
    return deduplicated
```

#### Complete Data Flow Diagram: Note Processing

```
User enters note in UI
    ↓
POST /api/notes/analyze
    ↓
Validate input (note_text, contact_id)
    ↓
Verify contact ownership
    ↓
Try Celery async task
    ├─ Success → Return 202 + task_id
    │   ↓
    │   Celery Worker: process_note_async
    │   ↓
    │   NoteService.process_note()
    │   ├─ Save RawNote to database
    │   ├─ Store in ChromaDB (for future RAG)
    │   ├─ Retrieve relevant history (RAG)
    │   ├─ Call AIService.analyze_note()
    │   │   ├─ Try Gemini API
    │   │   ├─ Fallback to OpenAI
    │   │   └─ Fallback to local analysis
    │   ├─ Parse & normalize response
    │   ├─ Validate categories
    │   ├─ Filter low-quality extractions
    │   └─ Save SynthesizedEntry records
    │   ↓
    │   Update task state: SUCCESS
    │   ↓
    │   Frontend polls: GET /api/notes/task/<task_id>/status
    │   ↓
    │   Display synthesis results
    │   ↓
    │   User reviews and edits
    │   ↓
    │   POST /api/notes/save-synthesis
    │   ↓
    │   Save approved synthesis to database
    └─ Failure → Fallback to sync processing
```

#### ChromaDB Integration Details

**Collection Naming Convention:**
```python
# Per-contact collections
collection_name = f"contact_{contact_id}"  # e.g., "contact_123"

# Master collection (optional, for cross-contact search)
master_collection = "master_contacts"
```

**Document Storage Format:**
```python
collection.add(
    documents=[note_content],  # The actual note text
    ids=[f"note_{raw_note_id}"],  # Unique identifier
    metadatas=[{
        "contact_id": contact_id,
        "note_id": raw_note_id,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "manual"  # or "telegram", "voice", "file"
    }]
)
```

**Query Parameters:**
```python
results = collection.query(
    query_texts=[query_text],  # Search query (first 30 words of new note)
    n_results=3,  # Number of similar notes to retrieve
    # Optional filters:
    # where={"contact_id": contact_id},  # Filter by metadata
    # include=["documents", "metadatas", "distances"]  # What to return
)
```

**Key Decision Points:**
- ✅ **Per-contact collections** - Isolated semantic spaces
- ✅ **Store full note text** - For accurate similarity matching
- ✅ **Include metadata** - For filtering and debugging
- ✅ **Query with first 30 words** - Focus on key concepts
- ✅ **Top 3 results** - Balance context vs prompt size

#### Error Handling & Resilience

**Error Handling Strategy:**
```python
def process_note_with_error_handling(contact_id, content, user_id):
    """Process note with comprehensive error handling"""
    try:
        # 1. Database operations
        try:
            raw_note = save_raw_note(contact_id, content)
        except DatabaseError as e:
            logger.error(f"Database error saving note: {e}")
            return {'error': 'Failed to save note', 'code': 'database_error'}
        
        # 2. ChromaDB operations (non-critical)
        try:
            store_in_chromadb(contact_id, content, raw_note.id)
        except Exception as e:
            logger.warning(f"ChromaDB storage failed (non-critical): {e}")
            # Continue - ChromaDB is optional
        
        # 3. RAG retrieval (non-critical)
        try:
            context = get_relevant_history(contact_id, content)
        except Exception as e:
            logger.warning(f"RAG retrieval failed (non-critical): {e}")
            context = "No relevant history found."
        
        # 4. AI analysis (critical, but has fallbacks)
        try:
            result = ai_service.analyze_note(content, contact_name, context)
        except RateLimitError as e:
            logger.error(f"AI rate limit: {e}")
            return {'error': 'AI service temporarily unavailable', 'code': 'rate_limit'}
        except APIError as e:
            logger.error(f"AI API error: {e}")
            # Try fallback service
            result = try_fallback_ai_service(content, contact_name)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Use local fallback
            result = local_fallback_analysis(content, contact_name)
        
        # 5. Save synthesis (critical)
        try:
            save_synthesis(contact_id, result, raw_note.id)
        except DatabaseError as e:
            logger.error(f"Failed to save synthesis: {e}")
            return {'error': 'Analysis completed but failed to save', 'code': 'save_error'}
        
        return {'success': True, 'result': result}
        
    except Exception as e:
        logger.exception(f"Unexpected error in note processing: {e}")
        return {'error': 'Unexpected error', 'code': 'unknown_error'}
```

**Key Decision Points:**
- ✅ **Non-critical operations** - ChromaDB failures don't block processing
- ✅ **Multiple fallbacks** - Gemini → OpenAI → Local
- ✅ **Always save raw note** - Never lose user input
- ✅ **Specific error codes** - Help frontend show appropriate messages
- ✅ **Log all errors** - Comprehensive debugging information

#### Performance Optimization

**1. Caching AI Responses** (optional, for similar notes)
```python
from functools import lru_cache
import hashlib

def get_note_hash(content: str) -> str:
    """Generate hash for note content (for caching)"""
    normalized = content.lower().strip()
    return hashlib.md5(normalized.encode()).hexdigest()

# Cache AI responses (with size limit)
@lru_cache(maxsize=100)
def cached_analyze_note(content_hash: str, contact_name: str) -> Dict[str, Any]:
    """Cached version of analyze_note (for identical notes)"""
    # Note: This is simplified - actual implementation would need
    # to handle the full content, not just hash
    pass
```

**2. Batch ChromaDB Operations**
```python
def batch_store_notes(contact_id: int, notes: List[Dict]):
    """Store multiple notes in ChromaDB efficiently"""
    collection = get_contact_collection(contact_id)
    
    documents = [note['content'] for note in notes]
    ids = [f"note_{note['id']}" for note in notes]
    metadatas = [{
        "contact_id": contact_id,
        "note_id": note['id'],
        "timestamp": note['timestamp']
    } for note in notes]
    
    # Single batch operation
    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
```

**3. Async ChromaDB Operations**
```python
from celery import current_task

@celery_app.task
def store_note_in_chromadb_async(contact_id: int, note_content: str, note_id: int):
    """Store note in ChromaDB asynchronously (non-blocking)"""
    try:
        collection = get_contact_collection(contact_id)
        collection.add(
            documents=[note_content],
            ids=[f"note_{note_id}"],
            metadatas=[{
                "contact_id": contact_id,
                "note_id": note_id,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
    except Exception as e:
        logger.warning(f"Async ChromaDB storage failed: {e}")
```

#### Quality Assurance Measures

**1. Confidence Score Thresholds**
```python
CONFIDENCE_THRESHOLDS = {
    'high': 0.8,      # Very confident - save automatically
    'medium': 0.5,    # Moderate confidence - user review recommended
    'low': 0.3        # Low confidence - flag for review
}

def categorize_by_confidence(entry: Dict) -> str:
    """Categorize entry by confidence level"""
    confidence = entry.get('confidence', 0.0)
    if confidence >= CONFIDENCE_THRESHOLDS['high']:
        return 'high'
    elif confidence >= CONFIDENCE_THRESHOLDS['medium']:
        return 'medium'
    else:
        return 'low'
```

**2. Content Quality Scoring**
```python
def score_content_quality(content: str) -> float:
    """Score content quality (0.0-1.0)"""
    score = 1.0
    
    # Penalize very short content
    if len(content) < 20:
        score -= 0.3
    
    # Penalize placeholder text
    if any(word in content.lower() for word in ['example', 'test', 'placeholder']):
        score -= 0.5
    
    # Penalize mostly punctuation
    alnum_ratio = sum(1 for c in content if c.isalnum()) / len(content) if content else 0
    if alnum_ratio < 0.5:
        score -= 0.3
    
    return max(0.0, score)
```

**3. Validation Before Saving**
```python
def validate_before_saving(categories: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate categories before saving, return (is_valid, errors)"""
    errors = []
    
    # Check for required structure
    if not isinstance(categories, dict):
        errors.append("Categories must be a dictionary")
        return False, errors
    
    # Check each category
    for category, data in categories.items():
        # Validate category name
        if category not in VALID_CATEGORIES:
            errors.append(f"Invalid category: {category}")
        
        # Validate content exists
        if isinstance(data, dict):
            content = data.get('content', '')
            if not content or len(content.strip()) < 10:
                errors.append(f"Category {category} has insufficient content")
        
        # Validate confidence
        if isinstance(data, dict):
            confidence = data.get('confidence', 0.0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                errors.append(f"Category {category} has invalid confidence: {confidence}")
    
    return len(errors) == 0, errors
```

#### Frontend Integration: Complete Flow

**Step 1: Note Input & Analysis** (`static/js/main.js`)
```javascript
// Complete note processing flow
async function processNote(contactId, noteText) {
    try {
        // 1. Show loading state
        showLoadingState('Analyzing note...');
        
        // 2. Submit for analysis (async)
        const response = await fetch('/api/notes/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                contact_id: contactId,
                note_text: noteText
            })
        });
        
        const data = await response.json();
        
        if (response.status === 202 && data.task_id) {
            // 3. Async processing - poll for status
            pollTaskStatus(data.task_id);
        } else if (response.ok && data.synthesis) {
            // 4. Synchronous processing - show results immediately
            displaySynthesisResults(data.synthesis);
        } else {
            showError(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

// Poll task status
async function pollTaskStatus(taskId) {
    const maxAttempts = 60; // 5 minutes max (5s intervals)
    let attempts = 0;
    
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/notes/task/${taskId}/status`, {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (data.state === 'SUCCESS') {
                clearInterval(pollInterval);
                displaySynthesisResults(data.result.synthesis);
                hideLoadingState();
            } else if (data.state === 'FAILURE') {
                clearInterval(pollInterval);
                showError(data.error || 'Analysis failed');
                hideLoadingState();
            } else if (data.state === 'PROGRESS') {
                updateProgress(data.progress || 0, data.status || 'Processing...');
            }
            
            attempts++;
            if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
                showError('Analysis timed out');
                hideLoadingState();
            }
            
        } catch (error) {
            clearInterval(pollInterval);
            showError('Error checking status: ' + error.message);
            hideLoadingState();
        }
    }, 5000); // Poll every 5 seconds
}

// Display and allow editing
function displaySynthesisResults(synthesis) {
    // 1. Show categories in editable form
    const container = document.getElementById('synthesis-results');
    container.innerHTML = '';
    
    for (const [category, data] of Object.entries(synthesis)) {
        const categoryDiv = createCategoryEditor(category, data);
        container.appendChild(categoryDiv);
    }
    
    // 2. Show save button
    showSaveButton();
}

// Save approved synthesis
async function saveSynthesis(contactId, rawNote, synthesis) {
    try {
        const response = await fetch('/api/notes/save-synthesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                contact_id: contactId,
                raw_note: rawNote,
                synthesis: synthesis  // User-edited synthesis
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showSuccess('Note saved successfully!');
            // Refresh contact view
            loadContactDetails(contactId);
        } else {
            showError(data.error || 'Failed to save');
        }
        
    } catch (error) {
        showError('Error saving: ' + error.message);
    }
}
```

**Key Frontend Points:**
- ✅ **Polling for async tasks** - Check status every 5 seconds
- ✅ **Timeout handling** - Max 5 minutes waiting
- ✅ **Progress updates** - Show progress bar for long operations
- ✅ **Editable results** - User can edit before saving
- ✅ **Error handling** - Network errors, timeouts, API errors

#### Testing Strategy for Note Processing

**Unit Tests:**
```python
def test_ai_service_initialization():
    """Test AI service initializes correctly"""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        service = AIService()
        assert service._available == True
        assert service.gemini_api_key == 'test_key'

def test_analyze_note_with_mocked_gemini():
    """Test note analysis with mocked Gemini"""
    with patch('app.services.ai_service.genai') as mock_genai:
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"categories": {"Actionable": {"content": "test", "confidence": 0.9}}}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        service = AIService()
        result = service.analyze_note("test note", "John Doe")
        
        assert 'categories' in result
        assert 'Actionable' in result['categories']

def test_response_parsing_with_markdown():
    """Test parsing JSON wrapped in markdown"""
    response_text = '```json\n{"categories": {"test": {"content": "data"}}}\n```'
    result = parse_ai_response(response_text)
    assert result['categories']['test']['content'] == 'data'

def test_category_normalization():
    """Test category name normalization"""
    assert normalize_category_name('actionable') == 'Actionable'
    assert normalize_category_name('relationship strategy') == 'Relationship_Strategy'
    assert normalize_category_name('invalid') == 'invalid'  # No mapping, use as-is
```

**Integration Tests:**
```python
def test_complete_note_processing_flow(client, authenticated_user, db_session):
    """Test complete flow: save → analyze → save synthesis"""
    # 1. Create contact
    contact = Contact(full_name='Test Contact', user_id=authenticated_user.id)
    db_session.add(contact)
    db_session.commit()
    
    # 2. Process note
    response = client.post('/api/notes/analyze', json={
        'contact_id': contact.id,
        'note_text': 'John likes pizza and works at Google'
    })
    
    assert response.status_code == 202
    task_id = response.json['task_id']
    
    # 3. Poll for completion
    import time
    for _ in range(10):
        status_response = client.get(f'/api/notes/task/{task_id}/status')
        data = status_response.json
        if data['state'] == 'SUCCESS':
            assert 'result' in data
            assert 'synthesis' in data['result']
            break
        time.sleep(1)
    
    # 4. Verify database
    raw_notes = db_session.query(RawNote).filter(
        RawNote.contact_id == contact.id
    ).all()
    assert len(raw_notes) == 1
    
    synthesized = db_session.query(SynthesizedEntry).filter(
        SynthesizedEntry.contact_id == contact.id
    ).all()
    assert len(synthesized) > 0
```

**Complete Category Reference:**

The system uses 15 predefined categories for note analysis. Here's the complete list with definitions:

1. **Actionable**
   - Immediate tasks, follow-ups, reminders, requests, or discussion topics requiring attention within days or weeks
   - Example: "Call John next week about the project"

2. **Goals**
   - Clearly defined aspirations and objectives across all life domains
   - Short-term (3-12 months), medium-term (1-5 years), long-term (5+ years)
   - Example: "Wants to start a business in 2 years"

3. **Relationship_Strategy**
   - Structured approaches to nurturing, deepening, or improving your relationship
   - Specific tactics for connection and support
   - Example: "Prefers weekly check-ins to stay connected"

4. **Social**
   - Comprehensive mapping of social ecosystem
   - Family dynamics, friendship networks, romantic relationships, professional connections, community involvement
   - Example: "Has two siblings, close with college friends"

5. **Professional_Background**
   - Detailed career history and occupational profile
   - Employment timeline, educational credentials, skill inventory, achievement record
   - Example: "Software engineer at Google, 5 years experience, CS degree from MIT"

6. **Financial_Situation**
   - Comprehensive portrait of economic circumstances
   - Money management approach, financial outlook
   - Example: "Saving for house down payment, conservative investor"

7. **Wellbeing**
   - Holistic health status
   - Physical, mental, emotional, and spiritual dimensions
   - Example: "Runs marathons, practices meditation daily"

8. **Avocation**
   - Comprehensive inventory of non-professional interests, passions, and recreational activities
   - Example: "Passionate photographer, collects vintage cameras"

9. **Environment_And_Lifestyle**
   - Detailed portrait of daily living context and routine patterns
   - Example: "Lives in downtown apartment, works from home 3 days/week"

10. **Psychology_And_Values**
    - In-depth profile of mental frameworks, belief systems, and guiding principles
    - Example: "Values honesty above all, very analytical thinker"

11. **Communication_Style**
    - Comprehensive analysis of interpersonal communication patterns and preferences across all contexts
    - Example: "Prefers text over calls, responds quickly to emails"

12. **Challenges_And_Development**
    - Nuanced exploration of struggles, growth areas, and evolution across personal and professional domains
    - Example: "Working on public speaking anxiety, taking improv classes"

13. **Deeper_Insights**
    - Profound observations about core essence, philosophical outlook, and unique qualities that transcend conventional categorization
    - Example: "Has an incredible ability to see patterns others miss"

14. **Admin_matters**
    - Administrative details including important dates, birthdays, anniversaries, and other key information to track
    - Example: "Birthday: March 15, Anniversary: June 20"

15. **Others**
    - Any other important information that doesn't fit into the categories above
    - Catch-all for miscellaneous but important information

**Category Storage in Database:**
- Categories are stored as JSON in `SynthesizedEntry.categories` field
- Each category entry includes:
  - `content`: The extracted information (string)
  - `confidence`: AI confidence score (float, 0.0-1.0)
- Only categories with relevant content are included (empty categories filtered out)
- Minimum content length: 10 characters (filtered in `NoteService.process_note()`)

#### Data Flow Diagram

```
Frontend: POST /api/notes/analyze
    ↓
API Endpoint: Validate input, verify contact ownership
    ↓
Try Celery Task (async)
    ├─ Success → Return 202 + task_id
    └─ Failure → Fallback to sync
        ↓
Celery Worker: process_note_async
    ↓
NoteService.process_note()
    ├─ Save RawNote to database
    ├─ Call AIService.analyze_note()
    │   ├─ Try Gemini API
    │   ├─ Fallback to OpenAI
    │   └─ Fallback to local analysis
    └─ Save SynthesizedEntry records
        ↓
Update Task State: SUCCESS + result
    ↓
Frontend: Poll GET /api/notes/task/<task_id>/status
    ↓
Return synthesis data to user
```

#### Integration Points

1. **Authentication**: `@login_required` ensures user is logged in
2. **Database**: `DatabaseManager` for session management
3. **AI Services**: `AIService` abstracts Gemini/OpenAI
4. **Celery**: `celery_app` for async task queue
5. **Logging**: `@log_performance` decorator for metrics
6. **Error Handling**: Multiple fallback layers

#### Implementation Flow: RAG Pipeline Integration

**Complete RAG Implementation** (Retrieval-Augmented Generation)

**Step 1: Store Notes in ChromaDB** (when note is saved)
```python
def store_note_for_rag(contact_id: int, note_content: str, note_id: int):
    """
    Store note in ChromaDB vector database for future semantic retrieval.
    This enables the RAG pipeline to retrieve relevant historical context.
    """
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        # 1. Get or create collection for this contact
        # Collection name: "contact_{contact_id}"
        collection = get_contact_collection(contact_id, prefix="contact_")
        
        # 2. Add note as document with metadata
        collection.add(
            documents=[note_content],  # The note text (will be embedded)
            ids=[f"note_{note_id}"],  # Unique ID: note_{raw_note_id}
            metadatas=[{
                "contact_id": contact_id,
                "note_id": note_id,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "manual"  # or "telegram", "voice", "file"
            }]
        )
        
        logger.debug(f"✅ Stored note {note_id} in ChromaDB for contact {contact_id}")
        
    except Exception as e:
        # CRITICAL: Don't fail note processing if ChromaDB fails
        # ChromaDB is enhancement, not requirement
        logger.warning(f"⚠️ Failed to store note in ChromaDB (non-critical): {e}")
        # Continue processing - note is still saved to database
```

**Key Decision Points:**
- ✅ **Per-contact collections** - Each contact has isolated vector space
- ✅ **Store after saving** - Only store successfully saved notes
- ✅ **Non-blocking** - ChromaDB failures don't stop note processing
- ✅ **Include metadata** - Contact ID, note ID, timestamp for filtering
- ✅ **Automatic embedding** - ChromaDB handles text embedding automatically

**Step 2: Retrieve Relevant History** (before AI analysis)
```python
def get_relevant_history_for_analysis(contact_id: int, new_note: str, n_results: int = 3) -> str:
    """
    Retrieve relevant historical notes from ChromaDB using semantic search.
    This provides context to the AI for better, more consistent analysis.
    """
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        # 1. Get contact's ChromaDB collection
        collection = get_contact_collection(contact_id, prefix="contact_")
        
        # 2. Create query from first 30 words of new note
        # Using first 30 words focuses on key concepts, not entire note
        query_words = new_note.split()[:30]
        query_text = " ".join(query_words)
        
        # 3. Query ChromaDB for semantically similar notes
        results = collection.query(
            query_texts=[query_text],  # Search query
            n_results=n_results,  # Get top N most relevant
            include=["documents", "metadatas", "distances"]  # Return full data
        )
        
        # 4. Format retrieved history for AI prompt
        if results['documents'] and len(results['documents'][0]) > 0:
            retrieved_docs = results['documents'][0]
            distances = results['distances'][0] if 'distances' in results else []
            
            # Combine documents with separators
            formatted_history = []
            for i, doc in enumerate(retrieved_docs):
                distance = distances[i] if i < len(distances) else None
                # Lower distance = more similar (ChromaDB uses cosine distance)
                similarity_score = 1.0 - distance if distance else None
                
                formatted_history.append(f"[Similarity: {similarity_score:.2f}]\n{doc}")
            
            retrieved_history = "\n---\n".join(formatted_history)
            
            logger.debug(f"✅ Retrieved {len(retrieved_docs)} relevant notes for contact {contact_id}")
            return retrieved_history
        else:
            logger.debug(f"ℹ️ No relevant history found for contact {contact_id}")
            return "No relevant history found."
            
    except Exception as e:
        # Graceful fallback - proceed without context
        logger.warning(f"⚠️ RAG pipeline unavailable, proceeding without context: {e}")
        return "No relevant history found."
```

**Key Decision Points:**
- ✅ **Use first 30 words** - Focus on key concepts, reduce noise
- ✅ **Top 3 results** - Balance between context and prompt size
- ✅ **Include similarity scores** - Help AI understand relevance
- ✅ **Separate with `---`** - Clear delimiter between historical notes
- ✅ **Graceful fallback** - Continue without context if ChromaDB fails
- ✅ **Log retrieval** - Monitor RAG effectiveness

**Step 3: Enhanced Prompt with RAG Context**
```python
def build_rag_enhanced_prompt(content: str, contact_name: str, retrieved_history: str) -> str:
    """Build AI prompt with RAG context for better analysis"""
    
    prompt = f"""
    Analyze this note about {contact_name} and extract structured information.
    
    **CONTEXT - Retrieved Relevant History:**
    {retrieved_history}
    
    Use this historical context to:
    1. Maintain consistency with previous information about {contact_name}
    2. Identify when new information contradicts or updates old information
    3. Build upon existing knowledge rather than repeating it
    4. Extract NEW information that wasn't in the history
    
    **NEW NOTE TO ANALYZE:**
    {content}
    
    **CATEGORY DEFINITIONS:**
    [Full category definitions as shown in Gemini prompt...]
    
    **INSTRUCTIONS:**
    - Compare the new note with the retrieved history
    - If information contradicts history, note it as an update
    - If information is new, extract it
    - If information repeats history, you may skip it or note it as confirmation
    - Maintain consistency in categorization across time
    
    Return JSON with categories...
    """
    
    return prompt
```

**Key Decision Points:**
- ✅ **Explicit context section** - Clear separation of history vs new note
- ✅ **Consistency instructions** - Guide AI to maintain coherence
- ✅ **Update detection** - Help identify contradictions
- ✅ **Avoid repetition** - Don't re-extract known information

**Step 4: Integrate RAG into NoteService**
```python
@log_performance("note_processing")
def process_note(self, contact_id: int, content: str, user_id: int) -> Dict[str, Any]:
    """Complete note processing with RAG pipeline"""
    
    with self.db_manager.get_session() as session:
        # 1. Verify contact ownership
        contact = self._get_user_contact(session, contact_id, user_id)
        if not contact:
            raise ValueError("Contact not found")
        
        # 2. Save raw note to database
        raw_note = RawNote(
            contact_id=contact_id,
            content=content.strip(),
            source='manual',
            created_at=datetime.utcnow()
        )
        session.add(raw_note)
        session.flush()  # Get ID
        
        # 3. Store in ChromaDB for future RAG (non-blocking)
        try:
            store_note_for_rag(contact_id, content, raw_note.id)
        except Exception as e:
            logger.warning(f"ChromaDB storage failed (non-critical): {e}")
        
        # 4. Retrieve relevant history for RAG context
        retrieved_history = get_relevant_history_for_analysis(contact_id, content, n_results=3)
        
        # 5. Analyze with AI (pass RAG context)
        try:
            analysis_result = self.ai_service.analyze_note(
                content=content,
                contact_name=contact.full_name,
                context=retrieved_history  # RAG context
            )
            
            # 6. Save synthesized entries
            synthesis_results = []
            for category, data in analysis_result['categories'].items():
                if data.get('content') and len(data['content'].strip()) > 10:
                    entry = SynthesizedEntry(
                        contact_id=contact_id,
                        raw_note_id=raw_note.id,
                        category=category,
                        content=data['content'].strip(),
                        confidence_score=data.get('confidence', 0.0),
                        created_at=datetime.utcnow()
                    )
                    session.add(entry)
                    synthesis_results.append({
                        'category': category,
                        'content': data['content'],
                        'confidence': data['confidence']
                    })
            
            session.commit()
            return {
                'success': True,
                'raw_note_id': raw_note.id,
                'synthesis': synthesis_results,
                'contact_name': contact.full_name
            }
            
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {ai_error}")
            # Still save raw note
            session.commit()
            return {
                'success': True,
                'raw_note_id': raw_note.id,
                'synthesis': [],
                'ai_error': str(ai_error)
            }
```

#### Implementation Flow: Response Normalization & Quality Control

**Step 1: Comprehensive Response Parser**
```python
def parse_and_normalize_ai_response(response_text: str, contact_name: str) -> Dict[str, Any]:
    """
    Parse AI response with comprehensive error handling and normalization.
    Handles markdown, JSON, partial JSON, and malformed responses.
    """
    import json
    import re
    
    # 1. Strip whitespace
    response_text = response_text.strip()
    
    # 2. Remove markdown code blocks (models often wrap JSON)
    markdown_patterns = [
        (r'^```json\s*', ''),  # Remove ```json at start
        (r'^```\s*', ''),      # Remove ``` at start
        (r'```\s*$', ''),      # Remove ``` at end
        (r'^```', ''),         # Catch any remaining ```
    ]
    
    for pattern, replacement in markdown_patterns:
        response_text = re.sub(pattern, replacement, response_text, flags=re.MULTILINE)
    
    response_text = response_text.strip()
    
    # 3. Try direct JSON parse
    try:
        result = json.loads(response_text)
        return normalize_categories(result, contact_name)
    except json.JSONDecodeError:
        pass
    
    # 4. Try to extract JSON from text (sometimes wrapped in explanation)
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    json_matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for json_str in json_matches:
        try:
            result = json.loads(json_str)
            return normalize_categories(result, contact_name)
        except json.JSONDecodeError:
            continue
    
    # 5. Try to fix common JSON errors
    try:
        # Fix trailing commas
        fixed = re.sub(r',\s*}', '}', response_text)
        fixed = re.sub(r',\s*]', ']', fixed)
        result = json.loads(fixed)
        return normalize_categories(result, contact_name)
    except json.JSONDecodeError:
        pass
    
    # 6. Final fallback: wrap entire response
    logger.warning(f"Failed to parse AI response, using fallback for {contact_name}")
    return {
        "categories": {
            "Others": {
                "content": response_text[:500],  # Limit length
                "confidence": 0.3
            }
        }
    }
```

**Step 2: Category Normalization**
```python
def normalize_categories(result: Dict[str, Any], contact_name: str) -> Dict[str, Any]:
    """Normalize category names and structure"""
    
    # Valid category names (exact match required)
    VALID_CATEGORIES = {
        'Actionable', 'Goals', 'Relationship_Strategy', 'Social',
        'Professional_Background', 'Financial_Situation', 'Wellbeing',
        'Avocation', 'Environment_And_Lifestyle', 'Psychology_And_Values',
        'Communication_Style', 'Challenges_And_Development', 'Deeper_Insights',
        'Admin_matters', 'Others'
    }
    
    # Category name mapping (handle variations)
    CATEGORY_MAP = {
        'actionable': 'Actionable',
        'goals': 'Goals',
        'relationship_strategy': 'Relationship_Strategy',
        'relationship strategy': 'Relationship_Strategy',
        'relationship-strategy': 'Relationship_Strategy',
        'social': 'Social',
        'professional_background': 'Professional_Background',
        'professional background': 'Professional_Background',
        'professional-background': 'Professional_Background',
        'financial_situation': 'Financial_Situation',
        'financial situation': 'Financial_Situation',
        'financial-situation': 'Financial_Situation',
        'wellbeing': 'Wellbeing',
        'well-being': 'Wellbeing',
        'avocation': 'Avocation',
        'environment_and_lifestyle': 'Environment_And_Lifestyle',
        'environment and lifestyle': 'Environment_And_Lifestyle',
        'psychology_and_values': 'Psychology_And_Values',
        'psychology and values': 'Psychology_And_Values',
        'communication_style': 'Communication_Style',
        'communication style': 'Communication_Style',
        'challenges_and_development': 'Challenges_And_Development',
        'challenges and development': 'Challenges_And_Development',
        'deeper_insights': 'Deeper_Insights',
        'deeper insights': 'Deeper_Insights',
        'admin_matters': 'Admin_matters',
        'admin matters': 'Admin_matters',
        'admin-matters': 'Admin_matters',
        'others': 'Others',
        'other': 'Others'
    }
    
    normalized = {}
    categories = result.get('categories', {})
    
    for category, data in categories.items():
        # 1. Normalize category name
        category_lower = category.lower().strip()
        normalized_category = CATEGORY_MAP.get(category_lower, category)
        
        # 2. Validate category
        if normalized_category not in VALID_CATEGORIES:
            logger.warning(f"Invalid category '{category}' for {contact_name}, mapping to 'Others'")
            normalized_category = 'Others'
        
        # 3. Extract and normalize data
        if isinstance(data, dict):
            content = data.get('content', '')
            confidence = normalize_confidence_score(data.get('confidence', 0.0))
        elif isinstance(data, str):
            content = data
            confidence = 0.5
        else:
            continue  # Skip invalid format
        
        # 4. Filter empty content
        if not content or len(content.strip()) < 10:
            continue
        
        # 5. Merge if category already exists
        if normalized_category in normalized:
            existing = normalized[normalized_category]
            existing['content'] = f"{existing['content']}\n{content.strip()}"
            existing['confidence'] = max(existing['confidence'], confidence)
        else:
            normalized[normalized_category] = {
                'content': content.strip(),
                'confidence': confidence
            }
    
    return {'categories': normalized}
```

**Step 3: Confidence Score Normalization**
```python
def normalize_confidence_score(confidence: Any) -> float:
    """
    Normalize confidence score to 0.0-1.0 range.
    Handles strings, percentages, and out-of-range values.
    """
    try:
        # Handle string confidence
        if isinstance(confidence, str):
            confidence_str = confidence.strip()
            
            # Handle percentage format (e.g., "85%")
            if '%' in confidence_str:
                value = float(confidence_str.replace('%', ''))
                return max(0.0, min(1.0, value / 100.0))
            
            # Handle decimal string (e.g., "0.85")
            if '.' in confidence_str:
                return max(0.0, min(1.0, float(confidence_str)))
            
            # Handle integer string (e.g., "85" = 0.85)
            value = float(confidence_str)
            if value > 1.0:
                return max(0.0, min(1.0, value / 100.0))
            return max(0.0, min(1.0, value))
        
        # Handle numeric confidence
        confidence_float = float(confidence)
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, confidence_float))
        
    except (ValueError, TypeError, AttributeError):
        # Default to 0.5 if can't parse
        logger.warning(f"Invalid confidence value: {confidence}, defaulting to 0.5")
        return 0.5
```

#### Implementation Flow: Complete NoteService with RAG

**Full NoteService Implementation** (`app/services/note_service.py`)
```python
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.models.note import RawNote, SynthesizedEntry
from app.models.contact import Contact
from app.services.ai_service import AIService
from app.utils.database import DatabaseManager
from app.utils.structured_logging import log_performance
import logging

logger = logging.getLogger(__name__)

class NoteService:
    """Service for processing notes with AI analysis and RAG pipeline"""
    
    def __init__(self, db_manager: DatabaseManager, ai_service: AIService):
        self.db_manager = db_manager
        self.ai_service = ai_service
    
    @log_performance("note_processing")
    def process_note(self, contact_id: int, content: str, user_id: int) -> Dict[str, Any]:
        """
        Complete note processing pipeline:
        1. Verify contact ownership
        2. Save raw note to database
        3. Store in ChromaDB for future RAG
        4. Retrieve relevant history (RAG)
        5. Analyze with AI (with context)
        6. Parse and normalize response
        7. Save synthesized entries
        8. Return results
        """
        with self.db_manager.get_session() as session:
            # STEP 1: Verify contact ownership
            contact = self._get_user_contact(session, contact_id, user_id)
            if not contact:
                raise ValueError("Contact not found")
            
            # STEP 2: Save raw note to database
            raw_note = RawNote(
                contact_id=contact_id,
                content=content.strip(),
                source='manual',
                created_at=datetime.utcnow(),
                metadata_tags={
                    "type": "manual_note",
                    "source": "ui_note_input",
                    "user_id": user_id,
                    "processed_at": datetime.utcnow().isoformat()
                }
            )
            session.add(raw_note)
            session.flush()  # Get ID without committing
            
            # STEP 3: Store in ChromaDB (non-blocking, non-critical)
            try:
                from app.utils.chromadb_client import get_contact_collection
                collection = get_contact_collection(contact_id)
                collection.add(
                    documents=[content],
                    ids=[f"note_{raw_note.id}"],
                    metadatas=[{
                        "contact_id": contact_id,
                        "note_id": raw_note.id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "manual"
                    }]
                )
                logger.debug(f"Stored note {raw_note.id} in ChromaDB")
            except Exception as e:
                logger.warning(f"ChromaDB storage failed (non-critical): {e}")
            
            # STEP 4: Retrieve relevant history for RAG context
            retrieved_history = "No relevant history found."
            try:
                from app.utils.chromadb_client import get_contact_collection
                collection = get_contact_collection(contact_id)
                
                # Use first 30 words for semantic search
                query_words = content.split()[:30]
                query_text = " ".join(query_words)
                
                results = collection.query(
                    query_texts=[query_text],
                    n_results=3  # Top 3 most relevant
                )
                
                if results['documents'] and len(results['documents'][0]) > 0:
                    retrieved_docs = results['documents'][0]
                    retrieved_history = "\n---\n".join(retrieved_docs)
                    logger.debug(f"Retrieved {len(retrieved_docs)} relevant notes for RAG")
            except Exception as e:
                logger.debug(f"RAG retrieval failed (non-critical): {e}")
            
            # STEP 5: Analyze with AI (with RAG context)
            try:
                analysis_result = self.ai_service.analyze_note(
                    content=content,
                    contact_name=contact.full_name,
                    context=retrieved_history  # Pass RAG context
                )
                
                # STEP 6: Parse and normalize response
                normalized_result = self._normalize_analysis_result(analysis_result, contact.full_name)
                
                # STEP 7: Save synthesized entries
                synthesis_results = []
                for category, data in normalized_result['categories'].items():
                    content_text = data.get('content', '')
                    confidence = data.get('confidence', 0.0)
                    
                    # Filter: only save meaningful content
                    if content_text and len(content_text.strip()) > 10:
                        entry = SynthesizedEntry(
                            contact_id=contact_id,
                            raw_note_id=raw_note.id,
                            category=category,
                            content=content_text.strip(),
                            confidence_score=confidence,
                            created_at=datetime.utcnow()
                        )
                        session.add(entry)
                        synthesis_results.append({
                            'category': category,
                            'content': content_text,
                            'confidence': confidence
                        })
                
                # STEP 8: Commit all changes
                session.commit()
                
                logger.info(f"Processed note {raw_note.id} for contact {contact_id}: {len(synthesis_results)} categories")
                
                return {
                    'success': True,
                    'raw_note_id': raw_note.id,
                    'synthesis': synthesis_results,
                    'contact_name': contact.full_name,
                    'categories_count': len(synthesis_results),
                    'rag_used': retrieved_history != "No relevant history found."
                }
                
            except Exception as ai_error:
                logger.error(f"AI analysis failed for note {raw_note.id}: {ai_error}")
                # Still save the raw note even if AI fails
                session.commit()
                return {
                    'success': True,
                    'raw_note_id': raw_note.id,
                    'synthesis': [],
                    'ai_error': str(ai_error),
                    'contact_name': contact.full_name
                }
    
    def _normalize_analysis_result(self, result: Dict[str, Any], contact_name: str) -> Dict[str, Any]:
        """Normalize AI analysis result: category names, confidence scores, content"""
        # Implementation as shown in normalize_categories above
        # ... (full implementation)
        pass
    
    def _get_user_contact(self, session, contact_id: int, user_id: int) -> Optional[Contact]:
        """Get a contact that belongs to the user"""
        return session.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == user_id
        ).first()
```

#### Implementation Flow: Quality Assurance & Validation

**Step 1: Content Quality Validation**
```python
def validate_extracted_content(content: str, confidence: float, category: str) -> Tuple[bool, str]:
    """
    Validate extracted content meets quality standards.
    Returns (is_valid, reason_if_invalid)
    """
    # 1. Minimum length check
    if not content or len(content.strip()) < 10:
        return False, "Content too short (minimum 10 characters)"
    
    # 2. Maximum length check (prevent extremely long extractions)
    if len(content) > 5000:
        return False, "Content too long (maximum 5000 characters)"
    
    # 3. Check for placeholder text
    placeholder_patterns = [
        'example', 'placeholder', 'test', 'lorem ipsum',
        'n/a', 'not applicable', 'none', 'no information',
        'sample', 'demo', 'placeholder text'
    ]
    content_lower = content.lower()
    if any(pattern in content_lower for pattern in placeholder_patterns):
        return False, f"Detected placeholder text: {content[:50]}"
    
    # 4. Check for meaningful content (not just punctuation/special chars)
    meaningful_chars = sum(1 for c in content if c.isalnum())
    total_chars = len(content)
    if total_chars > 0:
        meaningful_ratio = meaningful_chars / total_chars
        if meaningful_ratio < 0.3:  # Less than 30% alphanumeric
            return False, "Content contains too many special characters"
    
    # 5. Check for minimum word count
    word_count = len(content.split())
    if word_count < 2:
        return False, "Content has insufficient words (minimum 2)"
    
    # 6. Confidence threshold (optional - currently not enforced)
    # if confidence < 0.3:
    #     return False, f"Confidence too low: {confidence}"
    
    return True, ""
```

**Step 2: Category-Specific Validation**
```python
def validate_category_content(category: str, content: str) -> bool:
    """Category-specific validation rules"""
    
    # Actionable items should contain action verbs
    if category == 'Actionable':
        action_verbs = ['call', 'email', 'meet', 'send', 'follow', 'remind', 'schedule', 'check']
        content_lower = content.lower()
        if not any(verb in content_lower for verb in action_verbs):
            logger.debug(f"Actionable category may lack action verb: {content[:50]}")
            # Don't reject, just log
    
    # Goals should indicate timeframes or aspirations
    if category == 'Goals':
        goal_indicators = ['want', 'goal', 'plan', 'aspire', 'hope', 'aim', 'target', 'objective']
        content_lower = content.lower()
        if not any(indicator in content_lower for indicator in goal_indicators):
            logger.debug(f"Goals category may lack goal indicators: {content[:50]}")
    
    # Admin_matters should contain dates or administrative info
    if category == 'Admin_matters':
        admin_indicators = ['birthday', 'anniversary', 'date', 'address', 'phone', 'email']
        content_lower = content.lower()
        if not any(indicator in content_lower for indicator in admin_indicators):
            logger.debug(f"Admin_matters may lack administrative info: {content[:50]}")
    
    return True  # Always pass (validation is advisory, not blocking)
```

**Step 3: Deduplication Logic**
```python
def deduplicate_category_content(categories: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove duplicate or very similar content within and across categories.
    Uses exact matching and similarity detection.
    """
    from difflib import SequenceMatcher
    
    seen_content = {}  # normalized_content -> (category, original_content)
    deduplicated = {}
    SIMILARITY_THRESHOLD = 0.85  # 85% similarity = duplicate
    
    for category, data in categories.items():
        content = data.get('content', '') if isinstance(data, dict) else str(data)
        
        # Normalize for comparison
        normalized = content.lower().strip()
        
        # Check for exact duplicates
        if normalized in seen_content:
            existing_category, existing_content = seen_content[normalized]
            logger.debug(f"Skipping exact duplicate: {category} matches {existing_category}")
            continue
        
        # Check for similar content (fuzzy matching)
        is_duplicate = False
        for seen_normalized, (seen_cat, seen_orig) in seen_content.items():
            similarity = SequenceMatcher(None, normalized, seen_normalized).ratio()
            if similarity >= SIMILARITY_THRESHOLD:
                logger.debug(f"Skipping similar content: {category} ({similarity:.2f} similar to {seen_cat})")
                is_duplicate = True
                break
        
        if is_duplicate:
            continue
        
        # Add to seen and deduplicated
        seen_content[normalized] = (category, content)
        deduplicated[category] = data
    
    return deduplicated
```

#### Implementation Flow: Advanced Error Recovery

**Step 1: Retry Logic with Exponential Backoff**
```python
def analyze_note_with_retry(self, content: str, contact_name: str, max_retries: int = 3) -> Dict[str, Any]:
    """Analyze note with comprehensive retry logic"""
    
    retry_delays = [2, 4, 8]  # Exponential backoff: 2s, 4s, 8s
    
    for attempt in range(max_retries):
        try:
            # Try Gemini first
            if self.gemini_api_key:
                return self._analyze_with_gemini(content, contact_name)
        except google.api_core.exceptions.ResourceExhausted as e:
            # Rate limit - wait and retry
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                logger.warning(f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            else:
                # Try OpenAI fallback
                if self.openai_api_key:
                    logger.info("Gemini rate limit exceeded, trying OpenAI")
                    return self._analyze_with_openai(content, contact_name)
                raise
        
        except google.api_core.exceptions.ServiceUnavailable as e:
            # Service temporarily unavailable
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                logger.warning(f"Service unavailable, retrying in {delay}s")
                time.sleep(delay)
                continue
            else:
                # Try OpenAI fallback
                if self.openai_api_key:
                    return self._analyze_with_openai(content, contact_name)
                raise
        
        except Exception as e:
            # Other errors - try fallback immediately
            logger.warning(f"Gemini error: {e}, trying fallback")
            if self.openai_api_key:
                try:
                    return self._analyze_with_openai(content, contact_name)
                except Exception as openai_error:
                    logger.error(f"OpenAI also failed: {openai_error}")
                    return self._fallback_analysis(content, contact_name)
            else:
                return self._fallback_analysis(content, contact_name)
    
    # All retries exhausted
    return self._fallback_analysis(content, contact_name)
```

**Step 2: Circuit Breaker Pattern** (for production)
```python
class AIServiceCircuitBreaker:
    """Circuit breaker to prevent cascading failures"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'  # Try again
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            # Success - reset failure count
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
            
            raise
```

#### Implementation Flow: Performance Optimization

**Step 1: Response Caching** (for identical notes)
```python
from functools import lru_cache
import hashlib
import json

def get_content_hash(content: str, contact_name: str) -> str:
    """Generate deterministic hash for caching"""
    normalized = content.lower().strip()
    combined = f"{contact_name}:{normalized}"
    return hashlib.sha256(combined.encode()).hexdigest()

# Cache with size limit (100 most recent)
@lru_cache(maxsize=100)
def cached_analyze_note(content_hash: str) -> Optional[Dict[str, Any]]:
    """Cached analysis - returns None if not in cache"""
    # Note: This requires storing content_hash -> result mapping
    # Implementation would use Redis or similar
    return None

def analyze_note_with_cache(self, content: str, contact_name: str) -> Dict[str, Any]:
    """Analyze with caching for identical notes"""
    content_hash = get_content_hash(content, contact_name)
    
    # Check cache
    cached_result = cached_analyze_note(content_hash)
    if cached_result:
        logger.debug(f"Cache hit for note analysis")
        return cached_result
    
    # Cache miss - analyze
    result = self._analyze_with_gemini(content, contact_name)
    
    # Store in cache (would need Redis implementation)
    # cache.set(content_hash, result, ttl=3600)  # 1 hour TTL
    
    return result
```

**Step 2: Batch ChromaDB Operations**
```python
def batch_store_notes_in_chromadb(contact_id: int, notes: List[Dict[str, Any]]):
    """Store multiple notes in ChromaDB efficiently (single operation)"""
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        collection = get_contact_collection(contact_id)
        
        # Prepare batch data
        documents = [note['content'] for note in notes]
        ids = [f"note_{note['id']}" for note in notes]
        metadatas = [{
            "contact_id": contact_id,
            "note_id": note['id'],
            "timestamp": note.get('timestamp', datetime.utcnow().isoformat()),
            "source": note.get('source', 'manual')
        } for note in notes]
        
        # Single batch operation (more efficient)
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Batch stored {len(notes)} notes in ChromaDB for contact {contact_id}")
        
    except Exception as e:
        logger.warning(f"Batch ChromaDB storage failed: {e}")
```

**Step 3: Async ChromaDB Operations** (non-blocking)
```python
@celery_app.task
def store_note_in_chromadb_async(contact_id: int, note_content: str, note_id: int):
    """Store note in ChromaDB asynchronously (don't block note processing)"""
    try:
        from app.utils.chromadb_client import get_contact_collection
        
        collection = get_contact_collection(contact_id)
        collection.add(
            documents=[note_content],
            ids=[f"note_{note_id}"],
            metadatas=[{
                "contact_id": contact_id,
                "note_id": note_id,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
        logger.debug(f"Async stored note {note_id} in ChromaDB")
    except Exception as e:
        logger.warning(f"Async ChromaDB storage failed: {e}")
        # Don't raise - this is non-critical
```

#### Implementation Flow: Production Considerations

**Step 1: Rate Limiting & Quota Management**
```python
class AIRateLimiter:
    """Manage API rate limits and quotas"""
    
    def __init__(self):
        self.gemini_requests_today = 0
        self.openai_requests_today = 0
        self.gemini_daily_limit = 1000  # Adjust based on your quota
        self.openai_daily_limit = 1000
    
    def check_quota(self, service: str) -> bool:
        """Check if service has remaining quota"""
        if service == 'gemini':
            return self.gemini_requests_today < self.gemini_daily_limit
        elif service == 'openai':
            return self.openai_requests_today < self.openai_daily_limit
        return True
    
    def record_request(self, service: str):
        """Record API request"""
        if service == 'gemini':
            self.gemini_requests_today += 1
        elif service == 'openai':
            self.openai_requests_today += 1
```

**Step 2: Cost Optimization**
```python
def select_model_by_complexity(content: str) -> str:
    """Select AI model based on note complexity (cost optimization)"""
    
    word_count = len(content.split())
    char_count = len(content)
    
    # Simple notes: use cheaper/faster model
    if word_count < 50 and char_count < 500:
        return 'gemini-2.0-flash-exp'  # Faster, cheaper
    
    # Medium notes: use balanced model
    elif word_count < 200:
        return 'gemini-2.5-pro'  # Balanced
    
    # Complex notes: use best model
    else:
        return 'gemini-2.5-pro'  # Best quality
```

**Step 3: Monitoring & Alerting**
```python
def log_ai_processing_metrics(operation: str, duration: float, success: bool, 
                               model: str, tokens_used: int = 0):
    """Log AI processing metrics for monitoring"""
    from app.utils.structured_logging import StructuredLogger
    
    logger = StructuredLogger()
    logger.log_ai_processing(
        service=model,
        operation=operation,
        duration=duration,
        tokens_used=tokens_used,
        success=success
    )
    
    # Alert if processing time is too long
    if duration > 30.0:  # 30 seconds
        logger.warning(f"Slow AI processing: {duration}s for {operation}")
    
    # Alert if failure rate is high
    # (would track in monitoring system)
```

#### Common Patterns

**Pattern 1: Async with Sync Fallback**
```python
try:
    task = async_task.delay(...)
    return jsonify({'task_id': task.id}), 202
except Exception:
    result = sync_operation(...)
    return jsonify({'result': result}), 200
```

**Pattern 2: Service Fallback Chain**
```python
if primary_service_available:
    try:
        return primary_service.analyze(...)
    except:
        if fallback_service_available:
            return fallback_service.analyze(...)
return local_fallback(...)
```

**Pattern 3: Task State Updates**
```python
self.update_state(state='PROGRESS', meta={'status': '...'})
# ... do work ...
self.update_state(state='SUCCESS', meta={'result': ...})
```

**Pattern 4: RAG Pipeline (Retrieval-Augmented Generation)**
```python
# 1. Store note in ChromaDB
store_note_in_chromadb(contact_id, content, note_id)

# 2. Retrieve relevant history
history = get_relevant_history(contact_id, content, n_results=3)

# 3. Include in AI prompt
prompt = build_prompt_with_context(content, contact_name, history)

# 4. Analyze with context
result = ai_service.analyze(prompt)
```

**Pattern 5: Graceful Degradation**
```python
try:
    # Try enhanced feature
    result = enhanced_operation()
except Exception:
    # Fallback to basic feature
    logger.warning("Enhanced feature failed, using fallback")
    result = basic_operation()
# Always return something, never fail completely
```

#### Error Handling Strategy

**Comprehensive Error Handling:**
```python
def process_note_with_comprehensive_error_handling(contact_id, content, user_id):
    """Process note with error handling at every level"""
    
    errors = []
    warnings = []
    
    # 1. Input validation errors
    try:
        validate_note_input(content, contact_id)
    except ValidationError as e:
        return {'error': str(e), 'code': 'validation_error'}, 400
    
    # 2. Database errors
    try:
        raw_note = save_raw_note(contact_id, content)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return {'error': 'Database error', 'code': 'database_error'}, 500
    
    # 3. ChromaDB errors (non-critical)
    try:
        store_in_chromadb(contact_id, content, raw_note.id)
    except Exception as e:
        warnings.append(f"ChromaDB storage failed: {e}")
        # Continue - ChromaDB is optional
    
    # 4. RAG retrieval errors (non-critical)
    try:
        context = get_relevant_history(contact_id, content)
    except Exception as e:
        warnings.append(f"RAG retrieval failed: {e}")
        context = "No relevant history found."
    
    # 5. AI service errors (with fallbacks)
    try:
        result = ai_service.analyze_note(content, contact_name, context)
    except RateLimitError as e:
        return {'error': 'AI service rate limited', 'code': 'rate_limit'}, 429
    except APIError as e:
        # Try fallback
        try:
            result = fallback_ai_service.analyze(content, contact_name)
        except Exception:
            result = local_fallback(content, contact_name)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        result = local_fallback(content, contact_name)
    
    # 6. Response parsing errors
    try:
        normalized = normalize_analysis_result(result)
    except Exception as e:
        logger.error(f"Response normalization failed: {e}")
        return {'error': 'Analysis result invalid', 'code': 'parse_error'}, 500
    
    # 7. Save errors
    try:
        save_synthesis(contact_id, normalized, raw_note.id)
    except DatabaseError as e:
        logger.error(f"Failed to save synthesis: {e}")
        return {'error': 'Failed to save', 'code': 'save_error'}, 500
    
    return {
        'success': True,
        'result': normalized,
        'warnings': warnings
    }
```

**Error Codes Reference:**
- `validation_error`: Input validation failed
- `database_error`: Database operation failed
- `rate_limit`: AI service rate limited
- `api_error`: AI service API error
- `parse_error`: Failed to parse AI response
- `save_error`: Failed to save to database
- `unknown_error`: Unexpected error

#### Performance Considerations

**1. Use async for long operations** - Don't block HTTP request
**2. Cache AI responses** - Consider caching for similar notes (Redis)
**3. Batch processing** - Use `batch_process_notes` for multiple notes
**4. Rate limiting** - Implement retry with exponential backoff
**5. Model selection** - Use faster models for simple notes
**6. ChromaDB batching** - Store multiple notes in single operation
**7. Async ChromaDB** - Don't block note processing on ChromaDB storage
**8. Response caching** - Cache identical notes (hash-based)
**9. Connection pooling** - Reuse database connections
**10. Lazy loading** - Don't load all relationships at once

### Frontend Implementation

**Complete Frontend Note Processing Flow** (`static/js/main.js`)

**Step 1: Note Input & Contact Selection**
```javascript
// Initialize note processing UI
function initializeNoteProcessing() {
    const noteInput = document.getElementById('note-input');
    const contactSelect = document.getElementById('contact-select');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    // Enable analyze button when note and contact are selected
    function updateAnalyzeButton() {
        const hasNote = noteInput.value.trim().length > 0;
        const hasContact = contactSelect.value !== '';
        analyzeBtn.disabled = !(hasNote && hasContact);
    }
    
    noteInput.addEventListener('input', updateAnalyzeButton);
    contactSelect.addEventListener('change', updateAnalyzeButton);
    
    // Handle analyze button click
    analyzeBtn.addEventListener('click', async () => {
        const contactId = parseInt(contactSelect.value);
        const noteText = noteInput.value.trim();
        
        if (!contactId || !noteText) {
            showError('Please select a contact and enter a note');
            return;
        }
        
        await processNote(contactId, noteText);
    });
}
```

**Step 2: Complete Note Processing Function**
```javascript
async function processNote(contactId, noteText) {
    try {
        // 1. Show loading state
        showLoadingState('Analyzing note with AI...');
        disableAnalyzeButton();
        
        // 2. Submit for analysis (prefer async)
        const response = await fetch('/api/notes/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                contact_id: contactId,
                note_text: noteText
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        const data = await response.json();
        
        // 3. Handle async vs sync response
        if (response.status === 202 && data.task_id) {
            // Async processing - poll for status
            await pollTaskStatus(data.task_id, contactId, noteText);
        } else if (data.synthesis) {
            // Synchronous processing - show results immediately
            displaySynthesisResults(data.synthesis, contactId, noteText);
            hideLoadingState();
        } else {
            throw new Error('Unexpected response format');
        }
        
    } catch (error) {
        hideLoadingState();
        showError('Analysis failed: ' + error.message);
        enableAnalyzeButton();
    }
}
```

**Step 3: Task Status Polling**
```javascript
async function pollTaskStatus(taskId, contactId, noteText) {
    const maxAttempts = 60; // 5 minutes max (5s intervals)
    const pollInterval = 5000; // 5 seconds
    let attempts = 0;
    
    const poller = setInterval(async () => {
        try {
            const response = await fetch(`/api/notes/task/${taskId}/status`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to check task status');
            }
            
            const data = await response.json();
            
            // Update UI based on task state
            if (data.state === 'SUCCESS') {
                clearInterval(poller);
                hideLoadingState();
                
                if (data.result && data.result.synthesis) {
                    displaySynthesisResults(data.result.synthesis, contactId, noteText);
                } else {
                    showError('Analysis completed but no results');
                }
                
            } else if (data.state === 'FAILURE') {
                clearInterval(poller);
                hideLoadingState();
                showError(data.error || 'Analysis failed');
                enableAnalyzeButton();
                
            } else if (data.state === 'PROGRESS') {
                // Update progress indicator
                updateProgressIndicator(
                    data.progress || 0,
                    data.status || 'Processing...'
                );
            } else if (data.state === 'PENDING') {
                updateProgressIndicator(0, 'Waiting to process...');
            }
            
            attempts++;
            if (attempts >= maxAttempts) {
                clearInterval(poller);
                hideLoadingState();
                showError('Analysis timed out after 5 minutes');
                enableAnalyzeButton();
            }
            
        } catch (error) {
            clearInterval(poller);
            hideLoadingState();
            showError('Error checking status: ' + error.message);
            enableAnalyzeButton();
        }
    }, pollInterval);
}
```

**Step 4: Display Synthesis Results (Editable)**
```javascript
function displaySynthesisResults(synthesis, contactId, rawNote) {
    // 1. Clear previous results
    const container = document.getElementById('synthesis-results');
    container.innerHTML = '';
    container.style.display = 'block';
    
    // 2. Create editable category cards
    const categories = Object.entries(synthesis);
    
    if (categories.length === 0) {
        container.innerHTML = '<p>No categories extracted. The note may not contain structured information.</p>';
        return;
    }
    
    categories.forEach(([category, data]) => {
        const categoryCard = createCategoryCard(category, data, contactId);
        container.appendChild(categoryCard);
    });
    
    // 3. Show save button
    showSaveButton(contactId, rawNote, synthesis);
}

function createCategoryCard(category, data, contactId) {
    const card = document.createElement('div');
    card.className = 'category-card';
    card.dataset.category = category;
    
    const content = data.content || data; // Handle both formats
    const confidence = data.confidence || 0.0;
    
    card.innerHTML = `
        <div class="category-header">
            <h4>${category}</h4>
            <span class="confidence-badge">Confidence: ${(confidence * 100).toFixed(0)}%</span>
        </div>
        <textarea class="category-content" data-category="${category}">${content}</textarea>
        <button class="remove-category-btn" onclick="removeCategory('${category}')">Remove</button>
    `;
    
    return card;
}

function showSaveButton(contactId, rawNote, synthesis) {
    const saveBtn = document.getElementById('save-synthesis-btn');
    saveBtn.style.display = 'block';
    saveBtn.onclick = () => saveSynthesis(contactId, rawNote, getEditedSynthesis());
}
```

**Step 5: Get Edited Synthesis & Save**
```javascript
function getEditedSynthesis() {
    const synthesis = {};
    const categoryCards = document.querySelectorAll('.category-card');
    
    categoryCards.forEach(card => {
        const category = card.dataset.category;
        const textarea = card.querySelector('.category-content');
        const content = textarea.value.trim();
        
        if (content && content.length > 10) {
            // Get original confidence if available
            const confidenceBadge = card.querySelector('.confidence-badge');
            const confidenceMatch = confidenceBadge?.textContent.match(/(\d+)%/);
            const confidence = confidenceMatch ? parseFloat(confidenceMatch[1]) / 100 : 0.5;
            
            synthesis[category] = {
                content: content,
                confidence: confidence
            };
        }
    });
    
    return synthesis;
}

async function saveSynthesis(contactId, rawNote, synthesis) {
    try {
        showLoadingState('Saving analysis...');
        
        const response = await fetch('/api/notes/save-synthesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                contact_id: contactId,
                raw_note: rawNote,
                synthesis: synthesis
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showSuccess(`Saved ${Object.keys(synthesis).length} categories successfully!`);
            
            // Clear note input
            document.getElementById('note-input').value = '';
            
            // Refresh contact details to show new data
            loadContactDetails(contactId);
            
            // Hide synthesis results
            document.getElementById('synthesis-results').style.display = 'none';
            
        } else {
            showError(data.error || 'Failed to save analysis');
        }
        
    } catch (error) {
        showError('Error saving: ' + error.message);
    } finally {
        hideLoadingState();
    }
}
```

**Step 6: UI Helper Functions**
```javascript
function showLoadingState(message) {
    const loader = document.getElementById('loading-indicator');
    loader.textContent = message;
    loader.style.display = 'block';
    
    // Show progress bar
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.display = 'block';
    progressBar.value = 0;
}

function updateProgressIndicator(progress, status) {
    const progressBar = document.getElementById('progress-bar');
    progressBar.value = progress;
    
    const statusText = document.getElementById('status-text');
    statusText.textContent = status;
}

function hideLoadingState() {
    document.getElementById('loading-indicator').style.display = 'none';
    document.getElementById('progress-bar').style.display = 'none';
}

function showError(message) {
    const toast = createToast('error', message);
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function showSuccess(message) {
    const toast = createToast('success', message);
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function createToast(type, message) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    return toast;
}
```

**Key Frontend Patterns:**
- ✅ **Polling with timeout** - Check status every 5s, max 5 minutes
- ✅ **Progress indicators** - Show progress bar and status text
- ✅ **Editable results** - User can edit categories before saving
- ✅ **Error handling** - Network errors, timeouts, API errors
- ✅ **State management** - Disable buttons during processing
- ✅ **User feedback** - Loading states, success/error messages
- ✅ **Auto-refresh** - Reload contact details after saving

### Testing Strategy for Note Processing

**Unit Tests:**
```python
def test_ai_service_initialization():
    """Test AI service initializes with API keys"""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        service = AIService()
        assert service._available == True
        assert service.gemini_api_key == 'test_key'

def test_analyze_note_with_mocked_gemini():
    """Test note analysis with mocked Gemini response"""
    with patch('app.services.ai_service.genai') as mock_genai:
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"categories": {"Actionable": {"content": "Call John", "confidence": 0.9}}}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        service = AIService()
        result = service.analyze_note("Call John next week", "John Doe")
        
        assert 'categories' in result
        assert 'Actionable' in result['categories']
        assert result['categories']['Actionable']['content'] == "Call John"

def test_response_parsing_with_markdown():
    """Test parsing JSON wrapped in markdown code blocks"""
    response_text = '```json\n{"categories": {"test": {"content": "data"}}}\n```'
    result = parse_ai_response(response_text)
    assert result['categories']['test']['content'] == 'data'

def test_category_normalization():
    """Test category name normalization"""
    assert normalize_category_name('actionable') == 'Actionable'
    assert normalize_category_name('relationship strategy') == 'Relationship_Strategy'
    assert normalize_category_name('invalid_category') == 'invalid_category'

def test_confidence_score_normalization():
    """Test confidence score normalization"""
    assert normalize_confidence_score(0.85) == 0.85
    assert normalize_confidence_score("0.85") == 0.85
    assert normalize_confidence_score("85%") == 0.85
    assert normalize_confidence_score(85) == 0.85  # Assume percentage
    assert normalize_confidence_score(2.0) == 1.0  # Clamp to max
    assert normalize_confidence_score(-0.5) == 0.0  # Clamp to min

def test_content_validation():
    """Test content quality validation"""
    assert validate_extracted_content("Valid content here", 0.8, "Actionable")[0] == True
    assert validate_extracted_content("short", 0.8, "Actionable")[0] == False  # Too short
    assert validate_extracted_content("example placeholder", 0.8, "Actionable")[0] == False  # Placeholder
```

**Integration Tests:**
```python
def test_complete_note_processing_flow(client, authenticated_user, db_session):
    """Test complete flow: save → analyze → save synthesis"""
    # 1. Create contact
    contact = Contact(full_name='Test Contact', user_id=authenticated_user.id)
    db_session.add(contact)
    db_session.commit()
    
    # 2. Process note (async)
    response = client.post('/api/notes/analyze', json={
        'contact_id': contact.id,
        'note_text': 'John likes pizza and works at Google'
    })
    
    assert response.status_code == 202
    task_id = response.json['task_id']
    
    # 3. Poll for completion
    import time
    for _ in range(10):
        status_response = client.get(f'/api/notes/task/{task_id}/status')
        data = status_response.json
        if data['state'] == 'SUCCESS':
            assert 'result' in data
            assert 'synthesis' in data['result']
            break
        time.sleep(1)
    
    # 4. Verify database
    raw_notes = db_session.query(RawNote).filter(
        RawNote.contact_id == contact.id
    ).all()
    assert len(raw_notes) == 1
    
    synthesized = db_session.query(SynthesizedEntry).filter(
        SynthesizedEntry.contact_id == contact.id
    ).all()
    assert len(synthesized) > 0

def test_rag_pipeline_integration(client, authenticated_user, db_session):
    """Test RAG pipeline retrieves relevant history"""
    # 1. Create contact and add historical notes
    contact = Contact(full_name='Test Contact', user_id=authenticated_user.id)
    db_session.add(contact)
    db_session.commit()
    
    # 2. Add historical note to ChromaDB
    from app.utils.chromadb_client import get_contact_collection
    collection = get_contact_collection(contact.id)
    collection.add(
        documents=["John works at Google and likes pizza"],
        ids=["note_1"],
        metadatas=[{"contact_id": contact.id, "note_id": 1}]
    )
    
    # 3. Process new note (should retrieve history)
    # ... test that history is retrieved and used
```

**End-to-End Tests:**
```python
def test_user_journey_note_processing(browser, authenticated_user):
    """Test complete user journey: enter note → analyze → review → save"""
    # 1. Navigate to contact
    browser.get('/')
    browser.find_element_by_id('contact-select').send_keys('Test Contact')
    
    # 2. Enter note
    note_input = browser.find_element_by_id('note-input')
    note_input.send_keys('John mentioned he wants to start a business')
    
    # 3. Click analyze
    browser.find_element_by_id('analyze-btn').click()
    
    # 4. Wait for results
    WebDriverWait(browser, 60).until(
        EC.presence_of_element_located((By.ID, 'synthesis-results'))
    )
    
    # 5. Verify categories displayed
    categories = browser.find_elements_by_class_name('category-card')
    assert len(categories) > 0
    
    # 6. Edit a category
    textarea = browser.find_element_by_css_selector('.category-content')
    textarea.clear()
    textarea.send_keys('Updated content')
    
    # 7. Save
    browser.find_element_by_id('save-synthesis-btn').click()
    
    # 8. Verify success message
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'toast-success'))
    )
```

### UnifiedAIService & SmartModelSelector

**Overview:**
Intelligent AI model selection system that automatically chooses the optimal AI provider and model based on task type, context size, and cost optimization. Provides a unified interface for OpenAI and Gemini with automatic fallback.

**Components:**

1. **UnifiedAIService** (`app/services/unified_ai_service.py`)
   - Unified interface for OpenAI and Gemini
   - Smart model selection based on task requirements
   - Automatic fallback between providers

2. **SmartModelSelector** (`app/services/smart_model_selector.py`)
   - Task-specific model selection
   - Token estimation and context size awareness
   - Cost optimization
   - Model capability matching

**Key Features:**

1. **Task-Specific Selection**
   - `transcription` → OpenAI transcription model (specialized)
   - `telegram_history` → Gemini (large context, cost-effective)
   - `general_analysis` → Gemini for large context, GPT-5 for small/medium

2. **Context Size Awareness**
   - Estimates token count (~4 chars per token)
   - Uses Gemini for contexts ≥ 150K tokens
   - Uses GPT-5 for contexts < 150K tokens

3. **Cost Optimization**
   - Selects cheaper models when appropriate
   - Gemini preferred for large contexts (lower cost)
   - GPT-5 for small contexts (better quality)

4. **Automatic Fallback**
   - Gemini → OpenAI if Gemini unavailable
   - Graceful degradation with error reporting

**High-Level Implementation**

#### Implementation Flow: Unified AI Analysis

**Step 1: UnifiedAIService.analyze_content()**
```python
class UnifiedAIService:
    """Unified service for AI analysis using smart model selection"""
    
    def __init__(self):
        self.smart_selector = smart_selector
        self.gemini_service = gemini_service
    
    def analyze_content(self, content: str, task_type: str, prompt: str = "") -> Dict[str, Any]:
        """
        Analyze content using the optimal AI model.
        
        Args:
            content: The content to analyze
            task_type: Type of task ('transcription', 'telegram_history', 'general_analysis')
            prompt: Additional prompt/instruction
            
        Returns:
            Dict with analysis results
        """
        try:
            # 1. Select optimal model
            model_info = self.smart_selector.select_model(content, task_type, prompt)
            logger.info(f"Selected model: {model_info['model_name']} ({model_info['reason']})")
            
            # 2. Prepare full prompt
            full_prompt = f"{prompt}\n\nContent to analyze:\n{content}" if prompt else content
            
            # 3. Route to appropriate service
            if model_info['provider'] == 'google':
                return self._analyze_with_gemini(full_prompt, model_info)
            elif model_info['provider'] == 'openai':
                return self._analyze_with_openai(full_prompt, model_info)
            else:
                raise ValueError(f"Unknown provider: {model_info['provider']}")
                
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model': 'unknown',
                'provider': 'unknown',
                'reason': f'Analysis failed: {str(e)}'
            }
```

**Key Decision Points:**
- ✅ **Smart selection first** - Let SmartModelSelector choose optimal model
- ✅ **Unified interface** - Same method signature regardless of provider
- ✅ **Error handling** - Return structured error response
- ✅ **Logging** - Track model selection decisions

**Step 2: SmartModelSelector.select_model()**
```python
class SmartModelSelector:
    """Intelligent model selection based on task requirements and context size"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (~4 chars per token for English)"""
        if not text:
            return 0
        estimated_tokens = len(text) // 4
        return max(estimated_tokens, 1)
    
    def select_model(self, content: str, task_type: str, prompt: str = "") -> Dict[str, Any]:
        """
        Select optimal model based on task type and context size.
        
        Returns:
            {
                'model_name': str,
                'provider': str,
                'api_key': str,
                'max_tokens': int,
                'reason': str
            }
        """
        # Calculate total context size
        total_content = content + " " + prompt if prompt else content
        estimated_tokens = self.estimate_tokens(total_content)
        
        logger.info(f"Model selection: task_type={task_type}, estimated_tokens={estimated_tokens}")
        
        # Task-specific selection
        if task_type == "transcription":
            return {
                'model_name': DEFAULT_TRANSCRIPTION_MODEL,  # 'gpt-4o-transcribe'
                'provider': 'openai',
                'api_key': self.openai_api_key,
                'max_tokens': 2000,
                'reason': 'Transcription task - using specialized transcription model'
            }
        
        elif task_type == "telegram_history":
            # Always use Gemini for Telegram (large context by nature)
            if not self.google_api_key:
                logger.warning("Google API key not found, falling back to GPT-5")
                return self._fallback_to_gpt5(estimated_tokens)
            
            return {
                'model_name': GEMINI_MODEL,  # 'gemini-2.0-flash-exp'
                'provider': 'google',
                'api_key': self.google_api_key,
                'max_tokens': GEMINI_MAX_TOKENS,  # 2M tokens
                'reason': 'Telegram history - always using Gemini for large context handling'
            }
        
        elif task_type == "general_analysis":
            # Smart selection based on context size
            if estimated_tokens >= LARGE_CONTEXT_THRESHOLD:  # 150K tokens
                # Large context - use Gemini
                if not self.google_api_key:
                    logger.warning("Google API key not found, falling back to GPT-5")
                    return self._fallback_to_gpt5(estimated_tokens)
                
                return {
                    'model_name': GEMINI_MODEL,
                    'provider': 'google',
                    'api_key': self.google_api_key,
                    'max_tokens': GEMINI_MAX_TOKENS,
                    'reason': f'Large context ({estimated_tokens} tokens) - using Gemini for optimal performance'
                }
            else:
                # Small/medium context - use GPT-5
                return {
                    'model_name': DEFAULT_OPENAI_MODEL,  # 'gpt-5'
                    'provider': 'openai',
                    'api_key': self.openai_api_key,
                    'max_tokens': 2000,
                    'reason': f'Small context ({estimated_tokens} tokens) - using GPT-5 for efficiency'
                }
        
        else:
            # Unknown task type - default to GPT-5
            logger.warning(f"Unknown task type: {task_type}, defaulting to GPT-5")
            return {
                'model_name': DEFAULT_OPENAI_MODEL,
                'provider': 'openai',
                'api_key': self.openai_api_key,
                'max_tokens': 2000,
                'reason': f'Unknown task type - defaulting to GPT-5'
            }
    
    def _fallback_to_gpt5(self, estimated_tokens: int) -> Dict[str, Any]:
        """Fallback to GPT-5 when Gemini is unavailable"""
        return {
            'model_name': DEFAULT_OPENAI_MODEL,
            'provider': 'openai',
            'api_key': self.openai_api_key,
            'max_tokens': 2000,
            'reason': f'Fallback to GPT-5 (Gemini unavailable, {estimated_tokens} tokens)'
        }
```

**Key Decision Points:**
- ✅ **Task-specific routing** - Different models for different tasks
- ✅ **Token estimation** - Simple but effective (~4 chars per token)
- ✅ **Context threshold** - 150K tokens for large context detection
- ✅ **Fallback logic** - Graceful degradation when preferred model unavailable
- ✅ **Reason logging** - Track why each model was selected

**Step 3: Provider-Specific Analysis**

**Gemini Analysis:**
```python
def _analyze_with_gemini(self, prompt: str, model_info: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content using Gemini"""
    try:
        if not self.gemini_service:
            raise ValueError("Gemini service not available")
        
        result = self.gemini_service.analyze_content(
            prompt,
            max_tokens=model_info['max_tokens']
        )
        
        if result['success']:
            logger.info(f"Gemini analysis successful: {result['reason']}")
            return result
        else:
            raise Exception(result['error'])
            
    except Exception as e:
        logger.error(f"Gemini analysis failed: {str(e)}")
        # Fallback to OpenAI if Gemini fails
        logger.info("Falling back to OpenAI due to Gemini failure")
        return self._fallback_to_openai(prompt, model_info)
```

**OpenAI Analysis:**
```python
def _analyze_with_openai(self, prompt: str, model_info: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content using OpenAI"""
    try:
        if _openai_chat is None:
            raise Exception("OpenAI chat function not available")
        
        response_content = _openai_chat(
            messages=[{"role": "user", "content": prompt}],
            model=model_info['model_name'],
            max_tokens=model_info['max_tokens'],
            temperature=DEFAULT_AI_TEMPERATURE,
        )
        
        return {
            'success': True,
            'content': response_content,
            'model': model_info['model_name'],
            'provider': 'openai',
            'reason': f'OpenAI analysis completed with {model_info["model_name"]}'
        }
        
    except Exception as e:
        logger.error(f"OpenAI analysis failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'model': model_info['model_name'],
            'provider': 'openai',
            'reason': f'OpenAI analysis failed: {str(e)}'
        }
```

**Data Flow Diagram: Smart Model Selection**

```
User requests AI analysis
    ↓
UnifiedAIService.analyze_content(content, task_type, prompt)
    ↓
SmartModelSelector.select_model(content, task_type, prompt)
    ├─ Estimate tokens (~4 chars per token)
    ├─ Check task_type
    │   ├─ transcription → GPT-4o Transcribe
    │   ├─ telegram_history → Gemini (always)
    │   └─ general_analysis → Check context size
    │       ├─ ≥ 150K tokens → Gemini
    │       └─ < 150K tokens → GPT-5
    └─ Return model_info (model_name, provider, api_key, max_tokens, reason)
    ↓
Route to provider
    ├─ provider == 'google' → _analyze_with_gemini()
    │   ├─ Call GeminiService
    │   ├─ Success → Return result
    │   └─ Failure → Fallback to OpenAI
    └─ provider == 'openai' → _analyze_with_openai()
        ├─ Call OpenAI API
        ├─ Success → Return result
        └─ Failure → Return error
    ↓
Return unified result format
    {
        'success': bool,
        'content': str,
        'model': str,
        'provider': str,
        'reason': str
    }
```

**Model Selection Rules**

| Task Type | Context Size | Selected Model | Reason |
|-----------|--------------|----------------|--------|
| `transcription` | Any | GPT-4o Transcribe | Specialized transcription model |
| `telegram_history` | Any | Gemini 2.0 Flash | Large context, cost-effective |
| `general_analysis` | ≥ 150K tokens | Gemini 2.0 Flash | Large context handling |
| `general_analysis` | < 150K tokens | GPT-5 | Better quality for small contexts |
| Unknown | Any | GPT-5 | Safe default |

**Integration Points**

1. **AIService**: Can be used as alternative to direct AIService calls
2. **GeminiService**: Uses existing GeminiService for Gemini calls
3. **OpenAI**: Uses `_openai_chat` function from app.py
4. **Constants**: Uses `DEFAULT_OPENAI_MODEL`, `GEMINI_MODEL`, `LARGE_CONTEXT_THRESHOLD` from constants

**Common Patterns**

**Pattern 1: Task-Specific Routing**
```python
if task_type == "transcription":
    return transcription_model_config
elif task_type == "telegram_history":
    return gemini_config  # Always Gemini
elif task_type == "general_analysis":
    if estimated_tokens >= LARGE_CONTEXT_THRESHOLD:
        return gemini_config
    else:
        return gpt5_config
```

**Pattern 2: Fallback Chain**
```python
try:
    result = self._analyze_with_gemini(prompt, model_info)
    return result
except Exception as e:
    logger.warning(f"Gemini failed: {e}, falling back to OpenAI")
    return self._fallback_to_openai(prompt, model_info)
```

**Pattern 3: Token Estimation**
```python
# Simple but effective estimation
estimated_tokens = len(text) // 4  # ~4 chars per token

# For production, consider using tiktoken for accurate estimation
# import tiktoken
# encoding = tiktoken.encoding_for_model("gpt-4")
# estimated_tokens = len(encoding.encode(text))
```

**Performance Considerations**

1. **Token Estimation**: Simple division is fast but approximate
2. **Model Selection**: O(1) operation, no external calls
3. **Fallback Overhead**: Minimal, only on failure
4. **Caching**: Consider caching model selection decisions for similar content

**Cost Optimization**

1. **Gemini for Large Contexts**: Lower cost per token for large inputs
2. **GPT-5 for Small Contexts**: Better quality-to-cost ratio for small inputs
3. **Task-Specific Models**: Use specialized models when available (transcription)
4. **Fallback Strategy**: Prevents failed requests (wasted API calls)

**Error Handling**

1. **Missing API Keys**: Fallback to available provider
2. **Model Unavailable**: Fallback to alternative
3. **API Errors**: Return structured error response
4. **Unknown Task Type**: Default to GPT-5 with warning

**Usage Example**

```python
from app.services.unified_ai_service import unified_ai_service

# Analyze Telegram history (will use Gemini)
result = unified_ai_service.analyze_content(
    content=telegram_messages,
    task_type="telegram_history",
    prompt="Summarize key points from this conversation"
)

# Analyze small note (will use GPT-5)
result = unified_ai_service.analyze_content(
    content="Meeting with John about Q4 strategy",
    task_type="general_analysis"
)

# Transcribe audio (will use GPT-4o Transcribe)
result = unified_ai_service.analyze_content(
    content=audio_transcript,
    task_type="transcription"
)

# Check result
if result['success']:
    print(f"Analysis completed using {result['model']} ({result['provider']})")
    print(f"Reason: {result['reason']}")
    print(f"Content: {result['content']}")
else:
    print(f"Analysis failed: {result['error']}")
```

**Testing Approach**

- Test model selection for each task type
- Test token estimation accuracy
- Test context size threshold (150K tokens)
- Test fallback logic (Gemini → OpenAI)
- Test missing API keys handling
- Test cost optimization (verify cheaper models selected when appropriate)
- Test error handling and recovery

### Testing Approach
- Mock AI service responses
- Test synchronous vs async processing
- Test RAG context retrieval
- Test category extraction accuracy
- Test error handling for AI failures
- Test smart model selection logic
- Test fallback mechanisms

---

## Feature 4: Tag & Category System

### Overview
Hierarchical tag system for organizing contacts. Tags can be nested, have colors, and are user-specific. Categories are AI-extracted from notes and can be converted to tags.

### User-Facing Pages
- **Tag Management** (Settings view or dedicated section)
  - Tag creation/edit form
  - Tag hierarchy display
  - Tag assignment to contacts
  - Category-to-tag conversion

### API Endpoints

**`GET /api/tags`**
- Get all tags for current user
- Response: `[{ "id": int, "name": string, "parent_id": int|null, "color": string, ... }]`

**`POST /api/tags`**
- Create new tag
- Request: `{ "name": string, "parent_id": int|null, "color": string }`

**`PUT /api/tags/<id>`**
- Update tag

**`DELETE /api/tags/<id>`**
- Delete tag (removes from contacts)

**`POST /api/tags/<tag_id>/assign`**
- Assign tag to contact
- Request: `{ "contact_id": int }`

**`DELETE /api/tags/<tag_id>/assign`**
- Remove tag from contact
- Request: `{ "contact_id": int }`

**`GET /api/categories`**
- Get all available AI categories
- Response: `[{ "name": string, "description": string }]`

### Database Models

**Tag Model** (`models.py`)
```python
class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('tags.id'), nullable=True)
    color = Column(String(7))  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = relationship("Tag", remote_side=[id], backref="children")
    contacts = relationship("Contact", secondary="contact_tags")
```

**ContactTag Association** (`models.py`)
```python
contact_tags = Table('contact_tags', Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)
```

### Services

**TagService** (`app/services/tag_service.py`)
- `create_tag(user_id, name, parent_id, color)` - Create with hierarchy validation
- `get_tags_by_user(user_id)` - Get all user tags with hierarchy
- `assign_tag_to_contact(tag_id, contact_id, user_id)` - Assign with ownership check
- `remove_tag_from_contact(tag_id, contact_id, user_id)` - Remove assignment

### Frontend Implementation

**Tag Management** (`static/js/tag-management.js`)
- Tag tree visualization
- Tag creation modal
- Drag-and-drop hierarchy
- Color picker
- Contact tag assignment UI

### High-Level Implementation

#### Implementation Flow: Create Tag

**Step 1: API Endpoint** (`app/api/tags.py`)
```python
@tags_bp.route('/', methods=['POST'])
@login_required
@inject
def create_tag(tag_service: TagService = Provide[Container.tag_service]):
    """Create a new tag"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        color = data.get('color', '#97C2FC')  # Default blue
        description = data.get('description', '').strip()
        
        # Validate required fields
        if not name:
            return jsonify({'error': 'Tag name is required'}), 400
        
        # Validate color format (hex)
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return jsonify({'error': 'Invalid color format. Use hex format (#RRGGBB)'}), 400
        
        # Create tag via service
        tag = tag_service.create_tag(
            user_id=current_user.id,
            name=name,
            color=color,
            description=description
        )
        
        if tag:
            return jsonify(tag), 201
        else:
            return jsonify({'error': 'Tag with this name already exists'}), 409
            
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        return jsonify({'error': 'Failed to create tag'}), 500
```

**Key Decision Points:**
- ✅ **Validate color format** - Ensure valid hex color
- ✅ **Strip whitespace** - Clean input
- ✅ **Check for duplicates** - TagService handles this
- ✅ **Return 409 for conflicts** - Standard HTTP status for duplicates

**Step 2: TagService.create_tag()** (`app/services/tag_service.py`)
```python
def create_tag(self, user_id: int, name: str, color: str = '#97C2FC', description: str = None) -> Optional[Dict]:
    """Create a new tag with duplicate checking"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Check for duplicate name (case-insensitive)
            existing_tag = session.query(Tag).filter(
                Tag.user_id == user_id,
                func.lower(Tag.name) == func.lower(name)
            ).first()
            
            if existing_tag:
                logger.warning(f"Tag '{name}' already exists for user {user_id}")
                return None
            
            # 2. Create tag
            tag = Tag(
                user_id=user_id,
                name=name,
                color=color,
                description=description
            )
            
            session.add(tag)
            session.commit()
            session.refresh(tag)
            
            # 3. Convert to dict before session closes
            tag_dict = tag.to_dict()
            
            logger.info(f"Created tag {tag.id}: {tag.name} for user {user_id}")
            return tag_dict
            
    except IntegrityError as e:
        logger.error(f"Integrity error creating tag '{name}': {e}")
        session.rollback()
        return None
    except Exception as e:
        logger.error(f"Error creating tag '{name}': {e}")
        session.rollback()
        return None
```

**Key Decision Points:**
- ✅ **Case-insensitive duplicate check** - "Work" and "work" are same
- ✅ **Use func.lower()** - Database-level case-insensitive comparison
- ✅ **Convert to dict** - Avoid detached instance errors
- ✅ **Rollback on error** - Maintain data consistency

#### Implementation Flow: Assign Tag to Contact

**Step 1: API Endpoint** (`app/api/tags.py`)
```python
@tags_bp.route('/<int:tag_id>/assign', methods=['POST'])
@login_required
@inject
def assign_tag(tag_id: int, tag_service: TagService = Provide[Container.tag_service]):
    """Assign a tag to a contact"""
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        
        if not contact_id:
            return jsonify({'error': 'contact_id is required'}), 400
        
        # Assign via service
        success = tag_service.add_tag_to_contact(
            contact_id=contact_id,
            tag_id=tag_id,
            user_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Tag assigned to contact'
            }), 200
        else:
            return jsonify({'error': 'Failed to assign tag. Contact or tag not found.'}), 404
            
    except Exception as e:
        logger.error(f"Error assigning tag: {e}")
        return jsonify({'error': 'Failed to assign tag'}), 500
```

**Step 2: TagService.add_tag_to_contact()**
```python
def add_tag_to_contact(self, contact_id: int, tag_id: int, user_id: int) -> bool:
    """Add a tag to a contact with ownership verification"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Verify contact ownership
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            # 2. Verify tag ownership
            tag = session.query(Tag).filter(
                Tag.id == tag_id,
                Tag.user_id == user_id
            ).first()
            
            if not contact or not tag:
                logger.warning(f"Contact {contact_id} or tag {tag_id} not found for user {user_id}")
                return False
            
            # 3. Check if association already exists
            existing = session.query(ContactTag).filter(
                ContactTag.contact_id == contact_id,
                ContactTag.tag_id == tag_id
            ).first()
            
            if existing:
                logger.info(f"Contact {contact_id} already has tag {tag_id}")
                return True  # Already assigned, consider success
            
            # 4. Create association
            contact_tag = ContactTag(
                contact_id=contact_id,
                tag_id=tag_id
            )
            session.add(contact_tag)
            session.commit()
            
            logger.info(f"Added tag {tag_id} ({tag.name}) to contact {contact_id}")
            return True
            
    except IntegrityError as e:
        logger.error(f"Integrity error assigning tag: {e}")
        session.rollback()
        return False
    except Exception as e:
        logger.error(f"Error adding tag to contact: {e}")
        session.rollback()
        return False
```

**Key Decision Points:**
- ✅ **Verify ownership of both** - Contact AND tag must belong to user
- ✅ **Idempotent operation** - Already assigned = success
- ✅ **Use association table** - Many-to-many relationship
- ✅ **Log tag name** - Better debugging

#### Implementation Flow: Get Tags for Contact

**Step 1: API Endpoint**
```python
@contacts_bp.route('/<int:contact_id>/tags', methods=['GET'])
@login_required
@inject
def get_contact_tags(contact_id: int, tag_service: TagService = Provide[Container.tag_service]):
    """Get all tags assigned to a contact"""
    try:
        tags = tag_service.get_tags_for_contact(contact_id, current_user.id)
        
        if tags is None:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'tags': [tag.to_dict() for tag in tags]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting contact tags: {e}")
        return jsonify({'error': 'Failed to get tags'}), 500
```

**Step 2: TagService.get_tags_for_contact()**
```python
def get_tags_for_contact(self, contact_id: int, user_id: int) -> Optional[List[Tag]]:
    """Get all tags assigned to a contact"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Verify contact ownership
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                logger.warning(f"Contact {contact_id} not found for user {user_id}")
                return None
            
            # 2. Get tags through many-to-many relationship
            tags = session.query(Tag).join(ContactTag).filter(
                ContactTag.contact_id == contact_id,
                Tag.user_id == user_id
            ).all()
            
            # 3. Expunge to avoid detached instance errors
            for tag in tags:
                session.expunge(tag)
            
            logger.info(f"Retrieved {len(tags)} tags for contact {contact_id}")
            return tags
            
    except Exception as e:
        logger.error(f"Error retrieving tags for contact: {e}")
        return None
```

#### Implementation Flow: Delete Tag with Reassignment

**Step 1: TagService.delete_tag()**
```python
def delete_tag(self, tag_id: int, user_id: int, reassign_to_tag_id: int = None) -> bool:
    """Delete a tag, optionally reassigning contacts to another tag"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Verify tag ownership
            tag = session.query(Tag).filter(
                Tag.id == tag_id,
                Tag.user_id == user_id
            ).first()
            
            if not tag:
                logger.warning(f"Tag {tag_id} not found for user {user_id}")
                return False
            
            # 2. Handle reassignment if specified
            if reassign_to_tag_id:
                reassign_tag = session.query(Tag).filter(
                    Tag.id == reassign_to_tag_id,
                    Tag.user_id == user_id
                ).first()
                
                if not reassign_tag:
                    logger.warning(f"Reassignment tag {reassign_to_tag_id} not found")
                    return False
                
                # 3. Get all contact-tag associations
                contact_tags = session.query(ContactTag).filter(
                    ContactTag.tag_id == tag_id
                ).all()
                
                # 4. Reassign contacts (avoid duplicates)
                for contact_tag in contact_tags:
                    # Check if contact already has reassignment tag
                    existing = session.query(ContactTag).filter(
                        ContactTag.contact_id == contact_tag.contact_id,
                        ContactTag.tag_id == reassign_to_tag_id
                    ).first()
                    
                    if not existing:
                        # Create new association
                        new_contact_tag = ContactTag(
                            contact_id=contact_tag.contact_id,
                            tag_id=reassign_to_tag_id
                        )
                        session.add(new_contact_tag)
                    
                    # Remove old association
                    session.delete(contact_tag)
                
                logger.info(f"Reassigned {len(contact_tags)} contacts from tag {tag_id} to {reassign_to_tag_id}")
            
            # 5. Delete the tag (cascade will remove ContactTag associations)
            session.delete(tag)
            session.commit()
            
            logger.info(f"Deleted tag {tag_id}: {tag.name}")
            return True
            
    except Exception as e:
        logger.error(f"Error deleting tag {tag_id}: {e}")
        session.rollback()
        return False
```

**Key Decision Points:**
- ✅ **Optional reassignment** - Preserve data when deleting tags
- ✅ **Avoid duplicate assignments** - Check before reassigning
- ✅ **Cascade deletion** - ContactTag associations removed automatically
- ✅ **Log reassignment count** - Track data migration

#### Data Flow Diagram: Tag Assignment

```
User assigns tag to contact
    ↓
POST /api/tags/<tag_id>/assign
    ↓
Extract contact_id from request
    ↓
TagService.add_tag_to_contact()
    ├─ Verify contact ownership
    ├─ Verify tag ownership
    ├─ Check if already assigned
    │   ├─ Yes → Return success (idempotent)
    │   └─ No → Create ContactTag association
    ↓
Commit to database
    ↓
Return success response
```

#### Integration Points

1. **Database**: Uses `ContactTag` association table for many-to-many
2. **User Isolation**: Always filter by `user_id` for both contacts and tags
3. **Error Handling**: IntegrityError for duplicates, rollback on failure
4. **Logging**: Comprehensive logging for debugging

#### Common Patterns

**Pattern 1: Verify Ownership Before Operation**
```python
# Always verify both resources belong to user
contact = session.query(Contact).filter(
    Contact.id == contact_id,
    Contact.user_id == user_id
).first()

tag = session.query(Tag).filter(
    Tag.id == tag_id,
    Tag.user_id == user_id
).first()

if not contact or not tag:
    return False  # Not found or unauthorized
```

**Pattern 2: Idempotent Operations**
```python
# Check if association exists
existing = session.query(ContactTag).filter(
    ContactTag.contact_id == contact_id,
    ContactTag.tag_id == tag_id
).first()

if existing:
    return True  # Already done, consider success
```

**Pattern 3: Expunge Before Returning**
```python
# Expunge objects to avoid detached instance errors
for tag in tags:
    session.expunge(tag)
return tags
```

### Categories Management API

**Overview:**
Dedicated API endpoints for managing contact categories with comprehensive change tracking. This API provides granular control over category updates with detailed diff computation and audit logging.

**API Endpoints** (`app/api/categories.py`)

**`PUT /api/categories/contact/<contact_id>/categories`**
- Replace all synthesized category entries for a contact
- Request Body:
```json
{
  "categorized_updates": [
    {"category": "Actionable", "details": ["Follow up on proposal", "Schedule meeting"]},
    {"category": "Goals", "details": ["Wants to expand to 3 markets"]}
  ],
  "raw_note": "Edited multiple categories via UI"
}
```
- Response:
```json
{
  "status": "success",
  "message": "Categories updated",
  "details": {
    "categories_saved": 2,
    "categories_modified": 2,
    "items_added": 3,
    "items_removed": 1
  }
}
```

**`GET /api/categories/contact/<contact_id>/categories`**
- Get all synthesized category entries for a contact
- Response:
```json
{
  "status": "success",
  "contact_id": 123,
  "categorized_data": {
    "Actionable": ["Follow up on proposal", "Schedule meeting"],
    "Goals": ["Wants to expand to 3 markets"],
    "Professional_Background": ["CEO of TechCorp"]
  }
}
```

**Key Features:**

1. **Category Normalization**
   - Handles variations: underscores vs spaces, case differences
   - Maps to canonical category names from `CATEGORY_ORDER`
   - Defaults to 'Others' if category not found

2. **Detailed Diff Computation**
   - Tracks added, removed, and unchanged items per category
   - Provides granular change tracking for audit purposes

3. **Change Logging**
   - Creates RawNote entry with metadata containing:
     - Before/after snapshots
     - Detailed changes (added/removed/unchanged)
     - Summary statistics
   - Enables full audit trail of category edits

4. **Summary Generation**
   - Human-readable summaries: "Edited 3 categories via UI: Actionable, Goals, Social (+5 added, -2 removed)"
   - Truncates long category lists with ellipsis

**High-Level Implementation**

#### Implementation Flow: Replace Contact Categories

**Step 1: API Endpoint** (`app/api/categories.py`)
```python
@categories_bp.route('/contact/<int:contact_id>/categories', methods=['PUT'])
@login_required
def replace_contact_categories(contact_id: int):
    """Replace all synthesized category entries with detailed change tracking"""
    try:
        payload = request.get_json() or {}
        updates = payload.get('categorized_updates', [])
        raw_note_text = payload.get('raw_note')
        
        if not isinstance(updates, list):
            return jsonify({"error": "categorized_updates must be a list"}), 400
        
        # Normalize and clean input
        cleaned = []
        for item in updates:
            raw_category = (item or {}).get('category', '').strip()
            details = [d.strip() for d in (item or {}).get('details') or [] if d.strip()]
            
            # Normalize category name
            normalized_category = normalize_category(raw_category)
            
            if details:
                cleaned.append({
                    "category": normalized_category,
                    "details": details
                })
        
        db = DatabaseManager()
        with db.get_session() as session:
            # Verify contact ownership
            contact = session.query(Contact).filter_by(
                id=contact_id,
                user_id=current_user.id
            ).first()
            
            if not contact:
                return jsonify({"error": "Contact not found"}), 404
            
            # Snapshot before state
            before = {}
            existing = session.query(SynthesizedEntry).filter_by(
                contact_id=contact_id
            ).all()
            for e in existing:
                before.setdefault(e.category, []).append(e.content)
            
            # Replace all entries
            session.query(SynthesizedEntry).filter_by(
                contact_id=contact_id
            ).delete(synchronize_session=False)
            
            for item in cleaned:
                for detail in item['details']:
                    session.add(SynthesizedEntry(
                        contact_id=contact_id,
                        category=item['category'],
                        content=detail,
                        created_at=datetime.utcnow()
                    ))
            
            # Snapshot after state
            session.flush()
            after = {}
            new_entries = session.query(SynthesizedEntry).filter_by(
                contact_id=contact_id
            ).all()
            for e in new_entries:
                after.setdefault(e.category, []).append(e.content)
            
            # Compute changes
            changed_categories = []
            added_count = 0
            removed_count = 0
            all_cats = set(list(before.keys()) + list(after.keys()))
            
            for cat in all_cats:
                b = before.get(cat, []) or []
                a = after.get(cat, []) or []
                if b != a:
                    changed_categories.append(cat)
                    added_count += sum(1 for x in a if x not in b)
                    removed_count += sum(1 for x in b if x not in a)
            
            # Generate summary
            if changed_categories:
                if len(changed_categories) == 1:
                    summary = f"Edited 1 category via UI: {changed_categories[0].replace('_', ' ')}"
                else:
                    preview = ', '.join([c.replace('_', ' ') for c in changed_categories[:3]])
                    ellipsis = '…' if len(changed_categories) > 3 else ''
                    summary = f"Edited {len(changed_categories)} categories via UI: {preview}{ellipsis}"
                summary += f" (+{added_count} added, -{removed_count} removed)"
            else:
                summary = 'Saved categories with no changes'
            
            # Compute detailed changes
            detailed_changes = compute_detailed_diff(before, after)
            
            # Create audit log entry
            tags_obj = {
                "type": "category_edit",
                "source": "ui_edit",
                "before": before,
                "after": after,
                "detailed_changes": detailed_changes,
                "summary": {
                    "categories_modified": [cat.replace('_', ' ') for cat in changed_categories],
                    "total_added": added_count,
                    "total_removed": removed_count
                }
            }
            
            session.add(RawNote(
                contact_id=contact_id,
                content=summary,
                metadata_tags=tags_obj,
                created_at=datetime.utcnow()
            ))
            
            session.commit()
            
            return jsonify({
                "status": "success",
                "message": "Categories updated",
                "details": {
                    "categories_saved": len(cleaned),
                    "categories_modified": len(changed_categories),
                    "items_added": added_count,
                    "items_removed": removed_count
                }
            })
            
    except Exception as e:
        logger.error(f"Failed to save categories: {e}", exc_info=True)
        return jsonify({"error": f"Failed to replace categories: {e}"}), 500
```

**Key Decision Points:**
- ✅ **Snapshot before/after** - Capture state for diff computation
- ✅ **Delete all, then insert** - Simple replace strategy
- ✅ **Normalize categories** - Handle variations in category names
- ✅ **Compute detailed diff** - Track granular changes
- ✅ **Create audit log** - Store change history in RawNote
- ✅ **Generate human-readable summary** - User-friendly change description

**Step 2: Category Normalization Function**
```python
def normalize_category(category_name: str) -> str:
    """Normalize category names to match CATEGORY_ORDER format"""
    if not isinstance(category_name, str):
        return 'Others'
    
    cleaned = category_name.strip()
    
    # Build lowercase lookup map
    category_lookup = {
        cat.lower().replace('_', ' '): cat 
        for cat in CATEGORY_ORDER
    }
    
    # Try various normalizations
    test_keys = [
        cleaned.lower(),
        cleaned.lower().replace('_', ' '),
        cleaned.lower().replace(' ', '_'),
    ]
    
    for test_key in test_keys:
        normalized_key = test_key.replace('_', ' ')
        if normalized_key in category_lookup:
            return category_lookup[normalized_key]
    
    # No match found
    logger.warning(f"Category '{category_name}' not found, defaulting to 'Others'")
    return 'Others'
```

**Key Decision Points:**
- ✅ **Multiple normalization attempts** - Handle various input formats
- ✅ **Case-insensitive matching** - "Actionable" = "actionable" = "ACTIONABLE"
- ✅ **Underscore/space handling** - "Actionable" = "actionable" = "action able"
- ✅ **Default to 'Others'** - Graceful fallback for unknown categories

**Step 3: Detailed Diff Computation**
```python
def compute_detailed_diff(before: dict, after: dict) -> dict:
    """Compute granular item-level changes between before and after states"""
    all_categories = set(list(before.keys()) + list(after.keys()))
    changes = {}
    
    for category in all_categories:
        before_items = set(before.get(category, []) or [])
        after_items = set(after.get(category, []) or [])
        
        added = list(after_items - before_items)
        removed = list(before_items - after_items)
        unchanged = list(before_items & after_items)
        
        if added or removed:  # Only include if there were actual changes
            changes[category] = {
                "added": added,
                "removed": removed,
                "unchanged": unchanged
            }
    
    return changes
```

**Key Decision Points:**
- ✅ **Set-based comparison** - Efficient diff computation
- ✅ **Track added/removed/unchanged** - Complete change picture
- ✅ **Only include changed categories** - Reduce noise in diff output

**Step 4: Get Contact Categories**
```python
@categories_bp.route('/contact/<int:contact_id>/categories', methods=['GET'])
@login_required
def get_contact_categories(contact_id: int):
    """Return all synthesized category entries in UI-friendly format"""
    try:
        db = DatabaseManager()
        with db.get_session() as session:
            # Verify ownership
            contact = session.query(Contact).filter_by(
                id=contact_id,
                user_id=current_user.id
            ).first()
            
            if not contact:
                return jsonify({"error": "Contact not found"}), 404
            
            # Get all entries ordered by category
            entries = (
                session.query(SynthesizedEntry)
                .filter_by(contact_id=contact_id)
                .order_by(SynthesizedEntry.category.asc(), SynthesizedEntry.id.asc())
                .all()
            )
            
            # Group by category
            categorized = {}
            for e in entries:
                categorized.setdefault(e.category, []).append(e.content)
            
            return jsonify({
                "status": "success",
                "contact_id": contact_id,
                "categorized_data": categorized
            })
            
    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}", exc_info=True)
        return jsonify({"error": f"Failed to fetch categories: {e}"}), 500
```

**Data Flow Diagram: Category Update**

```
User edits categories in UI
    ↓
PUT /api/categories/contact/<id>/categories
    ↓
Extract categorized_updates from request
    ↓
Normalize category names
    ├─ Handle underscores/spaces
    ├─ Case-insensitive matching
    └─ Default to 'Others' if unknown
    ↓
Snapshot before state
    ├─ Query all SynthesizedEntry for contact
    └─ Group by category → before dict
    ↓
Delete all existing entries
    ↓
Insert new entries from updates
    ↓
Snapshot after state
    ├─ Query all SynthesizedEntry for contact
    └─ Group by category → after dict
    ↓
Compute detailed diff
    ├─ Added items (after - before)
    ├─ Removed items (before - after)
    └─ Unchanged items (before ∩ after)
    ↓
Generate summary
    ├─ Count changed categories
    ├─ Count added/removed items
    └─ Create human-readable message
    ↓
Create RawNote audit log
    ├─ Store before/after snapshots
    ├─ Store detailed changes
    └─ Store summary statistics
    ↓
Commit transaction
    ↓
Return success with change details
```

**Integration Points**

1. **Database**: Uses `SynthesizedEntry` model for category storage
2. **User Isolation**: Always verify contact ownership via `user_id`
3. **Change Tracking**: Creates `RawNote` with metadata for audit trail
4. **Category Constants**: Uses `CATEGORY_ORDER` from constants for normalization

**Common Patterns**

**Pattern 1: Snapshot Before/After for Diff**
```python
# Before
before = {}
existing = session.query(SynthesizedEntry).filter_by(contact_id=contact_id).all()
for e in existing:
    before.setdefault(e.category, []).append(e.content)

# Make changes
# ... delete and insert ...

# After
after = {}
new_entries = session.query(SynthesizedEntry).filter_by(contact_id=contact_id).all()
for e in new_entries:
    after.setdefault(e.category, []).append(e.content)

# Compute diff
changes = compute_detailed_diff(before, after)
```

**Pattern 2: Category Normalization**
```python
# Always normalize user input
raw_category = item.get('category', '').strip()
normalized_category = normalize_category(raw_category)

# Use normalized category for storage
session.add(SynthesizedEntry(
    category=normalized_category,  # Use normalized
    content=detail
))
```

**Pattern 3: Audit Logging**
```python
# Store comprehensive change metadata
tags_obj = {
    "type": "category_edit",
    "source": "ui_edit",
    "before": before,
    "after": after,
    "detailed_changes": detailed_changes,
    "summary": {
        "categories_modified": changed_categories,
        "total_added": added_count,
        "total_removed": removed_count
    }
}

session.add(RawNote(
    contact_id=contact_id,
    content=summary,  # Human-readable summary
    metadata_tags=tags_obj,  # Structured metadata
    created_at=datetime.utcnow()
))
```

**Security Considerations**

1. **User Isolation**: Always verify contact ownership before operations
2. **Input Validation**: Validate category updates are lists, strip whitespace
3. **Category Validation**: Normalize to known categories, prevent injection
4. **Transaction Safety**: Use database transactions for atomic updates

**Performance Considerations**

1. **Batch Operations**: Delete all entries in one query, insert in batch
2. **Eager Loading**: Load all entries at once for snapshot
3. **Index Usage**: Ensure `contact_id` and `category` are indexed
4. **Diff Computation**: Use sets for efficient comparison

**Error Scenarios**

1. **Contact Not Found**: Return 404 with clear error message
2. **Invalid Category**: Normalize to 'Others' and log warning
3. **Empty Updates**: Allow empty list (clears all categories)
4. **Database Errors**: Rollback transaction, return 500 with error details

**Frontend Integration**

```javascript
// Update categories
async function updateContactCategories(contactId, categorizedUpdates) {
    const response = await fetch(`/api/categories/contact/${contactId}/categories`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            categorized_updates: categorizedUpdates,
            raw_note: 'Edited categories via UI'
        })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
        // Show success message with change summary
        showNotification(
            `Updated ${result.details.categories_modified} categories ` +
            `(+${result.details.items_added} added, -${result.details.items_removed} removed)`
        );
        
        // Refresh contact view
        loadContactDetails(contactId);
    }
}

// Get categories
async function getContactCategories(contactId) {
    const response = await fetch(`/api/categories/contact/${contactId}/categories`);
    const result = await response.json();
    
    if (result.status === 'success') {
        return result.categorized_data;
    }
    return {};
}
```

**Testing Approach**

- Test category normalization (underscores, spaces, case)
- Test detailed diff computation (added/removed/unchanged)
- Test change logging (RawNote creation with metadata)
- Test summary generation (single vs multiple categories)
- Test user isolation (cannot edit other users' contacts)
- Test empty updates (clears all categories)
- Test invalid categories (normalizes to 'Others')

### Testing Approach
- Test tag hierarchy (parent/child)
- Test tag assignment/removal
- Test user isolation
- Test category-to-tag conversion
- Test duplicate tag names (case-insensitive)
- Test tag deletion with reassignment
- Test category normalization and change tracking

---

## Feature 5: Search Functionality

### Overview
Full-text search across contacts and notes with semantic search via ChromaDB. Includes autocomplete suggestions, result highlighting, and filtering.

### User-Facing Pages
- **Search Bar** (top of main contacts view)
  - Real-time search input
  - Autocomplete dropdown
  - Search results display
  - Result highlighting

### API Endpoints

**`GET /api/search`**
- Search across contacts and notes
- Query params: `q` (query string), `scope` (all|contacts|notes), `limit` (default 50)
- Response: `{ "contacts": [...], "notes": [...], "total_results": int }`

**`GET /api/search/suggestions`**
- Get autocomplete suggestions
- Query params: `q` (partial query)
- Response: `{ "suggestions": ["string", ...] }`

### Services

**SearchService** (`app/services/search_service.py`)
- `search(query, user_id, scope, limit)` - Main search method
  - Full-text search in PostgreSQL
  - Semantic search in ChromaDB
  - Combine and rank results
- `get_suggestions(query, user_id)` - Autocomplete from search history
- `save_search_query(query, user_id)` - Store for suggestions

### Frontend Implementation

**Search** (`static/js/debounced-search.js`)
- Debounced input (300ms)
- Autocomplete dropdown
- Result highlighting
- Search result display
- Cache search results (5min TTL)

### High-Level Implementation

#### Implementation Flow: Search Contacts and Notes

**Step 1: API Endpoint** (`app/api/search.py`)
```python
@search_bp.route('/', methods=['GET'])
@login_required
@inject
def search(search_service: SearchService = Provide[Container.search_service]):
    """Perform search across contacts and notes"""
    try:
        # 1. Extract query parameters
        query = request.args.get('q', '').strip()
        scope = request.args.get('scope', 'all')  # all, contacts, notes
        limit = request.args.get('limit', 50, type=int)
        
        # 2. Validate parameters
        if not query:
            return jsonify({
                'success': True,
                'contacts': [],
                'notes': [],
                'query': '',
                'total_results': 0
            })
        
        if scope not in ['all', 'contacts', 'notes']:
            return jsonify({'error': 'Invalid scope. Must be all, contacts, or notes'}), 400
        
        if limit < 1 or limit > 100:
            limit = 50  # Clamp to reasonable range
        
        # 3. Perform search
        results = search_service.search(
            query=query,
            user_id=current_user.id,
            scope=scope,
            limit=limit
        )
        
        # 4. Save search query for history/suggestions
        search_service.save_search_query(query, current_user.id)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'contacts': [],
            'notes': [],
            'query': query,
            'total_results': 0
        }), 500
```

**Key Decision Points:**
- ✅ **Validate scope** - Only allow valid values
- ✅ **Clamp limit** - Prevent excessive results
- ✅ **Save search history** - For suggestions
- ✅ **Return empty on no query** - Don't error on empty search

**Step 2: SearchService.search()** (`app/services/search_service.py`)
```python
def search(self, query: str, user_id: int, scope: str = 'all', limit: int = 50) -> Dict[str, Any]:
    """Perform search across contacts and notes"""
    try:
        # 1. Validate minimum query length
        if not query or len(query.strip()) < 2:
            return {
                'success': True,
                'contacts': [],
                'notes': [],
                'query': query,
                'total_results': 0
            }
        
        query = query.strip()
        results = {
            'success': True,
            'contacts': [],
            'notes': [],
            'query': query,
            'total_results': 0
        }
        
        with self.db_manager.get_session() as session:
            # 2. Search contacts if scope includes contacts
            if scope in ['all', 'contacts']:
                contacts = self._search_contacts(session, query, user_id, limit)
                results['contacts'] = contacts
            
            # 3. Search notes if scope includes notes
            if scope in ['all', 'notes']:
                notes = self._search_notes(session, query, user_id, limit)
                results['notes'] = notes
            
            # 4. Calculate total
            results['total_results'] = len(results['contacts']) + len(results['notes'])
            
            logger.info(f"Search '{query}' returned {results['total_results']} results")
            return results
            
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        return {
            'success': False,
            'error': 'Search failed',
            'contacts': [],
            'notes': [],
            'query': query,
            'total_results': 0
        }
```

**Step 3: Search Contacts Implementation**
```python
def _search_contacts(self, session, query: str, user_id: int, limit: int) -> List[Dict[str, Any]]:
    """Search contacts by name, username, phone, handle"""
    try:
        # 1. Build search conditions (case-insensitive LIKE)
        search_conditions = [
            Contact.user_id == user_id,
            or_(
                Contact.full_name.ilike(f'%{query}%'),
                Contact.telegram_username.ilike(f'%{query}%'),
                Contact.telegram_handle.ilike(f'%{query}%'),
                Contact.telegram_phone.ilike(f'%{query}%')
            )
        ]
        
        # 2. Execute query
        contacts = session.query(Contact).filter(
            and_(*search_conditions)
        ).limit(limit).all()
        
        # 3. Format results with highlighting
        results = []
        for contact in contacts:
            result = contact.to_dict()
            
            # Add search highlighting for frontend
            result['search_highlights'] = self._highlight_search_terms(
                contact.full_name, query
            )
            
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching contacts: {e}")
        return []
```

**Key Decision Points:**
- ✅ **Multiple field search** - Name, username, handle, phone
- ✅ **Case-insensitive** - Use `ilike()` for better UX
- ✅ **Wildcard matching** - `%query%` matches anywhere
- ✅ **Add highlighting** - Help frontend highlight matches

**Step 4: Search Notes Implementation**
```python
def _search_notes(self, session, query: str, user_id: int, limit: int) -> List[Dict[str, Any]]:
    """Search notes with snippet generation"""
    try:
        # 1. Search raw notes through contact relationship
        notes = session.query(RawNote).join(Contact).filter(
            Contact.user_id == user_id,
            RawNote.content.ilike(f'%{query}%')
        ).limit(limit).all()
        
        # 2. Format results with snippets
        results = []
        for note in notes:
            # Find search term position
            content_lower = note.content.lower()
            query_lower = query.lower()
            start_pos = content_lower.find(query_lower)
            
            # Generate snippet (50 chars before/after match)
            snippet_start = max(0, start_pos - 50)
            snippet_end = min(len(note.content), start_pos + len(query) + 50)
            snippet = note.content[snippet_start:snippet_end]
            
            # Add ellipsis if truncated
            if snippet_start > 0:
                snippet = '...' + snippet
            if snippet_end < len(note.content):
                snippet = snippet + '...'
            
            result = {
                'id': note.id,
                'content': note.content,
                'snippet': snippet,
                'offsets': {
                    'start': start_pos if start_pos >= 0 else 0,
                    'end': start_pos + len(query) if start_pos >= 0 else 0
                },
                'contact_name': note.contact.full_name if note.contact else 'Unknown',
                'contact_id': note.contact_id,
                'created_at': note.created_at.isoformat() if note.created_at else None,
                'search_highlights': self._highlight_search_terms(snippet, query)
            }
            
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        return []
```

**Key Decision Points:**
- ✅ **Snippet generation** - Show context around match
- ✅ **Offset tracking** - For frontend highlighting
- ✅ **Include contact info** - Link note to contact
- ✅ **Handle missing matches** - Graceful fallback

**Step 5: Search Highlighting**
```python
def _highlight_search_terms(self, text: str, query: str) -> List[Dict[str, Any]]:
    """Find all occurrences of query in text for highlighting"""
    try:
        if not text or not query:
            return []
        
        highlights = []
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Find all occurrences (case-insensitive)
        start = 0
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            
            highlights.append({
                'start': pos,
                'end': pos + len(query)
            })
            start = pos + 1  # Continue searching
        
        return highlights
        
    except Exception as e:
        logger.error(f"Error highlighting search terms: {e}")
        return []
```

#### Implementation Flow: Autocomplete Suggestions

**Step 1: API Endpoint**
```python
@search_bp.route('/suggestions', methods=['GET'])
@login_required
@inject
def get_suggestions(search_service: SearchService = Provide[Container.search_service]):
    """Get autocomplete suggestions"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query or len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = search_service.get_search_suggestions(
            query=query,
            user_id=current_user.id,
            limit=limit
        )
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({'suggestions': []}), 500
```

**Step 2: SearchService.get_search_suggestions()**
```python
def get_search_suggestions(self, query: str, user_id: int, limit: int = 10) -> List[str]:
    """Get search suggestions from contacts and tags"""
    try:
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        suggestions = []
        
        with self.db_manager.get_session() as session:
            # 1. Get contact name suggestions
            contacts = session.query(Contact.full_name).filter(
                Contact.user_id == user_id,
                Contact.full_name.ilike(f'%{query}%')
            ).limit(limit // 2).all()
            
            for contact in contacts:
                suggestions.append(contact.full_name)
            
            # 2. Get tag suggestions (prefixed with #)
            tags = session.query(Tag.name).filter(
                Tag.user_id == user_id,
                Tag.name.ilike(f'%{query}%')
            ).limit(limit // 2).all()
            
            for tag in tags:
                suggestions.append(f"#{tag.name}")  # Tag prefix
            
            # 3. Remove duplicates and limit
            suggestions = list(set(suggestions))[:limit]
            
            return suggestions
            
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return []
```

**Key Decision Points:**
- ✅ **Split between contacts and tags** - Balanced suggestions
- ✅ **Tag prefix (#)** - Visual distinction
- ✅ **Remove duplicates** - Clean results
- ✅ **Limit results** - Performance

#### Implementation Flow: Semantic Search (ChromaDB)

**Step 1: Enhanced Search with Semantic Search**
```python
def search_with_semantic(self, query: str, user_id: int, limit: int = 50) -> Dict[str, Any]:
    """Search with both keyword and semantic search"""
    try:
        # 1. Keyword search (existing implementation)
        keyword_results = self.search(query, user_id, scope='all', limit=limit)
        
        # 2. Semantic search via ChromaDB (if available)
        semantic_contact_ids = []
        try:
            from app.utils.chromadb_client import get_master_collection
            
            master_collection = get_master_collection(name="master_contacts")
            semantic_results = master_collection.query(
                query_texts=[query],
                n_results=limit,
                where={"user_id": user_id}  # Filter by user
            )
            
            if semantic_results['metadatas'] and len(semantic_results['metadatas'][0]) > 0:
                semantic_contact_ids = [
                    int(meta['contact_id']) 
                    for meta in semantic_results['metadatas'][0]
                ]
        except Exception as e:
            logger.debug(f"Semantic search unavailable: {e}")
        
        # 3. Combine and deduplicate results
        combined_contact_ids = set()
        
        # Add keyword results
        for contact in keyword_results['contacts']:
            combined_contact_ids.add(contact['id'])
        
        # Add semantic results
        combined_contact_ids.update(semantic_contact_ids)
        
        # 4. Fetch full contact details for combined IDs
        if combined_contact_ids:
            with self.db_manager.get_session() as session:
                contacts = session.query(Contact).filter(
                    Contact.id.in_(list(combined_contact_ids)),
                    Contact.user_id == user_id
                ).all()
                
                # Update results with combined list
                keyword_results['contacts'] = [
                    contact.to_dict() for contact in contacts
                ]
                keyword_results['total_results'] = len(keyword_results['contacts']) + len(keyword_results['notes'])
        
        return keyword_results
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return self.search(query, user_id, scope='all', limit=limit)  # Fallback to keyword
```

**Key Decision Points:**
- ✅ **Combine both methods** - Keyword + semantic
- ✅ **Deduplicate results** - Use set for unique IDs
- ✅ **Graceful fallback** - Continue if ChromaDB unavailable
- ✅ **User filtering** - Always filter by user_id

#### Data Flow Diagram: Search

```
User enters search query
    ↓
GET /api/search?q=query&scope=all
    ↓
SearchService.search()
    ├─ Validate query (min 2 chars)
    ├─ Search contacts (if scope includes contacts)
    │   ├─ Search name, username, handle, phone
    │   └─ Add highlighting
    ├─ Search notes (if scope includes notes)
    │   ├─ Search note content
    │   ├─ Generate snippets
    │   └─ Add highlighting
    └─ Combine results
    ↓
Save search query (for history)
    ↓
Return results with highlights
```

#### Integration Points

1. **Database**: Full-text search via SQL `ILIKE` (PostgreSQL) or `LIKE` (SQLite)
2. **ChromaDB**: Semantic search via master collection (optional enhancement)
3. **User Isolation**: Always filter by `user_id`
4. **Frontend**: Highlighting data structure for UI rendering

#### Common Patterns

**Pattern 1: Case-Insensitive Search**
```python
# Use ilike() for case-insensitive matching
Contact.full_name.ilike(f'%{query}%')
```

**Pattern 2: Multiple Field Search**
```python
# Search across multiple fields
or_(
    Contact.full_name.ilike(f'%{query}%'),
    Contact.telegram_username.ilike(f'%{query}%'),
    Contact.telegram_handle.ilike(f'%{query}%')
)
```

**Pattern 3: Snippet Generation**
```python
# Generate context snippet around match
start_pos = content.lower().find(query.lower())
snippet_start = max(0, start_pos - 50)
snippet_end = min(len(content), start_pos + len(query) + 50)
snippet = content[snippet_start:snippet_end]
```

### Testing Approach
- Test full-text search accuracy
- Test semantic search (if ChromaDB available)
- Test result ranking
- Test autocomplete suggestions
- Test search caching
- Test highlighting accuracy
- Test snippet generation
- Test empty query handling

---

## Feature 6: Relationship Graph

### Overview
Interactive network graph visualization showing relationships between contacts. Built with vis.js, supports filtering, node selection, and relationship management.

### User-Facing Pages
- **Relationship Graph View** (tab in SPA)
  - Interactive graph canvas
  - Node (contact) selection
  - Edge (relationship) display
  - Filter controls
  - Zoom/pan controls

- **Manage Graph View** (separate tab)
  - Add/remove relationships
  - Edit relationship types
  - Graph layout controls

### API Endpoints

**`GET /api/graph`**
- Get graph data (nodes and edges)
- Query params: `tier` (optional filter)
- Response: `{ "nodes": [...], "edges": [...] }`

**`POST /api/graph/relationships`**
- Create relationship between contacts
- Request: `{ "contact1_id": int, "contact2_id": int, "relationship_type": string }`

**`DELETE /api/graph/relationships/<id>`**
- Remove relationship

### Database Models

**Relationship Model** (if separate table, or stored in Contact.custom_fields)
```python
# Relationships can be stored in Contact.custom_fields as JSON
# Or in a separate relationships table
```

### Services

**GraphService** (or part of ContactService)
- `get_graph_data(user_id, tier_filter=None)` - Build nodes and edges
- `create_relationship(contact1_id, contact2_id, type, user_id)` - Add relationship
- `remove_relationship(relationship_id, user_id)` - Delete relationship

### Frontend Implementation

**Graph Visualization** (`static/js/relationship-graph.js`)
- Initialize vis.js network
- Load graph data from API
- Handle node clicks (show contact details)
- Handle edge clicks (show relationship info)
- Filter by tier
- Layout algorithms (force-directed, hierarchical)

### High-Level Implementation

#### Implementation Flow: Generate Graph Data

**Step 1: API Endpoint** (`app/api/graph.py`)
```python
@graph_bp.route('/graph-data', methods=['GET'])
@login_required
def get_graph_data():
    """Fetch and format graph data (nodes and edges)"""
    user_id = current_user.id
    tier_filter = request.args.get('tier', type=int)  # Optional tier filter
    dm = DatabaseManager()
    
    try:
        with dm.get_session() as session:
            # 1. Fetch all contacts (nodes)
            query = session.query(Contact).options(
                selectinload(Contact.tags)  # Eager load tags
            ).filter_by(user_id=user_id)
            
            # Apply tier filter if provided
            if tier_filter:
                query = query.filter_by(tier=tier_filter)
            
            contacts = query.all()
            
            # 2. Build nodes dictionary
            nodes_dict = {}
            for contact in contacts:
                # Calculate node size based on interaction count
                interaction_count = session.query(SynthesizedEntry).filter_by(
                    contact_id=contact.id
                ).count()
                
                nodes_dict[contact.id] = {
                    "id": contact.id,
                    "label": contact.full_name,
                    "group": None,  # Will be set by group membership
                    "tier": contact.tier,
                    "value": 10 + interaction_count,  # Node size
                    "title": f"{contact.full_name} (Tier {contact.tier})"  # Tooltip
                }
            
            # 3. Fetch group memberships and assign groups
            memberships = session.query(ContactGroupMembership).join(Contact).filter(
                Contact.user_id == user_id
            ).all()
            
            for member in memberships:
                if member.contact_id in nodes_dict:
                    nodes_dict[member.contact_id]['group'] = member.group_id
            
            # 4. Fetch relationships (edges)
            relationships = session.query(ContactRelationship).filter_by(
                user_id=user_id
            ).all()
            
            edges = []
            for rel in relationships:
                # Only include edges if both nodes exist
                if rel.source_contact_id in nodes_dict and rel.target_contact_id in nodes_dict:
                    edges.append({
                        "from": rel.source_contact_id,
                        "to": rel.target_contact_id,
                        "label": rel.label or "",
                        "arrows": "to",  # Directed edge
                        "length": 150  # Edge length
                    })
            
            # 5. Fetch group definitions for styling
            groups_db = session.query(ContactGroup).filter_by(user_id=user_id).all()
            group_definitions = {
                group.id: {
                    "color": group.color,
                    "name": group.name
                } for group in groups_db
            }
            
            # 6. Add "self" node (user)
            nodes_dict[0] = {
                "id": 0,
                "label": "You",
                "group": "self",
                "fixed": True,  # Fixed position
                "value": 40,  # Larger node
                "title": "You"
            }
            group_definitions["self"] = {
                "color": "#FF6384",
                "name": "Self"
            }
            
            # 7. Add edges from "You" to Tier 1 contacts
            for contact in contacts:
                if contact.tier == 1:
                    edges.append({
                        "from": 0,
                        "to": contact.id,
                        "length": 150,  # Shorter for closer contacts
                        "label": "Close"
                    })
            
            return jsonify({
                "nodes": list(nodes_dict.values()),
                "edges": edges,
                "groups": group_definitions
            })
            
    except Exception as e:
        logger.exception("Failed to fetch graph data")
        return jsonify({"error": f"Failed to fetch graph data: {e}"}), 500
```

**Key Decision Points:**
- ✅ **Eager load tags** - Prevent N+1 queries
- ✅ **Node size by interactions** - Visual importance
- ✅ **Tier-based edges** - Connect user to Tier 1 contacts
- ✅ **Group styling** - Color-coded groups
- ✅ **Filter by tier** - Optional filtering

**Step 2: Create Relationship**
```python
@graph_bp.route('/relationships', methods=['POST'])
@login_required
def create_relationship():
    """Create a relationship between two contacts"""
    try:
        data = request.get_json()
        source_id = data.get('source_contact_id')
        target_id = data.get('target_contact_id')
        label = data.get('label', '').strip()
        relationship_type = data.get('relationship_type', 'connection')
        
        if not source_id or not target_id:
            return jsonify({'error': 'source_contact_id and target_contact_id required'}), 400
        
        if source_id == target_id:
            return jsonify({'error': 'Cannot create relationship to self'}), 400
        
        dm = DatabaseManager()
        with dm.get_session() as session:
            # 1. Verify both contacts exist and belong to user
            source = session.query(Contact).filter(
                Contact.id == source_id,
                Contact.user_id == current_user.id
            ).first()
            
            target = session.query(Contact).filter(
                Contact.id == target_id,
                Contact.user_id == current_user.id
            ).first()
            
            if not source or not target:
                return jsonify({'error': 'One or both contacts not found'}), 404
            
            # 2. Check if relationship already exists
            existing = session.query(ContactRelationship).filter(
                ContactRelationship.user_id == current_user.id,
                ContactRelationship.source_contact_id == source_id,
                ContactRelationship.target_contact_id == target_id
            ).first()
            
            if existing:
                return jsonify({'error': 'Relationship already exists'}), 409
            
            # 3. Create relationship
            relationship = ContactRelationship(
                user_id=current_user.id,
                source_contact_id=source_id,
                target_contact_id=target_id,
                label=label or relationship_type,
                relationship_type=relationship_type
            )
            
            session.add(relationship)
            session.commit()
            
            logger.info(f"Created relationship: {source.full_name} -> {target.full_name}")
            
            return jsonify({
                'success': True,
                'relationship': {
                    'id': relationship.id,
                    'from': source_id,
                    'to': target_id,
                    'label': relationship.label
                }
            }), 201
            
    except IntegrityError as e:
        logger.error(f"Integrity error creating relationship: {e}")
        return jsonify({'error': 'Failed to create relationship'}), 500
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        return jsonify({'error': 'Failed to create relationship'}), 500
```

**Key Decision Points:**
- ✅ **Prevent self-relationships** - Validate source != target
- ✅ **Check for duplicates** - Avoid duplicate edges
- ✅ **Verify ownership** - Both contacts must belong to user
- ✅ **Return 409 for conflicts** - Standard HTTP status

**Step 3: Delete Relationship**
```python
@graph_bp.route('/relationships/<int:relationship_id>', methods=['DELETE'])
@login_required
def delete_relationship(relationship_id: int):
    """Delete a relationship"""
    try:
        dm = DatabaseManager()
        with dm.get_session() as session:
            # 1. Verify relationship exists and belongs to user
            relationship = session.query(ContactRelationship).filter(
                ContactRelationship.id == relationship_id,
                ContactRelationship.user_id == current_user.id
            ).first()
            
            if not relationship:
                return jsonify({'error': 'Relationship not found'}), 404
            
            # 2. Delete relationship
            session.delete(relationship)
            session.commit()
            
            logger.info(f"Deleted relationship {relationship_id}")
            
            return jsonify({
                'success': True,
                'message': 'Relationship deleted'
            }), 200
            
    except Exception as e:
        logger.error(f"Error deleting relationship: {e}")
        return jsonify({'error': 'Failed to delete relationship'}), 500
```

#### Implementation Flow: Frontend Graph Visualization

**Step 1: Initialize vis.js Network** (`static/js/relationship-graph.js`)
```javascript
let network = null;
let graphData = { nodes: [], edges: [] };

async function initializeGraphView() {
    try {
        // 1. Get graph container
        const container = document.getElementById('graph-container');
        if (!container) {
            console.error('Graph container not found');
            return;
        }
        
        // 2. Fetch graph data from API
        const response = await fetch('/api/graph/graph-data', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to load graph data');
        }
        
        const data = await response.json();
        
        // 3. Prepare nodes and edges for vis.js
        const nodes = new vis.DataSet(data.nodes.map(node => ({
            id: node.id,
            label: node.label,
            group: node.group || 'default',
            value: node.value || 10,
            title: node.title || node.label,
            fixed: node.fixed || false
        })));
        
        const edges = new vis.DataSet(data.edges.map(edge => ({
            from: edge.from,
            to: edge.to,
            label: edge.label || '',
            arrows: edge.arrows || 'to',
            length: edge.length || 200
        })));
        
        graphData = { nodes, edges };
        
        // 4. Configure network options
        const options = {
            nodes: {
                shape: 'dot',
                font: { size: 14 },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                enabled: true,
                stabilization: {
                    iterations: 200
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true
            }
        };
        
        // 5. Create network
        network = new vis.Network(container, graphData, options);
        
        // 6. Add event listeners
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                if (nodeId !== 0) {  // Not the "You" node
                    showContactDetails(nodeId);
                }
            }
        });
        
        network.on('hoverNode', function(params) {
            container.style.cursor = 'pointer';
        });
        
        network.on('blurNode', function(params) {
            container.style.cursor = 'default';
        });
        
    } catch (error) {
        console.error('Error initializing graph:', error);
        showError('Failed to load relationship graph');
    }
}
```

**Step 2: Filter Graph by Tier**
```javascript
function filterGraphByTier(tier) {
    // Reload graph data with tier filter
    const url = tier ? `/api/graph/graph-data?tier=${tier}` : '/api/graph/graph-data';
    
    fetch(url, { credentials: 'include' })
        .then(response => response.json())
        .then(data => {
            // Update graph data
            graphData.nodes.clear();
            graphData.edges.clear();
            
            graphData.nodes.add(data.nodes);
            graphData.edges.add(data.edges);
            
            // Re-stabilize network
            network.stabilize();
        })
        .catch(error => {
            console.error('Error filtering graph:', error);
        });
}
```

**Step 3: Create Relationship from UI**
```javascript
async function createRelationship(sourceId, targetId, label) {
    try {
        const response = await fetch('/api/graph/relationships', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                source_contact_id: sourceId,
                target_contact_id: targetId,
                label: label || 'connection'
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Add edge to graph
            graphData.edges.add({
                from: sourceId,
                to: targetId,
                label: label,
                arrows: 'to'
            });
            
            showSuccess('Relationship created successfully');
        } else {
            showError(data.error || 'Failed to create relationship');
        }
        
    } catch (error) {
        console.error('Error creating relationship:', error);
        showError('Failed to create relationship');
    }
}
```

#### Data Flow Diagram: Graph Generation

```
User requests graph data
    ↓
GET /api/graph/graph-data
    ↓
Fetch contacts (nodes)
    ├─ Load tags (eager loading)
    ├─ Calculate interaction count
    └─ Build node objects
    ↓
Fetch relationships (edges)
    ├─ Verify both nodes exist
    └─ Build edge objects
    ↓
Fetch group definitions
    └─ For styling
    ↓
Add "You" node and Tier 1 edges
    ↓
Return nodes, edges, groups
    ↓
Frontend: Initialize vis.js network
    ├─ Create DataSets
    ├─ Configure options
    └─ Render graph
```

#### Integration Points

1. **Database**: Uses `ContactRelationship` model for edges
2. **vis.js**: Frontend visualization library
3. **User Isolation**: Always filter by `user_id`
4. **Eager Loading**: `selectinload()` prevents N+1 queries

#### Common Patterns

**Pattern 1: Eager Load Relationships**
```python
# Prevent N+1 queries
contacts = session.query(Contact).options(
    selectinload(Contact.tags)
).filter_by(user_id=user_id).all()
```

**Pattern 2: Calculate Node Size**
```python
# Node size based on data richness
interaction_count = session.query(SynthesizedEntry).filter_by(
    contact_id=contact.id
).count()
value = 10 + interaction_count  # Base size + interactions
```

**Pattern 3: Validate Both Contacts**
```python
# Always verify both contacts exist and belong to user
source = session.query(Contact).filter(
    Contact.id == source_id,
    Contact.user_id == user_id
).first()

target = session.query(Contact).filter(
    Contact.id == target_id,
    Contact.user_id == user_id
).first()

if not source or not target:
    return error
```

### Testing Approach
- Test graph data generation
- Test relationship creation/deletion
- Test graph filtering by tier
- Test node/edge interactions
- Test "You" node and Tier 1 connections
- Test group assignments
- Test frontend graph rendering
- Test relationship validation (self-relationships, duplicates)

---

## Feature 7: Telegram Integration

### Overview
Import and sync contacts and conversations from Telegram. Uses Telethon library, supports async operations, and can process chat history automatically.

### User-Facing Pages
- **Telegram Settings** (Settings view)
  - Connection status
  - Sync button
  - Import history button
  - Sync status display

### API Endpoints

**`GET /api/telegram/contacts`**
- Get Telegram contacts (enhanced)
- Response: `[{ "telegram_id": string, "username": string, ... }]`

**`POST /api/telegram/sync-contact-history`**
- Sync chat history for a contact
- Request: `{ "contact_id": int, "telegram_handle": string }`
- Response: `{ "task_id": string, "status": "pending" }`

**`POST /api/telegram/sync-all-history`**
- Sync all contacts' history
- Response: `{ "task_id": string }`

**`GET /api/telegram/sync-status/<task_id>`**
- Get sync task status
- Response: `{ "status": string, "progress": int, "contacts_synced": int }`

### Services

**TelegramService** (`app/services/telegram_service.py`)
- `connect()` - Establish Telegram session
- `get_contacts()` - Fetch Telegram contacts
- `sync_contact_history(contact_id, telegram_handle)` - Import chat history
- `process_chat_messages(messages)` - Convert to notes

### Celery Tasks

**Telegram Tasks** (`app/tasks/telegram_tasks.py`)
```python
@celery_app.task(bind=True)
def sync_telegram_history_async(self, contact_id, telegram_handle, user_id):
    # Long-running Telegram sync
    # Updates progress
    # Creates notes from messages
```

### Frontend Implementation

**Telegram Integration** (`static/js/telegram-enhanced.js`)
- Connection status display
- Sync button handlers
- Progress polling for async tasks
- Contact matching UI

### High-Level Implementation

#### Implementation Flow: Connect to Telegram

**Step 1: Enhanced Telegram Integration Service** (`app/services/enhanced_telegram_integration.py`)
```python
class EnhancedTelegramIntegration:
    """
    Enhanced Telegram integration with hybrid session management.
    Handles authentication, session persistence, and sync operations.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_manager = HybridTelegramSession(user_id)
        self.client = None
        
        if not self.api_id or not self.api_hash:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
    
    async def connect(self) -> bool:
        """Connect to Telegram with automatic session restoration"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Telegram for user {self.user_id} (attempt {attempt + 1}/{max_retries})")
                
                # 1. Try to restore existing session
                session_data = await self.session_manager.restore_session()
                
                if session_data:
                    logger.info(f"Restoring existing session for user {self.user_id}")
                    try:
                        # Use stored session file name
                        saved_session_name = session_data.get('session_name')
                        if saved_session_name:
                            self.client = TelegramClient(
                                saved_session_name, 
                                self.api_id, 
                                self.api_hash
                            )
                        else:
                            # Fallback: create new session
                            session_name = f"kith_telegram_{self.user_id}_{int(datetime.now().timestamp())}"
                            self.client = TelegramClient(session_name, self.api_id, self.api_hash)
                        
                        # Connect without prompts
                        await self.client.connect()
                        
                        # 2. Verify session is still valid
                        if await self._verify_session():
                            logger.info(f"Successfully restored session for user {self.user_id}")
                            return True
                        else:
                            logger.warning(f"Restored session is invalid")
                            await self.client.disconnect()
                            self.client = None
                    except Exception as e:
                        logger.warning(f"Failed to restore session: {e}")
                        if self.client:
                            await self.client.disconnect()
                            self.client = None
                
                # 3. Fallback: Try working session file
                logger.info(f"Trying fallback session file")
                try:
                    fallback_session_name = "kith_telegram_session"
                    await asyncio.sleep(0.5)  # Prevent race conditions
                    
                    self.client = TelegramClient(fallback_session_name, self.api_id, self.api_hash)
                    await self.client.connect()
                    
                    if await self._verify_session():
                        logger.info(f"Successfully connected using fallback session")
                        return True
                    else:
                        await self.client.disconnect()
                        self.client = None
                except Exception as e:
                    logger.warning(f"Failed to use fallback session: {e}")
                    if self.client:
                        await self.client.disconnect()
                        self.client = None
                
                # 4. If no valid session, need authentication
                logger.info(f"Starting new authentication")
                return await self._authenticate_new_session()
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'database is locked' in error_msg and attempt < max_retries - 1:
                    logger.warning(f"Database locked, retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"Failed to connect to Telegram: {e}")
                    return False
        
        return False
    
    async def _verify_session(self) -> bool:
        """Verify that the current session is valid"""
        try:
            if not self.client:
                return False
            
            # Try to get current user info
            me = await self.client.get_me()
            return me is not None
        except Exception as e:
            logger.warning(f"Session verification failed: {e}")
            return False
```

**Key Decision Points:**
- ✅ **Session restoration first** - Try to reuse existing session
- ✅ **Fallback session** - Use known working session file
- ✅ **Session verification** - Check if session is still valid
- ✅ **Retry logic** - Handle database locks and transient errors
- ✅ **Non-interactive** - Don't trigger prompts in API context

#### Implementation Flow: Get Telegram Contacts

**Step 1: Get Contacts Implementation**
```python
async def get_contacts(self) -> List[Dict[str, Any]]:
    """Get Telegram contacts from dialogs"""
    if not self.client:
        if not await self.connect():
            return []
    
    try:
        contacts = []
        async for dialog in self.client.iter_dialogs():
            # Only include User entities (not bots, groups, channels)
            if isinstance(dialog.entity, User) and not dialog.entity.bot:
                contact = {
                    'id': dialog.entity.id,
                    'first_name': dialog.entity.first_name or '',
                    'last_name': dialog.entity.last_name or '',
                    'username': dialog.entity.username or '',
                    'phone': dialog.entity.phone or '',
                    'is_verified': dialog.entity.verified or False,
                    'is_premium': dialog.entity.premium or False,
                    'last_seen': dialog.entity.status.__class__.__name__ if dialog.entity.status else 'Unknown',
                    'full_name': f"{dialog.entity.first_name or ''} {dialog.entity.last_name or ''}".strip()
                }
                contacts.append(contact)
        
        logger.info(f"Retrieved {len(contacts)} contacts for user {self.user_id}")
        return contacts
        
    except Exception as e:
        logger.error(f"Failed to get contacts: {e}")
        return []
```

**Key Decision Points:**
- ✅ **Filter bots** - Only include real users
- ✅ **Extract all fields** - Username, phone, verification status
- ✅ **Handle missing fields** - Use empty strings for None values
- ✅ **Async iteration** - Efficient for large contact lists

**Step 2: API Endpoint** (`app/api/telegram_enhanced.py`)
```python
@telegram_enhanced_bp.route('/contacts', methods=['GET'])
@login_required
@async_route
async def get_enhanced_contacts():
    """Get Telegram contacts with enhanced session management"""
    try:
        user_id = str(current_user.id)  # Convert to string for session manager
        integration = EnhancedTelegramIntegration(user_id)
        
        contacts = await integration.get_contacts()
        
        return jsonify({
            'success': True,
            'contacts': contacts,
            'count': len(contacts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get contacts: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get contacts: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500
```

**Key Decision Points:**
- ✅ **Use @async_route decorator** - Handle async functions in Flask
- ✅ **Convert user_id to string** - Session manager expects string
- ✅ **Return timestamp** - For cache invalidation
- ✅ **Comprehensive error handling** - Never expose internal errors

#### Implementation Flow: Sync Contact History

**Step 1: Sync Contact History Implementation**
```python
async def sync_contact_history(
    self, 
    contact_identifier: str, 
    days_back: int = 30,
    last_sync_id: Optional[int] = None,
    incremental: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Sync chat history for a specific contact.
    
    Supports incremental sync to only fetch messages since last_sync_id,
    saving massive API overhead for frequent syncs.
    
    Args:
        contact_identifier: Username, phone, or display name
        days_back: Fallback time window if incremental sync not available
        last_sync_id: Last message ID from previous sync (for incremental)
        incremental: If True, use last_sync_id; if False, use days_back
    
    Returns:
        Conversation dict with messages, or None if contact not found
    """
    if not self.client:
        if not await self.connect():
            return None
    
    try:
        ident_clean = (contact_identifier or '').strip()
        logger.info(f"[SyncContact] Resolving identifier: {ident_clean}, incremental={incremental}, last_sync_id={last_sync_id}")
        
        # 1. Resolve entity by username or phone
        entity = None
        try:
            # Try raw identifier
            entity = await self.client.get_entity(ident_clean)
            if not isinstance(entity, User):
                entity = None
            
            # Try with leading @ for usernames
            if entity is None and ident_clean and not ident_clean.startswith('+') and not ident_clean.isdigit():
                entity = await self.client.get_entity('@' + ident_clean)
        except Exception:
            entity = None
        
        # 2. Fallback: scan dialogs to match username/phone case-insensitively
        if entity is None:
            async for dialog in self.client.iter_dialogs():
                if isinstance(dialog.entity, User):
                    uname = (dialog.entity.username or '').lower()
                    phone = (dialog.entity.phone or '').lower()
                    first = (dialog.entity.first_name or '').lower()
                    last = (dialog.entity.last_name or '').lower()
                    display = f"{first} {last}".strip()
                    ident = ident_clean.replace('@', '').lower()
                    
                    # Match by username or phone
                    if ident and (ident == uname or ident == phone):
                        entity = dialog.entity
                        break
                    
                    # Match by display name (contains)
                    if ident and ident in display:
                        entity = dialog.entity
                        break
        
        if not isinstance(entity, User):
            logger.warning(f"Could not resolve entity for {ident_clean}")
            return None
        
        # 3. Build conversation from messages
        conversation = {
            'contact_id': entity.id,
            'contact_name': f"{entity.first_name or ''} {entity.last_name or ''}".strip(),
            'username': entity.username or '',
            'phone': entity.phone or '',
            'messages': [],
            'last_sync_id': None,  # Will be set to latest message ID
            'sync_type': 'incremental' if incremental and last_sync_id else 'full'
        }
        
        # 4. INCREMENTAL SYNC: Fetch only messages since last_sync_id
        if incremental and last_sync_id:
            logger.info(f"[SyncContact] Incremental sync: fetching messages after ID {last_sync_id}")
            message_count = 0
            max_id = None  # Start from most recent
            
            async for message in self.client.iter_messages(
                entity,
                min_id=last_sync_id,  # Only messages after last_sync_id
                reverse=False  # Get newest first
            ):
                if message.text and message.id > last_sync_id:
                    conversation['messages'].append({
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'sender': 'Me' if message.out else conversation['contact_name'],
                        'text': message.text,
                        'outgoing': message.out
                    })
                    message_count += 1
                    max_id = max(max_id or 0, message.id)
                    
                    # Limit to prevent memory issues
                    if message_count >= 1000:
                        break
            
            conversation['last_sync_id'] = max_id or last_sync_id
            logger.info(f"[SyncContact] Incremental sync: fetched {len(conversation['messages'])} new messages")
        
        # 5. FALLBACK: Full sync using days_back (if incremental not available or no last_sync_id)
        else:
            logger.info(f"[SyncContact] Full sync: fetching messages from last {days_back} days")
            since_date = datetime.now() - timedelta(days=days_back)
            message_count = 0
            max_id = None
            
            async for message in self.client.iter_messages(
                entity, 
                offset_date=since_date, 
                reverse=True
            ):
                if message.text:
                    conversation['messages'].append({
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'sender': 'Me' if message.out else conversation['contact_name'],
                        'text': message.text,
                        'outgoing': message.out
                    })
                    message_count += 1
                    max_id = max(max_id or 0, message.id)
                    
                    # Limit to prevent memory issues
                    if message_count >= 1000:
                        break
            
            # 6. Fallback: if no messages in date range, fetch deeper history
            if not conversation['messages']:
                async for message in self.client.iter_messages(entity, limit=2000, reverse=True):
                    if message.text:
                        conversation['messages'].append({
                            'id': message.id,
                            'date': message.date.isoformat(),
                            'sender': 'Me' if message.out else conversation['contact_name'],
                            'text': message.text,
                            'outgoing': message.out
                        })
                        max_id = max(max_id or 0, message.id)
                        if len(conversation['messages']) >= 2000:
                            break
            
            conversation['last_sync_id'] = max_id
        
        if conversation['messages']:
            logger.info(f"Synced {len(conversation['messages'])} messages for contact {ident_clean} (type: {conversation['sync_type']})")
            return conversation
        
        logger.info(f"No messages found for {ident_clean}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to sync contact history: {e}")
        return None
```

**Key Decision Points:**
- ✅ **Multiple resolution strategies** - Username, phone, display name
- ✅ **Case-insensitive matching** - Better user experience
- ✅ **Date-bounded fetch** - Efficient, only recent messages
- ✅ **Fallback to deeper history** - If no recent messages
- ✅ **Message limit** - Prevent memory issues (1000-2000 messages)

**Step 2: API Endpoint for Sync**
```python
@telegram_enhanced_bp.route('/sync-contact-history', methods=['POST'])
@login_required
@async_route
async def sync_contact_history():
    """Sync chat history for a specific contact"""
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        telegram_handle = data.get('telegram_handle') or data.get('identifier')
        days_back = data.get('days_back', 30)
        
        if not telegram_handle:
            return jsonify({
                'success': False,
                'message': 'telegram_handle or identifier is required'
            }), 400
        
        user_id = str(current_user.id)
        integration = EnhancedTelegramIntegration(user_id)
        
        # Sync history
        conversation = await integration.sync_contact_history(telegram_handle, days_back)
        
        if conversation:
            # Store last_sync_id for next incremental sync
            if conversation.get('last_sync_id'):
                from app.utils.database import DatabaseManager
                from app.models import Contact
                
                db_manager = DatabaseManager()
                with db_manager.get_session() as session:
                    contact = session.query(Contact).filter(
                        Contact.user_id == current_user.id,
                        (Contact.telegram_username == telegram_handle) |
                        (Contact.telegram_handle == telegram_handle)
                    ).first()
                    
                    if contact:
                        # Store last_sync_id in metadata for next sync
                        if not contact.telegram_metadata:
                            contact.telegram_metadata = {}
                        contact.telegram_metadata['last_sync_id'] = conversation['last_sync_id']
                        contact.telegram_last_sync = datetime.utcnow()
                        session.commit()
            
            # Process messages into notes (async task)
            task = process_telegram_messages_async.delay(
                user_id=current_user.id,
                contact_id=contact_id,
                conversation=conversation
            )
            
            return jsonify({
                'success': True,
                'task_id': task.id,
                'message': f'Synced {len(conversation["messages"])} messages',
                'sync_type': conversation.get('sync_type', 'full'),
                'last_sync_id': conversation.get('last_sync_id'),
                'status': 'processing'
            }), 202
        else:
            return jsonify({
                'success': False,
                'message': 'No messages found or contact not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Failed to sync contact history: {e}")
        return jsonify({
            'success': False,
            'message': f'Sync failed: {str(e)}'
        }), 500
```

#### Implementation Flow: Process Messages into Notes

**Step 1: Celery Task for Message Processing** (`app/tasks/telegram_tasks.py`)
```python
@celery_app.task(bind=True)
def process_telegram_messages_async(self, user_id: int, contact_id: int, conversation: Dict[str, Any]):
    """Process Telegram messages and create notes"""
    try:
        from app.services.note_service import NoteService
        from app.services.ai_service import AIService
        from app.utils.database import DatabaseManager
        
        # 1. Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Processing messages...', 'progress': 0}
        )
        
        # 2. Initialize services
        db_manager = DatabaseManager()
        ai_service = AIService()
        note_service = NoteService(db_manager, ai_service)
        
        messages = conversation.get('messages', [])
        total_messages = len(messages)
        processed = 0
        notes_created = 0
        
        # 3. Process messages in batches
        batch_size = 10  # Process 10 messages at a time
        for i in range(0, total_messages, batch_size):
            batch = messages[i:i + batch_size]
            
            # Combine batch into single note
            note_text = "\n".join([
                f"[{msg['date']}] {msg['sender']}: {msg['text']}"
                for msg in batch
            ])
            
            # 4. Process note with AI analysis
            try:
                result = note_service.process_note(
                    contact_id=contact_id,
                    content=note_text,
                    user_id=user_id
                )
                
                if result.get('success'):
                    notes_created += 1
                    processed += len(batch)
                    
                    # Update progress
                    progress = int((processed / total_messages) * 100)
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'status': f'Processed {processed}/{total_messages} messages',
                            'progress': progress,
                            'notes_created': notes_created
                        }
                    )
            except Exception as e:
                logger.error(f"Error processing message batch: {e}")
                # Continue with next batch
                processed += len(batch)
        
        # 5. Final state update
        self.update_state(
            state='SUCCESS',
            meta={
                'status': f'Processed {processed} messages, created {notes_created} notes',
                'messages_processed': processed,
                'notes_created': notes_created
            }
        )
        
        return {
            'messages_processed': processed,
            'notes_created': notes_created
        }
        
    except Exception as e:
        logger.error(f"Error processing Telegram messages: {e}")
        self.update_state(
            state='FAILURE',
            meta={'status': 'Failed to process messages', 'error': str(e)}
        )
        raise
```

**Key Decision Points:**
- ✅ **Batch processing** - Combine multiple messages into single note
- ✅ **Progress tracking** - Update state for each batch
- ✅ **Continue on error** - Don't stop on single batch failure
- ✅ **Format messages** - Include timestamp and sender
- ✅ **AI analysis** - Process notes through AI pipeline

#### Implementation Flow: Sync All Contacts

**Step 1: Sync All Contacts Implementation**
```python
@telegram_enhanced_bp.route('/sync-all-history', methods=['POST'])
@login_required
@async_route
async def sync_all_history():
    """Sync chat history for all contacts"""
    try:
        data = request.get_json() or {}
        days_back = data.get('days_back', 30)
        
        user_id = str(current_user.id)
        integration = EnhancedTelegramIntegration(user_id)
        
        # 1. Get all contacts
        contacts = await integration.get_contacts()
        
        if not contacts:
            return jsonify({
                'success': False,
                'message': 'No contacts found'
            }), 404
        
        # 2. Start async task for batch sync
        task = sync_all_telegram_history_async.delay(
            user_id=current_user.id,
            contact_identifiers=[c.get('username') or c.get('phone') for c in contacts],
            days_back=days_back
        )
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'contacts_count': len(contacts),
            'status': 'queued'
        }), 202
        
    except Exception as e:
        logger.error(f"Failed to start sync: {e}")
        return jsonify({
            'success': False,
            'message': f'Sync failed: {str(e)}'
        }), 500
```

**Step 2: Celery Task for Batch Sync**
```python
@celery_app.task(bind=True)
def sync_all_telegram_history_async(self, user_id: int, contact_identifiers: List[str], days_back: int = 30):
    """Sync history for all contacts"""
    try:
        from app.services.enhanced_telegram_integration import EnhancedTelegramIntegration
        
        integration = EnhancedTelegramIntegration(str(user_id))
        
        # Connect
        if not await integration.connect():
            self.update_state(
                state='FAILURE',
                meta={'status': 'Failed to connect to Telegram'}
            )
            return
        
        total_contacts = len(contact_identifiers)
        synced = 0
        failed = 0
        
        # Process each contact
        for i, identifier in enumerate(contact_identifiers):
            if not identifier:
                continue
            
            try:
                # Update progress
                progress = int((i / total_contacts) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Syncing contact {i+1}/{total_contacts}: {identifier}',
                        'progress': progress,
                        'synced': synced,
                        'failed': failed
                    }
                )
                
                # Sync contact history
                conversation = await integration.sync_contact_history(identifier, days_back)
                
                if conversation:
                    # Process messages
                    process_telegram_messages_async.delay(
                        user_id=user_id,
                        contact_id=None,  # Will need to match by identifier
                        conversation=conversation
                    )
                    synced += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error syncing {identifier}: {e}")
                failed += 1
        
        # Final state
        self.update_state(
            state='SUCCESS',
            meta={
                'status': f'Synced {synced}/{total_contacts} contacts',
                'synced': synced,
                'failed': failed
            }
        )
        
        return {
            'synced': synced,
            'failed': failed,
            'total': total_contacts
        }
        
    except Exception as e:
        logger.error(f"Error in batch sync: {e}")
        self.update_state(
            state='FAILURE',
            meta={'status': 'Batch sync failed', 'error': str(e)}
        )
        raise
```

**Key Decision Points:**
- ✅ **Batch processing** - Process all contacts sequentially
- ✅ **Progress tracking** - Update for each contact
- ✅ **Continue on error** - Don't stop on single failure
- ✅ **Async message processing** - Offload to separate tasks
- ✅ **Error counting** - Track successes and failures

#### Implementation Flow: Match Telegram Contacts to Kith Contacts

**Step 1: Contact Matching Service**
```python
def match_telegram_to_kith_contact(
    telegram_contact: Dict[str, Any],
    user_id: int,
    session
) -> Optional[Contact]:
    """Match Telegram contact to existing Kith contact"""
    try:
        # 1. Try to match by Telegram ID
        if telegram_contact.get('id'):
            contact = session.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.telegram_id == str(telegram_contact['id'])
            ).first()
            if contact:
                return contact
        
        # 2. Try to match by username
        if telegram_contact.get('username'):
            contact = session.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.telegram_username == telegram_contact['username']
            ).first()
            if contact:
                return contact
        
        # 3. Try to match by phone
        if telegram_contact.get('phone'):
            contact = session.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.telegram_phone == telegram_contact['phone']
            ).first()
            if contact:
                return contact
        
        # 4. Try to match by name (fuzzy)
        if telegram_contact.get('full_name'):
            full_name = telegram_contact['full_name'].strip()
            contact = session.query(Contact).filter(
                Contact.user_id == user_id,
                func.lower(Contact.full_name) == func.lower(full_name)
            ).first()
            if contact:
                return contact
        
        # 5. No match found
        return None
        
    except Exception as e:
        logger.error(f"Error matching contact: {e}")
        return None
```

**Step 2: Import or Update Contact**
```python
def import_or_update_telegram_contact(
    telegram_contact: Dict[str, Any],
    user_id: int,
    session
) -> Contact:
    """Import Telegram contact or update existing"""
    try:
        # 1. Try to find existing contact
        contact = match_telegram_to_kith_contact(telegram_contact, user_id, session)
        
        if contact:
            # 2. Update existing contact
            contact.telegram_id = str(telegram_contact.get('id', ''))
            contact.telegram_username = telegram_contact.get('username')
            contact.telegram_phone = telegram_contact.get('phone')
            contact.telegram_handle = telegram_contact.get('username')
            contact.is_verified = telegram_contact.get('is_verified', False)
            contact.is_premium = telegram_contact.get('is_premium', False)
            contact.telegram_last_sync = datetime.utcnow()
            
            logger.info(f"Updated contact {contact.id} with Telegram data")
        else:
            # 3. Create new contact
            contact = Contact(
                user_id=user_id,
                full_name=telegram_contact.get('full_name', 'Unknown'),
                telegram_id=str(telegram_contact.get('id', '')),
                telegram_username=telegram_contact.get('username'),
                telegram_phone=telegram_contact.get('phone'),
                telegram_handle=telegram_contact.get('username'),
                is_verified=telegram_contact.get('is_verified', False),
                is_premium=telegram_contact.get('is_premium', False),
                telegram_last_sync=datetime.utcnow(),
                tier=2  # Default tier
            )
            session.add(contact)
            logger.info(f"Created new contact from Telegram: {contact.full_name}")
        
        session.flush()
        return contact
        
    except Exception as e:
        logger.error(f"Error importing/updating contact: {e}")
        session.rollback()
        raise
```

**Key Decision Points:**
- ✅ **Multiple matching strategies** - ID, username, phone, name
- ✅ **Update existing** - Don't create duplicates
- ✅ **Fuzzy name matching** - Case-insensitive
- ✅ **Update sync timestamp** - Track last sync time

#### Data Flow Diagram: Telegram Sync

```
User initiates sync
    ↓
POST /api/telegram/sync-contact-history
    ↓
EnhancedTelegramIntegration.connect()
    ├─ Restore session
    ├─ Verify session
    └─ Fallback to authentication
    ↓
sync_contact_history(identifier)
    ├─ Resolve entity (username/phone/name)
    ├─ Fetch messages (date-bounded)
    └─ Return conversation
    ↓
Celery Task: process_telegram_messages_async
    ├─ Batch messages (10 per batch)
    ├─ Format as note text
    ├─ NoteService.process_note()
    │   ├─ Save raw note
    │   ├─ AI analysis
    │   └─ Save synthesized entries
    └─ Update progress
    ↓
Return task_id
    ↓
Frontend polls: GET /api/notes/task/<task_id>/status
```

#### Integration Points

1. **Telethon**: Async Telegram client library
2. **Session Management**: HybridTelegramSession for persistence
3. **Database**: Contact matching and note creation
4. **Celery**: Async message processing
5. **AI Service**: Note analysis pipeline

#### Common Patterns

**Pattern 1: Async Route Decorator**
```python
def async_route(f):
    """Decorator to handle async functions in Flask routes"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper
```

**Pattern 2: Entity Resolution**
```python
# Try multiple strategies to find contact
entity = await client.get_entity(identifier)  # Direct
if not entity:
    entity = await client.get_entity('@' + identifier)  # With @
if not entity:
    # Scan dialogs for fuzzy match
    async for dialog in client.iter_dialogs():
        if match_criteria(dialog.entity, identifier):
            entity = dialog.entity
            break
```

**Pattern 3: Message Batching**
```python
# Process messages in batches to create notes
batch_size = 10
for i in range(0, len(messages), batch_size):
    batch = messages[i:i + batch_size]
    note_text = "\n".join([format_message(msg) for msg in batch])
    process_note(note_text)
```

**Pattern 4: Progress Tracking**
```python
# Update Celery task state for progress
progress = int((processed / total) * 100)
self.update_state(
    state='PROGRESS',
    meta={
        'status': f'Processing {processed}/{total}',
        'progress': progress
    }
)
```

#### Error Handling & Resilience

**Connection Errors:**
```python
try:
    await client.connect()
except asyncio.TimeoutError:
    logger.error("Connection timeout")
    return False
except Exception as e:
    logger.error(f"Connection failed: {e}")
    # Retry with exponential backoff
    return False
```

**Session Validation:**
```python
# Always verify session before operations
if not await self._verify_session():
    logger.warning("Session invalid, reconnecting...")
    await self.disconnect()
    return await self.connect()
```

**Message Processing Errors:**
```python
# Continue processing even if some messages fail
for message in messages:
    try:
        process_message(message)
    except Exception as e:
        logger.error(f"Error processing message {message.id}: {e}")
        # Continue with next message
        continue
```

### Testing Approach
- Mock Telethon responses
- Test contact matching logic (ID, username, phone, name)
- Test message-to-note conversion
- Test async sync progress
- Test session restoration
- Test entity resolution (multiple strategies)
- Test batch message processing
- Test error handling and retries

---

## Feature 8: File Upload & Processing

### Overview
Upload and process various file types (PDF, images, CSV, vCard). Supports OCR for images, PDF text extraction, and automatic note creation from files.

### User-Facing Pages
- **File Upload** (in contact detail view or main view)
  - File input/drag-and-drop
  - Upload progress
  - Processed file display

### API Endpoints

**`POST /api/files/upload`**
- Upload file for processing
- Request: Multipart form with file
- Query params: `contact_id` (optional)
- Response: `{ "file_id": int, "filename": string, "status": "uploaded" }`

**`POST /api/files/process`**
- Process uploaded file (OCR, text extraction)
- Request: `{ "file_id": int, "contact_id": int }`
- Response: `{ "task_id": string }` (async)

**`GET /api/files/<file_id>`**
- Get file metadata and processed content
- Response: `{ "filename": string, "content": string, "type": string }`

### Services

**FileService** (`app/services/file_service.py`)
- `upload_file(user_id, file, contact_id=None)` - Save uploaded file
- `process_file(file_id, contact_id)` - Extract text/content
  - PDF: PyPDF2 or pdfplumber
  - Images: Google Vision API OCR
  - CSV: Parse and import
  - vCard: Parse contacts
- `get_file_content(file_id, user_id)` - Retrieve processed content

### Frontend Implementation

**File Upload** (`static/js/main.js` or dedicated file)
- Drag-and-drop zone
- File input handler
- Upload progress bar
- Processed content display

### High-Level Implementation

#### Implementation Flow: Upload File

**Step 1: API Endpoint** (`app/api/files.py`)
```python
@files_bp.route('/upload', methods=['POST'])
@login_required
@inject
def upload_file(file_service: FileService = Provide[Container.file_service]):
    """Upload a file with validation and storage"""
    try:
        # 1. Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 2. Get contact ID (optional)
        contact_id = request.form.get('contact_id', type=int)
        
        # 3. Get optional description
        description = request.form.get('description', '').strip()
        
        # 4. Validate contact_id if provided
        if contact_id:
            # Verify contact ownership
            from app.utils.database import DatabaseManager
            from app.models import Contact
            
            db_manager = DatabaseManager()
            with db_manager.get_session() as session:
                contact = session.query(Contact).filter(
                    Contact.id == contact_id,
                    Contact.user_id == current_user.id
                ).first()
                
                if not contact:
                    return jsonify({'error': 'Contact not found'}), 404
        
        # 5. Upload file via service
        if contact_id:
            uploaded_file = file_service.upload_file(
                file=file,
                contact_id=contact_id,
                user_id=current_user.id,
                description=description
            )
            
            if not uploaded_file:
                return jsonify({'error': 'Failed to upload file. Check file type and size.'}), 400
            
            return jsonify({
                'success': True,
                'file_id': uploaded_file['id'],
                'file_path': uploaded_file['file_path'],
                'original_filename': uploaded_file['original_filename'],
                'file_size': uploaded_file['file_size_bytes'],
                'file_type': uploaded_file['file_type'],
                'message': 'File uploaded successfully'
            }), 201
        else:
            # Minimal success response when no contact_id provided
            return jsonify({
                'success': True, 
                'message': 'File received', 
                'filename': file.filename
            }), 201
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': 'Failed to upload file'}), 500
```

**Key Decision Points:**
- ✅ **Validate file presence** - Check both file key and filename
- ✅ **Optional contact_id** - Allow uploads without contact association
- ✅ **Verify contact ownership** - If contact_id provided, verify it belongs to user
- ✅ **Return detailed error** - Help user understand what went wrong

**Step 2: FileService.upload_file()** (`app/services/file_service.py`)
```python
def upload_file(self, file, contact_id: int, user_id: int, description: str = None) -> Optional[Dict]:
    """Upload a file with validation, storage, and database record"""
    try:
        # 1. Validate file presence
        if not file or not file.filename:
            logger.warning("No file provided")
            return None
        
        # 2. Check file extension
        if not self.is_allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            return None
        
        # 3. Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.max_file_size:
            logger.warning(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            return None
        
        # 4. Generate secure filename
        original_filename = secure_filename(file.filename)
        stored_filename = self.generate_unique_filename(original_filename)
        file_path = os.path.join(self.upload_folder, stored_filename)
        
        # 5. Save file to disk
        try:
            file.save(file_path)
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            return None
        
        # 6. Get file metadata
        file_info = self.get_file_info(file_path)
        mime_type = file_info.get('mime_type', 'application/octet-stream')
        
        # 7. Create database record
        with self.db_manager.get_session() as session:
            # Verify contact ownership
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                # Clean up file if contact not found
                try:
                    os.remove(file_path)
                except:
                    pass
                logger.warning(f"Contact {contact_id} not found for user {user_id}")
                return None
            
            # Create UploadedFile record
            uploaded_file = UploadedFile(
                contact_id=contact_id,
                user_id=user_id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_type=mime_type,
                file_size_bytes=file_size,
                description=description
            )
            
            session.add(uploaded_file)
            session.commit()
            session.refresh(uploaded_file)
            
            # Convert to dict before session closes
            file_dict = {
                'id': uploaded_file.id,
                'contact_id': uploaded_file.contact_id,
                'user_id': uploaded_file.user_id,
                'original_filename': uploaded_file.original_filename,
                'stored_filename': uploaded_file.stored_filename,
                'file_path': uploaded_file.file_path,
                'file_type': uploaded_file.file_type,
                'file_size_bytes': uploaded_file.file_size_bytes,
                'description': uploaded_file.description,
                'analysis_task_id': uploaded_file.analysis_task_id,
                'generated_raw_note_id': uploaded_file.generated_raw_note_id,
                'created_at': uploaded_file.created_at.isoformat() if uploaded_file.created_at else None
            }
            
            logger.info(f"Uploaded file {uploaded_file.id}: {original_filename} ({file_size} bytes)")
            return file_dict
            
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        # Clean up file if database operation failed
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        return None
```

**Key Decision Points:**
- ✅ **Validate before saving** - Check extension and size before disk write
- ✅ **Secure filename** - Use `secure_filename()` to prevent path traversal
- ✅ **Unique filename** - UUID-based to prevent collisions
- ✅ **Cleanup on error** - Remove file if database operation fails
- ✅ **File size check** - Prevent large file uploads (10MB limit)

#### Implementation Flow: Process File (OCR & Text Extraction)

**Step 1: Celery Task for File Processing** (`app/tasks/file_tasks.py`)
```python
@celery_app.task(bind=True)
def process_file_async(self, file_id: int, user_id: int):
    """Process uploaded file: extract text, OCR, create note"""
    try:
        from app.services.file_service import FileService
        from app.services.note_service import NoteService
        from app.services.ai_service import AIService
        from app.utils.database import DatabaseManager
        
        # 1. Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Loading file...', 'progress': 0}
        )
        
        # 2. Initialize services
        db_manager = DatabaseManager()
        file_service = FileService(db_manager)
        ai_service = AIService()
        note_service = NoteService(db_manager, ai_service)
        
        # 3. Get file record
        uploaded_file = file_service.get_file_by_id(file_id, user_id)
        if not uploaded_file:
            self.update_state(
                state='FAILURE',
                meta={'status': 'File not found', 'error': 'File not found'}
            )
            return None
        
        # 4. Extract text based on file type
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Extracting text...', 'progress': 20}
        )
        
        extracted_text = extract_text_from_file(
            file_path=uploaded_file.file_path,
            mime_type=uploaded_file.file_type
        )
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            self.update_state(
                state='FAILURE',
                meta={'status': 'No text extracted', 'error': 'Could not extract text from file'}
            )
            return None
        
        # 5. Process note with AI analysis
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Analyzing content...', 'progress': 60}
        )
        
        result = note_service.process_note(
            contact_id=uploaded_file.contact_id,
            content=extracted_text,
            user_id=user_id
        )
        
        # 6. Update file record with note ID
        if result.get('success') and result.get('raw_note_id'):
            file_service.update_file_metadata(
                file_id=file_id,
                user_id=user_id,
                generated_raw_note_id=result['raw_note_id']
            )
        
        # 7. Final state
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'File processed successfully',
                'progress': 100,
                'raw_note_id': result.get('raw_note_id'),
                'categories_count': len(result.get('synthesis', []))
            }
        )
        
        return {
            'file_id': file_id,
            'raw_note_id': result.get('raw_note_id'),
            'categories_count': len(result.get('synthesis', []))
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {e}")
        self.update_state(
            state='FAILURE',
            meta={'status': 'Processing failed', 'error': str(e)}
        )
        raise
```

**Step 2: Text Extraction Function**
```python
def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """Extract text from file using appropriate method"""
    extracted_text = ""
    
    try:
        # 1. Text files - direct read
        if mime_type.startswith('text/'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                extracted_text = f.read()[:50000]  # Limit to 50KB
        
        # 2. PDF files - multiple extraction methods
        elif mime_type == 'application/pdf':
            extracted_text = extract_pdf_text(file_path)
        
        # 3. Image files - OCR
        elif mime_type.startswith('image/'):
            extracted_text = extract_image_text(file_path)
        
        # 4. CSV files - parse and format
        elif mime_type == 'text/csv' or file_path.endswith('.csv'):
            extracted_text = extract_csv_text(file_path)
        
        # 5. vCard files - parse contacts
        elif mime_type == 'text/vcard' or file_path.endswith('.vcf'):
            extracted_text = extract_vcard_text(file_path)
        
        else:
            logger.warning(f"Unsupported file type: {mime_type}")
            extracted_text = f"[File type {mime_type} not supported for text extraction]"
        
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return f"[Error extracting text: {str(e)}]"
```

**Step 3: PDF Text Extraction** (Multiple Fallback Methods)
```python
def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF using multiple fallback methods"""
    extracted_text = ""
    
    # Method 1: PyPDF2 - fast and works for most PDFs
    try:
        import PyPDF2
        text_chunks = []
        with open(file_path, 'rb') as pf:
            reader = PyPDF2.PdfReader(pf)
            for page in reader.pages:
                t = page.extract_text() or ''
                if t.strip():
                    text_chunks.append(t)
        if text_chunks:
            extracted_text = '\n'.join(text_chunks)[:50000]
            logger.info(f"PyPDF2 extracted {len(extracted_text)} characters")
    except Exception as e:
        logger.debug(f"PyPDF2 extraction failed: {e}")
    
    # Method 2: pdfplumber - better for complex layouts
    if not extracted_text:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text_chunks = []
                for page in pdf.pages:
                    t = page.extract_text() or ''
                    if t.strip():
                        text_chunks.append(t)
                if text_chunks:
                    extracted_text = '\n'.join(text_chunks)[:50000]
                    logger.info(f"pdfplumber extracted {len(extracted_text)} characters")
        except Exception as e:
            logger.debug(f"pdfplumber extraction failed: {e}")
    
    # Method 3: pdfminer.six - fallback for tough PDFs
    if not extracted_text:
        try:
            from pdfminer.high_level import extract_text
            t = extract_text(file_path) or ''
            if t.strip():
                extracted_text = t.strip()[:50000]
                logger.info(f"pdfminer extracted {len(extracted_text)} characters")
        except Exception as e:
            logger.debug(f"pdfminer extraction failed: {e}")
    
    # Method 4: Google Vision OCR for image-based PDFs
    if not extracted_text:
        try:
            if os.getenv('KITH_VISION_OCR_ENABLED', 'false').lower() == 'true':
                extracted_text = google_ocr_pdf(file_path)
                if extracted_text:
                    logger.info(f"Google Vision OCR extracted {len(extracted_text)} characters from PDF")
        except Exception as e:
            logger.debug(f"Google Vision OCR failed: {e}")
    
    # Final fallback
    if not extracted_text:
        extracted_text = '[PDF content could not be extracted - file may be image-based or corrupted]'
    
    return extracted_text
```

**Key Decision Points:**
- ✅ **Multiple fallback methods** - Try PyPDF2 → pdfplumber → pdfminer → OCR
- ✅ **Limit text length** - Prevent memory issues (50KB limit)
- ✅ **Log extraction method** - For debugging and optimization
- ✅ **Graceful fallback** - Continue even if one method fails

**Step 4: Image OCR** (Google Vision API)
```python
def extract_image_text(file_path: str) -> str:
    """Extract text from image using OCR"""
    extracted_text = ""
    
    # Method 1: Google Vision API OCR (if enabled)
    try:
        if os.getenv('KITH_VISION_OCR_ENABLED', 'false').lower() == 'true':
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            with open(file_path, 'rb') as f:
                content = f.read()
            
            image = vision.Image(content=content)
            resp = client.document_text_detection(image=image)
            
            # Check for errors
            if getattr(resp, 'error', None) and getattr(resp.error, 'message', None):
                logger.warning(f"Google Vision error: {resp.error.message}")
            else:
                # Prefer full_text_annotation when present
                try:
                    extracted_text = (resp.full_text_annotation.text or "").strip()
                except Exception:
                    pass
                
                # Fallback to text_annotations
                if not extracted_text and getattr(resp, 'text_annotations', None):
                    try:
                        extracted_text = (resp.text_annotations[0].description or "").strip()
                    except Exception:
                        pass
                
                if extracted_text:
                    logger.info(f"Google Vision OCR extracted {len(extracted_text)} characters")
    except Exception as e:
        logger.debug(f"Google Vision OCR not available: {e}")
    
    # Method 2: OpenAI Vision (if Google Vision unavailable)
    if not extracted_text:
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and os.getenv('OPENAI_VISION_MODEL'):
                import base64
                import openai
                
                with open(file_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                
                mime_type = mimetypes.guess_type(file_path)[0] or 'image/png'
                data_uri = f"data:{mime_type};base64,{b64}"
                
                response = openai.ChatCompletion.create(
                    model=os.getenv('OPENAI_VISION_MODEL'),
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all visible text from this image. Output plaintext only."},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }],
                    max_tokens=2000
                )
                
                extracted_text = response.choices[0].message.content.strip()
                if extracted_text:
                    logger.info(f"OpenAI Vision extracted {len(extracted_text)} characters")
        except Exception as e:
            logger.debug(f"OpenAI Vision not available: {e}")
    
    # Method 3: Gemini Vision (if others unavailable)
    if not extracted_text:
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                import google.generativeai as genai
                import base64
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                
                with open(file_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                
                mime_type = mimetypes.guess_type(file_path)[0] or 'image/png'
                prompt = [
                    "Extract all visible text from this image. Output plaintext only.",
                    {"mime_type": mime_type, "data": b64}
                ]
                
                resp = model.generate_content(prompt)
                extracted_text = (resp.text or "").strip()
                
                if extracted_text:
                    logger.info(f"Gemini Vision extracted {len(extracted_text)} characters")
        except Exception as e:
            logger.debug(f"Gemini Vision not available: {e}")
    
    # Final fallback
    if not extracted_text:
        extracted_text = '[Image text could not be extracted - OCR services may be unavailable]'
    
    return extracted_text
```

**Key Decision Points:**
- ✅ **Multiple OCR providers** - Google Vision → OpenAI Vision → Gemini Vision
- ✅ **Prefer document_text_detection** - Better for structured text
- ✅ **Fallback to text_annotations** - If full_text_annotation unavailable
- ✅ **Graceful degradation** - Continue if OCR unavailable

**Step 5: CSV Text Extraction**
```python
def extract_csv_text(file_path: str) -> str:
    """Extract and format CSV content as text"""
    try:
        import csv
        
        text_lines = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            
            # Get headers
            headers = reader.fieldnames or []
            text_lines.append(f"CSV Headers: {', '.join(headers)}")
            text_lines.append("")
            
            # Get rows (limit to prevent huge output)
            row_count = 0
            for row in reader:
                if row_count >= 100:  # Limit to first 100 rows
                    text_lines.append(f"\n... (showing first 100 rows, total rows may be more)")
                    break
                
                row_text = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                text_lines.append(row_text)
                row_count += 1
        
        return "\n".join(text_lines)
        
    except Exception as e:
        logger.error(f"Error extracting CSV text: {e}")
        return f"[Error reading CSV file: {str(e)}]"
```

**Step 6: vCard Text Extraction**
```python
def extract_vcard_text(file_path: str) -> str:
    """Extract contact information from vCard file"""
    try:
        import vobject
        
        contacts = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Parse vCard (may contain multiple contacts)
            for vcard in vobject.readComponents(content):
                contact_info = []
                
                # Extract name
                if hasattr(vcard, 'fn') and vcard.fn.value:
                    contact_info.append(f"Name: {vcard.fn.value}")
                
                # Extract organization
                if hasattr(vcard, 'org') and vcard.org.value:
                    contact_info.append(f"Organization: {vcard.org.value}")
                
                # Extract email
                if hasattr(vcard, 'email_list'):
                    emails = [e.value for e in vcard.email_list]
                    contact_info.append(f"Emails: {', '.join(emails)}")
                
                # Extract phone
                if hasattr(vcard, 'tel_list'):
                    phones = [t.value for t in vcard.tel_list]
                    contact_info.append(f"Phones: {', '.join(phones)}")
                
                # Extract notes
                if hasattr(vcard, 'note') and vcard.note.value:
                    contact_info.append(f"Notes: {vcard.note.value}")
                
                if contact_info:
                    contacts.append("\n".join(contact_info))
        
        if contacts:
            return "\n\n--- Contact ---\n".join(contacts)
        else:
            return "[No contact information found in vCard file]"
            
    except Exception as e:
        logger.error(f"Error extracting vCard text: {e}")
        return f"[Error reading vCard file: {str(e)}]"
```

#### Implementation Flow: Get File Content

**Step 1: API Endpoint**
```python
@files_bp.route('/<int:file_id>/content', methods=['GET'])
@login_required
@inject
def get_file_content(file_id: int, file_service: FileService = Provide[Container.file_service]):
    """Get file content as text (for text files)"""
    try:
        # 1. Get file record
        file = file_service.get_file_by_id(file_id, current_user.id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # 2. Check file type (only allow text files for content viewing)
        if not file.file_type.startswith('text/'):
            return jsonify({
                'error': 'File type not supported for content viewing',
                'file_type': file.file_type
            }), 400
        
        # 3. Get file content
        content = file_service.get_file_content(file_id, current_user.id)
        if content is None:
            return jsonify({'error': 'Failed to read file content'}), 500
        
        # 4. Decode content
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'File contains non-text content'}), 400
        
        return jsonify({
            'content': text_content,
            'filename': file.original_filename,
            'file_type': file.file_type,
            'file_size': file.file_size_bytes
        })
        
    except Exception as e:
        logger.error(f"Error reading file content {file_id}: {e}")
        return jsonify({'error': 'Failed to read file content'}), 500
```

#### Implementation Flow: Download File

**Step 1: Download Endpoint**
```python
@files_bp.route('/<int:file_id>/download', methods=['GET'])
@login_required
@inject
def download_file(file_id: int, file_service: FileService = Provide[Container.file_service]):
    """Download a file"""
    try:
        # 1. Get file record
        file = file_service.get_file_by_id(file_id, current_user.id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # 2. Check if physical file exists
        if not os.path.exists(file.file_path):
            logger.error(f"Physical file not found: {file.file_path}")
            return jsonify({'error': 'File not found on disk'}), 404
        
        # 3. Send file
        return send_file(
            file.file_path,
            as_attachment=True,
            download_name=file.original_filename,
            mimetype=file.file_type
        )
        
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        return jsonify({'error': 'Failed to download file'}), 500
```

#### Implementation Flow: Delete File

**Step 1: FileService.delete_file()**
```python
def delete_file(self, file_id: int, user_id: int) -> bool:
    """Delete a file (both physical file and database record)"""
    try:
        with self.db_manager.get_session() as session:
            # 1. Get file record
            file = session.query(UploadedFile).filter(
                UploadedFile.id == file_id,
                UploadedFile.user_id == user_id
            ).first()
            
            if not file:
                logger.warning(f"File {file_id} not found for user {user_id}")
                return False
            
            file_path = file.file_path
            
            # 2. Delete physical file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted physical file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete physical file: {e}")
                    # Continue with database deletion even if file deletion fails
            
            # 3. Delete database record
            session.delete(file)
            session.commit()
            
            logger.info(f"Deleted file {file_id}: {file.original_filename}")
            return True
            
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        session.rollback()
        return False
```

**Key Decision Points:**
- ✅ **Delete both physical and database** - Complete cleanup
- ✅ **Continue on file deletion failure** - Don't block database deletion
- ✅ **Verify ownership** - Only allow user to delete their own files

#### Data Flow Diagram: File Upload & Processing

```
User uploads file
    ↓
POST /api/files/upload
    ├─ Validate file (type, size)
    ├─ Generate secure filename
    ├─ Save to disk
    └─ Create database record
    ↓
Return file_id
    ↓
(Optional) POST /api/files/process
    ↓
Celery Task: process_file_async
    ├─ Extract text based on file type
    │   ├─ PDF: PyPDF2 → pdfplumber → pdfminer → OCR
    │   ├─ Image: Google Vision → OpenAI → Gemini
    │   ├─ CSV: Parse and format
    │   └─ vCard: Parse contacts
    ├─ Process note with AI
    │   ├─ NoteService.process_note()
    │   ├─ AI analysis
    │   └─ Save synthesized entries
    └─ Update file record with note_id
    ↓
Return task_id
    ↓
Frontend polls: GET /api/files/status/<task_id>
```

#### Integration Points

1. **File Storage**: Local filesystem (`uploads/` directory)
2. **OCR Services**: Google Vision API, OpenAI Vision, Gemini Vision
3. **PDF Libraries**: PyPDF2, pdfplumber, pdfminer.six
4. **Database**: UploadedFile model for metadata
5. **Note Processing**: Integration with NoteService and AI analysis
6. **Celery**: Async file processing

#### Common Patterns

**Pattern 1: Multiple Fallback Methods**
```python
# Try multiple extraction methods in order
extracted_text = ""
try:
    extracted_text = method1()
except:
    pass

if not extracted_text:
    try:
        extracted_text = method2()
    except:
        pass
```

**Pattern 2: File Validation**
```python
# Validate before processing
if not self.is_allowed_file(filename):
    return None

if file_size > self.max_file_size:
    return None

# Then proceed with upload
```

**Pattern 3: Cleanup on Error**
```python
try:
    # Save file
    file.save(file_path)
    # Create database record
    # ...
except Exception as e:
    # Clean up file if database operation fails
    if os.path.exists(file_path):
        os.remove(file_path)
    raise
```

**Pattern 4: Secure Filename**
```python
# Use secure_filename to prevent path traversal
original_filename = secure_filename(file.filename)
# Generate unique filename to prevent collisions
stored_filename = f"{uuid.uuid4()}{ext}"
```

#### Error Handling & Resilience

**File Upload Errors:**
```python
# Validate before saving
if not self.is_allowed_file(file.filename):
    return None  # Invalid file type

if file_size > self.max_file_size:
    return None  # File too large

# Clean up on database error
try:
    file.save(file_path)
    # Create database record
except Exception as e:
    if os.path.exists(file_path):
        os.remove(file_path)
    raise
```

**Text Extraction Errors:**
```python
# Try multiple methods with fallback
extracted_text = ""
for method in [method1, method2, method3]:
    try:
        extracted_text = method(file_path)
        if extracted_text:
            break
    except Exception as e:
        logger.debug(f"Method failed: {e}")
        continue

# Final fallback
if not extracted_text:
    extracted_text = "[Could not extract text]"
```

**OCR Service Errors:**
```python
# Graceful degradation if OCR unavailable
try:
    extracted_text = google_vision_ocr(file_path)
except Exception as e:
    logger.debug(f"Google Vision unavailable: {e}")
    # Try next method
    try:
        extracted_text = openai_vision_ocr(file_path)
    except:
        extracted_text = "[OCR services unavailable]"
```

### Testing Approach

#### Current Test Coverage

**Existing Tests:**
- ✅ **Integration Tests**: `tests/integration/test_file_upload.py` (15 test functions)
- ✅ **E2E Tests**: `tests/test_app_consolidation.py` (file upload, vCard upload)
- ⚠️ **Unit Tests**: Limited (no dedicated unit tests for FileService)
- ⚠️ **Functional Tests**: Partially covered (mixed with integration)
- ⚠️ **OCR Tests**: Limited (no tests for OCR accuracy)
- ⚠️ **PDF Extraction Tests**: Limited (no tests for multiple extraction methods)

**Test Coverage Breakdown:**

**✅ Covered:**
1. **File Upload Authentication** - `test_file_upload_requires_auth()`
2. **Successful Upload** - `test_file_upload_success()`
3. **Validation** - `test_file_upload_no_file()`, `test_file_upload_invalid_file_type()`
4. **File Size Limits** - `test_file_upload_large_file()`
5. **File Storage** - `test_file_upload_storage()`
6. **File Deletion** - `test_file_upload_cleanup()`
7. **Security** - `test_file_upload_security()` (path traversal)
8. **User Isolation** - `test_file_upload_permissions()`
9. **Metadata** - `test_file_upload_metadata()`
10. **Processing Flag** - `test_file_upload_processing()`

**⚠️ Partially Covered:**
1. **Multiple File Upload** - `test_file_upload_multiple_files()` (basic test)
2. **File Processing** - `test_file_upload_processing()` (flag only, no actual processing)

**❌ Missing:**
1. **Unit Tests for FileService** - No dedicated unit tests
2. **PDF Text Extraction** - No tests for PyPDF2, pdfplumber, pdfminer
3. **OCR Tests** - No tests for Google Vision, OpenAI Vision, Gemini
4. **CSV Parsing** - No tests for CSV text extraction
5. **vCard Parsing** - No tests for vCard extraction
6. **File Processing Workflow** - No tests for complete processing pipeline
7. **Error Handling** - Limited error scenario tests
8. **File Content Retrieval** - No tests for `/api/files/<id>/content`
9. **File Download** - No tests for `/api/files/<id>/download`
10. **File Update** - No tests for metadata updates

#### Recommended Test Suite

**1. Unit Tests** (`tests/unit/test_file_service.py`)
```python
@pytest.mark.unit
class TestFileService:
    """Unit tests for FileService"""
    
    def test_is_allowed_file_valid_extensions(self):
        """Test file extension validation"""
        service = FileService(Mock())
        assert service.is_allowed_file('test.pdf') is True
        assert service.is_allowed_file('test.jpg') is True
        assert service.is_allowed_file('test.exe') is False
    
    def test_is_allowed_file_invalid(self):
        """Test invalid file extensions"""
        service = FileService(Mock())
        assert service.is_allowed_file('') is False
        assert service.is_allowed_file(None) is False
        assert service.is_allowed_file('noextension') is False
    
    def test_generate_unique_filename(self):
        """Test unique filename generation"""
        service = FileService(Mock())
        filename1 = service.generate_unique_filename('test.pdf')
        filename2 = service.generate_unique_filename('test.pdf')
        
        assert filename1 != filename2  # Should be unique
        assert filename1.endswith('.pdf')
        assert filename2.endswith('.pdf')
    
    def test_get_file_info(self, tmp_path):
        """Test file info retrieval"""
        service = FileService(Mock())
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        info = service.get_file_info(str(test_file))
        assert 'size' in info
        assert 'mime_type' in info
        assert info['size'] > 0
```

**2. PDF Extraction Tests** (`tests/unit/test_pdf_extraction.py`)
```python
@pytest.mark.unit
class TestPDFExtraction:
    """Unit tests for PDF text extraction"""
    
    def test_extract_pdf_text_pypdf2(self, sample_pdf_file):
        """Test PyPDF2 extraction"""
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = 'Test PDF content'
            mock_reader.return_value.pages = [mock_page]
            
            text = extract_pdf_text(sample_pdf_file)
            assert 'Test PDF content' in text
    
    def test_extract_pdf_text_pdfplumber(self, sample_pdf_file):
        """Test pdfplumber extraction"""
        with patch('pdfplumber.open') as mock_open:
            mock_page = Mock()
            mock_page.extract_text.return_value = 'Test content'
            mock_open.return_value.__enter__.return_value.pages = [mock_page]
            
            text = extract_pdf_text(sample_pdf_file)
            assert 'Test content' in text
    
    def test_extract_pdf_text_fallback_chain(self, sample_pdf_file):
        """Test fallback chain when methods fail"""
        # PyPDF2 fails
        with patch('PyPDF2.PdfReader', side_effect=Exception('PyPDF2 failed')):
            # pdfplumber succeeds
            with patch('pdfplumber.open') as mock_open:
                mock_page = Mock()
                mock_page.extract_text.return_value = 'Fallback content'
                mock_open.return_value.__enter__.return_value.pages = [mock_page]
                
                text = extract_pdf_text(sample_pdf_file)
                assert 'Fallback content' in text
    
    def test_extract_pdf_text_all_methods_fail(self, sample_pdf_file):
        """Test when all extraction methods fail"""
        with patch('PyPDF2.PdfReader', side_effect=Exception()), \
             patch('pdfplumber.open', side_effect=Exception()), \
             patch('pdfminer.high_level.extract_text', side_effect=Exception()):
            
            text = extract_pdf_text(sample_pdf_file)
            assert '[PDF content could not be extracted' in text
```

**3. OCR Tests** (`tests/unit/test_ocr_extraction.py`)
```python
@pytest.mark.unit
class TestOCRExtraction:
    """Unit tests for OCR text extraction"""
    
    @patch('google.cloud.vision.ImageAnnotatorClient')
    def test_extract_image_text_google_vision(self, mock_client, sample_image_file):
        """Test Google Vision OCR"""
        mock_response = Mock()
        mock_response.full_text_annotation.text = 'Extracted text from image'
        mock_response.error = None
        mock_client.return_value.document_text_detection.return_value = mock_response
        
        with patch.dict('os.environ', {'KITH_VISION_OCR_ENABLED': 'true'}):
            text = extract_image_text(sample_image_file)
            assert 'Extracted text from image' in text
    
    @patch('openai.ChatCompletion.create')
    def test_extract_image_text_openai_vision(self, mock_openai, sample_image_file):
        """Test OpenAI Vision OCR"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'OpenAI extracted text'
        mock_openai.return_value = mock_response
        
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_VISION_MODEL': 'gpt-4-vision'
        }):
            text = extract_image_text(sample_image_file)
            assert 'OpenAI extracted text' in text
    
    @patch('google.generativeai.GenerativeModel')
    def test_extract_image_text_gemini_vision(self, mock_model, sample_image_file):
        """Test Gemini Vision OCR"""
        mock_response = Mock()
        mock_response.text = 'Gemini extracted text'
        mock_model.return_value.generate_content.return_value = mock_response
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            text = extract_image_text(sample_image_file)
            assert 'Gemini extracted text' in text
    
    def test_extract_image_text_fallback_chain(self, sample_image_file):
        """Test OCR fallback chain"""
        # Google Vision fails
        with patch('google.cloud.vision.ImageAnnotatorClient', side_effect=Exception()):
            # OpenAI succeeds
            with patch('openai.ChatCompletion.create') as mock_openai:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = 'Fallback OCR text'
                mock_openai.return_value = mock_response
                
                text = extract_image_text(sample_image_file)
                assert 'Fallback OCR text' in text
```

**4. Integration Tests** (Enhanced - `tests/integration/test_file_upload.py`)
```python
@pytest.mark.integration
@pytest.mark.file_upload
class TestFileUploadIntegration:
    """Integration tests for file upload and processing"""
    
    def test_complete_file_processing_workflow(self, authenticated_client, db_session):
        """Test complete workflow: upload → process → note creation"""
        # 1. Create contact
        contact = Contact(full_name='Test Contact', user_id=authenticated_user.id)
        db_session.add(contact)
        db_session.commit()
        
        # 2. Upload PDF file
        pdf_content = b'%PDF-1.4\n...'  # Minimal PDF
        test_file = (io.BytesIO(pdf_content), 'test.pdf')
        
        upload_response = authenticated_client.post(
            '/api/files/upload',
            data={'file': test_file, 'contact_id': contact.id}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.get_json()['file_id']
        
        # 3. Process file
        with patch('app.tasks.file_tasks.process_file_async.delay') as mock_process:
            mock_task = Mock()
            mock_task.id = 'test-task-id'
            mock_process.return_value = mock_task
            
            process_response = authenticated_client.post(
                '/api/files/process',
                json={'file_id': file_id, 'contact_id': contact.id}
            )
            assert process_response.status_code == 202
            assert 'task_id' in process_response.get_json()
    
    def test_file_download(self, authenticated_client, db_session):
        """Test file download"""
        # Upload file
        contact = Contact(full_name='Test', user_id=authenticated_user.id)
        db_session.add(contact)
        db_session.commit()
        
        test_file = (io.BytesIO(b'test content'), 'test.txt')
        upload_response = authenticated_client.post(
            '/api/files/upload',
            data={'file': test_file, 'contact_id': contact.id}
        )
        file_id = upload_response.get_json()['file_id']
        
        # Download file
        download_response = authenticated_client.get(f'/api/files/{file_id}/download')
        assert download_response.status_code == 200
        assert download_response.data == b'test content'
        assert 'attachment' in download_response.headers['Content-Disposition']
    
    def test_file_content_retrieval(self, authenticated_client, db_session):
        """Test file content retrieval for text files"""
        contact = Contact(full_name='Test', user_id=authenticated_user.id)
        db_session.add(contact)
        db_session.commit()
        
        test_file = (io.BytesIO(b'text file content'), 'test.txt')
        upload_response = authenticated_client.post(
            '/api/files/upload',
            data={'file': test_file, 'contact_id': contact.id}
        )
        file_id = upload_response.get_json()['file_id']
        
        # Get content
        content_response = authenticated_client.get(f'/api/files/{file_id}/content')
        assert content_response.status_code == 200
        data = content_response.get_json()
        assert data['content'] == 'text file content'
        assert data['filename'] == 'test.txt'
    
    def test_file_content_non_text_file(self, authenticated_client, db_session):
        """Test content retrieval for non-text files fails"""
        contact = Contact(full_name='Test', user_id=authenticated_user.id)
        db_session.add(contact)
        db_session.commit()
        
        pdf_file = (io.BytesIO(b'%PDF-1.4'), 'test.pdf')
        upload_response = authenticated_client.post(
            '/api/files/upload',
            data={'file': pdf_file, 'contact_id': contact.id}
        )
        file_id = upload_response.get_json()['file_id']
        
        # Try to get content (should fail for non-text)
        content_response = authenticated_client.get(f'/api/files/{file_id}/content')
        assert content_response.status_code == 400
        assert 'not supported' in content_response.get_json()['error']
```

**5. Functional Tests** (`tests/functional/test_file_workflows.py`)
```python
@pytest.mark.functional
class TestFileWorkflows:
    """Functional tests for file upload workflows"""
    
    def test_upload_pdf_and_create_note(self, authenticated_client, db_session):
        """Test: Upload PDF → Extract text → Create note → AI analysis"""
        # 1. Create contact
        contact = Contact(full_name='John Doe', user_id=authenticated_user.id)
        db_session.add(contact)
        db_session.commit()
        
        # 2. Upload PDF
        pdf_content = create_test_pdf('John works at Google and likes pizza')
        upload_response = authenticated_client.post(
            '/api/files/upload',
            data={'file': (io.BytesIO(pdf_content), 'resume.pdf'), 'contact_id': contact.id}
        )
        file_id = upload_response.get_json()['file_id']
        
        # 3. Process file (async)
        process_response = authenticated_client.post(
            '/api/files/process',
            json={'file_id': file_id}
        )
        task_id = process_response.get_json()['task_id']
        
        # 4. Wait for processing
        wait_for_task_completion(task_id, timeout=30)
        
        # 5. Verify note created
        notes = db_session.query(RawNote).filter_by(contact_id=contact.id).all()
        assert len(notes) > 0
        assert 'Google' in notes[0].content or 'pizza' in notes[0].content
        
        # 6. Verify synthesized entries created
        entries = db_session.query(SynthesizedEntry).filter_by(contact_id=contact.id).all()
        assert len(entries) > 0
```

**6. E2E Tests** (`tests/e2e/test_file_upload_e2e.py`)
```python
@pytest.mark.e2e
class TestFileUploadE2E:
    """End-to-end tests for file upload"""
    
    def test_complete_file_upload_journey(self, authenticated_client):
        """E2E: Login → Create Contact → Upload File → Process → View Note"""
        # 1. Create contact via API
        contact_response = authenticated_client.post(
            '/api/contacts',
            json={'full_name': 'Test Contact', 'tier': 2}
        )
        contact_id = contact_response.get_json()['id']
        
        # 2. Upload file
        file_response = authenticated_client.post(
            '/api/files/upload',
            data={
                'file': (io.BytesIO(b'Meeting notes: Discussed project timeline'), 'notes.txt'),
                'contact_id': contact_id
            }
        )
        assert file_response.status_code == 201
        file_id = file_response.get_json()['file_id']
        
        # 3. Process file
        process_response = authenticated_client.post(
            '/api/files/process',
            json={'file_id': file_id}
        )
        task_id = process_response.get_json()['task_id']
        
        # 4. Poll for completion
        status = poll_task_status(task_id, max_wait=60)
        assert status == 'SUCCESS'
        
        # 5. Get contact details (should include note from file)
        contact_response = authenticated_client.get(f'/api/contacts/{contact_id}')
        contact_data = contact_response.get_json()
        
        # Verify note was created
        assert 'categorized_data' in contact_data
```

#### Test Execution Commands

**Run All File Upload Tests:**
```bash
# All file upload tests
pytest -m file_upload

# Integration tests only
pytest tests/integration/test_file_upload.py

# Unit tests (when created)
pytest tests/unit/test_file_service.py

# Functional tests (when created)
pytest -m functional tests/functional/test_file_workflows.py

# E2E tests (when created)
pytest -m e2e tests/e2e/test_file_upload_e2e.py
```

#### Test Coverage Goals

**Current Coverage:**
- **Integration Tests**: ~60% (15 tests covering basic upload flows)
- **Unit Tests**: ~0% (no dedicated unit tests)
- **Functional Tests**: ~30% (basic workflow tests)
- **E2E Tests**: ~20% (minimal E2E coverage)
- **OCR Tests**: ~0% (no OCR-specific tests)
- **PDF Extraction Tests**: ~0% (no PDF extraction tests)

**Target Coverage:**
- **Unit Tests**: 80%+ (FileService, extraction methods)
- **Integration Tests**: 90%+ (all API endpoints, workflows)
- **Functional Tests**: 80%+ (complete workflows)
- **E2E Tests**: 70%+ (user journeys)
- **OCR Tests**: 70%+ (all OCR providers)
- **PDF Extraction Tests**: 80%+ (all extraction methods)

#### Missing Test Scenarios

**Priority 1: Critical Missing Tests**
1. ❌ **PDF text extraction** - Test PyPDF2, pdfplumber, pdfminer methods
2. ❌ **OCR accuracy** - Test Google Vision, OpenAI, Gemini OCR
3. ❌ **File processing workflow** - Test complete upload → extract → note → AI pipeline
4. ❌ **Error handling** - Test corrupted files, missing files, processing failures
5. ❌ **File download** - Test download endpoint
6. ❌ **File content retrieval** - Test content endpoint for text files

**Priority 2: Important Missing Tests**
1. ❌ **CSV parsing** - Test CSV text extraction
2. ❌ **vCard parsing** - Test vCard contact extraction
3. ❌ **File update** - Test metadata updates
4. ❌ **Concurrent uploads** - Test multiple simultaneous uploads
5. ❌ **Large file handling** - Test files near size limit

**Priority 3: Nice-to-Have Tests**
1. ❌ **File type detection** - Test MIME type detection
2. ❌ **File cleanup** - Test orphaned file cleanup
3. ❌ **Storage backend** - Test S3 storage (if implemented)
4. ❌ **Performance** - Test upload/processing performance
5. ❌ **Security** - Test file injection, path traversal, XSS in filenames

#### Recommended Test Improvements

**Immediate Actions:**
1. ✅ **Create unit tests** for FileService methods
2. ✅ **Add PDF extraction tests** for all methods
3. ✅ **Add OCR tests** for all providers
4. ✅ **Enhance integration tests** with processing workflow
5. ✅ **Add file download/content tests**

**Medium-term Actions:**
1. ✅ **Create functional test suite** for complete workflows
2. ✅ **Add E2E tests** for user journeys
3. ✅ **Add error scenario tests** (corrupted files, missing files)
4. ✅ **Add performance tests** (large files, concurrent uploads)

**Long-term Actions:**
1. ✅ **Add regression test suite** for file processing
2. ✅ **Add security tests** (file injection, path traversal)
3. ✅ **Add storage backend tests** (S3, local filesystem)
4. ✅ **Add monitoring tests** (file processing metrics)

---

---

## Feature 9: Analytics & Insights

### Overview
Relationship health scoring, trend analysis, network insights, and personalized recommendations. Includes system health monitoring and performance analytics. Provides actionable insights to help users maintain and improve their relationships.

### User-Facing Pages
- **Analytics Dashboard** (`/admin/dashboard` or Settings for admins)
  - Relationship health scores with visual indicators
  - Trend charts showing interaction frequency over time
  - Network insights (total contacts, tier distribution)
  - Recommendations list with priority indicators
  - System health monitoring (database, Redis, Celery)
  - Test run analytics and trends

### API Endpoints

**`GET /api/analytics/health/comprehensive`**
- Comprehensive system health check
- Response: `{ "status": "healthy|degraded|unhealthy", "health_percentage": float, "checks": {...} }`
- Checks: database, Redis, Celery, system resources, migrations, data consistency, task queuing, AI services, ChromaDB, security, performance

**`GET /api/analytics/dashboard/overview`**
- High-level dashboard metrics
- Response: `{ "summary": {...}, "recent_runs": [...], "generated_at": "..." }`
- Includes: success rate (24h), failed tests, average execution time

**`GET /api/analytics/dashboard/trends`**
- Trends over time period
- Query params: `days` (default: 7, max: 90)
- Response: `{ "trends": [{ "date": "...", "success_rate": float, "avg_execution_time": float }], "range": {...} }`

**`GET /api/analytics/dashboard/test-categories`**
- Category success rates for donut chart
- Response: `{ "categories": [{ "category": string, "success_rate": int }] }`

**`POST /api/analytics/test-runs`**
- Start a test run (async via Celery)
- Request: `{ "markers": ["unit", "integration"], "parallel": bool }`
- Response: `{ "task_id": string, "status": "running" }`

**`GET /api/analytics/test-runs`**
- List recent test runs
- Response: `{ "runs": [{ "id": int, "status": string, "total_tests": int, ... }] }`

**`GET /api/analytics/test-runs/<run_id>`**
- Get detailed test run results
- Response: `{ "run": {...}, "results": [...] }`

**`POST /api/analytics/diagnose`**
- Run comprehensive diagnostic (async via Celery)
- Response: `{ "task_id": string, "status": "running" }`

**`POST /api/analytics/diagnose-direct`**
- Run diagnostic directly (synchronous, returns immediately)
- Response: `{ "status": "completed", "results": {...} }`

**`POST /api/analytics/health/run-comprehensive`**
- Run comprehensive health check and store results
- Response: `{ "message": "...", "status": "completed", "results": {...} }`

**`GET /api/analytics/health/categories`**
- Get health check categories and descriptions
- Response: `{ "categories": {...} }`

### Database Models

**TestRun** (`app/models.py`)
```python
class TestRun(Base):
    __tablename__ = 'test_runs'
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50))  # 'running', 'completed', 'failed'
    triggered_by = Column(String(255))
    trigger_type = Column(String(50))  # 'manual', 'scheduled', 'health_check'
    environment = Column(String(50))
    version = Column(String(255))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    total_tests = Column(Integer)
    passed_tests = Column(Integer)
    failed_tests = Column(Integer)
    skipped_tests = Column(Integer)
    execution_time_seconds = Column(Float)
    error_message = Column(Text)
    
    # Relationships
    test_results = relationship("TestResult", back_populates="test_run")
```

**TestResult** (`app/models.py`)
```python
class TestResult(Base):
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('test_runs.id'))
    test_name = Column(String(500))
    nodeid = Column(String(1000))
    test_module = Column(String(500))
    test_category = Column(String(100))  # 'unit', 'integration', 'api', etc.
    status = Column(String(50))  # 'passed', 'failed', 'skipped'
    execution_time_seconds = Column(Float)
    failure_message = Column(Text)
    traceback_excerpt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="test_results")
```

### Services

**RelationshipAnalytics** (`kith-platform/analytics.py`)
- `calculate_relationship_health_score(contact_id)` - Compute comprehensive health score
- `get_relationship_trends(contact_id, days)` - Analyze trends over time
- `get_network_insights()` - Network-wide analytics
- `get_actionable_recommendations(contact_id)` - Personalized recommendations

**HealthChecker** (`app/utils/monitoring.py`)
- `check_database()` - Database connectivity and performance
- `check_redis()` - Redis connectivity
- `check_celery()` - Celery worker status
- `check_system_resources()` - CPU, memory, disk usage
- `check_database_migrations()` - Verify migrations applied
- `check_data_consistency()` - Check for orphaned records
- `check_transaction_rollbacks()` - Test transaction handling
- `check_connection_pooling()` - Test concurrent connections
- `check_task_queuing()` - Test Celery task queuing
- `check_task_failure_handling()` - Test failure handling
- `check_ai_service_connectivity()` - Test AI service connectivity
- `check_chromadb_connectivity()` - Test ChromaDB connectivity
- `check_password_hashing()` - Test password hashing
- `check_input_sanitization()` - Test input sanitization
- `check_api_performance()` - Test API response times
- `check_concurrent_users()` - Test concurrent load
- `get_comprehensive_health()` - Run all checks and return summary

**MetricsCollector** (`app/utils/monitoring.py`)
- `record_request(endpoint, method, status_code, duration)` - Record HTTP metrics
- `record_database_query(query_type, duration, rows_affected)` - Record DB metrics
- `record_ai_processing(operation, duration, tokens_used)` - Record AI metrics
- `get_metrics_summary()` - Get summary of all metrics

### High-Level Implementation

#### Relationship Health Score Calculation

**Flow:**
1. Fetch all synthesized entries for contact
2. Calculate metrics:
   - **Recency Score**: `max(0, 100 - (days_since_last * 2))` (lose 2 points per day)
   - **Engagement Score**: `min(100, interactions_per_week * 10)` (10 interactions/week = 100)
   - **Quality Score**: `min(100, avg_confidence * 10)` (convert 0-10 scale to 0-100)
   - **Diversity Score**: `min(100, unique_categories * 5)` (20 categories = 100)
3. Weighted average: `(recency * 0.3) + (engagement * 0.3) + (quality * 0.2) + (diversity * 0.2)`
4. Generate insights based on score and category distribution

**Code Example:**
```python
def calculate_relationship_health_score(self, contact_id: int) -> Dict:
    """Calculate comprehensive relationship health score for a contact."""
    with self.db_manager.get_session() as session:
        entries = session.query(SynthesizedEntry).filter(
            SynthesizedEntry.contact_id == contact_id
        ).order_by(SynthesizedEntry.created_at.desc()).all()
        
        if not entries:
            return {
                "health_score": 0,
                "total_interactions": 0,
                "last_interaction": None,
                "category_distribution": {},
                "confidence_avg": 0,
                "insights": ["No data available for this contact"]
            }
        
        # Calculate metrics
        total_interactions = len(entries)
        confidence_scores = [e.confidence_score for e in entries if e.confidence_score is not None]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Category distribution
        categories = [entry.category for entry in entries]
        category_dist = Counter(categories)
        
        # Recency score (more recent = better)
        latest_date = max(entry.created_at for entry in entries)
        days_since_last = (datetime.now() - latest_date).days
        recency_score = max(0, 100 - (days_since_last * Analytics.RECENCY_POINTS_LOSS_PER_DAY))
        
        # Engagement score based on interaction frequency
        if total_interactions > 0:
            first_date = min(entry.created_at for entry in entries)
            total_days = (latest_date - first_date).days + 1
            interactions_per_week = (total_interactions / total_days) * 7
            engagement_score = min(100, interactions_per_week * (100 / Analytics.INTERACTIONS_PER_WEEK_MAX_SCORE))
        else:
            engagement_score = 0
        
        # Quality score based on confidence
        quality_score = min(100, avg_confidence * Analytics.CONFIDENCE_SCALE_MULTIPLIER)
        
        # Diversity score (more categories = better)
        diversity_score = min(100, len(category_dist) * Analytics.CATEGORY_DIVERSITY_MULTIPLIER)
        
        # Calculate overall health score
        health_score = (
            recency_score * Analytics.RECENCY_WEIGHT +
            engagement_score * Analytics.ENGAGEMENT_WEIGHT +
            quality_score * Analytics.QUALITY_WEIGHT +
            diversity_score * Analytics.DIVERSITY_WEIGHT
        )
        
        # Generate insights
        insights = self._generate_insights(entries, category_dist, health_score)
        
        return {
            "health_score": round(health_score, 1),
            "total_interactions": total_interactions,
            "last_interaction": latest_date,
            "days_since_last": days_since_last,
            "category_distribution": dict(category_dist),
            "confidence_avg": round(avg_confidence, 2),
            "recency_score": round(recency_score, 1),
            "engagement_score": round(engagement_score, 1),
            "quality_score": round(quality_score, 1),
            "diversity_score": round(diversity_score, 1),
            "insights": insights
        }
```

#### Comprehensive Health Check

**Flow:**
1. Run all health checks in parallel where possible
2. Categorize checks:
   - **Core System**: database, Redis, Celery, system resources
   - **Database Operations**: migrations, consistency, transactions, pooling
   - **Background Jobs**: task queuing, failure handling
   - **External Services**: AI services, ChromaDB
   - **Security**: password hashing, input sanitization
   - **Performance**: API performance, concurrent users
3. Calculate overall health percentage
4. Determine status: `healthy` (≥90%), `degraded` (≥70%), `unhealthy` (<70%)

**Code Example:**
```python
def get_comprehensive_health(self) -> Dict[str, Any]:
    """Get comprehensive system health status with all new checks"""
    checks = {
        # Core system checks
        'database': self.check_database(),
        'redis': self.check_redis(),
        'celery': self.check_celery(),
        'system': self.check_system_resources(),
        
        # Database operations & data integrity
        'database_migrations': self.check_database_migrations(),
        'data_consistency': self.check_data_consistency(),
        'transaction_rollbacks': self.check_transaction_rollbacks(),
        'connection_pooling': self.check_connection_pooling(),
        
        # Background job processing
        'task_queuing': self.check_task_queuing(),
        'task_failure_handling': self.check_task_failure_handling(),
        
        # External service dependencies
        'ai_service_connectivity': self.check_ai_service_connectivity(),
        'chromadb_connectivity': self.check_chromadb_connectivity(),
        
        # Security & authentication
        'password_hashing': self.check_password_hashing(),
        'input_sanitization': self.check_input_sanitization(),
        
        # Network & performance
        'api_performance': self.check_api_performance(),
        'concurrent_users': self.check_concurrent_users()
    }
    
    # Determine overall status
    healthy_checks = sum(1 for check in checks.values() if check.get('status') == 'healthy')
    total_checks = len(checks)
    health_percentage = (healthy_checks / total_checks) * 100
    
    if health_percentage >= 90:
        overall_status = 'healthy'
    elif health_percentage >= 70:
        overall_status = 'degraded'
    else:
        overall_status = 'unhealthy'
    
    uptime = datetime.utcnow() - self.start_time
    
    return {
        'status': overall_status,
        'health_percentage': round(health_percentage, 1),
        'healthy_checks': healthy_checks,
        'total_checks': total_checks,
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': uptime.total_seconds(),
        'checks': checks
    }
```

#### Test Run Analytics

**Flow:**
1. User triggers test run via `/api/analytics/test-runs` (POST)
2. Celery task `run_test_suite` executes pytest with specified markers
3. Task parses JUnit XML output and stores results in database
4. Results include: test name, status, execution time, failure messages
5. Dashboard aggregates: success rate, trends, category breakdowns

**Code Example:**
```python
@analytics_bp.route('/test-runs', methods=['POST'])
@login_required
def start_test_run():
    """Start a real test run using Celery background worker."""
    try:
        body = request.get_json(silent=True) or {}
        markers = body.get('markers')
        parallel = bool(body.get('parallel', True))
        
        # Get Celery app
        celery_app = current_app.extensions.get('celery_app')
        if celery_app is None:
            from app.celery_app import celery_app
            current_app.extensions['celery_app'] = celery_app
        
        # Import test_tasks to ensure registration
        from app.tasks import test_tasks
        
        # Enqueue task
        task_name = 'app.tasks.test_tasks.run_test_suite'
        task = celery_app.send_task(
            task_name, 
            kwargs={
                'markers': markers, 
                'parallel': parallel, 
                'triggered_by': 'admin'
            }
        )
        
        return jsonify({
            'task_id': task.id,
            'message': 'Test run started successfully',
            'status': 'running'
        }), 202
        
    except Exception as exc:
        logger.exception('Failed to start test run')
        return jsonify({
            'error': 'failed_to_start', 
            'detail': str(exc)
        }), 500
```

### Data Flow Diagrams

```
┌─────────────────────────────────────────────────────────────┐
│              Analytics & Insights Flow                       │
└─────────────────────────────────────────────────────────────┘

Relationship Health Score:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Contact    │────▶│ Synthesized  │────▶│   Metrics    │
│      ID      │     │   Entries    │     │ Calculation  │
└──────────────┘     └──────────────┘     └──────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────┐
                                            │ Health Score │
                                            │  + Insights  │
                                            └──────────────┘

System Health Check:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Health     │────▶│   Multiple   │────▶│   Aggregate  │
│  Checker     │     │   Checks     │     │   Results    │
└──────────────┘     └──────────────┘     └──────────────┘
      │                     │                      │
      │                     │                      │
      ▼                     ▼                      ▼
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│Database │      │   Redis/     │      │   Celery/    │
│         │      │   External   │      │   System     │
└──────────┘      └──────────────┘      └──────────────┘
```

### Integration Points

1. **Database**: Queries `synthesized_entries`, `contacts`, `test_runs`, `test_results`
2. **Celery**: Async test execution, health check tasks
3. **Redis**: Health check connectivity test
4. **AI Services**: Connectivity and response quality checks
5. **ChromaDB**: Vector database connectivity checks
6. **Monitoring**: Metrics collection and aggregation

### Common Patterns

1. **Weighted Scoring**: Health scores use weighted averages for different factors
2. **Threshold-Based Insights**: Recommendations based on configurable thresholds
3. **Async Processing**: Long-running operations (test runs, diagnostics) use Celery
4. **Fallback Mechanisms**: Direct execution if Celery unavailable
5. **Comprehensive Checks**: Multiple health checks aggregated into overall status

### Security Considerations

1. **Authentication Required**: All analytics endpoints require `@login_required`
2. **Admin-Only Access**: Some endpoints (test runs, diagnostics) may be admin-only
3. **Data Isolation**: Health checks don't expose sensitive user data
4. **Input Validation**: Test markers and parameters validated before execution

### Performance Considerations

1. **Caching**: Health check results can be cached (5-minute TTL)
2. **Parallel Execution**: Health checks run in parallel where possible
3. **Timeout Handling**: Health checks have timeouts to prevent hanging
4. **Efficient Queries**: Analytics queries use indexes and aggregations
5. **Batch Processing**: Test results stored in batches

### Error Scenarios

1. **No Data Available**: Return zero scores with helpful messages
2. **Database Unavailable**: Health check returns `unhealthy` status
3. **Celery Unavailable**: Fall back to direct execution
4. **AI Service Errors**: Handle rate limits, invalid keys gracefully
5. **Test Execution Failures**: Store error messages in test run record

### Frontend Implementation

**Analytics Dashboard** (`templates/admin_dashboard.html`, `static/js/analytics.js`)
- Real-time health status indicators
- Interactive charts (Chart.js or similar)
- Test run history table with filters
- Trend visualization (line charts)
- Category breakdown (donut charts)
- Recommendations list with priority badges

**Key Frontend Functions:**
```javascript
// Fetch comprehensive health
async function fetchHealthStatus() {
    const response = await fetch('/api/analytics/health/comprehensive');
    const data = await response.json();
    updateHealthIndicators(data);
}

// Start test run
async function startTestRun(markers) {
    const response = await fetch('/api/analytics/test-runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markers, parallel: true })
    });
    const { task_id } = await response.json();
    pollTestRunStatus(task_id);
}

// Poll test run status
async function pollTestRunStatus(taskId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/analytics/test-runs/${taskId}`);
        const data = await response.json();
        if (data.run.status === 'completed') {
            clearInterval(interval);
            updateTestResults(data);
        }
    }, 2000);
}
```

### Testing Strategy

**Current Coverage:**
- ✅ Integration tests for analytics dashboard (`test_admin_dashboard.py`)
- ✅ Integration tests for health checks (`test_comprehensive_health_checks.py`)
- ✅ Unit tests for health checker methods (`test_monitoring.py`)
- ⚠️ Limited tests for relationship analytics (no dedicated test file)

**Recommended Test Suite:**

**Unit Tests** (`tests/unit/test_analytics.py`):
```python
def test_calculate_health_score_no_data():
    """Test health score calculation with no entries"""
    analytics = RelationshipAnalytics()
    result = analytics.calculate_relationship_health_score(999)
    assert result['health_score'] == 0
    assert 'No data available' in result['insights'][0]

def test_calculate_health_score_weighted_average():
    """Test health score uses correct weights"""
    # Create test entries
    # Verify weighted calculation matches expected formula

def test_health_checker_database():
    """Test database health check"""
    checker = HealthChecker()
    result = checker.check_database()
    assert result['status'] in ['healthy', 'unhealthy']
    assert 'response_time' in result

def test_health_checker_comprehensive():
    """Test comprehensive health aggregation"""
    checker = HealthChecker()
    result = checker.get_comprehensive_health()
    assert 'status' in result
    assert 'health_percentage' in result
    assert 0 <= result['health_percentage'] <= 100
```

**Integration Tests** (`tests/integration/test_analytics.py`):
```python
def test_analytics_dashboard_requires_auth(client):
    """Test analytics dashboard requires authentication"""
    response = client.get('/api/analytics/dashboard/overview')
    assert response.status_code == 401

def test_analytics_health_comprehensive(client, authenticated_user):
    """Test comprehensive health check endpoint"""
    response = client.get('/api/analytics/health/comprehensive')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'checks' in data

def test_analytics_test_run_flow(client, authenticated_user):
    """Test complete test run flow"""
    # Start test run
    response = client.post('/api/analytics/test-runs', json={
        'markers': ['unit'],
        'parallel': False
    })
    assert response.status_code == 202
    task_id = response.get_json()['task_id']
    
    # Poll for completion
    # Verify results stored in database
```

**Test Coverage Goals:**
- Unit tests: 80%+ coverage for analytics calculations
- Integration tests: All API endpoints covered
- Health checks: All check methods tested
- Error scenarios: Graceful degradation tested

---

## Feature 10: Calendar Integration

### Overview
Extract dates/times from notes, create calendar events from actionable items, and sync with external calendars (Google Calendar).

### User-Facing Pages
- **Calendar View** (optional, or in Settings)
  - Upcoming events list
  - Event creation form
  - Calendar sync status

### API Endpoints

**`GET /api/calendar/events`**
- Get upcoming calendar events
- Query params: `start_date`, `end_date`
- Response: `[{ "id": int, "title": string, "date": string, "contact_id": int }]`

**`POST /api/calendar/create-from-actionable`**
- Create event from actionable item
- Request: `{ "actionable_id": int, "date": string, "title": string }`

**`POST /api/calendar/extract-datetime`**
- Extract date/time from text (NLP)
- Request: `{ "text": string }`
- Response: `{ "datetime": string, "confidence": float }`

### Services

**CalendarService** (`app/services/calendar_service.py`)
- `extract_datetime(text)` - NLP date/time extraction
- `create_event(user_id, title, date, contact_id)` - Create calendar event
- `get_upcoming_events(user_id, start_date, end_date)` - Retrieve events
- `sync_with_google(user_id)` - Sync with Google Calendar (if implemented)

### Frontend Implementation

**Calendar Integration** (`static/js/calendar.js` or similar)
- Event list display
- Date picker for event creation
- Actionable item → event conversion

### Testing Approach
- Test date/time extraction accuracy
- Test event creation
- Test calendar sync (if implemented)

---

## Feature 11: Admin Functions

### Overview
Admin-only functions for user management, data export/import, system diagnostics, and platform administration. Provides comprehensive administrative tools for managing users, exporting/importing data, initializing the database, and monitoring system health.

### User-Facing Pages
- **Admin Dashboard** (`/admin/dashboard`)
  - User management table with role assignment
  - Export/import tools (CSV format)
  - System diagnostics and health monitoring
  - Performance metrics visualization
  - Database initialization tools
  - Test run management

### API Endpoints

**`GET /api/admin/users`**
- List all users (admin only)
- Response: `{ "users": [{ "id": int, "username": string, "role": string, "created_at": "..." }] }`

**`GET /api/admin/dashboard`**
- Render admin dashboard page
- Response: HTML page

**`GET /api/admin/init-database`**
- Initialize database schema and create default admin user
- Response: `{ "status": "success", "message": "...", "admin_username": "...", "admin_password": "..." }`

**`GET /api/admin/export/all-users-csv`**
- Export all users' contacts to CSV (admin only)
- Response: CSV file download with headers `Content-Disposition: attachment; filename="all_users_contacts.csv"`

**`POST /api/admin/import/all-users-csv`**
- Import contacts for all users from CSV (admin only)
- Request: Multipart form with `backup_file` field
- Response: `{ "status": "success", "total_rows": int, "created": int, "updated": int, "errors": [...] }`

### Database Models

**User** (`app/models.py`)
```python
class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_plaintext = Column(String(255), nullable=True)  # For admin viewing only
    role = Column(String(50), nullable=False, default='user')  # 'user' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contacts = relationship("Contact", back_populates="user")
```

### Services

**Admin Functions** (implemented directly in `app/api/admin.py`)
- User listing and management
- Database initialization
- Export/import via `ExportService` and `ImportService`

**ExportService** (`app/services/export_service.py`)
- `generate_contacts_csv(rows)` - Generate CSV from contact data

**ImportService** (`app/services/import_service.py`)
- `parse_and_validate(csv_bytes)` - Parse and validate CSV
- `upsert_contacts(session, rows)` - Upsert contacts into database

### High-Level Implementation

#### Admin Access Control

**Flow:**
1. All admin endpoints use `@login_required` decorator
2. Additional `@admin_required` decorator checks user role
3. Returns 403 Forbidden if user is not admin

**Code Example:**
```python
def admin_required(f):
    """Admin permission decorator"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if getattr(current_user, 'role', 'user') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        with DatabaseManager().get_session() as session:
            from app.models import User
            users = session.query(User).all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'username': user.username,
                    'role': getattr(user, 'role', 'user'),
                    'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
                })
            return jsonify({'users': user_list})
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

#### Database Initialization

**Flow:**
1. Check if admin user exists
2. If not, create default admin user with credentials from environment variables
3. Hash password using PBKDF2-SHA256
4. Store both hashed password and plaintext (for admin viewing only)
5. Return admin credentials in response

**Code Example:**
```python
@admin_bp.route('/init-database', methods=['GET'])
@login_required
@admin_required
@inject
def init_database(db_manager: DatabaseManager = Provide[Container.db_manager]):
    """Initialize database schema and create default admin user"""
    try:
        from sqlalchemy import text
        from werkzeug.security import generate_password_hash
        from app.models import User
        
        logger.info("🔧 Starting database initialization...")
        
        with db_manager.get_session() as session:
            messages = []
            
            # Check if admin user exists
            admin_user = session.query(User).filter(User.username == 'admin').first()
            
            if not admin_user:
                logger.info("🔧 Creating default admin user...")
                
                default_admin_user = os.getenv('DEFAULT_ADMIN_USER', 'admin')
                default_admin_pass = os.getenv('DEFAULT_ADMIN_PASS', 'admin123')
                hashed = generate_password_hash(default_admin_pass, method='pbkdf2:sha256')
                
                admin_user = User(
                    username=default_admin_user,
                    password_hash=hashed,
                    password_plaintext=default_admin_pass,  # For debugging only
                    role='admin'
                )
                
                session.add(admin_user)
                session.commit()
                
                messages.append(f"✅ Created default admin user: {default_admin_user}")
                logger.info(f"✅ Created admin user: {default_admin_user}")
                
                return jsonify({
                    "status": "success",
                    "message": "; ".join(messages),
                    "admin_username": default_admin_user,
                    "admin_password": default_admin_pass
                })
            else:
                logger.info(f"✅ Admin user already exists: {admin_user.username}")
                
                return jsonify({
                    "status": "success",
                    "message": f"Admin user '{admin_user.username}' already exists",
                    "admin_username": admin_user.username,
                    "admin_password": admin_user.password_plaintext or "Password not stored in plaintext"
                })
                
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize database: {str(e)}"
        }), 500
```

#### Export All Users CSV

**Flow:**
1. Verify admin access
2. Query all users and their contacts
3. Build row dictionaries with user and contact data
4. Generate CSV using `ExportService`
5. Return CSV file with appropriate headers

**Code Example:**
```python
@admin_export_import_bp.route('/export/all-users-csv', methods=['GET'])
@login_required
def export_all_users_csv():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    
    from app.services.export_service import ExportService
    from app.utils.database import DatabaseManager
    from app.models import User, Contact
    
    dm = DatabaseManager()
    with dm.get_session() as session:
        # Build row dicts per contact
        rows = []
        users = session.query(User).all()
        for u in users:
            contacts = session.query(Contact).filter_by(user_id=u.id).all()
            for c in contacts:
                cf = c.custom_fields or {}
                rows.append({
                    'user_id': u.id,
                    'user_username': getattr(u, 'username', ''),
                    'user_email': getattr(u, 'email', ''),
                    'contact_id': c.id,
                    'contact_external_id': c.vector_collection_id,
                    'contact_name': c.full_name,
                    'contact_phone': c.telegram_phone,
                    'contact_email': (cf or {}).get('email'),
                    'categories': cf.get('categories'),
                    'tags': cf.get('tags'),
                    'sources': cf.get('sources'),
                    'raw_logs_json': cf.get('raw_logs'),
                    'edits_json': cf.get('edits'),
                    'created_at': c.created_at.isoformat() if c.created_at else '',
                    'updated_at': c.updated_at.isoformat() if c.updated_at else '',
                })
        csv_bytes = ExportService.generate_contacts_csv(rows)
    
    return Response(
        csv_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename="all_users_contacts.csv"'}
    )
```

#### Import All Users CSV

**Flow:**
1. Verify admin access
2. Validate file upload
3. Parse and validate CSV using `ImportService`
4. Upsert contacts into database
5. Return summary of created/updated records

**Code Example:**
```python
@admin_export_import_bp.route('/import/all-users-csv', methods=['POST'])
@login_required
def import_all_users_csv():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    
    if 'backup_file' not in request.files:
        return jsonify({'error': 'CSV file is required (field name: backup_file)'}), 400
    
    file = request.files['backup_file']
    data = file.read()
    
    from app.services.import_service import ImportService
    from app.utils.database import DatabaseManager
    
    dm = DatabaseManager()
    rows, parse_errors = ImportService.parse_and_validate(data)
    
    if parse_errors:
        return jsonify({'status': 'error', 'errors': parse_errors}), 400
    
    with dm.get_session() as session:
        result = ImportService.upsert_contacts(session, rows)
    
    return jsonify({
        'status': 'success',
        'total_rows': result.total_rows,
        'created': result.created,
        'updated': result.updated,
        'errors': result.errors
    })
```

### Data Flow Diagrams

```
┌─────────────────────────────────────────────────────────────┐
│              Admin Functions Flow                            │
└─────────────────────────────────────────────────────────────┘

User Management:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Admin      │────▶│   Verify     │────▶│   Query      │
│  Request     │     │   Access     │     │   Users      │
└──────────────┘     └──────────────┘     └──────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────┐
                                            │   Return     │
                                            │ User List    │
                                            └──────────────┘

Export Flow:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Admin      │────▶│   Query All  │────▶│   Generate   │
│  Request     │     │   Users &     │     │     CSV      │
│              │     │   Contacts    │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────┐
                                            │   Download   │
                                            │   CSV File   │
                                            └──────────────┘

Import Flow:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CSV File   │────▶│   Parse &    │────▶│   Upsert     │
│   Upload     │     │   Validate   │     │  Contacts    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────┐
                                            │   Return     │
                                            │   Summary    │
                                            └──────────────┘
```

### Integration Points

1. **Database**: Direct queries to `users`, `contacts` tables
2. **ExportService**: CSV generation for contact data
3. **ImportService**: CSV parsing and validation
4. **Authentication**: Flask-Login for user verification
5. **Authorization**: Role-based access control (admin only)

### Common Patterns

1. **Decorator Pattern**: `@admin_required` decorator for access control
2. **Dependency Injection**: Services injected via Container
3. **Error Handling**: Try-catch blocks with proper error responses
4. **Session Management**: Context managers for database sessions
5. **File Handling**: Secure file uploads with validation

### Security Considerations

1. **Admin-Only Access**: All endpoints require admin role
2. **Authentication Required**: `@login_required` on all endpoints
3. **Password Security**: Passwords hashed with PBKDF2-SHA256
4. **Input Validation**: CSV files validated before processing
5. **SQL Injection Prevention**: Use parameterized queries
6. **File Upload Security**: Validate file types and sizes

### Performance Considerations

1. **Efficient Queries**: Use eager loading for relationships
2. **Batch Processing**: Import contacts in batches
3. **Streaming Responses**: Stream large CSV exports
4. **Caching**: Cache user lists if frequently accessed
5. **Async Processing**: Consider Celery for large imports

### Error Scenarios

1. **Unauthorized Access**: Return 403 Forbidden
2. **Missing File**: Return 400 Bad Request with error message
3. **Invalid CSV**: Return parse errors in response
4. **Database Errors**: Rollback transactions, return 500
5. **Admin User Exists**: Return existing user info instead of error

### Frontend Implementation

**Admin Dashboard** (`templates/admin_dashboard.html`, `static/js/admin.js`)
- User management table with role badges
- Export/import buttons with file upload
- Database initialization button
- System health indicators
- Test run management interface

**Key Frontend Functions:**
```javascript
// Get all users
async function loadUsers() {
    const response = await fetch('/api/admin/users');
    const data = await response.json();
    renderUserTable(data.users);
}

// Export CSV
function exportAllUsersCSV() {
    window.location.href = '/api/admin/export/all-users-csv';
}

// Import CSV
async function importAllUsersCSV(file) {
    const formData = new FormData();
    formData.append('backup_file', file);
    
    const response = await fetch('/api/admin/import/all-users-csv', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    showImportResults(result);
}

// Initialize database
async function initDatabase() {
    const response = await fetch('/api/admin/init-database');
    const data = await response.json();
    if (data.status === 'success') {
        showAdminCredentials(data);
    }
}
```

### Testing Strategy

**Current Coverage:**
- ✅ Integration tests for admin dashboard (`test_admin_dashboard.py`)
- ✅ Integration tests for export/import (`test_export_import.py`, `test_csv_import_export.py`)
- ✅ Integration tests for user management (`test_admin_dashboard.py`)
- ✅ Access control tests (auth required, admin required)

**Recommended Test Suite:**

**Unit Tests** (`tests/unit/test_admin.py`):
```python
def test_admin_required_decorator():
    """Test admin_required decorator blocks non-admin users"""
    # Create non-admin user
    # Attempt to access admin endpoint
    # Verify 403 response

def test_admin_required_allows_admin():
    """Test admin_required decorator allows admin users"""
    # Create admin user
    # Access admin endpoint
    # Verify success
```

**Integration Tests** (`tests/integration/test_admin_dashboard.py`):
```python
def test_admin_dashboard_requires_auth(client):
    """Test admin dashboard requires authentication"""
    response = client.get('/api/admin/dashboard')
    assert response.status_code == 401

def test_admin_dashboard_requires_admin(client, authenticated_user):
    """Test admin dashboard requires admin role"""
    response = client.get('/api/admin/dashboard')
    assert response.status_code == 403

def test_admin_users_success(client, authenticated_admin_user):
    """Test admin can list all users"""
    response = client.get('/api/admin/users')
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert isinstance(data['users'], list)

def test_admin_export_all_users_csv_success(client, authenticated_admin_user):
    """Test admin can export all users CSV"""
    response = client.get('/api/admin/export/all-users-csv')
    assert response.status_code == 200
    assert response.content_type == 'text/csv'
    assert 'Content-Disposition' in response.headers

def test_admin_import_all_users_csv_success(client, authenticated_admin_user):
    """Test admin can import all users CSV"""
    # Create test CSV file
    csv_data = b'user_id,contact_name\n1,Test Contact'
    response = client.post(
        '/api/admin/import/all-users-csv',
        data={'backup_file': (io.BytesIO(csv_data), 'test.csv')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

def test_admin_init_database_success(client, authenticated_admin_user):
    """Test admin can initialize database"""
    response = client.get('/api/admin/init-database')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'admin_username' in data

def test_admin_permissions_isolation(client, db_session):
    """Test admin cannot access other users' data incorrectly"""
    # Create two users
    # Verify admin can see both, but regular user cannot see other's data
```

**Test Coverage Goals:**
- Unit tests: 80%+ coverage for admin decorators and utilities
- Integration tests: All admin endpoints covered
- Access control: All permission checks tested
- Error scenarios: Invalid inputs, unauthorized access tested

---

## Cross-Cutting Concerns

### Authentication & Authorization

**Flask-Login Integration** (`app/__init__.py`)

**Configuration:**
```python
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'  # Strong session protection
```

**User Loader:**
```python
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        from app.utils.database import DatabaseManager
        from app.models import User
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == int(user_id)).first()
            if user:
                # Create lightweight AuthUser to avoid SQLAlchemy session issues
                from app.api.auth import AuthUser
                return AuthUser(user.id, user.username, getattr(user, 'role', 'user'))
            return None
    except Exception as e:
        logging.error(f"Error loading user {user_id}: {e}")
        return None
```

**AuthUser Class** (`app/api/auth.py`):
```python
from flask_login import UserMixin

class AuthUser(UserMixin):
    """Lightweight user object for Flask-Login"""
    def __init__(self, user_id, username, role='user'):
        self.id = user_id
        self.username = username
        self.role = role
    
    def is_admin(self):
        return self.role == 'admin'
```

**Session Configuration:**
```python
# Session security settings
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

**Protected Routes:**
```python
from flask_login import login_required, current_user

@app.route('/api/protected')
@login_required
def protected_route():
    user_id = current_user.id
    username = current_user.username
    # Route logic here
```

### Database Management

**DatabaseManager** (`app/utils/database.py`)

**Connection Management:**
```python
class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._database_url = self._resolve_database_url()
    
    def _resolve_database_url(self) -> str:
        """Resolve database URL from environment or defaults"""
        # Allow forcing SQLite for tests
        if os.getenv('FORCE_SQLITE_FOR_TESTS') == '1' or os.getenv('FLASK_ENV') == 'testing':
            return 'sqlite:///kith_platform.db'
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            database_url = 'sqlite:///kith_platform.db'
        
        # Normalize postgres:// to postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        return database_url
    
    def _ensure_engine(self):
        """Create database engine if not exists"""
        if self.engine is not None:
            return
        
        engine_url = self._database_url
        if engine_url.startswith('postgresql://') and '+psycopg' not in engine_url:
            engine_url = engine_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        
        self.engine = create_engine(
            engine_url, 
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,  # Connection pool size
            max_overflow=20  # Max overflow connections
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine, 
            expire_on_commit=False  # Keep objects usable after commit
        )
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        self._ensure_engine()
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
```

**Key Features:**
- **Connection Pooling**: Reuses connections for better performance
- **Pool Pre-ping**: Verifies connections before use (handles stale connections)
- **Session Management**: Context manager ensures proper cleanup
- **Transaction Handling**: Automatic rollback on errors
- **Environment-Aware**: Supports SQLite for tests, PostgreSQL for production

**Migrations** (`migrations/`)
- **Alembic**: Database schema version control
- **Migration Commands**:
  ```bash
  alembic revision --autogenerate -m "description"
  alembic upgrade head
  alembic downgrade -1
  ```

### Logging & Monitoring

**Structured Logging** (`app/utils/logging_config.py`)

**Setup:**
```python
def setup_logging(
    app_name: str = "kith_platform",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 10,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """Setup comprehensive logging configuration"""
    
    # Create logs directory
    if enable_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()
    
    # Formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    colored_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(colored_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers with rotation
    if enable_file:
        # Main application log
        app_log_file = os.path.join(log_dir, f"{app_name}.log")
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log (errors only)
        error_log_file = os.path.join(log_dir, f"{app_name}_errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Celery tasks log
        celery_log_file = os.path.join(log_dir, f"{app_name}_celery.log")
        celery_handler = logging.handlers.RotatingFileHandler(
            celery_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        celery_handler.setLevel(logging.INFO)
        celery_handler.setFormatter(detailed_formatter)
        
        celery_logger = logging.getLogger('celery')
        celery_logger.addHandler(celery_handler)
        celery_logger.setLevel(logging.INFO)
```

**Structured Logging** (`app/utils/structured_logging.py`):
```python
class StructuredLogger:
    """Structured logging utility for the application"""
    
    @staticmethod
    def setup_logging(app):
        """Set up structured logging for the application"""
        # JSON formatter for structured logs
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for JSON logs
        file_handler = logging.FileHandler(
            os.path.join('logs', 'kith_platform_structured.log'),
            encoding='utf-8'
        )
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    @staticmethod
    def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None):
        """Log user actions with structured data"""
        logger = logging.getLogger('user_actions')
        log_data = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        logger.info('User action', extra=log_data)
```

**Performance Logging:**
```python
class PerformanceLogger:
    """Logger for performance metrics"""
    
    def log_database_query(self, query: str, duration: float, rows_affected: Optional[int] = None):
        """Log database query performance"""
        rows_info = f"rows={rows_affected}" if rows_affected is not None else ""
        self.logger.info(f"DB Query | duration={duration:.3f}s | {rows_info} | {query[:100]}...")
    
    def log_ai_processing(self, operation: str, duration: float, tokens_used: Optional[int] = None):
        """Log AI processing performance"""
        tokens_info = f"tokens={tokens_used}" if tokens_used else ""
        self.logger.info(f"AI Processing | {operation} | duration={duration:.3f}s | {tokens_info}")
```

**Monitoring** (`app/utils/monitoring.py`)
- **HealthChecker**: Comprehensive system health checks (see Feature 9)
- **MetricsCollector**: Performance metrics collection (see Feature 9)

### Caching

**Frontend Cache Manager** (`static/js/cache-manager.js`)
- 5-minute TTL for search results
- Cache hit/miss tracking
- Invalidation strategies
- LocalStorage-based caching

**Backend Redis Caching** (Flask-Caching)
```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
})
cache.init_app(app)

# Usage
@cache.cached(timeout=300, key_prefix='contacts')
def get_contacts(user_id):
    # Expensive query
    return contacts
```

### Error Handling

**Global Error Handlers** (`app/__init__.py`)

**404 Handler:**
```python
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404
```

**500 Handler:**
```python
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {error}", exc_info=True)
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500
```

**Exception Handler:**
```python
@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500
```

**Security Headers:**
```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://unpkg.com https://cdn.jsdelivr.net; "
        "frame-ancestors 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # Strict Transport Security (HTTPS only)
    if app.config.get('FORCE_HTTPS', False):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response
```

### Dependency Injection

**Container** (`app/utils/dependencies.py`)

**Configuration:**
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """Dependency injection container"""
    
    config = providers.Configuration()
    
    # Singleton services
    db_manager = providers.Singleton(DatabaseManager)
    ai_service = providers.Singleton(AIService)
    
    # Factory services (new instance per request)
    auth_service = providers.Factory(AuthService, db_manager=db_manager)
    note_service = providers.Factory(
        NoteService,
        db_manager=db_manager,
        ai_service=ai_service
    )
    contact_service = providers.Factory(ContactService, db_manager=db_manager)
    tag_service = providers.Factory(TagService, db_manager=db_manager)
    file_service = providers.Factory(FileService, db_manager=db_manager)
    search_service = providers.Factory(SearchService, db_manager=db_manager)
```

**Usage in Routes:**
```python
from dependency_injector.wiring import inject, Provide

@contacts_bp.route('/', methods=['GET'])
@login_required
@inject
def get_contacts(contact_service: ContactService = Provide[Container.contact_service]):
    contacts = contact_service.get_contacts_by_user(current_user.id)
    return jsonify([c.to_dict() for c in contacts])
```

**Benefits:**
- **Testability**: Easy to mock services in tests
- **Loose Coupling**: Services don't directly instantiate dependencies
- **Configuration**: Centralized service configuration
- **Lifecycle Management**: Singleton vs Factory pattern support

### Testing Strategy

**Current Coverage:**
- ✅ Unit tests for database manager (`test_database.py`)
- ✅ Unit tests for logging (`test_monitoring.py`)
- ✅ Integration tests for authentication (`test_auth_service.py`)
- ✅ Integration tests for dependency injection

**Recommended Test Suite:**

**Unit Tests** (`tests/unit/test_database.py`):
```python
def test_database_manager_connection():
    """Test database manager creates connections"""
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1

def test_database_manager_transaction_rollback():
    """Test transaction rollback on error"""
    db_manager = DatabaseManager()
    try:
        with db_manager.get_session() as session:
            # Intentionally cause error
            session.execute(text("INVALID SQL"))
    except Exception:
        pass
    # Verify rollback occurred
```

**Integration Tests** (`tests/integration/test_auth.py`):
```python
def test_login_required_decorator(client):
    """Test @login_required blocks unauthenticated requests"""
    response = client.get('/api/contacts')
    assert response.status_code == 401

def test_current_user_available(client, authenticated_user):
    """Test current_user available in authenticated routes"""
    response = client.get('/api/contacts')
    assert response.status_code == 200
```

**Test Coverage Goals:**
- Unit tests: 80%+ coverage for utilities
- Integration tests: All decorators and middleware tested
- Error handling: All error scenarios covered

---

## Deployment & Production

### Environment Configuration

**Production Settings**

**Environment Variables** (`.env` or Render.com environment):
```bash
# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=<generated-secret-key>
FLASK_APP=main.py

# Database
DATABASE_URL=postgresql://user:password@host:5432/kith_platform

# Redis
REDIS_URL=redis://host:6379/0

# AI Services
GEMINI_API_KEY=<your-gemini-key>
OPENAI_API_KEY=<your-openai-key>
GOOGLE_APPLICATION_CREDENTIALS_JSON=<json-credentials>

# Telegram
TELEGRAM_API_ID=<your-api-id>
TELEGRAM_API_HASH=<your-api-hash>

# Admin
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASS=<secure-password>

# Logging
LOG_LEVEL=INFO

# Security
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
```

**Configuration Classes** (`config/settings.py`):
```python
class ProductionConfig:
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Security
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

### Docker Support

**Dockerfile** (`Dockerfile`)

**Multi-Stage Build:**
```dockerfile
# Base stage
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=main.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Development stage
FROM base as development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
RUN pip install --no-cache-dir pytest pytest-cov
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

# Production stage
FROM base as production
ENV FLASK_ENV=production
COPY docker/production/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
```

**Production Entrypoint** (`docker/production/entrypoint.sh`):
```bash
#!/bin/bash
set -e

# Wait for database
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "Waiting for database..."
    sleep 2
done

# Run database migrations
python -m alembic upgrade head

# Start application
exec "$@"
```

**Docker Compose** (`docker-compose.yml`)

**Complete Stack:**
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: kith_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - kith_network

  # Redis for Celery
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - kith_network

  # Main Application
  web:
    build:
      context: .
      target: production
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/kith_platform
      REDIS_URL: redis://redis:6379/0
      FLASK_ENV: production
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY:-your-secret-key-change-in-production}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    networks:
      - kith_network
    restart: unless-stopped

  # Celery Worker
  celery-worker:
    build:
      context: .
      target: production
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/kith_platform
      REDIS_URL: redis://redis:6379/0
      FLASK_ENV: production
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY:-your-secret-key-change-in-production}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    command: ["python", "celery_worker.py"]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    networks:
      - kith_network
    restart: unless-stopped

  # Celery Beat (Scheduler)
  celery-beat:
    build:
      context: .
      target: production
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/kith_platform
      REDIS_URL: redis://redis:6379/0
      FLASK_ENV: production
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY:-your-secret-key-change-in-production}
    command: ["celery", "-A", "app.celery_app", "beat", "--loglevel=info"]
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - kith_network
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - kith_network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  kith_network:
    driver: bridge
```

**Nginx Configuration** (`docker/nginx/nginx.conf`):
```nginx
upstream flask_app {
    server web:5000;
}

server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://flask_app;
        access_log off;
    }
}
```

### Render.com Deployment

**render.yaml** (`render.yaml`)

**Complete Configuration:**
```yaml
services:
  - type: web
    name: kith-platform
    env: python
    branch: main
    runtime: python-3.11.0
    buildCommand: pip install -r requirements.txt
    startCommand: python init_production_db.py && gunicorn --workers 2 --bind 0.0.0.0:$PORT wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: kith-platform-main-db
          property: connectionString
      - key: REDIS_URL
        value: ${REDIS_URL}
      - key: DEFAULT_ADMIN_USER
        value: admin
      - key: DEFAULT_ADMIN_PASS
        value: admin123
      - key: GEMINI_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: GOOGLE_APPLICATION_CREDENTIALS_JSON
        sync: false
      - key: TELEGRAM_API_ID
        sync: false
      - key: TELEGRAM_API_HASH
        sync: false
    healthCheckPath: /health
    healthCheckTimeout: 300

databases:
  - name: kith-platform-main-db
    databaseName: kith_production
    user: kith_user
    plan: starter
```

**WSGI Application** (`wsgi.py`):
```python
from app import create_app
import os

# Create Flask application
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

**Production Database Initialization** (`init_production_db.py`):
```python
#!/usr/bin/env python3
"""Initialize production database with schema and default admin user"""

from app import create_app
from app.utils.database import DatabaseManager
from app.models import Base, User
from werkzeug.security import generate_password_hash
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_production_database():
    """Initialize database schema and create default admin user"""
    app = create_app()
    
    with app.app_context():
        db_manager = DatabaseManager()
        
        try:
            # Create all tables
            logger.info("Creating database tables...")
            Base.metadata.create_all(db_manager.engine)
            logger.info("✅ Database tables created")
            
            # Create default admin user if not exists
            with db_manager.get_session() as session:
                admin_user = session.query(User).filter(User.username == 'admin').first()
                
                if not admin_user:
                    logger.info("Creating default admin user...")
                    
                    default_admin_user = os.getenv('DEFAULT_ADMIN_USER', 'admin')
                    default_admin_pass = os.getenv('DEFAULT_ADMIN_PASS', 'admin123')
                    hashed = generate_password_hash(default_admin_pass, method='pbkdf2:sha256')
                    
                    admin_user = User(
                        username=default_admin_user,
                        password_hash=hashed,
                        password_plaintext=default_admin_pass,
                        role='admin'
                    )
                    
                    session.add(admin_user)
                    session.commit()
                    logger.info(f"✅ Created admin user: {default_admin_user}")
                else:
                    logger.info(f"✅ Admin user already exists: {admin_user.username}")
            
            logger.info("✅ Database initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    init_production_database()
```

### Gunicorn Configuration

**Gunicorn Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT \
         --workers 2 \
         --worker-class gevent \
         --timeout 120 \
         --max-requests 1000 \
         --max-requests-jitter 50 \
         --access-logfile - \
         --error-logfile - \
         wsgi:application
```

**Gunicorn Config File** (`gunicorn_config.py`):
```python
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gevent'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
```

### Health Checks

**Basic Health Check** (`GET /health`)

**Implementation:**
```python
@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    try:
        # Quick database connectivity check
        from app.utils.database import DatabaseManager
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            session.execute(text("SELECT 1"))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
```

**Comprehensive Health Check** (`GET /api/analytics/health/comprehensive`)
- See Feature 9: Analytics & Insights for detailed implementation

### Deployment Checklist

**Pre-Deployment:**
1. ✅ Set all environment variables
2. ✅ Run database migrations (`alembic upgrade head`)
3. ✅ Create default admin user
4. ✅ Verify database connectivity
5. ✅ Test Redis connectivity
6. ✅ Verify AI service API keys
7. ✅ Test Celery worker connectivity
8. ✅ Run test suite
9. ✅ Check security headers
10. ✅ Verify HTTPS configuration

**Post-Deployment:**
1. ✅ Verify health check endpoint
2. ✅ Test authentication flow
3. ✅ Test admin dashboard access
4. ✅ Monitor error logs
5. ✅ Check performance metrics
6. ✅ Verify file uploads work
7. ✅ Test background jobs (Celery)
8. ✅ Monitor database connections
9. ✅ Check Redis memory usage
10. ✅ Verify backup procedures

### Monitoring & Maintenance

**Log Monitoring:**
- Application logs: `logs/kith_platform.log`
- Error logs: `logs/kith_platform_errors.log`
- Celery logs: `logs/kith_platform_celery.log`

**Database Maintenance:**
```bash
# Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore database
psql $DATABASE_URL < backup_20240101.sql

# Run migrations
alembic upgrade head
```

**Performance Monitoring:**
- Use `/api/analytics/health/comprehensive` for system health
- Monitor database connection pool usage
- Track Redis memory and connection counts
- Monitor Celery task queue length
- Track API response times

### Testing Strategy

**Current Coverage:**
- ✅ Docker Compose setup tested locally
- ✅ Render.com deployment tested
- ✅ Health checks tested (`test_comprehensive_health_checks.py`)
- ⚠️ Limited production deployment tests

**Recommended Test Suite:**

**Integration Tests** (`tests/integration/test_deployment.py`):
```python
def test_health_check_endpoint(client):
    """Test basic health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] in ['healthy', 'unhealthy']

def test_production_config():
    """Test production configuration loads correctly"""
    os.environ['FLASK_ENV'] = 'production'
    app = create_app()
    assert not app.config['DEBUG']
    assert app.config['TESTING'] == False

def test_database_initialization():
    """Test production database initialization"""
    # Test init_production_db.py script
    # Verify tables created
    # Verify admin user created
```

**Test Coverage Goals:**
- Integration tests: All deployment scenarios covered
- Health checks: All endpoints tested
- Configuration: All environment configurations tested
- Error scenarios: Deployment failures handled gracefully

---

## Testing Strategy

### Comprehensive Testing Overview

**Current Status:**
- ✅ **Unit Tests**: 6 test files, ~100+ test functions
- ✅ **Integration Tests**: 15+ test files, ~400+ test functions  
- ⚠️ **Functional Tests**: Partially covered (mixed with integration tests)
- ⚠️ **End-to-End Tests**: Limited (some in `test_app_consolidation.py`)
- ✅ **Automated Tests**: Yes (pytest with markers)
- ✅ **Regression Tests**: Yes (via Celery task, but no CI/CD automation)

**Test Statistics:**
- **Total Test Files**: 29 files
- **Total Test Functions**: 556+ test functions
- **Total Test Code**: ~8,000 lines
- **Coverage Requirement**: 70% minimum (enforced)
- **Test Markers**: `unit`, `integration`, `slow`, `auth`, `admin`, `database`, `api`, `celery`

### Existing Test Suite

**The codebase has a comprehensive automated test suite with 33+ test files and 550+ test functions.**

### Test Structure

```
tests/
├── conftest.py                    # Pytest configuration, test isolation fixtures
├── test_app_consolidation.py     # Comprehensive endpoint tests
│
├── unit/                         # Unit tests (fast, isolated)
│   ├── test_ai_service.py        # AI service logic (mocked)
│   ├── test_auth_service.py      # Authentication service
│   ├── test_api.py               # API endpoint unit tests
│   ├── test_celery_tasks.py      # Celery task unit tests
│   ├── test_database.py           # Database utility tests
│   ├── test_monitoring.py        # Monitoring/health check tests
│   └── test_note_service.py      # Note service logic
│
└── integration/                  # Integration tests (real DB, real services)
    ├── test_api_endpoints.py     # Full API endpoint tests
    ├── test_admin_dashboard.py   # Admin functionality
    ├── test_comprehensive_health_checks.py  # System health checks
    ├── test_csv_import_export.py # CSV import/export
    ├── test_export_import.py     # Data export/import
    ├── test_file_upload.py       # File upload processing
    ├── test_graph_data.py        # Relationship graph
    ├── test_real_ai_services.py   # Real AI API calls (slow)
    ├── test_real_vs_mocked_ai.py  # Comparison of mocked vs real
    ├── test_search_discovery.py  # Search functionality
    ├── test_settings_page.py      # Settings UI
    ├── test_tag_management.py    # Tag CRUD operations
    ├── test_telegram_integration.py  # Telegram sync
    └── test_ui_features.py       # UI feature tests
```

### Test Configuration

**pytest.ini** (`kith-platform/pytest.ini`)
- Coverage requirement: 70% minimum (`--cov-fail-under=70`)
- Coverage reports: terminal + HTML (`htmlcov/`)
- Test markers: `unit`, `integration`, `slow`, `auth`, `admin`, `database`, `api`, `celery`
- Test paths: `tests/` directory
- Warnings: Filtered for SQLAlchemy, deprecation warnings

**Test Isolation** (`tests/conftest.py`)
- Temporary SQLite database per test session
- Temporary ChromaDB directory
- Environment variable isolation
- Automatic cleanup after tests

### Test Types & Coverage

**Unit Tests** (`tests/unit/`)
- ✅ AI Service (mocked Gemini/OpenAI)
- ✅ Auth Service (password hashing, user creation)
- ✅ Database utilities
- ✅ Celery tasks (mocked)
- ✅ Monitoring/health checks
- ✅ Note service logic

**Integration Tests** (`tests/integration/`)
- ✅ API endpoints (full request/response cycle)
- ✅ Authentication flows
- ✅ Contact CRUD operations
- ✅ Tag management
- ✅ Search functionality
- ✅ File upload/processing
- ✅ Telegram integration
- ✅ Admin dashboard
- ✅ UI features
- ✅ Graph data generation
- ✅ Export/import functionality
- ✅ Health checks (comprehensive)
- ✅ Real AI service calls (optional, slow)

**Test Fixtures** (in `tests/test_app_consolidation.py` and `conftest.py`)
- `app` - Flask application instance
- `client` - Test client for HTTP requests
- `authenticated_client` - Pre-authenticated test client
- `sample_contact` - Sample contact data
- `db_session` - Database session
- `db_manager` - Database manager instance
- `sample_user` - Test user with known credentials

### Running Tests

```bash
# All tests
cd kith-platform
pytest

# With coverage report
pytest --cov=app --cov-report=html
# View report: open htmlcov/index.html

# Only unit tests (fast)
pytest -m unit

# Only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Specific test file
pytest tests/integration/test_tag_management.py

# Specific test class
pytest tests/unit/test_auth_service.py::TestAuthService

# Verbose output
pytest -v

# With test output
pytest -s
```

### Test Coverage Goals

**Current Status:**
- Minimum coverage: 70% (enforced in pytest.ini)
- Target coverage: 80%+ overall
- Critical paths: 90%+ (auth, data operations)
- Security-sensitive: 100% (password hashing, input validation)

**Coverage Report:**
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### AI Service Integration Test Strategy

**Overview:**
Robust testing strategy for AI service integrations (OpenAI, Gemini, Google Vision) to ensure reliability, quality, and cost-effectiveness. This strategy covers contract testing, fallback resilience, response quality validation, and cost monitoring.

#### 1. Contract Testing Layer

**Purpose**: Validate that each AI service meets our expected interface contract and returns data in the expected format.

**Test File**: `tests/integration/ai_services/test_ai_contracts.py`

```python
import pytest
from app.services.ai_service import AIService

@pytest.mark.integration
class TestAIServiceContracts:
    """Verify each AI service meets our expected interface contract"""
    
    def test_openai_contract(self, ai_service):
        """Verify OpenAI API response structure"""
        # Test with minimal valid input
        response = ai_service._analyze_with_openai("Test note", "Test Contact")
        
        # Verify contract fields exist
        assert 'categories' in response
        assert isinstance(response['categories'], dict)
        
        # Verify category structure
        for category, data in response['categories'].items():
            assert 'content' in data
            assert 'confidence' in data
            assert isinstance(data['confidence'], (int, float))
            assert 0.0 <= data['confidence'] <= 1.0
    
    @pytest.mark.integration
    def test_gemini_contract(self, ai_service):
        """Verify Gemini API response structure"""
        response = ai_service._analyze_with_gemini("Test note", "Test Contact")
        
        # Same contract validation
        assert 'categories' in response
        assert isinstance(response['categories'], dict)
        
        for category, data in response['categories'].items():
            assert 'content' in data
            assert 'confidence' in data
            assert isinstance(data['confidence'], (int, float))
            assert 0.0 <= data['confidence'] <= 1.0
    
    @pytest.mark.integration
    def test_vision_api_contract(self, vision_service):
        """Verify Vision API response for image processing"""
        import io
        from PIL import Image
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        response = vision_service.extract_text(img_bytes)
        
        assert 'text_annotations' in response or 'text' in response
        assert 'confidence' in response or 'detection_confidence' in response
    
    def assert_contract_fields(self, response, expected_fields):
        """Helper to assert contract fields exist"""
        for field, field_type in expected_fields.items():
            assert field in response, f"Missing field: {field}"
            assert isinstance(response[field], field_type), \
                f"Field {field} should be {field_type}, got {type(response[field])}"
```

**Key Test Cases:**
- ✅ Response structure validation (categories, confidence scores)
- ✅ Data type validation (strings, floats, dicts)
- ✅ Value range validation (confidence 0.0-1.0)
- ✅ Required fields presence
- ✅ Error response format

#### 2. Fallback & Resilience Testing

**Purpose**: Test the multi-provider fallback strategy to ensure graceful degradation when services fail.

**Test File**: `tests/integration/ai_services/test_ai_resilience.py`

```python
import pytest
import time
from unittest.mock import patch, Mock
from app.services.ai_service import AIService

@pytest.mark.integration
class TestAIServiceResilience:
    """Test failover and degradation strategies"""
    
    @pytest.mark.integration
    def test_primary_service_timeout(self, ai_service, monkeypatch):
        """When OpenAI times out, should fallback to Gemini"""
        # Simulate OpenAI timeout
        def timeout_openai(*args, **kwargs):
            time.sleep(0.1)  # Simulate delay
            raise TimeoutError("OpenAI API timeout")
        
        monkeypatch.setattr(ai_service, '_analyze_with_openai', timeout_openai)
        
        # Should fallback to Gemini
        result = ai_service.analyze_note("Important contact note", "Test Contact")
        
        assert 'categories' in result  # Still got results
        assert result.get('provider') == 'gemini' or 'fallback' in str(result).lower()
        logger.info("✅ Fallback to Gemini successful")
    
    @pytest.mark.integration
    def test_rate_limit_handling(self, ai_service):
        """Test behavior when hitting API rate limits"""
        results = []
        rate_limit_hit = False
        
        # Send burst of requests
        for i in range(10):  # Adjust based on rate limits
            try:
                result = ai_service.analyze_note(f"Note {i}", "Test Contact")
                results.append(result)
            except Exception as e:
                if 'rate limit' in str(e).lower() or '429' in str(e):
                    rate_limit_hit = True
                    # Should see graceful degradation
                    assert 'queued' in str(e).lower() or 'retry' in str(e).lower()
                    break
        
        # Should handle rate limits gracefully
        if rate_limit_hit:
            assert len(results) > 0  # Some requests succeeded
            logger.info("✅ Rate limit handled gracefully")
    
    @pytest.mark.integration
    def test_cascade_failure(self, ai_service, monkeypatch):
        """When all AI services fail, should return graceful error"""
        # Mock all services to fail
        def fail_all(*args, **kwargs):
            raise Exception("Service unavailable")
        
        monkeypatch.setattr(ai_service, '_analyze_with_openai', fail_all)
        monkeypatch.setattr(ai_service, '_analyze_with_gemini', fail_all)
        
        result = ai_service.analyze_note("Test note", "Test Contact")
        
        # Should return fallback analysis
        assert result is not None
        assert 'categories' in result or 'error' in result
        assert result.get('status') == 'degraded' or 'fallback' in str(result).lower()
        logger.info("✅ Cascade failure handled gracefully")
    
    @pytest.mark.integration
    def test_retry_logic(self, ai_service, monkeypatch):
        """Test retry logic for transient failures"""
        call_count = [0]
        
        def fail_then_succeed(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Transient error")
            return {'categories': {'Actionable': {'content': 'test', 'confidence': 0.9}}}
        
        monkeypatch.setattr(ai_service, '_analyze_with_gemini', fail_then_succeed)
        
        result = ai_service.analyze_note("Test note", "Test Contact")
        
        assert call_count[0] == 3  # Retried 3 times
        assert 'categories' in result
        logger.info("✅ Retry logic working correctly")
```

**Key Test Cases:**
- ✅ Primary service timeout → Fallback to secondary
- ✅ Rate limit handling → Graceful degradation or queuing
- ✅ Cascade failure → Fallback to local analysis
- ✅ Retry logic → Transient failures retried
- ✅ Exponential backoff → Rate limit retries

#### 3. Response Quality Testing

**Purpose**: Validate that AI responses meet quality thresholds and are consistent across providers.

**Test File**: `tests/integration/ai_services/test_ai_quality.py`

```python
import pytest
from app.services.ai_service import AIService

@pytest.mark.integration
class TestAIResponseQuality:
    """Validate AI response quality and consistency"""
    
    @pytest.mark.integration
    @pytest.mark.parametrize("note_content,expected_categories", [
        ("Met with John from Microsoft about cloud migration", ["Actionable", "Professional_Background"]),
        ("Coffee with Sarah, discussed her new startup", ["Social", "Professional_Background"]),
        ("Doctor appointment with Dr. Smith", ["Admin_matters", "Wellbeing"]),
        ("John mentioned he loves golf and plays every weekend", ["Avocation", "Social"]),
    ])
    def test_categorization_accuracy(self, ai_service, note_content, expected_categories):
        """Test AI categorizes notes appropriately"""
        result = ai_service.analyze_note(note_content, "Test Contact")
        
        assert 'categories' in result
        result_categories = list(result['categories'].keys())
        
        # Check if expected categories are present
        found_categories = [cat for cat in expected_categories if cat in result_categories]
        assert len(found_categories) > 0, \
            f"Expected at least one of {expected_categories}, got {result_categories}"
        
        logger.info(f"✅ Categorization accurate: {found_categories} found in {result_categories}")
    
    @pytest.mark.integration
    def test_entity_extraction_completeness(self, ai_service):
        """Test AI extracts all relevant entities"""
        note = "Meeting with John Smith (CEO of TechCorp) at john@techcorp.com, phone 555-1234"
        result = ai_service.analyze_note(note, "John Smith")
        
        # Check if key information is captured
        categories = result.get('categories', {})
        
        # Professional_Background should contain company info
        if 'Professional_Background' in categories:
            prof_content = categories['Professional_Background'].get('content', '')
            assert 'TechCorp' in prof_content or 'CEO' in prof_content
        
        # Admin_matters should contain contact info
        if 'Admin_matters' in categories:
            admin_content = categories['Admin_matters'].get('content', '')
            assert 'john@techcorp.com' in admin_content or '555-1234' in admin_content
        
        logger.info("✅ Entity extraction complete")
    
    @pytest.mark.integration
    def test_consistency_across_providers(self, ai_service):
        """Same input should give similar results across providers"""
        note = "Important business meeting about Q4 strategy"
        
        # Test with OpenAI (if available)
        openai_result = None
        try:
            openai_result = ai_service._analyze_with_openai(note, "Test Contact")
        except Exception:
            pass
        
        # Test with Gemini (if available)
        gemini_result = None
        try:
            gemini_result = ai_service._analyze_with_gemini(note, "Test Contact")
        except Exception:
            pass
        
        if openai_result and gemini_result:
            openai_cats = set(openai_result.get('categories', {}).keys())
            gemini_cats = set(gemini_result.get('categories', {}).keys())
            overlap = openai_cats.intersection(gemini_cats)
            
            # At least 50% category overlap
            min_overlap = min(len(openai_cats), len(gemini_cats)) * 0.5
            assert len(overlap) >= min_overlap, \
                f"Low category overlap: {overlap} from {openai_cats} vs {gemini_cats}"
            
            logger.info(f"✅ Provider consistency: {len(overlap)} overlapping categories")
    
    @pytest.mark.integration
    def test_confidence_score_reasonableness(self, ai_service):
        """Test confidence scores are reasonable"""
        note = "Clear business meeting about project timeline"
        result = ai_service.analyze_note(note, "Test Contact")
        
        for category, data in result.get('categories', {}).items():
            confidence = data.get('confidence', 0)
            assert 0.0 <= confidence <= 1.0, \
                f"Confidence {confidence} out of range for category {category}"
            
            # Clear notes should have higher confidence
            if 'Actionable' in category or 'Professional_Background' in category:
                assert confidence >= 0.5, \
                    f"Low confidence {confidence} for clear category {category}"
        
        logger.info("✅ Confidence scores reasonable")
    
    @pytest.mark.integration
    def test_empty_note_handling(self, ai_service):
        """Test handling of empty or minimal notes"""
        result = ai_service.analyze_note("", "Test Contact")
        
        # Should return empty or minimal categories
        assert result is not None
        categories = result.get('categories', {})
        
        # Empty note should have few or no categories
        assert len(categories) <= 2, \
            f"Too many categories for empty note: {categories}"
        
        logger.info("✅ Empty note handled correctly")
```

**Key Test Cases:**
- ✅ Categorization accuracy (expected categories found)
- ✅ Entity extraction completeness (names, emails, phones extracted)
- ✅ Consistency across providers (similar results from OpenAI/Gemini)
- ✅ Confidence score reasonableness (0.0-1.0 range, higher for clear notes)
- ✅ Empty note handling (graceful handling of minimal input)

#### 4. Cost and Performance Monitoring Tests

**Purpose**: Track API usage, costs, and performance to optimize spending and response times.

**Test File**: `tests/integration/ai_services/test_ai_costs.py`

```python
import pytest
import time
from app.services.ai_service import AIService
from app.utils.monitoring import MetricsCollector

@pytest.mark.integration
class TestAIServiceCosts:
    """Monitor API usage and costs"""
    
    @pytest.mark.integration
    def test_token_usage_tracking(self, ai_service, metrics_collector):
        """Verify we're tracking token usage correctly"""
        initial_usage = metrics_collector.get_metrics_summary()
        initial_tokens = initial_usage.get('ai.analyze_note', {}).get('total_tokens', 0)
        
        # Process a known-length note
        note = "A" * 1000  # Roughly 250 tokens
        result = ai_service.analyze_note(note, "Test Contact")
        
        final_usage = metrics_collector.get_metrics_summary()
        final_tokens = final_usage.get('ai.analyze_note', {}).get('total_tokens', 0)
        tokens_used = final_tokens - initial_tokens
        
        # Verify token tracking
        assert tokens_used > 0, "Token usage not tracked"
        assert 200 <= tokens_used <= 400, \
            f"Token usage {tokens_used} outside expected range (200-400)"
        
        # Verify cost estimation
        if 'estimated_cost' in result:
            assert result['estimated_cost'] > 0
            assert result['estimated_cost'] < 0.01  # Should be cents for single note
        
        logger.info(f"✅ Token usage tracked: {tokens_used} tokens")
    
    @pytest.mark.integration
    def test_batch_processing_efficiency(self, ai_service):
        """Test batch processing is more efficient than individual calls"""
        notes = [f"Note {i}: Meeting with contact about project" for i in range(10)]
        
        # Individual processing
        individual_start = time.time()
        individual_results = []
        for note in notes:
            result = ai_service.analyze_note(note, "Test Contact")
            individual_results.append(result)
        individual_time = time.time() - individual_start
        
        # Batch processing (if implemented)
        batch_start = time.time()
        try:
            batch_results = ai_service.analyze_notes_batch(notes, "Test Contact")
            batch_time = time.time() - batch_start
            
            assert batch_time < individual_time * 0.7, \
                f"Batch processing {batch_time}s not faster than individual {individual_time}s"
            assert len(batch_results) == len(individual_results)
            logger.info(f"✅ Batch processing {batch_time:.2f}s vs individual {individual_time:.2f}s")
        except NotImplementedError:
            logger.warning("⚠️ Batch processing not implemented")
    
    @pytest.mark.integration
    def test_response_time_monitoring(self, ai_service, metrics_collector):
        """Test response time tracking"""
        start_time = time.time()
        result = ai_service.analyze_note("Test note", "Test Contact")
        duration = time.time() - start_time
        
        # Response should be reasonable (under 10 seconds)
        assert duration < 10.0, f"Response time {duration}s too slow"
        
        # Verify metrics recorded
        metrics = metrics_collector.get_metrics_summary()
        ai_metrics = metrics.get('ai.analyze_note', {})
        assert ai_metrics.get('count', 0) > 0
        assert ai_metrics.get('avg_duration', 0) > 0
        
        logger.info(f"✅ Response time: {duration:.2f}s")
    
    @pytest.mark.integration
    def test_cost_threshold_alerts(self, ai_service, metrics_collector):
        """Test cost threshold alerting"""
        # Simulate high usage
        for i in range(100):
            ai_service.analyze_note(f"Note {i}", "Test Contact")
        
        # Check if cost threshold exceeded
        metrics = metrics_collector.get_metrics_summary()
        total_cost = metrics.get('ai.total_cost', 0)
        
        # Alert if cost exceeds threshold (e.g., $1.00)
        if total_cost > 1.00:
            logger.warning(f"⚠️ Cost threshold exceeded: ${total_cost:.2f}")
            # In production, would trigger alert
        
        logger.info(f"✅ Cost monitoring: ${total_cost:.2f}")
```

**Key Test Cases:**
- ✅ Token usage tracking (accurate token counts)
- ✅ Cost estimation (reasonable cost calculations)
- ✅ Batch processing efficiency (faster than individual calls)
- ✅ Response time monitoring (under threshold)
- ✅ Cost threshold alerts (warnings when exceeded)

#### 5. Integration Test Fixtures

**Purpose**: Create reusable fixtures for consistent AI service testing.

**Test File**: `tests/fixtures/ai_fixtures.py`

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def ai_test_notes():
    """Standardized test notes for consistent testing"""
    return {
        'business': "Meeting with venture capitalists about Series A funding",
        'personal': "Birthday dinner with family at favorite restaurant",
        'health': "Annual checkup with Dr. Johnson, blood pressure normal",
        'complex': "Met John (CEO TechCorp) and Sarah (CFO) at john@tech.com about Q4 cloud migration. Follow up next Tuesday.",
        'actionable': "John asked me to review the proposal by Friday",
        'goals': "Sarah mentioned her goal to expand to 3 new markets this year",
    }

@pytest.fixture
def mock_ai_responses():
    """Predictable AI responses for testing"""
    return {
        'openai': lambda note: {
            'categories': {
                'Actionable': {'content': 'Follow up required', 'confidence': 0.95} 
                if 'meeting' in note.lower() or 'asked' in note.lower() 
                else {'content': note, 'confidence': 0.85}
            },
            'provider': 'openai'
        },
        'gemini': lambda note: {
            'categories': {
                'Professional_Background': {'content': 'Business context', 'confidence': 0.92}
                if 'meeting' in note.lower() or 'CEO' in note
                else {'content': note, 'confidence': 0.88}
            },
            'provider': 'gemini'
        }
    }

@pytest.fixture
def rate_limited_ai_service():
    """AI service that simulates rate limiting"""
    class RateLimitedService:
        def __init__(self):
            self.call_count = 0
            
        def analyze_note(self, note, contact_name):
            self.call_count += 1
            if self.call_count > 3:
                from requests.exceptions import HTTPError
                error = HTTPError()
                error.response = Mock(status_code=429)
                raise error
            return {
                'categories': {'Actionable': {'content': 'test', 'confidence': 0.9}},
                'provider': 'test'
            }
    
    return RateLimitedService()

@pytest.fixture
def ai_service_with_fallback():
    """AI service configured with fallback chain"""
    from app.services.ai_service import AIService
    service = AIService()
    # Configure with both providers
    service.gemini_api_key = 'test_gemini_key'
    service.openai_api_key = 'test_openai_key'
    return service

@pytest.fixture
def metrics_collector():
    """Metrics collector for cost/performance tracking"""
    from app.utils.monitoring import MetricsCollector
    return MetricsCollector()
```

**Fixture Usage:**
```python
def test_categorization_with_fixtures(ai_test_notes, ai_service):
    """Use standardized test notes"""
    result = ai_service.analyze_note(ai_test_notes['business'], "Test Contact")
    assert 'categories' in result

def test_rate_limiting(rate_limited_ai_service):
    """Test rate limit handling"""
    # First 3 calls succeed
    for i in range(3):
        result = rate_limited_ai_service.analyze_note("test", "Contact")
        assert 'categories' in result
    
    # 4th call should raise rate limit error
    with pytest.raises(Exception) as exc_info:
        rate_limited_ai_service.analyze_note("test", "Contact")
    assert '429' in str(exc_info.value) or 'rate limit' in str(exc_info.value).lower()
```

#### 6. Continuous Integration for AI Tests

**Purpose**: Automate AI service integration tests in CI/CD pipeline.

**GitHub Actions Workflow**: `.github/workflows/ai-integration-tests.yml`

```yaml
name: AI Service Integration Tests

on:
  schedule:
    - cron: '0 */4 * * *'  # Run every 4 hours
  workflow_dispatch:  # Manual trigger
  push:
    branches: [ main, develop ]
    paths:
      - 'kith-platform/app/services/ai_service.py'
      - 'kith-platform/tests/integration/ai_services/**'

jobs:
  test-ai-services:
    name: AI Service Integration Tests
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd kith-platform
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
    
    - name: Run AI Integration Tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY_TEST }}
        TEST_MODE: integration
        FORCE_SQLITE_FOR_TESTS: "1"
        FLASK_ENV: "testing"
      run: |
        cd kith-platform
        pytest tests/integration/ai_services/ \
          -v \
          --tb=short \
          --junitxml=ai-test-results.xml \
          --cov=app.services.ai_service \
          --cov-report=xml
    
    - name: Check API Usage
      if: always()
      run: |
        cd kith-platform
        python scripts/check_api_usage.py --alert-threshold=100 || true
    
    - name: Generate Cost Report
      if: always()
      run: |
        cd kith-platform
        python scripts/generate_cost_report.py > ai_costs.txt || echo "Cost report generation failed"
    
    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: ai-test-results
        path: |
          kith-platform/ai-test-results.xml
          kith-platform/ai_costs.txt
          kith-platform/htmlcov/
    
    - name: Comment PR with Results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const results = fs.readFileSync('kith-platform/ai-test-results.xml', 'utf8');
          // Parse and comment on PR
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## AI Service Integration Test Results\n\n${results}`
          });
```

**Cost Monitoring Script**: `scripts/check_api_usage.py`

```python
#!/usr/bin/env python3
"""Check API usage and alert if thresholds exceeded"""
import os
import sys
from app.utils.monitoring import MetricsCollector

def check_api_usage(alert_threshold=100):
    """Check API usage and alert if exceeded"""
    collector = MetricsCollector()
    metrics = collector.get_metrics_summary()
    
    ai_metrics = metrics.get('ai.analyze_note', {})
    total_calls = ai_metrics.get('count', 0)
    total_tokens = ai_metrics.get('total_tokens', 0)
    estimated_cost = ai_metrics.get('estimated_cost', 0)
    
    print(f"API Usage Summary:")
    print(f"  Total calls: {total_calls}")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    
    if total_calls > alert_threshold:
        print(f"⚠️ WARNING: API calls ({total_calls}) exceed threshold ({alert_threshold})")
        sys.exit(1)
    
    if estimated_cost > 10.0:
        print(f"⚠️ WARNING: Estimated cost (${estimated_cost:.2f}) exceeds $10.00")
        sys.exit(1)
    
    print("✅ API usage within acceptable limits")
    return 0

if __name__ == '__main__':
    threshold = int(os.getenv('ALERT_THRESHOLD', '100'))
    sys.exit(check_api_usage(threshold))
```

**Cost Report Script**: `scripts/generate_cost_report.py`

```python
#!/usr/bin/env python3
"""Generate cost report for AI service usage"""
from datetime import datetime, timedelta
from app.utils.monitoring import MetricsCollector

def generate_cost_report():
    """Generate cost report"""
    collector = MetricsCollector()
    metrics = collector.get_metrics_summary()
    
    print("=" * 60)
    print("AI Service Cost Report")
    print(f"Generated: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    for key, data in metrics.items():
        if key.startswith('ai.'):
            print(f"\n{key}:")
            print(f"  Calls: {data.get('count', 0)}")
            print(f"  Total tokens: {data.get('total_tokens', 0)}")
            print(f"  Avg tokens/call: {data.get('avg_tokens', 0):.0f}")
            print(f"  Estimated cost: ${data.get('estimated_cost', 0):.4f}")
            print(f"  Avg response time: {data.get('avg_duration', 0):.2f}s")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    generate_cost_report()
```

#### 7. Test Execution Strategy

**Running AI Integration Tests:**

```bash
# Run all AI service tests
pytest tests/integration/ai_services/ -v

# Run contract tests only
pytest tests/integration/ai_services/test_ai_contracts.py -v

# Run resilience tests only
pytest tests/integration/ai_services/test_ai_resilience.py -v

# Run quality tests only
pytest tests/integration/ai_services/test_ai_quality.py -v

# Run cost monitoring tests
pytest tests/integration/ai_services/test_ai_costs.py -v

# Run with real API keys (slow, requires credentials)
pytest tests/integration/ai_services/ -v --real-api-keys

# Run with mocked services (fast, no API calls)
pytest tests/integration/ai_services/ -v --mock-services
```

**Test Markers:**
```python
# In pytest.ini
markers =
    ai_contract: AI service contract tests
    ai_resilience: AI service resilience/fallback tests
    ai_quality: AI response quality tests
    ai_cost: AI cost monitoring tests
    real_api: Tests that require real API keys (slow)
    mock_api: Tests that use mocked APIs (fast)
```

**Usage:**
```bash
# Run only contract tests
pytest -m ai_contract

# Run only resilience tests
pytest -m ai_resilience

# Skip real API tests (use mocks)
pytest -m "not real_api"

# Run all AI tests except cost monitoring
pytest -m "ai_contract or ai_resilience or ai_quality"
```

#### 8. Test Coverage Goals for AI Services

**Target Coverage:**
- **Contract Tests**: 100% (all providers, all response fields)
- **Resilience Tests**: 90%+ (all failure scenarios)
- **Quality Tests**: 80%+ (key quality metrics)
- **Cost Tests**: 70%+ (usage tracking, cost estimation)

**Current Status:**
- ✅ Unit tests with mocked services: ~80% coverage
- ⚠️ Integration tests with real APIs: ~40% coverage (limited by API costs)
- ❌ Contract tests: Not implemented
- ❌ Resilience tests: Not implemented
- ❌ Quality tests: Not implemented
- ❌ Cost monitoring tests: Not implemented

**Recommended Priority:**
1. **High Priority**: Contract tests, Resilience tests (prevent production failures)
2. **Medium Priority**: Quality tests (ensure user experience)
3. **Low Priority**: Cost tests (optimization, can be added later)

### Automated Regression Testing

**Current Status:**
✅ **Testing Infrastructure EXISTS** - Comprehensive test suite with pytest
⚠️ **CI/CD Automation MISSING** - No automated test runs on commits/PRs
✅ **Programmatic Test Execution** - Celery task for running test suites
✅ **Test Markers** - Can filter tests by type (unit, integration, api, etc.)

**Existing Test Infrastructure:**

1. **Test Runner Script** (`kith-platform/run_tests.py`)
   - Supports filtering by test type (unit, integration, api, etc.)
   - Coverage reporting
   - Quick mode for fast feedback
   ```bash
   python run_tests.py --type unit        # Unit tests only
   python run_tests.py --type integration # Integration tests
   python run_tests.py --type api         # API tests
   python run_tests.py --quick             # Fast unit tests, no coverage
   ```

2. **Celery Test Task** (`app/tasks/test_tasks.py`)
   - Programmatic test execution via Celery
   - Stores test results in database (TestRun, TestResult models)
   - Parses JUnit XML for detailed results
   - Can be triggered via admin dashboard or API
   ```python
   from app.tasks.test_tasks import run_test_suite
   
   # Run all tests
   task = run_test_suite.delay()
   
   # Run specific test types
   task = run_test_suite.delay(markers=['unit', 'api'])
   ```

3. **Test Markers** (pytest.ini)
   - `@pytest.mark.unit` - Fast unit tests
   - `@pytest.mark.integration` - Integration tests
   - `@pytest.mark.api` - API endpoint tests
   - `@pytest.mark.slow` - Slow-running tests
   - `@pytest.mark.auth` - Authentication tests
   - `@pytest.mark.database` - Database tests
   - `@pytest.mark.celery` - Celery task tests

**Recommended: Set Up CI/CD for Automated Regression Testing**

**Option 1: GitHub Actions** (Recommended for GitHub repos)

Create `.github/workflows/regression-tests.yml`:
```yaml
name: Regression Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd kith-platform
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: |
          cd kith-platform
          pytest -m unit --cov=app --cov-report=xml --cov-report=term
        env:
          FORCE_SQLITE_FOR_TESTS: "1"
          FLASK_ENV: "testing"
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./kith-platform/coverage.xml
  
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd kith-platform
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run integration tests
        run: |
          cd kith-platform
          pytest -m integration --junitxml=integration-results.xml
        env:
          FORCE_SQLITE_FOR_TESTS: "1"
          FLASK_ENV: "testing"
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: integration-test-results
          path: kith-platform/integration-results.xml
  
  api-tests:
    name: API Tests
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd kith-platform
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run API tests
        run: |
          cd kith-platform
          pytest -m api --junitxml=api-results.xml
        env:
          FORCE_SQLITE_FOR_TESTS: "1"
          FLASK_ENV: "testing"
          # Optional: Add test API keys if needed
          # GEMINI_API_KEY: ${{ secrets.TEST_GEMINI_API_KEY }}
```

**Option 2: GitLab CI** (For GitLab repos)

Create `.gitlab-ci.yml`:
```yaml
stages:
  - test

variables:
  PYTHON_VERSION: "3.11"

unit-tests:
  stage: test
  image: python:${PYTHON_VERSION}
  script:
    - cd kith-platform
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest -m unit --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: kith-platform/coverage.xml

integration-tests:
  stage: test
  image: python:${PYTHON_VERSION}
  script:
    - cd kith-platform
    - pip install -r requirements.txt
    - pip install pytest
    - pytest -m integration --junitxml=integration-results.xml
  artifacts:
    reports:
      junit: kith-platform/integration-results.xml
  only:
    - main
    - develop
    - merge_requests
```

**Option 3: Scheduled Regression Tests** (Using Celery)

Set up a periodic Celery task to run regression tests:
```python
# app/tasks/scheduled_tasks.py
from celery.schedules import crontab
from app.celery_app import celery_app
from app.tasks.test_tasks import run_test_suite

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run regression tests daily at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        run_test_suite.s(markers=['unit', 'integration', 'api']),
        name='daily-regression-tests'
    )
    
    # Run full test suite weekly on Sunday at 3 AM
    sender.add_periodic_task(
        crontab(hour=3, minute=0, day_of_week=0),
        run_test_suite.s(markers=None),  # All tests
        name='weekly-full-test-suite'
    )
```

**Regression Test Strategy:**

1. **Fast Feedback Loop** (On every commit/PR)
   - Run unit tests only (`pytest -m unit`)
   - Fast execution (< 30 seconds)
   - Blocks merge if failures

2. **Integration Tests** (On PR, before merge)
   - Run integration tests (`pytest -m integration`)
   - Includes API endpoint tests
   - May take 2-5 minutes

3. **Full Regression Suite** (Scheduled)
   - All tests including slow tests
   - Run daily or weekly
   - Store results in database
   - Alert on failures

4. **Pre-Release Regression** (Before deployment)
   - Full test suite
   - All markers including `@pytest.mark.slow`
   - Real AI service tests (if configured)
   - Coverage report generation

**Test Result Tracking:**

The existing `TestRun` and `TestResult` models store:
- Test run metadata (status, duration, triggered_by)
- Individual test results (name, status, execution_time, failure_message)
- Test categories (unit, integration, api, etc.)

Query test history:
```python
from app.models import TestRun, TestResult
from app.utils.database import DatabaseManager

db_manager = DatabaseManager()
with db_manager.get_session() as session:
    # Get recent test runs
    recent_runs = session.query(TestRun).order_by(
        TestRun.started_at.desc()
    ).limit(10).all()
    
    # Get failed tests from last run
    last_run = recent_runs[0]
    failed_tests = session.query(TestResult).filter(
        TestResult.run_id == last_run.id,
        TestResult.status == 'failed'
    ).all()
```

**Recommended Regression Test Workflow:**

1. **Developer Workflow:**
   ```bash
   # Before committing
   python run_tests.py --type unit --quick
   
   # Before pushing
   python run_tests.py --type integration
   ```

2. **CI/CD Pipeline:**
   - On push to feature branch: Unit tests only
   - On PR creation: Unit + Integration tests
   - On merge to main: Full test suite
   - Scheduled: Daily regression tests

3. **Pre-Deployment:**
   ```bash
   # Run full regression suite
   pytest --cov=app --cov-report=html
   
   # Verify coverage threshold
   # Check test results in database
   ```

**Setting Up Automated Regression Testing:**

**Step 1: Create GitHub Actions Workflow**
```bash
mkdir -p .github/workflows
# Create .github/workflows/regression-tests.yml (see above)
```

**Step 2: Configure Secrets** (if needed)
- `TEST_GEMINI_API_KEY` - For real AI service tests
- `TEST_OPENAI_API_KEY` - For OpenAI fallback tests
- `DATABASE_URL` - Test database connection

**Step 3: Test the Workflow**
```bash
# Test locally first
cd kith-platform
pytest -m unit
pytest -m integration
pytest -m api
```

**Step 4: Monitor Test Results**
- GitHub Actions: View in Actions tab
- GitLab CI: View in CI/CD > Pipelines
- Celery: Query TestRun model in database

**Regression Test Checklist:**

Before deploying, ensure:
- ✅ All unit tests pass (`pytest -m unit`)
- ✅ All integration tests pass (`pytest -m integration`)
- ✅ All API tests pass (`pytest -m api`)
- ✅ Coverage above 70% (`pytest --cov=app`)
- ✅ No slow test failures (`pytest -m slow`)
- ✅ Database migrations tested
- ✅ Critical paths covered (auth, data operations)

**Current Gaps & Recommendations:**

**Missing:**
1. ❌ CI/CD configuration (GitHub Actions/GitLab CI)
2. ❌ Automated test runs on commits/PRs
3. ❌ Test result notifications (email/Slack)
4. ❌ Test flakiness detection
5. ❌ Performance regression tests
6. ⚠️ **Dedicated E2E test suite** (limited E2E coverage)
7. ⚠️ **Explicit functional test markers** (mixed with integration)
8. ⚠️ **Browser-based E2E tests** (Selenium/Playwright)

**Recommended Additions:**
1. ✅ Set up GitHub Actions workflow (see above)
2. ✅ Add test result notifications (Slack/email)
3. ✅ Track test execution time trends
4. ✅ Add performance benchmarks
5. ✅ Set up test result dashboard
6. ✅ Add smoke tests for critical paths
7. ✅ Configure branch protection (require tests to pass)
8. ✅ **Create dedicated E2E test suite** (user journey tests)
9. ✅ **Add functional test markers** (separate from integration)
10. ✅ **Add browser-based E2E tests** (for UI workflows)

### Test Type Breakdown

#### 1. Unit Tests ✅ (Comprehensive)

**Location**: `tests/unit/`
**Files**: 6 test files
**Coverage**: Services, utilities, isolated components

**Test Files:**
- `test_ai_service.py` - AI service logic (mocked)
- `test_auth_service.py` - Authentication service
- `test_api.py` - API endpoint unit tests
- `test_celery_tasks.py` - Celery task unit tests
- `test_database.py` - Database utility tests
- `test_monitoring.py` - Monitoring/health check tests
- `test_note_service.py` - Note service logic

**Example Unit Test:**
```python
@pytest.mark.unit
class TestAIService:
    def test_analyze_note_with_gemini(self, mock_genai):
        """Test note analysis using Gemini"""
        # Mock Gemini API
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"categories": {...}}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        service = AIService()
        result = service.analyze_note("John is 30 years old", "John Doe")
        
        assert 'categories' in result
        assert 'personal_info' in result['categories']
```

**Run Unit Tests:**
```bash
pytest -m unit                    # All unit tests
pytest tests/unit/                # All unit test files
pytest tests/unit/test_ai_service.py  # Specific file
```

#### 2. Integration Tests ✅ (Comprehensive)

**Location**: `tests/integration/`
**Files**: 15+ test files
**Coverage**: Full API endpoints, database operations, external services

**Test Files:**
- `test_api_endpoints.py` - Full API endpoint tests
- `test_admin_dashboard.py` - Admin functionality
- `test_comprehensive_health_checks.py` - System health checks
- `test_csv_import_export.py` - CSV import/export
- `test_export_import.py` - Data export/import
- `test_file_upload.py` - File upload processing
- `test_graph_data.py` - Relationship graph
- `test_real_ai_services.py` - Real AI API calls (slow)
- `test_real_vs_mocked_ai.py` - Comparison of mocked vs real
- `test_search_discovery.py` - Search functionality
- `test_settings_page.py` - Settings UI
- `test_tag_management.py` - Tag CRUD operations
- `test_telegram_integration.py` - Telegram sync
- `test_ui_features.py` - UI feature tests

**Example Integration Test:**
```python
@pytest.mark.integration
@pytest.mark.api
class TestAPIEndpoints:
    def test_auth_login_post_success(self, client, sample_user):
        """Test auth login POST with valid credentials"""
        response = client.post('/api/auth/login', 
                             json={'username': sample_user.username, 
                                   'password': 'test_password'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
```

**Run Integration Tests:**
```bash
pytest -m integration              # All integration tests
pytest tests/integration/          # All integration test files
pytest -m "integration and api"   # Integration API tests only
```

#### 3. Functional Tests ⚠️ (Partially Covered)

**Current Status**: Functional tests are mixed with integration tests
**Location**: `tests/integration/` (not explicitly marked as functional)

**What's Covered:**
- ✅ Contact CRUD operations
- ✅ Tag management workflows
- ✅ Search functionality
- ✅ File upload workflows
- ✅ Telegram sync workflows
- ✅ Admin dashboard workflows

**What's Missing:**
- ❌ Explicit `@pytest.mark.functional` marker
- ❌ Dedicated functional test directory
- ❌ User journey tests (complete workflows)

**Recommendation**: Add functional test markers and create dedicated functional test suite:
```python
@pytest.mark.functional
class TestContactManagementWorkflow:
    """Test complete contact management workflow"""
    def test_create_contact_add_notes_tag_and_search(self, authenticated_client):
        # 1. Create contact
        # 2. Add notes
        # 3. Assign tags
        # 4. Search for contact
        # 5. Verify all data
        pass
```

**Run Functional Tests (when implemented):**
```bash
pytest -m functional               # All functional tests
```

#### 4. End-to-End Tests ⚠️ (Limited)

**Current Status**: Some E2E tests exist in `test_app_consolidation.py`
**Location**: `tests/test_app_consolidation.py`

**What's Covered:**
- ✅ Full contact lifecycle (create → update → delete)
- ✅ Contact with notes and tags integration
- ✅ Authentication flows

**What's Missing:**
- ❌ Dedicated E2E test suite
- ❌ Browser-based E2E tests (Selenium/Playwright)
- ❌ Complete user journey tests
- ❌ Cross-browser testing

**Example E2E Test (Existing):**
```python
class TestIntegration:
    """End-to-end integration tests"""
    
    def test_full_contact_lifecycle(self, authenticated_client):
        """Test complete contact creation, update, and deletion flow"""
        # 1. Create contact
        create_response = authenticated_client.post('/api/contacts', json={
            'full_name': 'Lifecycle Test Contact',
            'tier': 2
        })
        contact_id = create_response.get_json().get('id')
        
        # 2. Get contact
        get_response = authenticated_client.get(f'/api/contacts/{contact_id}')
        assert get_response.status_code == 200
        
        # 3. Update contact
        update_response = authenticated_client.patch(
            f'/api/contact/{contact_id}',
            json={'tier': 3}
        )
        
        # 4. Delete contact
        delete_response = authenticated_client.delete(f'/api/contacts/{contact_id}')
        assert delete_response.status_code in [200, 204]
```

**Recommendation**: Create dedicated E2E test suite:
```python
# tests/e2e/test_user_journeys.py
@pytest.mark.e2e
class TestUserJourneys:
    """End-to-end user journey tests"""
    
    def test_complete_note_processing_journey(self, authenticated_client):
        """Test: Login → Create Contact → Add Note → AI Analysis → View Results"""
        # 1. Login
        # 2. Create contact
        # 3. Add note
        # 4. Wait for AI analysis
        # 5. View categorized results
        # 6. Edit categories
        # 7. Save synthesis
        pass
    
    def test_telegram_sync_journey(self, authenticated_client):
        """Test: Connect Telegram → Sync Contacts → Import History → View Notes"""
        # 1. Connect to Telegram
        # 2. Sync contacts
        # 3. Import chat history
        # 4. Verify notes created
        # 5. View categorized data
        pass
```

**Run E2E Tests:**
```bash
pytest -m e2e                      # All E2E tests (when implemented)
pytest tests/e2e/                   # E2E test directory
```

#### 5. Automated Tests ✅ (Comprehensive)

**Current Status**: Fully automated via pytest
**Configuration**: `pytest.ini` with markers and coverage

**Automation Features:**
- ✅ Test discovery (automatic)
- ✅ Test markers (filtering)
- ✅ Coverage reporting
- ✅ Parallel execution support (via pytest-xdist)
- ✅ Test result storage (via Celery task)

**Run All Automated Tests:**
```bash
pytest                              # All tests
pytest --cov=app --cov-report=html  # With coverage
pytest -n auto                      # Parallel execution (if pytest-xdist installed)
```

#### 6. Regression Tests ✅ (Available, Not Automated)

**Current Status**: Test suite can be run programmatically, but not automated in CI/CD
**Location**: `app/tasks/test_tasks.py`

**What Exists:**
- ✅ Celery task to run full test suite
- ✅ Test result storage in database
- ✅ JUnit XML parsing
- ✅ Test run history tracking

**What's Missing:**
- ❌ CI/CD automation (GitHub Actions/GitLab CI)
- ❌ Scheduled regression runs
- ❌ Pre-commit hooks
- ❌ Automatic test runs on PRs

**Run Regression Tests:**
```python
# Via Celery task
from app.tasks.test_tasks import run_test_suite
task = run_test_suite.delay(markers=['unit', 'integration'])

# Via command line
pytest --junitxml=results.xml
```

### Test Coverage by Feature

**Feature 1: Authentication & User Management**
- ✅ Unit tests: `test_auth_service.py`
- ✅ Integration tests: `test_api_endpoints.py` (auth endpoints)
- ✅ Functional tests: Login/logout workflows
- ⚠️ E2E tests: Limited

**Feature 2: Contact Management**
- ✅ Unit tests: Contact service logic
- ✅ Integration tests: `test_api_endpoints.py` (contact CRUD)
- ✅ Functional tests: Contact lifecycle
- ✅ E2E tests: Full contact lifecycle in `test_app_consolidation.py`

**Feature 3: Note Processing & AI Analysis**
- ✅ Unit tests: `test_ai_service.py`, `test_note_service.py`
- ✅ Integration tests: `test_real_ai_services.py`, `test_real_vs_mocked_ai.py`
- ✅ Functional tests: Note processing workflows
- ⚠️ E2E tests: Limited

**Feature 4: Tag & Category System**
- ✅ Unit tests: Tag service logic
- ✅ Integration tests: `test_tag_management.py` (comprehensive)
- ✅ Functional tests: Tag CRUD and assignment
- ⚠️ E2E tests: Limited

**Feature 5: Search Functionality**
- ✅ Unit tests: Search service logic
- ✅ Integration tests: `test_search_discovery.py`
- ✅ Functional tests: Search workflows
- ⚠️ E2E tests: Limited

**Feature 6: Relationship Graph**
- ✅ Integration tests: `test_graph_data.py`
- ⚠️ Unit tests: Limited
- ⚠️ E2E tests: Limited

**Feature 7: Telegram Integration**
- ✅ Integration tests: `test_telegram_integration.py` (comprehensive, 28 tests)
- ✅ Functional tests: Sync workflows, contact matching
- ⚠️ Unit tests: Limited (mocked)
- ⚠️ E2E tests: Limited

### Test Execution Strategy

**1. Fast Feedback (On Every Commit)**
```bash
pytest -m unit --tb=short          # Unit tests only (< 30 seconds)
```

**2. Integration Tests (On PR)**
```bash
pytest -m integration --tb=short   # Integration tests (2-5 minutes)
```

**3. Full Regression (Before Release)**
```bash
pytest --cov=app --cov-report=html  # All tests with coverage
```

**4. Slow Tests (Scheduled)**
```bash
pytest -m slow                      # Real AI service tests (requires API keys)
```

### Test Quality Metrics

**Current Coverage:**
- **Minimum Required**: 70% (enforced in pytest.ini)
- **Target Coverage**: 80%+ overall
- **Critical Paths**: 90%+ (auth, data operations)
- **Security-Sensitive**: 100% (password hashing, input validation)

**Test Execution:**
- **Unit Tests**: < 30 seconds
- **Integration Tests**: 2-5 minutes
- **Full Suite**: 5-10 minutes
- **With Slow Tests**: 10-15 minutes

**Test Reliability:**
- ✅ Test isolation (temporary databases)
- ✅ Fixture cleanup
- ✅ Mock external services
- ✅ Deterministic test data

### Recommended Test Improvements

**Priority 1: CI/CD Automation**
1. Set up GitHub Actions workflow
2. Run tests on every commit/PR
3. Block merges on test failures
4. Generate coverage reports

**Priority 2: E2E Test Suite**
1. Create `tests/e2e/` directory
2. Add browser-based tests (Playwright/Selenium)
3. Test complete user journeys
4. Cross-browser testing

**Priority 3: Functional Test Markers**
1. Add `@pytest.mark.functional` to workflow tests
2. Separate functional from integration tests
3. Create functional test documentation

**Priority 4: Performance Tests**
1. Add `@pytest.mark.performance` marker
2. Test API response times
3. Test database query performance
4. Load testing for critical endpoints

**Priority 5: Test Maintenance**
1. Remove duplicate test files (files with " 2" suffix)
2. Consolidate test utilities
3. Improve test documentation
4. Add test examples for new features

### Test Patterns

**Mocked Tests** (Fast, 0.00s)
- Use `@patch` decorator for external services
- Test logic without real API calls
- Example: `test_ai_service.py` with mocked Gemini

**Real Service Tests** (Slow, 2-5s)
- Actually call external APIs
- Verify API keys work
- Test real service responses
- Example: `test_real_ai_services.py`
- Marked with `@pytest.mark.slow`

**Integration Test Pattern:**
```python
@pytest.mark.integration
class TestFeature:
    def test_feature_requires_auth(self, client):
        """Test that feature requires authentication"""
        response = client.get('/api/feature')
        assert response.status_code == 302  # Redirect to login
    
    def test_feature_success(self, client, authenticated_user):
        """Test successful feature operation"""
        response = client.post('/api/feature', json={...})
        assert response.status_code == 200
        data = response.get_json()
        assert 'expected_field' in data
```

### Test Data Management

**Test Database:**
- Uses temporary SQLite database (`test_kith_platform.db`)
- Created fresh for each test session
- Automatically cleaned up
- Isolated from development/production databases

**Test Users:**
- Default admin user: `username='admin'`, `password='admin123'`
- Created automatically in `app` fixture
- Can create additional test users as needed

### Areas for Additional Testing

**Potential Gaps (to consider adding):**
1. **E2E User Flows**
   - Complete user journey tests
   - Multi-step workflows (create contact → add note → analyze → save)
   - Cross-feature interactions

2. **Performance Tests**
   - Load testing for API endpoints
   - Database query performance
   - Large dataset handling

3. **Error Handling Tests**
   - Network failure scenarios
   - Database connection failures
   - External service timeouts

4. **Calendar Integration Tests**
   - Date/time extraction
   - Event creation
   - Calendar sync (if implemented)

5. **Analytics Service Tests**
   - Health score calculation
   - Trend analysis
   - Recommendation generation

6. **Frontend JavaScript Tests**
   - UI component behavior
   - Cache management
   - Lazy loading

### Continuous Integration

**Recommended CI Setup:**
```yaml
# .github/workflows/tests.yml (example)
- Run: pytest --cov=app --cov-report=xml
- Fail if coverage < 70%
- Run on: push, pull_request
- Test matrix: Python 3.10, 3.11, 3.12
```

### Test Maintenance

**Best Practices:**
- Keep tests fast (use mocks for external services)
- Use real services for critical paths (marked as `@pytest.mark.slow`)
- Test both success and failure paths
- Test edge cases and boundary conditions
- Keep test data isolated
- Clean up after tests
- Document complex test scenarios

---

## Additional Resources

### Key Files to Review

1. **`app/__init__.py`** - Flask app factory, route registration
2. **`models.py`** - All database models
3. **`main.py`** - Application entry point
4. **`requirements.txt`** - All dependencies
5. **`templates/index.html`** - Main SPA template
6. **`static/js/main.js`** - Frontend entry point

### Development Guidelines

1. **Code Quality**
   - All code must be debuggable and well-documented
   - Comprehensive test coverage (80%+)
   - Error handling for all external API calls
   - Quality of analysis takes priority over speed

2. **Testing**
   - Write tests before/alongside features
   - Mock external dependencies
   - Test error conditions
   - Validate user isolation

3. **Database**
   - Use Alembic for all schema changes
   - Never modify models.py without migration
   - Test migrations on sample data
   - Optimize queries (avoid N+1)

4. **API Design**
   - RESTful conventions
   - Consistent error responses
   - Input validation
   - User ownership checks

5. **Frontend**
   - Progressive enhancement
   - Accessibility (ARIA labels)
   - Error state handling
   - Loading indicators

---

## Conclusion

This document provides a comprehensive guide to building the Kith Platform. Each feature section includes enough detail to implement from scratch, with references to actual code locations where applicable.

For questions or clarifications, refer to:
- Existing codebase for implementation examples
- Test files for expected behavior
- API endpoint code for request/response formats
- Service layer for business logic patterns

**Next Steps for New Developers:**
1. Set up development environment
2. Review Feature 1 (Authentication) first
3. Implement features in order (1-11)
4. Write tests alongside implementation
5. Refer to this document for architecture decisions

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*  
*Maintained by: Development Team*

