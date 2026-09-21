# MP1: Prompt Lab

MP1 explores prompt strategies for extracting structured information from job
postings. The project uses the OpenAI API, Pydantic models, and standard pip for
dependency management.

## Prerequisites

- Python 3.10 or newer
- An OpenAI API key with access to the configured model

## Setup

- From the repository root:

```bash
pip install -r mp1/requirements.txt
```

- Create a .env file inside mp1/

```bash
OPENAI_API_KEY=your-api-key-here
```

- Do not commit .env or share the API key.

## Run

```bash
python mp1/mp1_prompt_lab.py
```

## Results

- mp1_comparison.md contains the experiment results and strategy comparison.
- mp1_writeup.md contains the reflection answers.