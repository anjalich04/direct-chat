# 💬 DirectChat — Real-Time 1-on-1 Private Messaging Application

DirectChat is a full-stack real-time 1-on-1 private messaging web application built with Django, Django Channels, Daphne, WebSockets, Bootstrap, and Vanilla JavaScript. It allows authenticated users to exchange private messages in real time with chat history, read receipts, unread indicators, toast notifications, and typing status.

---

## Features

- User registration and login
- Session authentication
- 1-on-1 real-time messaging
- Chat history
- Delivery and read receipts (`✓` / `✓✓`)
- Unread message badges
- Toast notifications
- Typing indicators
- User search
- Responsive dark UI

---

## Tech Stack

| Category | Technology |
| :--- | :--- |
| Programming Language | Python 3.11+ |
| Web Framework | Django 5.1+ |
| Real-Time Framework | Django Channels 4.x |
| ASGI Gateway | Daphne |
| Database | SQLite |
| Frontend Markup & Styles | HTML5, CSS3, Bootstrap 5 |
| Client Scripting | Vanilla JavaScript |
| Communication Protocols | WebSockets, HTTP/JSON APIs |

---

## Project Structure

```text
direct-chat/
├── accounts/
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── chat/
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── direct_chat/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── home.html
│   ├── login.html
│   └── register.html
├── .env.example
├── manage.py
├── requirements.txt
└── README.md
```

---

## Authentication

DirectChat uses Django's built-in `User` model and session-based authentication:
- **Registration**: Validates unique usernames, unique email addresses, password rules, and password confirmation matching.
- **Login & Logout**: Authenticates user credentials and manages Django session state.
- **Protected Access**: Dashboard views and API routes require user authentication via `@login_required`.

---

## Real-Time Messaging

- **Direct Communication**: Messages are exchanged 1-on-1 between authenticated users.
- **Persistence**: Messages are saved to SQLite with sender, receiver, content, read status, and timestamp.
- **History Loading**: Dynamic Fetch API requests load past message exchanges chronologically upon selecting a contact.
- **Read State**: Sent messages track read status (`is_read`), updating status indicators when viewed by the recipient.

---

## Real-Time Features

- **WebSocket Connection**: Handles bi-directional message delivery asynchronously using Django Channels and Daphne.
- **Typing Indicator**: Client keydown events emit typing status updates, which automatically reset after 1 second of inactivity.
- **Read Receipts**: Opening an unread conversation updates database flags and emits WebSocket notifications to update sent check marks (`✓` to `✓✓`).
- **Unread Badges**: Live counters next to each contact in the sidebar increment when messages arrive from non-active chats.
- **Toast Notifications**: Floating alert popups inform users of incoming messages from inactive conversations.

---

## API Endpoints

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/users` | Retrieve list of registered users with unread message counts |
| `GET` | `/chat/messages/<user_id>/` | Fetch 1-on-1 chat history with a specific user |
| `PATCH` | `/api/messages/<other_user_id>/read` | Mark incoming unread messages from a user as read |
| `POST` | `/chat/send/` | HTTP endpoint fallback to send a message |

---

## WebSocket

- **Endpoint**: `/ws/chat/`
- **Consumer**: `ChatConsumer` (`AsyncWebsocketConsumer`)
- **Channel Groups**: Users join an isolated channel group (`user_<user_id>`) upon socket connection.
- **Events**:
  - `chat_message`: Direct message payload transmission
  - `typing` / `typing_status`: Real-time typing activity state
  - `messages_read`: Read receipt notification update

---

## Database

DirectChat uses SQLite with Django ORM for data storage:
- **User Relationship**: Foreign Keys link `sender` and `receiver` fields to Django's built-in `User` model.
- **Message Fields**:
  - `sender`: `ForeignKey(User)`
  - `receiver`: `ForeignKey(User)`
  - `content`: `TextField`
  - `is_read`: `BooleanField` (default `False`)
  - `created_at`: `DateTimeField` (auto-populated timestamp)

---

## UI

- **Framework**: Bootstrap 5 dark theme with high-contrast form controls.
- **Sidebar**: Displays registered users, unread badge counters, and client-side search filtering.
- **Chat Area**: Header displaying contact username and typing status, scrollable chat message panel, status check marks, and multi-line message input (`Enter` to send, `Shift + Enter` for newline).

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/anjalich04/direct-chat.git
   cd direct-chat
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

6. **Run database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser** *(optional)*:
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

   Access the application at `http://127.0.0.1:8000/`.

---

## Testing

Run Django configuration check:
```bash
python manage.py check
```

Run automated unit test suite:
```bash
python manage.py test
```

---

## Usage

1. Register two users at `http://127.0.0.1:8000/register/` (e.g., `user1` and `user2`).
2. Log in as `user1` in a primary browser window and `user2` in an Incognito window.
3. Select `user2` from `user1`'s sidebar to open the chat thread.
4. Type in the input box to observe the typing indicator (`"user1 is typing..."`) in `user2`'s chat header.
5. Send a message to verify real-time delivery, single check mark (`✓`), unread badges, and toast alerts.
6. Open the conversation in `user2`'s window to verify history loading, unread badge clearing, and read receipt updates (`✓` to `✓✓`).

---

## Future Improvements

Planned features for future iterations:
- Group messaging
- File/image attachments
- Redis channel layer for multi-worker deployment
- Online/offline presence

---

## Author

**Anjali CH**

- GitHub: https://github.com/anjalich04
- Repository: https://github.com/anjalich04/direct-chat
