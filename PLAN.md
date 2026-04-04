# Hotel Reservation System — Improvement Plan
> Transforming a basic CRUD app into a booking.com-caliber platform.
> Track progress by checking off tasks as they are completed.

---

## Current State

- **Backend:** Python Flask + Cassandra (DataStax Astra). Single table `hotel.reservations` with a `bucket='all'` anti-pattern.
- **Frontend:** React + Tailwind CSS (CDN). Single 200-line `App.js` component, no routing, no state management.
- **API:** 4 endpoints only — `POST/GET /api/reservations`, `PUT/DELETE /api/reservations/<id>`
- **Features:** Basic reservation CRUD, status transitions (Booked → Checked-In → Checked-Out → Canceled), date validation.
- **Deployment:** Frontend on GitHub Pages, Backend on Render.

---

## Architecture Decision: Hybrid Database

| Data | Database | Why |
|------|----------|-----|
| Users, hotels, rooms, bookings, reviews | PostgreSQL (Supabase free) | Relational queries, joins, transactions |
| Availability calendars, price history | Cassandra (Astra, existing) | High-write time-series, range queries by date |
| Session cache, availability locks | Redis (Upstash free) | Race condition prevention during checkout |

---

## Zero-Cost Production Stack

| Service | Purpose | Cost |
|---------|---------|------|
| GitHub Pages | React frontend | Free |
| Render | Flask API | Free |
| DataStax Astra | Cassandra | Free (existing) |
| Supabase | PostgreSQL | Free (500MB) |
| Upstash | Redis | Free (10k cmds/day) |
| Cloudinary | Image CDN | Free (25GB) |
| SendGrid | Email | Free (100/day) |
| Stripe | Payments | Free until live money |

---

## Phase Overview

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Foundation Restructure | ✅ Complete |
| Phase 2 | Multi-Hotel Listings + User Auth | ✅ Complete |
| Phase 3 | Full Booking Flow + Payments + Email | ✅ Complete |
| Phase 4 | Reviews + Ratings | ✅ Complete |
| Phase 5 | Admin Dashboard | ✅ Complete |
| Phase 6 | Dynamic Pricing | ✅ Complete |
| Phase 7 | Advanced Search + Maps + Wishlist | ✅ Complete |

---

## Phase 1 — Foundation Restructure
> Zero user-visible changes. Sets up the architecture that all future phases build on.

### Backend Tasks
- [x] Create `backend/config.py` with `DevelopmentConfig` / `ProductionConfig` classes
- [x] Create `backend/extensions.py` for shared singletons (db, cors, mail)
- [x] Create `backend/db/` directory → `backend/db/cassandra_client.py`
- [x] Create `backend/db/postgres_client.py` (SQLAlchemy setup, placeholder for Phase 2)
- [x] Create `backend/db/redis_client.py` (placeholder for Phase 3)
- [x] Create `backend/api/v1/` directory with Blueprint files: `auth.py`, `hotels.py`, `rooms.py`, `reservations.py`, `search.py`
- [x] Move all current routes from `app.py` into `api/v1/reservations.py`
- [x] Create `backend/models/reservation.py` (user/hotel/room models added in Phase 2)
- [x] Create `backend/utils/validators.py` (date validation extracted here)
- [x] Create `backend/utils/auth_helpers.py` (placeholder for Phase 2)
- [x] Refactor `app.py` to use the app factory pattern (register blueprints)
- [x] **Fix Cassandra `bucket='all'` anti-pattern** → re-partitioned by `check_in_month` ('YYYY-MM')
- [x] Update `requirements.txt` with new dependencies
- [ ] Verify all existing 4 endpoints still work after restructure ← **run this manually**

> **Migration note:** Cassandra primary key changed from `bucket` → `check_in_month`.
> If you have existing data in Astra, run `DROP TABLE <keyspace>.reservations;` before deploying.
> The new table is auto-created on first startup.

