# TikTik Smart Order System

## Overview
A smart system for generating professional quotes and orders for TikTik, a company specializing in tickets for sports and concert events.

The system aims to:
- Save agents time in creating orders.
- Generate professional PDFs with legal terms.
- Automatically send orders to customers via email.
- Allow for digital signatures.
- Track order statuses.
- Maintain order history and enable Excel export.

The project's ambition is to streamline the sales process, improve customer experience, and provide robust reporting capabilities.

## User Preferences
- Professional design matching current PowerPoint templates
- Full Hebrew support (RTL)
- Quick workflow for agents (minimize manual input)
- Both download and email sending options
- Event type selection for filtering/templates

## System Architecture

### UI/UX Decisions
- Streamlit framework for the main application.
- Comprehensive CSS media queries for mobile responsiveness (up to 768px and 480px screens) including font size adjustments, minimum touch targets, column stacking, reduced padding/margins, sidebar optimization, and touch-friendly controls.
- Enhanced drag & drop styling for all file uploaders with visual cues.
- Clipboard paste support for OCR functions using `streamlit-paste-button`.
- Clear form button to reset order details.
- Sidebar navigation for different sections (New Order, Order History, Export Reports, Admin Gallery).

### Technical Implementations
- **PDF Generation**: Uses `WeasyPrint` and `Jinja2` templates for professional, multi-page PDFs with RTL Hebrew support via CSS, integrating brand assets.
- **Database**: PostgreSQL with SQLAlchemy ORM for persistence of orders, event templates, order statuses, event types, hotel cache, and atmosphere images.
- **Hebrew Support**: Utilizes `python-bidi` and `arabic-reshaper` for proper RTL display in PDFs and UI. Custom `TikTikPDF` class extends `FPDF` for legacy PDF generation if needed.
- **Order Numbering**: `TT-YYYYMMDD-XXXXXXXX` format using UUID suffix for uniqueness.
- **Passenger Data**: Stored as structured JSON objects, supporting various ticket types.
- **Product Types**: Supports "Full Package" (hotel, flights, transfers, tickets) and "Tickets Only," with dynamic UI and PDF content based on selection.
- **Passport OCR**: Integrates Gemini AI for automatic extraction of passenger details from passport images, auto-populating fields. Includes retry logic for network errors.
- **Hotel Resolver**: Integrates Google Places API to auto-fetch hotel details (name, address, website, rating, check-in/out), download images, and apply star ratings. Features database caching for efficiency.
- **Flight Details**: Enhanced input with airport autocomplete using a curated database of airports, structured inputs for outbound/return flights.
- **Flight OCR**: Uses Gemini AI vision for extracting flight information from screenshots. Includes retry logic.
- **Baggage Options**: Checkboxes for trolley and dropdown for checked baggage, displayed in PDF.
- **Atmosphere Image Gallery**: Admin interface for managing categorized atmosphere images. Images are stored and randomly selected based on event type for PDF generation if no custom image is uploaded.
- **Automatic Stadium Maps**: Pre-defined stadium seating charts and data for major teams (e.g., Real Madrid, Barcelona), auto-displaying maps and filling stadium details based on team selection. Includes FIFA World Cup 2026 stadium maps with seating categories.
- **Football Fixtures Auto-Fill**: Integrates `openfootball` GitHub data to auto-fill match dates and times based on selected home and away teams. Includes comprehensive team name mappings and FIFA World Cup 2026 schedule with venue details.
- **Football Match Selection**: Two selection modes for football events:
  - **"בחר משחק מרשימה"**: Browse all season fixtures with team search filter (Hebrew/English support). Select a match to auto-fill all details (teams, date, time, round).
  - **"בחר קבוצות ידנית"**: Traditional manual team selection with dropdowns.
  - Filter shows first 50 matches, supports partial name matching in both languages.
  - Session state properly clears when switching between modes.
