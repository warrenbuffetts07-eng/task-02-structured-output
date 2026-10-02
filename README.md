# Task 02 — Structured Output

## Project Title

**Reliable JSON Output with Schema Validation and Retry**

## Objective

The objective of this project is to make an AI model return structured JSON that can be reliably consumed by Python code.

The project extracts customer order information from a natural-language message and converts it into a validated Python object.

The project demonstrates:

1. A schema that defines the required output.
2. Validation that rejects invalid model output.
3. A retry/repair mechanism when validation fails.

## Project Structure

```text
task-02-structured-output/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Output Schema

```json
{
  "customer_name": "string",
  "mobile_number": "10 digit string",
  "product": "string",
  "weight_kg": "positive number or null"
}
```

The schema is implemented using Pydantic. Additional fields are rejected, and the mobile number must contain exactly 10 digits.

## Example Input

```text
Hi, I need a 370 kg cultivator.
My name is Rajesh Sharma and my phone is 9876543210.
```

## Expected Output

```json
{
  "customer_name": "Rajesh Sharma",
  "mobile_number": "9876543210",
  "product": "cultivator",
  "weight_kg": 370.0
}
```

## How Validation Works

The model output is first parsed as JSON. The JSON is then validated against the Pydantic `CustomerOrder` schema.

Validation checks:

- Required fields
- Correct data types
- Customer name is not empty
- Mobile number contains exactly 10 digits
- Product is not empty
- Weight is positive or null
- No unexpected extra fields are allowed

If validation fails, the output is rejected.

## Retry / Repair Path

If the model returns invalid JSON or JSON that does not match the schema, the program catches the error.

It then sends a repair instruction containing the validation error and asks the model to return corrected JSON.

The program allows up to three attempts. If all three attempts fail, it raises an error instead of returning unreliable data.

## How to Run

### 1. Install Python

Python 3.10 or newer is recommended.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set the API key

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

On macOS/Linux:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Do not put the API key directly inside `main.py` or commit it to GitHub.

### 4. Run

```bash
python main.py
```

Expected successful output:

```text
Valid output received on attempt 1.

Validated customer order:
{
  "customer_name": "Rajesh Sharma",
  "mobile_number": "9876543210",
  "product": "cultivator",
  "weight_kg": 370.0
}
```

## Design Decision

The model response is treated as untrusted input. Pydantic is used as the validation layer so that downstream code receives a typed `CustomerOrder` object rather than arbitrary model output.

The retry path is intentionally limited to three attempts so that a persistent failure does not create an infinite loop.

## Key Learning

Simply asking an AI model to "return JSON" is not enough for reliable software. A schema defines what valid data looks like, validation rejects bad data, and a repair path gives the model an opportunity to correct invalid output.

The final flow is:

```text
User Input
    ↓
AI Model
    ↓
JSON Response
    ↓
Pydantic Validation
    ↓
Valid? ── Yes ──> Typed Data
    │
    No
    ↓
Repair Prompt
    ↓
AI Model
    ↓
Validation Again
```

## Conclusion

This project demonstrates a simple approach to using AI-generated structured data safely in software by validating the model response before allowing it into the application.