### Frontend Tasks
- [x] Add new dependencies to `package.json`: `react-router-dom`, `zustand`, `@tanstack/react-query`, `axios`
- [x] Create `src/api/client.js` (axios instance with base URL + auth interceptors)
- [x] Create `src/api/reservations.js` (existing fetch calls extracted here)
- [x] Create `src/api/hotels.js` (placeholder for Phase 2)
- [x] Create `src/api/auth.js` (placeholder for Phase 2)
- [x] Create `src/store/authStore.js` (zustand)
- [x] Create `src/store/searchStore.js` (zustand)
- [x] Create `src/components/common/`: `Button.jsx`, `Input.jsx`, `LoadingSpinner.jsx`, `StarRating.jsx`
- [x] Create `src/components/layout/`: `Navbar.jsx`, `Footer.jsx`, `PageWrapper.jsx`
- [x] Create `src/pages/HomePage.jsx` (existing reservation UI ported here, uses new components)
- [x] Refactor `App.js` to router + layout wrapper (BrowserRouter + QueryClientProvider)
- [ ] Run `npm install` then `npm start` to verify app still works ← **run this manually**

---

## Phase 2 — Multi-Hotel Listings + User Auth
> Highest impact phase. Users can register, browse hotels, and see hotel detail pages.

### Database: PostgreSQL Tables (New — Supabase)
- [ ] Provision Supabase free-tier PostgreSQL instance ← **do this manually**
- [x] `users`, `hotels`, `hotel_photos`, `amenities`, `hotel_amenities`, `rooms`, `room_photos` — all defined as SQLAlchemy models; `db.create_all()` creates them on first startup
- [ ] Set `DATABASE_URL` env var on Render ← **do this manually**

### Database: Cassandra Tables (New)
- [x] `room_availability` table added to `init_schema()` in `cassandra_client.py`

### Backend Tasks
- [x] Implement `POST /api/v1/auth/register`
- [x] Implement `POST /api/v1/auth/login` (returns JWT access + refresh tokens)
- [x] Implement `POST /api/v1/auth/refresh`
- [x] Implement `POST /api/v1/auth/logout`
- [x] Implement `GET /api/v1/auth/me`
- [x] Implement `GET /api/v1/hotels` with filters: city, stars, amenities, price, guests, sort, pagination
- [x] Implement `GET /api/v1/hotels/<slug>` (full hotel detail)
- [x] Implement `GET /api/v1/hotels/<id>/rooms` with Cassandra availability check
- [x] Implement `GET /api/v1/hotels/amenities`
- [x] Implement `POST /api/v1/hotels/admin` (hotel_admin role)
- [x] Implement `PUT /api/v1/hotels/admin/<id>`
- [x] Implement `POST /api/v1/hotels/admin/<id>/rooms`
- [x] Implement `PUT /api/v1/hotels/admin/rooms/<id>`
- [x] Created `backend/seed.py` with 3 hotels (NY, Miami, Denver), rooms, photos, amenities
- [x] Created `backend/.env.example`
- [ ] Run `pip install python-dotenv` then `python seed.py` after setting DATABASE_URL ← **do this manually**

### Frontend Tasks
- [x] `src/api/hotels.js` — fetchHotels, fetchHotel, fetchHotelRooms, fetchAmenities
- [x] `src/api/auth.js` — register, login, logout, getMe
- [x] `src/pages/LandingPage.jsx` — hero, search widget, featured destinations, why section
- [x] `src/pages/SearchResultsPage.jsx` — filter sidebar, hotel cards, sort, pagination
- [x] `src/pages/HotelDetailPage.jsx` — photo gallery, hotel info, amenities, rooms, review stub
- [x] `src/pages/auth/LoginPage.jsx`
- [x] `src/pages/auth/RegisterPage.jsx`
- [x] `src/components/common/ProtectedRoute.jsx`
- [x] `App.js` updated with all new routes (`/`, `/search`, `/hotels/:slug`, `/auth/login`, `/auth/register`, `/manage`)

