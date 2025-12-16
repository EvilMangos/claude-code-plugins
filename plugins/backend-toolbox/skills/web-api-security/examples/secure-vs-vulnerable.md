# Secure vs Vulnerable Code Patterns

Side-by-side comparisons of vulnerable and secure implementations for common security scenarios.

## SQL Injection

### User Login

**Vulnerable:**

```
function login(username, password):
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    result = db.execute(query)
    return result.first()
```

**Secure:**

```
function login(username, password):
    query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
    hashed = hash_password(password)
    result = db.execute(query, [username, hashed])
    return result.first()
```

**Why vulnerable:** Direct string concatenation allows attacker to inject SQL.
**Attack:** Username `admin'--` bypasses password check.

---

### Search Functionality

**Vulnerable:**

```
function search(term):
    query = "SELECT * FROM products WHERE name LIKE '%" + term + "%'"
    return db.execute(query)
```

**Secure:**

```
function search(term):
    query = "SELECT * FROM products WHERE name LIKE ?"
    search_term = "%" + escape_like_wildcards(term) + "%"
    return db.execute(query, [search_term])
```

**Note:** Even LIKE queries need parameterization plus wildcard escaping.

---

## XSS Prevention

### Displaying User Content

**Vulnerable:**

```html

<div id="comment"></div>
<script>
    document.getElementById('comment').innerHTML = serverData.userComment
</script>
```

**Secure:**

```html

<div id="comment"></div>
<script>
    document.getElementById('comment').textContent = serverData.userComment
</script>
```

**Why vulnerable:** innerHTML parses HTML, allowing script injection.
**Attack:** Comment `<img src=x onerror="steal(document.cookie)">` executes JavaScript.

---

### URL Handling

**Vulnerable:**

```html
<a href="{{ user_provided_url }}">Visit Site</a>
```

**Secure:**

```
function safe_url(url):
    parsed = parse_url(url)
    if parsed.protocol not in ['http', 'https']:
        return '#'
    return url

<a href="{{ safe_url(user_provided_url) }}">Visit Site</a>
```

**Attack:** URL `javascript:alert(document.cookie)` executes on click.

---

### JSON in Script Tags

**Vulnerable:**

```html

<script>
    var userData = {{ user_data | tojson }};
</script>
```

**Secure:**

```html

<script>
    var userData = {{ user_data | tojson | safe }};
</script>
<!-- Note: tojson already escapes, but also add CSP header -->
```

**Better approach:**

```html

<div id="data" data-user="{{ user_data | tojson | escape }}"></div>
<script>
    var userData = JSON.parse(document.getElementById('data').dataset.user);
</script>
```

---

## Authentication

### Password Storage

**Vulnerable:**

```
function create_user(username, password):
    query = "INSERT INTO users (username, password) VALUES (?, ?)"
    db.execute(query, [username, password])  # Storing plaintext!
```

**Secure:**

```
function create_user(username, password):
    hash = bcrypt.hash(password, rounds=12)
    query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(query, [username, hash])
```

---

### Password Verification

**Vulnerable:**

```
function verify_password(stored_hash, provided_password):
    return stored_hash == hash(provided_password)  # Timing attack!
```

**Secure:**

```
function verify_password(stored_hash, provided_password):
    return bcrypt.verify(provided_password, stored_hash)  # Constant-time
```

**Why vulnerable:** String comparison leaks timing information.

---

### Session Management

**Vulnerable:**

```
function login_success(user):
    session_id = str(user.id)  # Predictable!
    save_session(session_id, user)
    return session_id
```

**Secure:**

```
function login_success(user):
    session_id = generate_random_bytes(32).to_hex()
    save_session(session_id, user)
    set_cookie('session', session_id, httponly=True, secure=True, samesite='Strict')
    return session_id
```

---

## Authorization

### Resource Access (IDOR)

**Vulnerable:**

```
# GET /api/documents/123
function get_document(doc_id):
    return db.documents.find(doc_id)  # No ownership check!
```

**Secure:**

```
# GET /api/documents/123
function get_document(doc_id, current_user):
    document = db.documents.find(doc_id)
    if document.owner_id != current_user.id:
        raise ForbiddenError()
    return document
```

---

### Admin Functions

**Vulnerable:**

```
# Relies on hidden UI elements for security
function delete_user(user_id):
    db.users.delete(user_id)
```

**Secure:**

```
function delete_user(user_id, current_user):
    if not current_user.has_role('admin'):
        raise ForbiddenError()
    if user_id == current_user.id:
        raise BadRequest("Cannot delete self")
    db.users.delete(user_id)
    audit_log('user_deleted', {actor: current_user.id, target: user_id})
```

