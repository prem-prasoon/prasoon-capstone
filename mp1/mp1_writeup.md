# Mini Project 1: Prompt Strategy Evaluation & Reflection

## 1. Which strategy won, and on what dimension?
**Winner: Structured Prompting.**

Structured Prompting delivered the most balanced and reliable results across the 40 test runs. It achieved a perfect 3.00 / 3 accuracy across all snippets, maintained a 100% JSON parse rate, and received the highest average score of 3.90 / 4 from the gpt-4o judge. It remained fast (p50 latency ~1.86s) with a low total cost of $0.000436.

Few-Shot performed reasonably well (2.90 / 3 accuracy, 3.70 / 4 judge score), but passing worked examples in every prompt increased input token overhead ($0.000403). Chain-of-Thought (CoT) matched Structured on field accuracy (3.00 / 3) and earned a 3.80 / 4 judge score, but generating intermediate reasoning tokens increased median latency to 2.24s and pushed costs to $0.000652 (roughly 50% higher than Structured). For extracting three basic fields, that extra reasoning overhead adds delay and token spend without providing an accuracy advantage over a well-defined schema. Zero-Shot was the cheapest ($0.000340), but scored lowest on the judge rubric (3.50 / 4) due to less consistent output formatting.

## 2. Key Observations & Failure Patterns (Snippets j09 and j10)
Two specific snippets highlighted the differences between the prompting strategies:

- **Snippet j10 (Cyberdyne Systems — AI/ML Research Scientist):** The snippet states: *"We don't list a specific years requirement — we hire on demonstrated impact."* The correct extraction is `null`. Without clear schema instructions, basic prompts tend to latch onto other details (like "PhD preferred") and fabricate a number. Both Structured and CoT handled this cleanly, outputting `"years_experience_required": null` and earning 4/4 from the judge.
- **Snippet j09 (Stark Industries — Cybersecurity Analyst):** The requirement is stated as a range (*"Three to five years"*). The golden set convention takes the minimum (3). In the Few-Shot run (row 18), the model extracted this inconsistently, dropping its field accuracy to 2 / 3 and judge score to 3 / 4. Structured prompting, by contrast, resolved the integer cleanly across all 10 snippets.

## 3. What I Will Use for My Capstone
For my capstone backend ingestion pipeline, I will use **Structured Prompting**.

In an API pipeline, having predictable JSON responses that deserialize cleanly into Pydantic schemas without unexpected keys or data type mismatches is critical. Structured prompting provides that consistency while keeping latency low and token costs predictable. If domain ambiguity increases as the capstone corpus expands, targeted few-shot exemplars can be injected dynamically into the schema prompt.

## 4. Next Steps If I Had More Time
1. **Adopt Native Structured Outputs:** Instead of parsing JSON out of markdown text, migrate to OpenAI's native `response_format={"type": "json_schema"}` to guarantee schema conformance at the API gateway layer.
2. **Benchmark on Smaller Open-Source Models:** Run this exact 4-strategy evaluation harness against a local model like `llama3.2:3b` via Ollama to assess whether smaller models struggle with schema adherence without few-shot examples.
3. **Evaluate on Real Policy Documents:** Test the prompts against complex enterprise documents that contain nested conditionals, multi-tier requirements, and exceptions to measure how well each strategy isolates primary criteria.