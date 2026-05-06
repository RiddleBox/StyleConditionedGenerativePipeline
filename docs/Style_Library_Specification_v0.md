# Style Library Specification v0.1

---

## 1. Module Purpose

A minimal persistent storage system for Style JSON.

Supports:

* Save style
* Retrieve style
* List styles

---

## 2. Data Model

---

### 2.1 Style Record

```json
{
  "style_id": "string",
  "style": {Style JSON},
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## 3. Storage Requirements

* Storage type: JSON file OR lightweight database (e.g. SQLite)
* Must persist across sessions
* style_id must be unique

---

## 4. API Contract

---

### 4.1 Save Style

#### Input

```json
{
  "style_id": "string",
  "style": {Style JSON}
}
```

#### Behavior

* If style_id does NOT exist → create new
* If exists → overwrite
* Update timestamp

#### Output

```json
{
  "status": "ok"
}
```

---

### 4.2 Get Style

#### Input

```json
{
  "style_id": "string"
}
```

#### Output

```json
{
  "style_id": "string",
  "style": {Style JSON}
}
```

#### Error

```json
{
  "error": "STYLE_NOT_FOUND"
}
```

---

### 4.3 List Styles

#### Input

```json
{}
```

#### Output

```json
{
  "styles": [
    {
      "style_id": "string",
      "created_at": "timestamp"
    }
  ]
}
```

---

## 5. Validation Rules

* style must pass Style JSON Schema v1.0
* style_id:

  * must be string
  * no spaces
  * lowercase recommended

---

## 6. File Structure (if JSON storage)

```text
/styles/
  ├── arch_watercolor_v1.json
  ├── flat_ui_v1.json
```

---

## 7. Determinism

* Same style_id → always same Style JSON
* No mutation outside save()

---

## 8. Forbidden Behavior

* Storing invalid JSON
* Auto-generating style_id
* Silent overwrite without timestamp update

---

## 9. Minimal Implementation Example

```python
class StyleLibrary:

    def save_style(self, style_id, style):
        validate_schema(style)
        store[style_id] = {
            "style": style,
            "updated_at": now()
        }

    def get_style(self, style_id):
        if style_id not in store:
            raise Error("STYLE_NOT_FOUND")
        return store[style_id]

    def list_styles(self):
        return list(store.keys())
```

---

## 10. Future Extension Hooks (DO NOT IMPLEMENT YET)

```text
- metadata (quality_score, tags)
- versioning
- preset linkage
```

---