---

## Phase 3 — Full Booking Flow + Payments + Email
> Converts the browsing experience into a functional product.

### Database: PostgreSQL Tables (New)
- [ ] Create `bookings` table:
  ```sql
  CREATE TABLE bookings (
      id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id             UUID REFERENCES users(id),
      room_id             UUID REFERENCES rooms(id),
      hotel_id            UUID REFERENCES hotels(id),
      check_in_date       DATE NOT NULL,
      check_out_date      DATE NOT NULL,
      guest_first_name    TEXT NOT NULL,
      guest_last_name     TEXT NOT NULL,
      guest_email         TEXT NOT NULL,
      num_guests          SMALLINT DEFAULT 1,
      special_requests    TEXT,
      total_price_usd     DECIMAL(10,2) NOT NULL,
      stripe_payment_id   TEXT,
      status              TEXT DEFAULT 'confirmed',
      created_at          TIMESTAMPTZ DEFAULT NOW(),
      cancelled_at        TIMESTAMPTZ,
      cancellation_reason TEXT
  );
  ```

### Backend Tasks
- [ ] Provision Upstash Redis free-tier instance
- [ ] Set up Stripe account and test keys
- [ ] Set up SendGrid account and verify sender domain
- [ ] Implement `POST /api/v1/payments/create-intent`:
  1. Re-verify availability
  2. Acquire Redis lock on `{room_id}:{date_range}`
  3. Calculate final price
  4. Create Stripe PaymentIntent
  5. Return `client_secret`
- [ ] Implement `POST /api/v1/bookings` (confirm booking post-payment):
  1. Verify PaymentIntent status with Stripe API
  2. Decrement `room_availability` in Cassandra
  3. Create row in `bookings` PostgreSQL table
  4. Send confirmation email
  5. Release Redis lock
  6. Return booking reference