- **Concert Selection**: Features artist and venue dropdowns for concert orders, auto-filling event names and venue details. Includes 10 popular artists (Metallica, Coldplay, Ed Sheeran, etc.) and 16 major European venues.
- **Concert API Integration**: Combined search from Ticketmaster Discovery API + RapidAPI Real-Time Events via `concerts_service.py`. Features:
  - **Multi-Source Search**: Searches both Ticketmaster AND RapidAPI for comprehensive coverage (includes regional sites like Greece)
  - **Data Fields**: Event name, date, time, venue details (name, address, capacity, phone), city, country, pricing, currency, and event URLs
  - **Filtering**: European concerts only (33 European countries including Greece, Turkey, Russia)
  - **Database Caching**: `ConcertCache` model stores search results for 24 hours, shared across all users to reduce API calls
  - **Error Handling**: Rate limit and timeout handling
  - **Limitations**: No seating maps in API, but provides venue URLs with full seat selection on Ticketmaster
  - Uses `TICKETMASTER_API_KEY` and `RAPIDAPI_KEY` secrets.
- **Concert Venue Maps**: Venue map management for concerts with auto-caching. Features:
  - **Auto-save uploaded maps**: When user uploads a map for a concert venue, it's automatically saved to `attached_assets/concert_venue_maps/{venue_id}.png` for reuse
  - **URL paste option**: Users can paste a direct image URL to save the map
  - **Auto-display**: Previously saved maps display automatically when selecting the same venue
  - **Fallback**: Uses `assets/concert_bg.jpg` as default if no specific map is available
- **Saved Concerts**: Allows agents to save manually-entered concerts for quick reuse. Features:
  - **Save to Favorites**: "שמור להופעות קבועות" button when entering concert details manually
  - **Quick Selection**: "⭐ הופעות שמורות" option in artist dropdown to select previously saved concerts
  - **Management Page**: Sidebar tool "⭐ הופעות שמורות" to view and delete saved concerts
  - **Database Storage**: `SavedConcert` model stores artist, venue, city, country, date, time, and category
- **Package Templates**: Reusable package templates for recurring events with same flights/hotels. Features:
  - **Create Templates**: Save complete packages (event, flights, hotel, pricing) as templates via "📦 חבילות קבועות" sidebar
  - **Load in Orders**: Select a saved package in new order form to auto-fill all fields except passenger details
  - **Duplicate/Edit/Delete**: Manage templates with copy functionality for variations (e.g., same event with different ticket categories)
  - **Database Storage**: `PackageTemplate` model stores event info, flights JSON, hotel JSON, pricing, stadium maps (binary)
  - **Quick Workflow**: Agents only need to add passenger details when using a template
- **Help Page**: Comprehensive Hebrew user guide accessible via "❓ עזרה" button in sidebar. Features:
  - System overview and capabilities
  - Step-by-step guide for creating orders
  - Football events workflow
  - Concert handling guide
  - Passport OCR instructions with tips
  - Hotel search and flight details guide
  - Order history and status explanations
  - Export reports guide
  - FAQ section with common questions
- **AI Chatbot**: Gemini-powered assistant in sidebar for quick help. Features:
  - Expandable chat widget ("💬 שאל שאלה")
  - System-aware responses with TikTik knowledge
  - Chat history (last 3 Q&A pairs displayed)
  - Hebrew language support
  - Graceful error handling when AI unavailable

### Feature Specifications
- **Core Modules**: `app.py` (main Streamlit app), `models.py` (SQLAlchemy models), `pages/signature.py` (digital signature page), `terms.txt` (legal terms), `fonts/Arial.ttf` (Hebrew font).
- **Email Integration**: Uses `Resend` API for sending emails, with a fallback to download-only if the API key is not configured.

## External Dependencies

- **streamlit**: UI framework.
- **fpdf2**: PDF generation (legacy support).
- **WeasyPrint**: Primary PDF generation.
- **Jinja2**: Templating for PDF generation.
- **python-bidi**: Bidirectional algorithm support.
- **arabic-reshaper**: Arabic text reshaping for Hebrew.
- **Pillow**: Image processing.
- **resend**: Email sending service.
- **streamlit-drawable-canvas**: Digital signature capture.
- **SQLAlchemy**: ORM for database interaction.
- **psycopg2-binary**: PostgreSQL adapter.
- **openpyxl**: Excel export functionality.
- **Google Places API**: For hotel information lookup (`GOOGLE_PLACES_API_KEY`).
- **Gemini AI**: For Passport OCR and Flight OCR (via Replit AI Integrations).
- **openfootball GitHub data**: For football fixtures.