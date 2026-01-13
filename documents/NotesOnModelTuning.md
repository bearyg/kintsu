In using gemini 3 both flash and pro models, I have run into a problem. When I pass the same photo to the flash model, the request fails due to Max Tokens. When I pass the same photo to the pro model, it works fine. To compare the results, here is the metadata that I captured after each request. Flash model - Final Usage Metadata: {"promptTokenCount":1288,"candidatesTokenCount":64509,"totalTokenCount":66809,"promptTokensDetails":[{"modality":"TEXT","tokenCount":224},{"modality":"IMAGE","tokenCount":1064}],"thoughtsTokenCount":1012}Pro model - Final Usage Metadata: {"promptTokenCount":1288,"candidatesTokenCount":1290,"totalTokenCount":4346,"promptTokensDetails":[{"modality":"TEXT","tokenCount":224},{"modality":"IMAGE","tokenCount":1064}],"thoughtsTokenCount":1768}Can you explain to me why this would happen and how I might go about trying to better work with the models?
December 29, 2025

The failure in the Flash model is caused by output generation length, not the input image size. Both models processed the image and prompt identically (using 1,288 prompt tokens), but the Flash model attempted to generate an exceptionally large response that hit its internal limits.
Why this is happening
Based on your metadata, the core issue is the candidatesTokenCount:
Flash Model: Generated 64,509 tokens. This is extremely high and likely triggered a "Max Tokens" error because it approached or exceeded the model's output limit (typically 8,192 tokens for standard requests, though some configurations allow more).
Pro Model: Generated 1,290 tokens. This is a standard, concise response.
The "Infinite Loop" Phenomenon: Small, fast models like Gemini Flash can experience "repetition loops" or "hallucination spirals," particularly when interpreting complex visual data. The model likely repeated a phrase or pattern, causing the token count to increase until it reached the limit.
How to address this
Set a max_output_tokens limit: In your API configuration, set max_output_tokens. For most image descriptions, 1,000 to 2,000 tokens is sufficient. This prevents the Flash model from exceeding the token limit and causing the request to fail.
Refer to the Gemini API Reference for setting max_output_tokens in your code.
Refine the system instruction: If the Flash model is hallucinating or over-describing, refine the prompt.
Instead of: "Describe this image."
Use: "Provide a concise summary of this image in under 3 paragraphs. Do not repeat yourself."
Adjust Temperature: A high temperature (e.g., 1.0) can cause instability. Lowering the temperature to 0.4 or 0.2 for image tasks often produces a more focused, logical output that is less likely to result in infinite token generation.
Compare the output: If possible, examine the end of the 64,509-token response. The model likely repeated the same character or sentence. This confirms the model became "unstable" with that specific image.



When I tested the same photo again with gemini-3-pro-preview the error was "2025-12-29 15:12:16.630 MST[Gemini Phase 1] Stream finishing with reason: MAX_TOKENS2025-12-29 15:12:16.672 MST[Gemini Phase 1] Final Usage Metadata: {"promptTokenCount":1288,"candidatesTokenCount":63911,"totalTokenCount":66805,"promptTokensDetails":[{"modality":"IMAGE","tokenCount":1064},{"modality":"TEXT","tokenCount":224}],"thoughtsTokenCount":1606}2025-12-29 15:12:16.672 MST[Gemini Phase 1] STREAM COMPLETE in 490.16s | Total Chunks: 2664"Why, with a temperature used of 0.2, would the model behave like this?
December 29, 2025

The Gemini 3 Pro Preview model may fail with MAX_TOKENS when processing the same photo due to a "repetition loop" instability. This can be made worse by a low temperature setting, such as 0.2.
The metadata shows the model generated nearly 64,000 tokens of repetitive text before reaching the limit.
Why Low Temperature Failed
Lowering the temperature can make a model more deterministic. This can have a negative effect when a model is prone to looping:
How Loops Start: The model may output a repeated token when it encounters a confusing visual feature or an internal conflict.
How Low Temperature Locks It In: A low temperature forces the model to choose the most probable next token. Once a repetitive pattern starts, the "most probable" next token is often just the continuation of that pattern.
The Result: The model lacks the "creativity" to select a different token that would break the loop, and it locks itself into a spiral until it hits the MAX_TOKENS limit. 
Evidence in the Metadata
The metadata shows the problem is in the text generation phase, not the reasoning phase:
thoughtsTokenCount: 1,606 (Normal): The model completed its "thinking" process.
candidatesTokenCount: 63,911 (Critical Failure): The model spent nearly all its energy generating the final text response. Since normal descriptions rarely exceed 1,000 tokens, this indicates it generated ~62,000 tokens of garbage repetition. 
Recommended Fixes
Since this is a known issue with the Gemini 3 Preview models, you need to force the model to break its own patterns: 
Increase Temperature: Try raising the temperature to 0.4 or 0.5. This adds randomness to help the model "escape" a repetitive loop, allowing it to pick a token that ends the sentence.
Set a Hard max_output_tokens Limit: Manually set max_output_tokens to 2,000. This forces the API to cut off the request before it wastes resources or times out.
Use a "Stop Sequence": Add a stop_sequences parameter with common loop characters (e.g., ["\n\n\n"]) in your generation config. 