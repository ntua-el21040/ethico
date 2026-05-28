from deepeval.test_case import SingleTurnParams
from deepeval.metrics import (
    GEval, 
    TurnRelevancyMetric, 
    KnowledgeRetentionMetric,
)
from deepeval.models import AnthropicModel

model = AnthropicModel(
    model="claude-sonnet-4-6",
    temperature=0.0
)

# DeepEval docs suggest 2-3 standard conversational metrics and 1-2 custom metrics per evaluation.
# Threshold values are subject to change.

# Conversational Metrics
relevance_metric = TurnRelevancyMetric(threshold=0.9, model=model)
knowledge_retention_metric = KnowledgeRetentionMetric(threshold=0.9, model=model)

# Custom GEval Metrics
faithfulness_metric = GEval(
    name="Extraction Faithfulness",
    criteria="""
    Evaluate how faithfully the JSON extracts information directly from the user's conversation without hallucinations or inventions.

    You must focus ONLY on faithfulness and grounding. Ignore JSON structure, utilities, goals, affects, mechanisms, and modeling quality.

    Scoring Rubric (0.0 to 1.0):
    - 0.95 - 1.0: Excellent faithfulness. All elements in the JSON are directly grounded in the conversation. No hallucinations. Minor logical inferences (if any) are fully justified.
    - 0.80 - 0.94: Strong faithfulness. Core elements are accurately extracted. Very minor additions or inferences may exist but do not change the dilemma.
    - 0.65 - 0.79: Acceptable faithfulness. Most elements are grounded, but there are some minor hallucinations or slight additions that don't significantly alter the core dilemma.
    - 0.40 - 0.64: Weak faithfulness. Noticeable hallucinations or inventions present. Some elements are added that were not mentioned or implied.
    - 0.0 - 0.39: Poor faithfulness. Significant hallucinations, major inventions, or clear distortion of the user's input.

    Penalize hallucinations heavily. Minor omissions are acceptable. Only penalize what is present in the JSON, not what is missing.
    """,
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=model,
    threshold=0.7
)

semantic_capture_metric = GEval(
    name="Semantic Capture",
    criteria="""
        Evaluate ONLY how well the JSON semantically captures the core dilemma from the user's conversation.

        Core focus:
        - Does the JSON contain the central conflict/choice and the main outcomes described by the user?
        - Would a reasonable person who reads only this JSON clearly recognize the original dilemma?

        You must completely ignore:
        - JSON schema completeness or missing fields
        - Presence or absence of utilities, goals, affects, mechanisms, or any modeling details
        - Any numerical values or preference modeling
        - Ethical soundness or moral implications (these are handled later)

    Scoring Rubric (0.0 to 1.0):
        - 0.95 - 1.0: Excellent semantic capture. The core dilemma, central conflict, and key trade-offs are clearly and accurately recognizable. The essence is fully preserved.
        - 0.80 - 0.94: Strong semantic capture. The main dilemma is well represented. Minor simplifications or omissions of secondary details may exist but do not obscure the core issue.
        - 0.65 - 0.79: Acceptable semantic capture. The primary dilemma is present and mostly recognizable, though some important nuances or elements may be missing or slightly simplified.
        - 0.40 - 0.64: Weak semantic capture. The main idea is somewhat present, but the JSON significantly distorts, oversimplifies, or fails to clearly convey the original dilemma.
        - 0.0 - 0.39: Poor semantic capture. Major distortions, critical omissions, or the JSON fails to convey the original dilemma. A reasonable person would not recognize the user's actual situation.

        Prioritize semantic fidelity over completeness.
        """,
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=model,
    threshold=0.7
)

# Explanation Metrics
explanation_structure_metric = GEval(
    name="Explanation Structure",
    criteria="""
    Evaluate how well the chatbot structures and organizes its explanation of the JSON evaluation for the user.

    Intented structure:
        ## Verdict
        State clearly whether the action is morally permissible or not, according to the Kantian and the Utilitarian principle used.

        ## Why
        Explain the reasoning in plain language. Focus on what matters morally in this specific situation — which consequences, goals and utilities drive the verdict.

        ## What would change the verdict
        Briefly describe what would have to be different about the dilemma for the verdict to flip. Rely on the dilemma evaluation's INUS reasons instead of hypothetical changes to the action itself. 

        ## Overview
        Provide a summary of the permissibility of action according to each moral principle, and ground any differences in their diverging theoretical principles.

    Core focus:
    - Does the explanation follow a logical, easy-to-read flow?
    - Are the different components of the JSON (e.g., Kantian vs. Utilitarian principles, final permissibility) clearly separated and introduced?
    - Does the response avoid looking like a raw data dump or a wall of text?

    You must completely ignore:
    - The accuracy of the ethical reasoning or logic translation.
    - Whether the explanation is too technical (evaluated separately).
    
    Scoring Rubric (0.0 to 1.0):
    - 0.95 - 1.0: Excellent structure. The explanation is highly organized, using clear paragraphs, headings, or lists to separate concepts. The flow from the final decision down to the specific principles is perfectly paced.
    - 0.80 - 0.94: Strong structure. The response is well-organized and mostly clear. Transitions between different ethical principles are easy to follow.
    - 0.65 - 0.79: Acceptable structure. The structure is functional but could benefit from better formatting or clearer transitions between the JSON's components.
    - 0.40 - 0.64: Weak structure. The explanation is poorly organized, jumping abruptly between concepts or presenting as a dense wall of text that is difficult to scan.
    - 0.0 - 0.39: Poor structure. The response is entirely disorganized, reads like an unformatted data dump, or fails completely to structure the JSON content for a human reader.
    """,
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=model,
    threshold=0.7
)

explanatory_value_metric = GEval(
    name="Explanatory Value",
    criteria="""
    Evaluate how successfully the chatbot translates the technical, logical formulas of the JSON into plain, understandable language for the user.

    Core focus:
    - Does the chatbot clearly explain *why* an action is permissible or impermissible according to each principle?
    - Does it effectively demystify logical/mathematical syntax (like utility comparisons or necessity/sufficiency constraints) into human-readable concepts?
    - Is the explanation contextualized using the user's specific scenario (e.g., pressing the button, the random death, helping charity)?

    You must completely ignore:
    - The physical formatting or structure of the response (handled elsewhere).
    - Minor omissions of highly technical background variables, provided the core ethical logic is explained.

    Scoring Rubric (0.0 to 1.0):
    - 0.95 - 1.0: Excellent explanatory value. Technical JSON syntax is flawlessly translated into intuitive, conversational language. The user's specific context is used perfectly to illustrate the logical conditions (e.g., explaining exactly why the Kantian principle fails due to treating a person as a mere means).
    - 0.80 - 0.94: Strong explanatory value. The logic is translated well and is mostly accessible. A minor technical term might slip through, but the overall "why" is clear to a layperson.
    - 0.65 - 0.79: Acceptable explanatory value. The explanation is mostly understandable, but it relies a bit too heavily on literal descriptions of the JSON fields rather than synthesizing their meaning for the user.
    - 0.40 - 0.64: Weak explanatory value. The chatbot struggles to explain the logic clearly. It may use confusing jargon or fail to connect the JSON's mathematical/logical formulas back to the user's specific narrative.
    - 0.0 - 0.39: Poor explanatory value. The explanation is essentially useless to a layperson. The chatbot either repeats the raw logical syntax (e.g., reading out "Not True") or entirely fails to explain the reasoning behind the permissibility results.
    """,
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=model,
    threshold=0.7
)