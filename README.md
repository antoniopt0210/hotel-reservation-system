# StayEasy — Hotel Reservation System

A full-stack hotel booking platform inspired by Booking.com. Search 200+ hotels across 100 US cities, book rooms with Stripe payments, leave reviews, and manage everything from an admin dashboard.

**[Live Demo](https://antoniopt0210.github.io/hotel-reservation-system/)** | **[Backend API](https://hotel-reservation-system-backend-aeqb.onrender.com/api/health)**

---

## Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **React Router v6** | Client-side routing (HashRouter for GitHub Pages) |
| **TanStack Query** | Server state management, caching, pagination |
| **Zustand** | Client state (auth, search) |
| **Axios** | HTTP client with JWT interceptor |
| **Tailwind CSS** (CDN) | Utility-first styling |
| **Stripe.js** | Secure payment card element |

### Backend
| Technology | Purpose |
|------------|---------|
| **Python / Flask** | REST API with app factory pattern and Blueprints |
| **PostgreSQL** (Supabase) | Relational data — users, hotels, rooms, bookings, reviews, wishlist |
| **SQLAlchemy** | ORM with auto-migration via `db.create_all()` |
| **Apache Cassandra** (DataStax Astra) | Room availability calendar, per-night pricing overrides |
| **Redis** (Upstash) | Booking locks to prevent double-reservation |
| **Stripe** | Payment intent creation and server-side verification |
| **Flask-Mail** (SendGrid) | Transactional emails (confirmation, reminders, cancellation) |
| **Flask-JWT-Extended** | JWT access + refresh token authentication |
| **bcrypt** | Password hashing |
| **APScheduler** | Daily check-in reminder cron job |
| **Gunicorn** | Production WSGI server |

### Infrastructure
| Service | Purpose |
|---------|---------|
| **Render** | Backend hosting (Python 3.11) |
| **GitHub Pages** | Frontend hosting (static SPA) |
| **Supabase** | Managed PostgreSQL |
| **DataStax Astra** | Managed Cassandra |
| **Upstash** | Managed Redis |

---

## Features

### Discovery & Search
- **Landing page** with hero search bar, popular destinations, and recently viewed hotels
- **Search autocomplete** — type-ahead suggestions for cities and hotel names
- **Advanced filters** — filter by city, star rating, price range, guest count, and amenities
- **Sort options** — top rated, price low-to-high, price high-to-low
- **Pagination** across all listing pages

### Hotel Detail
- **Photo gallery** with full-screen modal viewer and keyboard navigation
- **Interactive map** (OpenStreetMap embed, no API key needed)
- **Room listings** with availability, pricing, occupancy, and photos
- **Guest reviews** with star ratings, rating breakdown bars, and pagination
- **Wishlist** — save hotels with a heart toggle

### Booking Flow
- **3-step checkout** — guest details, payment, confirmation
- **Stripe integration** for secure card payments (test mode with `4242 4242 4242 4242`)
- **Test mode bypass** — "Skip Payment" button for development/demo
- **Dynamic pricing** — weekend surcharges, seasonal multipliers, per-night overrides
- **Price breakdown** with expandable nightly rate detail
- **Redis locks** to prevent double-booking during checkout
- **Email notifications** — booking confirmation, check-in reminders, cancellation (coming soon)

### User Accounts
- **JWT authentication** with access + refresh tokens
- **Registration & login** with bcrypt password hashing
- **Profile page** — edit name, phone, change password
- **My Bookings** — view history, see details, cancel bookings
- **Wishlist page** — view and manage saved hotels
- **Review submission** — rate and review any hotel

### Admin Dashboard
- **Stats overview** — total hotels, rooms, bookings, revenue, reviews, users
- **Booking management** — filter by status, update status (confirmed, checked_in, checked_out, cancelled, refunded)
- **User management** (superadmin) — view all users, change roles (guest, hotel_admin, superadmin)
- **Hotel & room CRUD** — create/edit hotels and rooms via API
- **Price overrides** — set per-night pricing via Cassandra

### UI/UX
- **Responsive design** — mobile filter drawer, adaptive layouts
- **Toast notifications** for non-blocking feedback
- **Error boundary** for crash recovery
- **404 page** for unknown routes
- **Recently viewed hotels** persisted in localStorage

---

## Architecture

```
Frontend (React)                    Backend (Flask)
GitHub Pages                        Render
     |                                  |
     |--- axios + JWT ----------------->|
     |                                  |--- SQLAlchemy ---> PostgreSQL (Supabase)
     |                                  |--- cassandra-driver -> Cassandra (Astra)
     |                                  |--- redis ---------> Redis (Upstash)
     |                                  |--- stripe --------> Stripe API
     |                                  |--- Flask-Mail ----> SendGrid SMTP
     |<--- JSON responses --------------|
```

**Hybrid database design:**
- **PostgreSQL** handles relational data (users, hotels, rooms, bookings, reviews, wishlist) with full ACID transactions
- **Cassandra** handles time-series availability data partitioned by `(room_id, year_month)` for fast calendar lookups, and per-night price overrides

---

## Project Structure

```
hotel-reservation-system/
├── backend/
│   ├── api/v1/            # Blueprints: auth, hotels, rooms, bookings, reviews, admin, wishlist, search
│   ├── db/                # Database clients: postgres, cassandra, redis
│   ├── models/            # SQLAlchemy models: User, Hotel, Room, Booking, Review, WishlistItem
│   ├── utils/             # Pricing engine, email, auth helpers, validators
│   ├── app.py             # App factory + health endpoints
│   ├── config.py          # Dev/Prod config classes
│   ├── seed.py            # Seeds 200+ hotels across 100 US cities
│   ├── Procfile           # Gunicorn start command for Render
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios API clients (auth, hotels, bookings, reviews, wishlist, admin, search)
│   │   ├── components/    # Reusable UI: Button, Input, Toast, StarRating, ReviewList, BookingsTable, etc.
│   │   ├── hooks/         # Custom hooks (useRecentlyViewed)
│   │   ├── pages/         # Route pages: Landing, Search, HotelDetail, Booking flow, Account, Admin
│   │   ├── store/         # Zustand stores (auth, search)
│   │   └── App.js         # Router + providers
│   └── package.json
├── PLAN.md                # Development roadmap (all 8 phases complete)
└── README.md
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login, returns JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |
| PUT | `/api/v1/auth/me` | Update profile / password |

### Hotels
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/hotels` | List hotels with filters & pagination |
| GET | `/api/v1/hotels/:slug` | Hotel detail with rooms |
| GET | `/api/v1/hotels/:id/rooms` | Rooms with availability check |
| GET | `/api/v1/hotels/amenities` | All amenities |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/bookings/payment-intent` | Create Stripe PaymentIntent |
| POST | `/api/v1/bookings` | Confirm booking after payment |
| POST | `/api/v1/bookings/test-confirm` | Book without payment (test mode) |
| GET | `/api/v1/bookings/mine` | User's booking history |
| GET | `/api/v1/bookings/:id` | Booking detail |
| PUT | `/api/v1/bookings/:id/cancel` | Cancel booking |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/hotels/:id/reviews` | Paginated reviews |
| POST | `/api/v1/hotels/:id/reviews` | Submit review (auth required) |
| GET | `/api/v1/hotels/:id/reviews/summary` | Rating breakdown |
| DELETE | `/api/v1/reviews/:id` | Delete review |

### Wishlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/wishlist` | User's wishlist |
| POST | `/api/v1/wishlist/:hotel_id` | Add to wishlist |
| DELETE | `/api/v1/wishlist/:hotel_id` | Remove from wishlist |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/stats` | Dashboard stats |
| GET | `/api/v1/admin/bookings` | All bookings with filters |
| PUT | `/api/v1/admin/bookings/:id/status` | Update booking status |
| GET | `/api/v1/admin/users` | All users (superadmin) |
| PUT | `/api/v1/admin/users/:id/role` | Change user role (superadmin) |

---

## Local Development

### Prerequisites
- Python 3.10+ (3.11 recommended; cassandra-driver doesn't build on 3.14)
- Node.js 18+

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env    # Fill in your keys
python seed.py          # Seed 200+ hotels
python app.py           # Runs on http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local    # Set API URL to http://127.0.0.1:5000
npm start                     # Runs on http://localhost:3000
```

### Environment Variables

**Backend** (`backend/.env`):
```
DATABASE_URL=postgresql://...          # Supabase connection string
JWT_SECRET_KEY=your-secret             # JWT signing key
STRIPE_SECRET_KEY=sk_test_...          # Stripe secret key
ASTRA_DB_APPLICATION_TOKEN=AstraCS:... # DataStax Astra token (optional)
ASTRA_DB_KEYSPACE=default_keyspace     # Astra keyspace (optional)
REDIS_URL=rediss://...                 # Upstash Redis URL (optional)
MAIL_PASSWORD=SG....                   # SendGrid API key (optional)
```

**Frontend** (`frontend/.env.local`):
```
REACT_APP_API_URL=http://127.0.0.1:5000
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Test Payment
Use Stripe test card: `4242 4242 4242 4242`, any future expiry, any CVC. Or click "Skip Payment (Test Mode)" to bypass Stripe entirely.

---

## Deployment

- **Backend** auto-deploys to Render on push to `main` (from `backend/` directory)
- **Frontend** deploys to GitHub Pages via `npm run deploy` (from `frontend/` directory)

---

## License

MIT
