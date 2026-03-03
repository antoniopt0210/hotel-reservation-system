# hotel-reservation-system [(click for demo)](https://antoniopt0210.github.io/hotel-reservation-system/)

This is a full-stack web application for managing hotel reservations, designed to showcase a modern, multi-tiered software architecture. The system provides a simple interface for booking, checking in, checking out, and canceling reservations. (Inspired by **[Google's Apply Your Coding Knowledge Series](https://careersonair.withgoogle.com/events/apply-your-knowledge-pt1)**)

# Features
Book a Reservation: A user-friendly form to create new reservations with guest details, dates, and room type.

Real-time Status Updates: View all current reservations and their status in real-time.

Check-in/Check-out: Seamlessly change a reservation's status, reflecting the guest's journey.

Cancel Reservation: A function to permanently delete reservations from the system.

# Technologies
## Frontend
- React: For building a dynamic, single-page application and managing component state.

- JavaScript: For all client-side logic and API calls.

- Tailwind CSS: For fast, utility-first styling and a responsive UI design.

## Backend
- Python: The core programming language for the server-side logic.

- Flask: A lightweight micro-framework for building a RESTful API.

- Apache Cassandra: A distributed NoSQL database for scalable data persistence.

- Flask-CORS: To handle Cross-Origin Resource Sharing and enable frontend/backend communication.

# Cassandra Setup

The backend supports **local Cassandra** (development) and **DataStax Astra** (cloud deployment).

## Option A: DataStax Astra (Recommended for hosting online)

Astra is a managed Cassandra service with a free tier. Ideal for demos and production.

1. **Create an Astra database** at [astra.datastax.com](https://astra.datastax.com)
   - Create a new database (free tier)
   - Astra provides `default_keyspace` automatically — no need to create one

2. **Download the Secure Connect Bundle**
   - In your Astra dashboard → Database → Connect
   - Download the Secure Connect Bundle (ZIP file)
   - Rename it to `secure-connect-bundle.zip` and place it in the `backend/` folder
   - The bundle is safe to commit (contains connection info; your token is the secret)

3. **Create an Application Token**
   - Astra dashboard → Organization Settings → Token Management
   - Generate a token with **Database Administrator** role
   - Copy the token (starts with `AstraCS:...`)

4. **Deploy to Render** (or similar)
   - Connect your repo and deploy the backend
   - Add environment variables:
     - `ASTRA_DB_APPLICATION_TOKEN`: Your token from step 3
     - `ASTRA_DB_KEYSPACE`: Optional — defaults to `default_keyspace` (use `hotel` if you created a custom keyspace)
   - The bundle in `backend/` is used automatically

## Option B: Local Cassandra (Development)

1. **Install Cassandra** (e.g., via Docker):
   ```bash
   docker run -d -p 9042:9042 --name cassandra cassandra:latest
   ```
   Note: Cassandra may take 30-60 seconds to become ready after starting.

2. **Configure connection** (optional - defaults work for localhost):
   - `CASSANDRA_HOSTS`: Comma-separated host list (default: `127.0.0.1`)
   - `CASSANDRA_PORT`: Port number (default: `9042`)
   - `CASSANDRA_KEYSPACE`: Keyspace name (default: `hotel`)

3. **Install Python dependencies and run**:
   ```bash
   cd backend && pip install -r requirements.txt && python app.py
   ```

The keyspace and table are created automatically on first request.
