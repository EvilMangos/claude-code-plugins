# Injection Attack Patterns & Prevention

Deep dive into injection vulnerabilities: how they work, how to detect them in code, and how to prevent them.

## SQL Injection

### Attack Anatomy

SQL injection occurs when user input is incorporated into SQL queries without proper handling.

**Basic exploitation flow:**
1. Attacker identifies input field that builds SQL query
2. Attacker crafts input containing SQL syntax
3. Application concatenates input into query string
4. Database executes attacker's injected SQL

### Common Attack Patterns

#### Authentication Bypass
```sql
-- Original query
SELECT * FROM users WHERE username='[INPUT]' AND password='[INPUT]'

-- Attack input for username: admin'--
-- Resulting query:
SELECT * FROM users WHERE username='admin'--' AND password='anything'
-- The -- comments out the password check
```

#### Data Extraction (UNION-based)
```sql
-- Original query
SELECT name, price FROM products WHERE id=[INPUT]

-- Attack input: 1 UNION SELECT username, password FROM users--
-- Resulting query:
SELECT name, price FROM products WHERE id=1 UNION SELECT username, password FROM users--
```

#### Blind SQL Injection
```sql
-- Boolean-based: infer data from true/false responses
-- Input: 1 AND (SELECT SUBSTRING(username,1,1) FROM users WHERE id=1)='a'

-- Time-based: infer data from response time
-- Input: 1; IF (1=1) WAITFOR DELAY '0:0:5'--
```

### Vulnerable Code Patterns

**Pattern 1: String concatenation**
```
query = "SELECT * FROM users WHERE id = " + userId
```

**Pattern 2: String formatting**
```
query = f"SELECT * FROM users WHERE id = {userId}"
query = "SELECT * FROM users WHERE id = %s" % userId
```

**Pattern 3: String interpolation in ORM raw queries**
```
Model.raw("SELECT * FROM users WHERE id = " + userId)
```

### Prevention Patterns

**Parameterized queries (correct):**
```
# Placeholder syntax varies by language/driver
query = "SELECT * FROM users WHERE id = ?"
execute(query, [userId])

query = "SELECT * FROM users WHERE id = :id"
execute(query, {id: userId})

query = "SELECT * FROM users WHERE id = $1"
execute(query, [userId])
```

**ORM usage (correct):**
```
User.find(userId)
User.where(id: userId).first
```

---

## NoSQL Injection

### Attack Anatomy

NoSQL injection exploits operator syntax in document databases.

### Common Attack Patterns

#### Query Operator Injection
```javascript
// Original intended query
db.users.find({username: userInput, password: passInput})

// Attack: if userInput is an object: {"$gt": ""}
// Resulting query:
db.users.find({username: {"$gt": ""}, password: passInput})
// Returns first user where username > "" (any non-empty username)
```

#### Array Injection
```javascript
// If application expects: {role: "user"}
// Attack passes: {role: {"$in": ["user", "admin"]}}
```

### Vulnerable Code Patterns

**Pattern 1: Direct object assignment**
```javascript
// If req.body.username can be an object, this is vulnerable
db.users.find({username: req.body.username})
```

**Pattern 2: String to query conversion**
```javascript
// JSON.parse of user input directly into query
const criteria = JSON.parse(userInput)
db.users.find(criteria)
```

### Prevention Patterns

**Type validation (correct):**
```javascript
// Ensure input is string, not object
if (typeof username !== 'string') {
  throw new Error('Invalid input type')
}
db.users.find({username: username})
```

**Schema validation (correct):**
```javascript
// Use schema to enforce types
const schema = {
  username: {type: 'string', required: true},
  password: {type: 'string', required: true}
}
validate(input, schema)
```

---

## Command Injection

### Attack Anatomy

Command injection occurs when user input is passed to system shell execution.

### Common Attack Patterns

#### Command Chaining
```bash
# Original command
ping [userInput]

# Attack input: 127.0.0.1; cat /etc/passwd
# Resulting command:
ping 127.0.0.1; cat /etc/passwd
```

#### Command Substitution
```bash
# Attack input: $(cat /etc/passwd)
# Or: `cat /etc/passwd`
```

#### Argument Injection
```bash
# Original: tar -cf archive.tar [userInput]
# Attack: --checkpoint=1 --checkpoint-action=exec=malicious.sh
```

### Vulnerable Code Patterns

**Pattern 1: Direct shell execution**
```
system("ping " + host)
exec("convert " + filename + " output.png")
```

**Pattern 2: Shell=true flag**
```python
subprocess.run("echo " + message, shell=True)
```

**Pattern 3: eval/exec with user input**
```javascript
eval("process(" + userInput + ")")
```

### Prevention Patterns