- [ ] Implement `GET /api/v1/bookings/mine` (current user's booking history)
- [ ] Implement `GET /api/v1/bookings/<id>` (single booking detail)
- [ ] Implement `PUT /api/v1/bookings/<id>/cancel`
- [ ] Implement `GET /api/v1/rooms/<id>/availability?month=YYYY-MM`
- [ ] Configure Flask-Mail with SendGrid SMTP
- [ ] Create email templates: booking confirmation, check-in reminder, cancellation
- [ ] Add APScheduler job: send check-in reminders daily at 9am
- [ ] Update `requirements.txt`:
  - `stripe`
  - `flask-mail`
  - `APScheduler`

### Frontend Tasks
- [ ] Add Stripe.js to `public/index.html`
- [ ] Build booking wizard:
  - `src/pages/booking/GuestDetailsPage.jsx` (pre-filled from user profile, price breakdown)
  - `src/pages/booking/PaymentPage.jsx` (Stripe Elements card form)
  - `src/pages/booking/ConfirmationPage.jsx` (booking reference, summary)
- [ ] Build `src/pages/account/MyBookingsPage.jsx` (booking history list)
- [ ] Build `src/pages/account/BookingDetailPage.jsx` (single booking with cancel option)
- [ ] Add price breakdown component (base rate × nights + taxes + total)
- [ ] Add availability calendar component on hotel detail page

---

## Phase 4 — Reviews + Ratings
> Adds trust signals. Dramatically increases perceived legitimacy.

### Database: PostgreSQL Tables (New)
- [ ] Create `reviews` table:
  ```sql
  CREATE TABLE reviews (
      id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      hotel_id          UUID REFERENCES hotels(id) ON DELETE CASCADE,
      booking_id        UUID REFERENCES bookings(id),
      user_id           UUID REFERENCES users(id),
      rating            SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
      title             TEXT,
      body              TEXT,
      cleanliness_score SMALLINT,
      location_score    SMALLINT,
      value_score       SMALLINT,
      service_score     SMALLINT,
      is_verified       BOOLEAN DEFAULT FALSE,
      created_at        TIMESTAMPTZ DEFAULT NOW()
  );
  ```
- [ ] Create `hotel_rating_summary` table (denormalized aggregate for fast reads):
  ```sql
  CREATE TABLE hotel_rating_summary (
      hotel_id        UUID PRIMARY KEY REFERENCES hotels(id),
      avg_rating      DECIMAL(3,2),
      review_count    INTEGER DEFAULT 0,
      avg_cleanliness DECIMAL(3,2),
      avg_location    DECIMAL(3,2),
      avg_value       DECIMAL(3,2),
      avg_service     DECIMAL(3,2),
      updated_at      TIMESTAMPTZ DEFAULT NOW()
  );
  ```

### Backend Tasks
- [ ] Implement `POST /api/v1/hotels/<id>/reviews` (requires completed booking at hotel)
- [ ] Implement `GET /api/v1/hotels/<id>/reviews?page=&sort=recent|rating`
- [ ] Implement `PUT /api/v1/reviews/<id>` (edit own review)
- [ ] Implement `DELETE /api/v1/reviews/<id>` (delete own review)
- [ ] Add DB trigger or post-insert hook to update `hotel_rating_summary` on every review write

### Frontend Tasks
- [ ] Build `src/components/reviews/ReviewCard.jsx`
- [ ] Build `src/components/reviews/ReviewList.jsx` (paginated, sortable)
- [ ] Build `src/components/reviews/ReviewForm.jsx` (gated to verified guests only)
- [ ] Build `src/components/reviews/RatingSummary.jsx` (overall score + category bars)
- [ ] Build `src/components/common/StarRating.jsx`
- [ ] Integrate review section into `HotelDetailPage.jsx`
- [ ] Add "Leave a Review" prompt in `BookingDetailPage.jsx` after checkout

---

## Phase 5 — Admin Dashboard
> Required for hotel admins to manage properties.

### Backend Tasks
- [ ] Provision Cloudinary free-tier account
- [ ] Implement `GET /api/v1/admin/bookings?hotel_id=&status=&from=&to=`
- [ ] Implement `PUT /api/v1/admin/bookings/<id>` (status updates: check-in, check-out)
- [ ] Implement `GET /api/v1/admin/analytics?hotel_id=&from=&to=` (occupancy, revenue, ADR)
- [ ] Implement `POST /api/v1/admin/hotels/<id>/photos/upload` (Cloudinary integration)
- [ ] Implement `DELETE /api/v1/admin/hotels/<id>/photos/<photo_id>`
- [ ] Implement `PUT /api/v1/admin/hotels/<id>/amenities`
- [ ] Implement `POST /api/v1/admin/rooms/<id>/availability/block` (block dates)
- [ ] Implement `POST /api/v1/admin/rooms/<id>/availability/price` (price override for date range)

### Frontend Tasks
- [ ] Add `recharts` to `package.json`
- [ ] Create `src/pages/admin/` directory with protected `AdminLayout.jsx`
- [ ] Build `src/pages/admin/HotelListPage.jsx`
- [ ] Build `src/pages/admin/HotelEditorPage.jsx`:
  - Basic info tab
  - Photos tab (Cloudinary upload widget)
  - Amenities tab (checkbox grid)
  - Rooms tab (room list + editor modal)
- [ ] Build `src/pages/admin/BookingsPage.jsx`:
  - Filter bar (status, date range, hotel)
  - Data table with inline status actions
  - CSV export button
- [ ] Build `src/pages/admin/AvailabilityCalendarPage.jsx`:
  - Month grid view, color-coded by availability
  - Click date range → set price override or block
- [ ] Build `src/pages/admin/AnalyticsPage.jsx`:
  - Occupancy rate chart
  - Revenue by month bar chart
  - Average daily rate metric

---

## Phase 6 — Dynamic Pricing
> Pricing rules applied at search time and payment confirmation.

### Database: PostgreSQL Tables (New)
- [ ] Create `pricing_rules` table:
  ```sql
  CREATE TABLE pricing_rules (
      id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      hotel_id     UUID REFERENCES hotels(id) ON DELETE CASCADE,
      room_id      UUID REFERENCES rooms(id),  -- NULL = applies to all rooms in hotel
      rule_type    TEXT NOT NULL,  -- 'seasonal' | 'day_of_week' | 'last_minute' | 'early_bird'
      multiplier   DECIMAL(4,3),  -- 1.5 = 50% markup, 0.8 = 20% discount
      date_from    DATE,
      date_to      DATE,
      days_of_week TEXT[],        -- e.g. ['Saturday', 'Sunday']
      days_before  SMALLINT,      -- for last_minute / early_bird rules
      priority     SMALLINT DEFAULT 0,
      is_active    BOOLEAN DEFAULT TRUE
  );
  ```

### Backend Tasks
- [ ] Create `backend/utils/pricing.py` with `calculate_price(room_id, check_in, check_out, base_price)`:
  1. Load all active pricing rules for room/hotel
  2. For each date in stay range, apply highest-priority matching rule
  3. Return per-night breakdown and total
- [ ] Integrate `calculate_price()` into `GET /api/v1/hotels/<id>/rooms` (show prices in search)
- [ ] Integrate `calculate_price()` into `POST /api/v1/payments/create-intent` (authoritative final price)
- [ ] Cassandra `price_override` field takes precedence over all rules

### Frontend Tasks
- [ ] Build `src/pages/admin/PricingRulesPage.jsx` (create/edit/delete rules)
- [ ] Update price breakdown component to show per-night rate variations
- [ ] Show "price calendar" on hotel detail page (color-coded nightly rates)

---

## Phase 7 — Advanced Search + Maps + Wishlist
> Polish and discovery features.

### Database: PostgreSQL Tables (New)
- [ ] Create `wishlists` table:
  ```sql
  CREATE TABLE wishlists (
      user_id  UUID REFERENCES users(id),
      hotel_id UUID REFERENCES hotels(id),
      saved_at TIMESTAMPTZ DEFAULT NOW(),
      PRIMARY KEY (user_id, hotel_id)
  );
  ```
- [ ] Add `tsvector` search column to `hotels` table for full-text search

### Backend Tasks
- [ ] Enrich `GET /api/v1/hotels` with full query params:
  - `min_price`, `max_price`, `stars`, `amenities`, `sort=price_asc|price_desc|rating_desc|distance`
- [ ] Add PostgreSQL full-text search on hotel name and city (`tsvector` / `tsquery`)
- [ ] Cross-DB search pipeline: PostgreSQL attributes filter → Cassandra availability filter → merge in Python → cache in Redis (2-min TTL)
- [ ] Implement `POST /api/v1/wishlists/<hotel_id>` (save hotel)
- [ ] Implement `DELETE /api/v1/wishlists/<hotel_id>` (unsave hotel)
- [ ] Implement `GET /api/v1/wishlists` (current user's saved hotels)

### Frontend Tasks
- [ ] Add `leaflet` and `react-leaflet` to `package.json`
- [ ] Add map toggle to `SearchResultsPage.jsx` (list view / map view)
- [ ] Render hotel pins on Leaflet map using `latitude`/`longitude` fields
- [ ] Add price range slider and multi-select amenity filter to search sidebar
- [ ] Add sort dropdown (Price: Low to High, Rating, Distance)
- [ ] Add heart icon to hotel cards (wishlist toggle)
- [ ] Build `src/pages/account/SavedHotelsPage.jsx`

---

## Key Technical Challenges

| Challenge | Solution |
|-----------|----------|
| Availability race conditions (two users book last room simultaneously) | Redis lock on `{room_id}:{date_range}` during payment confirmation; return 409 if lock held or units = 0 |
| Cassandra `bucket='all'` partition hotspot | Re-partition to `(hotel_id, year_month)` in Phase 1 — critical before any scale |
| Cross-DB search (availability in Cassandra, attributes in PostgreSQL) | Query PostgreSQL first → get room IDs → parallel Cassandra availability check → merge in Python |
| Photo storage on ephemeral Render filesystem | Cloudinary free tier — photos go browser → Cloudinary directly, backend stores only the URL |
| JWT security on GitHub Pages | Move to `httpOnly` SameSite cookies by serving React build from Flask on same domain |
| Stripe PCI compliance | Card details never touch your server — use Stripe.js `confirmCardPayment()` with client_secret |

---

## New Dependencies Summary

### Backend (`requirements.txt`)
| Package | Added In | Purpose |
|---------|----------|---------|
| `flask-jwt-extended` | Phase 1 | JWT auth tokens |
| `flask-sqlalchemy` | Phase 1 | PostgreSQL ORM |
| `psycopg2-binary` | Phase 1 | PostgreSQL driver |
| `marshmallow` | Phase 1 | Request/response serialization |
| `bcrypt` | Phase 1 | Password hashing |
| `redis` | Phase 1 | Redis client |
| `stripe` | Phase 3 | Payment processing |
| `flask-mail` | Phase 3 | Email sending |
| `APScheduler` | Phase 3 | Background cron jobs |

### Frontend (`package.json`)
| Package | Added In | Purpose |
|---------|----------|---------|
| `react-router-dom` | Phase 1 | Client-side routing |
| `zustand` | Phase 1 | Lightweight state management |
| `@tanstack/react-query` | Phase 1 | Server state + caching |
| `axios` | Phase 1 | HTTP client with interceptors |
| `recharts` | Phase 5 | Analytics charts |
| `leaflet` + `react-leaflet` | Phase 7 | Interactive maps |

---

## Progress Log
> Append entries here as work is completed.

| Date | Phase | What Was Done |
|------|-------|---------------|
| 2026-04-04 | — | Plan created |
| 2026-04-04 | Phase 1 | Backend restructured into app factory + Blueprints. Cassandra client moved to `db/cassandra_client.py` with `check_in_month` partitioning (fixes `bucket='all'` hotspot). Added `config.py`, `extensions.py`, `models/`, `utils/validators.py`, placeholder `db/postgres_client.py` and `db/redis_client.py`. Frontend restructured with `react-router-dom`, `zustand`, `@tanstack/react-query`, `axios`. New `src/api/`, `src/store/`, `src/components/`, `src/pages/` directories. `App.js` is now a router wrapper; reservation UI lives in `pages/HomePage.jsx`. |
| 2026-04-04 | Phase 3 | Stripe payment flow (create-intent → confirmCardPayment → confirm booking). Booking model + `bookings` table. Cassandra availability decrement/increment on book/cancel. Flask-Mail + SendGrid email (confirmation, check-in reminder, cancellation). APScheduler daily reminder job (opt-in via ENABLE_SCHEDULER env var). Redis lock prevents double-booking. Frontend: 3-step booking wizard (GuestDetailsPage → PaymentPage with Stripe CardElement → ConfirmationPage), MyBookingsPage, BookingDetailPage, PriceBreakdown component. All booking routes protected. `npm install` needed after adding `@stripe/react-stripe-js` and `@stripe/stripe-js`. |
| 2026-04-04 | Phase 2 | PostgreSQL models added (User, Hotel, HotelPhoto, Amenity, Room, RoomPhoto) via SQLAlchemy — auto-created by `db.create_all()`. JWT auth endpoints (register/login/refresh/logout/me). Full hotel API (list with filters, detail, rooms with Cassandra availability check, admin CRUD). Cassandra `room_availability` table added to schema. Seed script with 3 sample hotels. Frontend: LandingPage (hero + search + featured cities), SearchResultsPage (filters + cards + pagination), HotelDetailPage (gallery + rooms + reserve), LoginPage, RegisterPage, ProtectedRoute. `App.js` updated with all routes. |
