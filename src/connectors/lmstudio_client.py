from openai import OpenAI

# timeout=90 -- without this, a hung/frozen LM Studio server blocks the
# request indefinitely with no way to interrupt cleanly (Ctrl+C doesn't
# reach a blocked socket read on Windows). 90s is generous for a single
# completion at max_tokens=400 on a 9B model; anything longer than that
# means the server is actually stuck, not just slow, and should fail loud
# so the caller's retry/error-handling logic can take over instead of
# hanging the whole sweep.
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed", timeout=90.0)


def call_model(prompt: str, model: str = "qwen/qwen3.5-9b", temperature: float = 0.7, max_tokens: int = 400, max_retries: int = 2):
    # max_tokens bumped 300 -> 400 as a safety margin. Confirmed via LM
    # Studio's dev console that enable_thinking=False (extra_body) is not
    # reliably honored for this model/quant: a real call spent 299/300
    # tokens on reasoning_content with content="" and finish_reason="length"
    # -- it was still reasoning when the budget ran out, never reached the
    # answer. /no_think is Qwen's own inline chat-template directive,
    # applied at template-render time rather than via API plumbing, so it's
    # appended to every prompt as the primary suppression mechanism. The
    # extra_body flag is kept alongside it as a second signal -- harmless
    # either way.
    last_finish_reason = None
    last_reasoning_tokens = None
    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"{prompt}\n/no_think"}],
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        choice = response.choices[0]
        content = choice.message.content
        last_finish_reason = choice.finish_reason

        usage = response.usage
        if usage and getattr(usage, "completion_tokens_details", None):
            last_reasoning_tokens = getattr(usage.completion_tokens_details, "reasoning_tokens", None)

        if content and content.strip():
            return content

        print(f"  [lmstudio] empty completion (finish_reason={last_finish_reason}, "
              f"reasoning_tokens={last_reasoning_tokens}/{max_tokens}), attempt {attempt+1}/{max_retries}")

    raise RuntimeError(
        f"LM Studio returned an empty completion after {max_retries} attempts "
        f"(last finish_reason={last_finish_reason}, reasoning_tokens={last_reasoning_tokens}/{max_tokens}). "
        f"If reasoning_tokens is near max_tokens, thinking suppression (/no_think + enable_thinking=False) "
        f"is still not taking effect -- check LM Studio's console for this timeframe."
    )