**Use arrays instead of strings (correct):**
```python
# Avoid shell=True, use array of arguments
subprocess.run(["ping", "-c", "4", host], shell=False)
```

**Use language-native APIs (correct):**
```python
# Instead of: system("rm " + filename)
# Use: os.remove(filename)

# Instead of: system("mkdir " + dirname)
# Use: os.makedirs(dirname)
```

**Allowlist validation (correct):**
```python
ALLOWED_HOSTS = {"google.com", "github.com"}
if host not in ALLOWED_HOSTS:
    raise ValueError("Host not allowed")
```

---

## XSS (Cross-Site Scripting)

### Attack Anatomy

XSS occurs when attacker-controlled data is rendered in a browser without proper encoding.

### XSS Types

| Type | Storage | Execution |
|------|---------|-----------|
| Reflected | URL/request | Immediate in response |
| Stored | Database | When data is displayed |
| DOM-based | Client-side | JavaScript manipulation |

### Common Attack Patterns

#### Basic Script Injection
```html
<!-- Input stored/reflected without encoding -->
<div>Hello, <script>alert(document.cookie)</script></div>
```

#### Event Handler Injection
```html
<img src=x onerror="alert(1)">
<body onload="alert(1)">
<input onfocus="alert(1)" autofocus>
```

#### JavaScript Context Injection
```javascript
// If user input placed in JS context:
var name = '[userInput]';

// Attack input: '; alert(document.cookie); '
// Result:
var name = ''; alert(document.cookie); '';
```

#### DOM XSS
```javascript
// Vulnerable: inserting URL parameter into DOM
document.getElementById('name').innerHTML = getUrlParam('name')

// Attack URL: page.html?name=<img src=x onerror=alert(1)>
```

### Vulnerable Code Patterns

**Pattern 1: Direct HTML insertion**
```javascript
element.innerHTML = userInput
document.write(userInput)
```

**Pattern 2: Disabled template escaping**
```html
<!-- Various template engines -->
{{{userInput}}}        <!-- Handlebars raw -->
<%- userInput %>       <!-- EJS raw -->
{{ userInput | safe }} <!-- Jinja2 raw -->
@Html.Raw(userInput)   <!-- Razor raw -->
```

**Pattern 3: URL in href/src without validation**
```html
<a href="{{userInput}}">Click</a>
<!-- Attack: javascript:alert(1) -->
```

### Prevention Patterns

**Context-aware encoding (correct):**
```
HTML context:  < → &lt;  > → &gt;  & → &amp;
Attribute:     " → &quot;  ' → &#x27;
JavaScript:    Use JSON.stringify() for data
URL:           encodeURIComponent()
```

**Use safe APIs (correct):**
```javascript
// Instead of innerHTML, use textContent
element.textContent = userInput

// For URLs, validate protocol
if (!url.startsWith('https://')) {
    throw new Error('Invalid URL')
}
```

**Content Security Policy (defense in depth):**
```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

---

## LDAP Injection

### Attack Patterns

```
# Original filter
(&(uid=[userInput])(password=[passInput]))

# Attack input for uid: *)(uid=*))(|(uid=*
# Resulting filter:
(&(uid=*)(uid=*))(|(uid=*)(password=anything))
# Always matches
```

### Prevention

- Use parameterized LDAP queries if available
- Escape special characters: `* ( ) \ NUL`
- Validate input against strict pattern

---

## Template Injection (SSTI)

### Attack Patterns

Server-Side Template Injection occurs when user input is embedded in template syntax.

```python
# Vulnerable
render_template_string("Hello " + username)

# Attack input: {{config.items()}}
# Or: {{''.__class__.__mro__[1].__subclasses__()}}
```

### Prevention

- Never pass user input directly to template engine
- Use templates with variables, not string concatenation
- Enable sandboxing if available

---

## Detection Checklist for Code Review

When reviewing code, look for these patterns:

### SQL Injection Indicators
- [ ] String concatenation building SQL queries
- [ ] f-strings, format(), or % formatting in SQL
- [ ] Raw SQL methods in ORMs without parameterization
- [ ] Dynamic table/column names from user input

### Command Injection Indicators
- [ ] system(), exec(), spawn(), popen() with user input
- [ ] shell=True with user-influenced arguments
- [ ] eval(), exec() of user data
- [ ] Backticks or $() in scripts with user data

### XSS Indicators
- [ ] innerHTML assignment with external data
- [ ] document.write() with user input
- [ ] Template raw/unescaped output directives
- [ ] Missing Content-Security-Policy header
- [ ] href/src attributes with unchecked URLs

### General Injection Indicators
- [ ] User input directly in interpreter syntax
- [ ] Missing input validation at system boundary
- [ ] Disabled encoding/escaping
- [ ] Custom query builders with string operations
