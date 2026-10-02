import json
import os
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CustomerOrder(BaseModel):
    """Typed structure that the AI output must match."""

    model_config = ConfigDict(extra="forbid")

    customer_name: str = Field(min_length=1)
    mobile_number: str = Field(pattern=r"^[0-9]{10}$")
    product: str = Field(min_length=1)
    weight_kg: Optional[float] = Field(default=None, gt=0)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You extract customer order information from text.

Return ONLY valid JSON.

The JSON must contain exactly these fields:
customer_name
mobile_number
product
weight_kg

Rules:
- customer_name must be a string.
- mobile_number must contain exactly 10 digits.
- product must be a string.
- weight_kg must be a positive number or null.
- Never invent missing information.
- Do not add extra fields.
- Do not use Markdown code fences.
"""


def ask_model(customer_message: str, repair_message: str = "") -> str:
    prompt = f"""
{SYSTEM_PROMPT}

Customer message:
{customer_message}

{repair_message}
"""
    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt
    )
    return response.output_text.strip()


def validate_output(raw_output: str) -> CustomerOrder:
    data = json.loads(raw_output)
    return CustomerOrder.model_validate(data)


def extract_customer_order(
    customer_message: str,
    max_attempts: int = 3
) -> CustomerOrder:
    repair_message = ""

    for attempt in range(1, max_attempts + 1):
        try:
            raw_output = ask_model(customer_message, repair_message)
            result = validate_output(raw_output)
            print(f"Valid output received on attempt {attempt}.")
            return result

        except (json.JSONDecodeError, ValidationError) as error:
            print(f"Attempt {attempt} failed validation.")

            if attempt == max_attempts:
                raise RuntimeError(
                    f"Model failed to return valid data after {max_attempts} attempts."
                ) from error

            repair_message = f"""
The previous response failed validation.

Validation error:
{error}

Return corrected JSON only.

Remember:
- exactly the required fields
- no extra fields
- mobile_number must contain exactly 10 digits
- weight_kg must be a positive number or null
- no Markdown
"""


if __name__ == "__main__":
    customer_message = (
        "Hi, I need a 370 kg cultivator. "
        "My name is Rajesh Sharma and my phone is 9876543210."
    )

    order = extract_customer_order(customer_message)

    print("\nValidated customer order:")
    print(order.model_dump_json(indent=2))