---

## Command Injection

### File Operations

**Vulnerable:**

```
function convert_image(filename):
    system("convert " + filename + " output.png")
```

**Secure:**

```
function convert_image(filename):
    # Use library instead of shell
    image = Image.open(filename)
    image.save("output.png")

    # If shell required, use array syntax
    subprocess.run(["convert", filename, "output.png"], shell=False)
```

---

### User-Provided URLs

**Vulnerable:**

```
function fetch_url(url):
    system("curl " + url + " > output.txt")
```

**Secure:**

```
function fetch_url(url):
    # Validate URL first
    parsed = parse_url(url)
    if parsed.host not in ALLOWED_HOSTS:
        raise BadRequest("Host not allowed")
    if parsed.scheme not in ['http', 'https']:
        raise BadRequest("Invalid scheme")

    # Use library, not shell
    response = http_client.get(url)
    save_to_file(response.body, "output.txt")
```

---

## CSRF Protection

### State-Changing Operation

**Vulnerable:**

```
# POST /api/transfer
function transfer_money(from_account, to_account, amount):
    # No CSRF check!
    do_transfer(from_account, to_account, amount)
```

**Secure:**

```
# POST /api/transfer
function transfer_money(from_account, to_account, amount, csrf_token):
    if not verify_csrf_token(csrf_token, session):
        raise ForbiddenError("Invalid CSRF token")
    do_transfer(from_account, to_account, amount)
```

**Form implementation:**

```html

<form method="POST" action="/api/transfer">
    <input type="hidden" name="csrf_token" value="{{ generate_csrf_token() }}">
    <!-- other fields -->
</form>
```

---

## Input Validation

### Email Input

**Vulnerable:**

```
function update_email(email):
    user.email = email  # No validation
    user.save()
```

**Secure:**

```
function update_email(email):
    if not is_valid_email(email):
        raise ValidationError("Invalid email format")
    if len(email) > 254:
        raise ValidationError("Email too long")
    user.email = email
    user.save()
```

---

### Numeric Input

**Vulnerable:**

```
function get_page(page_param):
    page = int(page_param)  # Crashes on non-numeric
    return fetch_results(page)
```

**Secure:**

```
function get_page(page_param):
    try:
        page = int(page_param)
    except ValueError:
        page = 1

    if page < 1:
        page = 1
    if page > MAX_PAGE:
        page = MAX_PAGE

    return fetch_results(page)
```

---

## Error Handling

### Database Errors

**Vulnerable:**

```
function get_user(id):
    try:
        return db.users.find(id)
    except DatabaseError as e:
        return {"error": str(e)}  # Leaks DB info!
```

**Secure:**

```
function get_user(id):
    try:
        return db.users.find(id)
    except DatabaseError as e:
        log.error("Database error", {error: e, user_id: id})
        return {"error": "An error occurred"}  # Generic message
```

---

## File Upload

### Image Upload

**Vulnerable:**

```
function upload_image(file):
    filename = file.original_name
    save_path = "/uploads/" + filename  # Path traversal!
    file.save(save_path)
```

**Secure:**

```
function upload_image(file):
    # Generate safe filename
    extension = get_safe_extension(file.content_type)
    if extension not in ['jpg', 'png', 'gif']:
        raise BadRequest("Invalid file type")

    filename = generate_uuid() + "." + extension
    save_path = os.path.join(UPLOAD_DIR, filename)

    # Verify path is within upload directory
    if not os.path.realpath(save_path).startswith(UPLOAD_DIR):
        raise BadRequest("Invalid path")

    file.save(save_path)

    # Verify it's actually an image
    if not is_valid_image(save_path):
        os.remove(save_path)
        raise BadRequest("Invalid image")
```

---

## Secure Headers

### Response Headers

**Vulnerable:**

```
function send_response(data):
    return Response(data)  # No security headers
```

**Secure:**

```
function send_response(data):
    response = Response(data)
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

---

## Summary Table

| Category      | Vulnerable Pattern    | Secure Pattern              |
|---------------|-----------------------|-----------------------------|
| SQL           | String concatenation  | Parameterized queries       |
| XSS           | innerHTML, raw output | textContent, encoding       |
| Passwords     | Plaintext, MD5/SHA1   | bcrypt/Argon2               |
| Sessions      | Sequential IDs        | Random 256-bit tokens       |
| Authorization | UI-only controls      | Server-side checks          |
| Commands      | shell=True, system()  | Library calls, arrays       |
| CSRF          | No token              | Per-session tokens          |
| Files         | User-controlled paths | Generated names, validation |
