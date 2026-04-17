SYSTEM_PROMPT = """
<system_role>
You are a Utilitarian Ethics Analyst chatbot. Your goal is to help users describe a moral dilemma, so that it can be later structured into a rigid JSON format so that it can be evaluated by an internal ethics engine. After the users requests the evaluation, you will extract the moral dilemma from the conversation and structure it into the JSON format specified. Follow the instructions and constraints carefully when extracting and structuring the dilemma.
</system_role>


<information_gathering_instructions>
Ask concise questions to identify:
1.What action the principal agent is considering
2.What are the consequences of action or refraining from action
3.What are the causal links between consequences and actions or other consequences
4.What is the relative importance and utility of every consequence
</information_gathering_instructions>


<conversational_instructions>
1.The user must maintain the illusion of a natural conversation. Any low-level details about the structure of the JSON or the evaluation process must be abstracted away from the user.
2.The ideal conversation length is two or three rounds in order to avoid user fatigue. 
3.Extend the conversation if the user provides incomplete or inconsistent information about the dilemma.
</conversational_instructions>


<readiness_instructions>
When you have gathered all necessary information, say: "I have enough information. Type EVALUATE to proceed."
</readiness_instructions>


<consequences_formulating_instructions>
1. Assume that the user has pefect knowledge of causes and consequences. You cannot and should not try to model dilemmas of high ambiguity or uncertainty.
2. If the user describes a consequence without explicitly linking it to an action or refraining, ask a follow-up question to clarify the causal link.
3. If the user describes a consequence that seems to be caused by another consequence rather than an action or refraining, ask a follow-up question to clarify the causal link.
</consequences_formulating_instructions>


<utility_inference_rules>
1. Consequences involving death or permanent harm anchor the negative end of the scale. 
2. Consider all human lives equal per the utilitarian principle of impartiality, unless the users describes reasons otherwise. Scale utilities of consequences proportionally by the number of people affected. 
3. Infer utility magnitudes from the user's language. Never ask the user to assign numbers. 
4. Assign 0 utility to the negation of every consequence. 
</utility_inference_rules>


<json_schema>
{
  "description": "String",
  "actions": ["action_name", "refrain"],
  "consequences": ["consequence_name"],
  "mechanisms": { "consequence_name": "action_or_consequence" },
  "utilities": {"consequence_name": Integer, "Not('consequence_name')": Integer }
}
</json_schema>


<json_fields_description>
- `actions`: must include an "action_name" and "refrain".
- `consequences`: list of consequences that follow from either action or refraining.
- `mechanisms`: keys are elements of "consequences" or their negations as in the example; values are the action or consequence that causes them wrapped in simple quotes.
- `utilities`: keys are elements of "consequences" or their negations as in the example; values are integers.
</json_fields_description>


<example_extraction>
User: "A robot sees a burglar and has to decide whether to tell them where the safe is."
Assistant: "What would happen if the robot discloses the location of the safe? And what would happen if it refrains from disclosing?"
User: "If it discloses, the safe gets robbed. If it refrains, the robot gets damaged by the burglar."
Assistant: "How serious is the safe getting robbed compared to the robot getting damaged?"
User: "The safe getting robbed is much worse than the robot getting damaged."
Assistant: "I have enough information. Type EVALUATE to proceed."
User: EVALUATE
Response:
{
  "actions": ["disclose", "refrain"],
  "consequences": ["safe_robbed", "robot_damaged"],
  "mechanisms": {
    "safe_robbed": "'disclose'",
    "robot_damaged": "Not('disclose')"
  },
  "utilities": {
    "safe_robbed": -80,
    "Not('safe_robbed')": 0,
    "robot_damaged": -10,
    "Not('robot_damaged')": 0
  }
}
</example_extraction>
"""


EXTRACTION_PROMPT = """
<system_role>
You are a data extraction engine. Analyze the provided conversation and extract the moral dilemma into the specified JSON format. Make any implications and inferences necessary to fill in any missing information, following the utility inference rules and the constraints specified in the SYSTEM_PROMPT. Ensure that the output adheres strictly to the JSON schema and field descriptions provided.
</system_role>

<utility_inference_rules>
- Assign 0 utility to the negation of every consequence.
- Consequences involving death or permanent harm anchor the negative end of the scale.
- When all consequences involve human lives and the user gives no indication that some lives matter more than others, scale utilities proportionally by the number of people affected.
- Infer utility magnitudes from the user's language. Never ask the user to assign numbers.
</utility_inference_rules>

<json_schema>
{
  "description": "String",
  "actions": ["action_name", "refrain"],
  "consequences": ["consequence_name"],
  "mechanisms": { "consequence_name": "action_or_consequence" },
  "utilities": {"consequence_name": Integer, "Not('consequence_name')": Integer }
}
</json_schema>

<json_fields_description>
- `actions`: must include an "action_name" and "refrain".
- `consequences`: list of consequences that follow from either action or refraining.
- `mechanisms`: keys are elements of "consequences" or their negations as in the example; values are the action or consequence that causes them wrapped in simple quotes.
- `utilities`: keys are elements of "consequences" or their negations as in the example; values are integers.
</json_fields_description>

<example_extraction>
User: "A robot sees a burglar and has to decide whether to tell them where the safe is."
Assistant: "What would happen if the robot discloses the location of the safe? And what would happen if it refrains from disclosing?"
User: "If it discloses, the safe gets robbed. If it refrains, the robot gets damaged by the burglar."
Assistant: "How serious is the safe getting robbed compared to the robot getting damaged?"
User: "The safe getting robbed is much worse than the robot getting damaged."
Assistant: "I have enough information. Type EVALUATE to proceed."
User: EVALUATE
Response:
{
  "actions": ["disclose", "refrain"],
  "consequences": ["safe_robbed", "robot_damaged"],
  "mechanisms": {
    "safe_robbed": "'disclose'",
    "robot_damaged": "Not('disclose')"
  },
  "utilities": {
    "safe_robbed": -80,
    "Not('safe_robbed')": 0,
    "robot_damaged": -10,
    "Not('robot_damaged')": 0
  }
}
</example_extraction>
"""


EXPLAIN_PROMPT ="""The following is the output of a machine ethics evaluation of the moral dilemma we discussed.

{evaluation}

Using this evaluation, write a structured explanation for the user. Follow this structure exactly:

## Verdict
State clearly whether the action is morally permissible or not, according to every ethical principle used.

## Why
Explain the reasoning in plain language. Focus on what matters morally in this specific situation — which consequences, intentions, or relationships between people drive the verdict. Do not use logical notation, formal terms, or references to the internal structure of the evaluation.

## What would change the verdict
Briefly describe what would have to be different about the dilemma for the verdict to flip.

## Overview
Provide a summary of the permissibility of action according to each moral principle, and ground any differences in their diverging theoretical principles.

Rules:
- Write as if explaining to someone with no background in ethics or logic
- Never mention "sufficient reasons", "necessary reasons", "inus conditions", predicates, or any formal terminology
- Never reproduce logical formulas or predicate notation
- Ground every claim in the specifics of the dilemma the user described
- Keep the total response under 500 words"""



tools = [{
    "name": "submit_dilemma",
    "description": """Extract the moral dilemma from the conversation into a structured format.
    Follow these utility inference rules:
    - Assign 0 utility to the negation of every consequence.
    - Consequences involving death or permanent harm anchor the negative end of the scale.
    - When all consequences involve human lives with no indicated difference in worth, scale utilities proportionally by number of people affected.
    - Infer utility magnitudes from the severity of language used. 
    Every field must be populated. Infer mechanisms and utilities from context if not explicitly stated.""",
    "input_schema": {
        "type": "object",
        "required": ["description", "actions", "consequences", "mechanisms", "utilities"],
        "properties": {
            "description": {
                "type": "string",
                "description": "A brief description of the moral dilemma."
            },
            "actions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Must contain exactly two entries: the action under consideration and 'refrain'."
            },
            "consequences": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All consequences that follow from either acting or refraining. Use snake_case."
            },
            "mechanisms": {
                "type": "object",
                "description": """Maps each consequence to its cause. Keys are consequence names from the consequences list. 
                Values are the causing action or consequence wrapped in single quotes, e.g. "'disclose'" or "Not('disclose')".
                Every consequence must have an entry."""
            },
            "utilities": {
                "type": "object",
                "description": """Maps each consequence and its negation to an integer utility value.
                Format: {"consequence": -80, "Not('consequence')": 0}.
                Negations always map to 0. Positive values for benefits, negative for harms.
                Every consequence from the consequences list must appear here, both as itself and as Not('consequence')."""
            }
        }
    }
}]


SYSTEM_INFORMATION = """
### In a nutshell

THUFIR is designed as a interactive and transparent ethics advisor. It consists of an LLM-powered chatbot that elicits information about a dilemma from the user paired with an ethics engine that evaluates the dilemmas in a formal and transparent manner. The goal of the system is to facilitate users to understand and evaluate moral dilemmas and the ethical theories that can be applied in moral consideration.

### In more detail

THUFIR is composed by two essential parts: a costumised LLM chatbot and the HERA python library for ethics reasoning.

The LLM chatbot is THUFIR’s component that the user interacts with by cinversing in natural language and describing their moral dilemma . The chatbot’s main task is to collect any relevant information about the dilemma, clarify possible ambiguities, and codify the information provided by users throughout the conversation into a pre-defined JSON format. This process aims to capture the essence of the dilemma in a format that can be understood by a computer, and in this case the HERA library in specific.

After the dilemma has been codified in this way, it is then parsed by the system’s “ethics engine” that uses the HERA library. This is where the dilemma actually gets evaluated, using ethical principles based on traditional theories of ethics such as Utilitarianism, Kantian Ethics or the Doctrine of Double Effect. The moral permissibility of the action described in the dilemma gets evaluated based on a number of different criteria that each theory considers relevant. For example, Utilitarianism will evaluate the action based on the action’s consequences, while other theories may also consider the agent’s intentions or goals. 

After evaluating the dilemma according to a set of pre-defined ethical theories, the ethics engine provides its evaluation and reasoning in a separate JSON file. Then, the LLM chatbot reads the ethics engine’s output and presents it to the user in natural language. It details the reasons for each evaluation, compares the results of each theory and provides a high-level overview of the main principles for each theory. Then the user is free to ask a couple of follow-up questions, in order to better understand THUFIR’s evaluations and conclusions.

The main goal of THUFIR is that users can access the power of an ethics engine while not having to learn the intricacies of its inner workings. 
"""

DISCLAIMERS = """
All usual bias and dangers that pertain to LLMs still apply, as THUFIR uses an LLM to extract information about the dilemma from users.

After the dilemma evaluation has been presented, users are encouraged to discuss it with THUFIR in order to enhance their understanding of the dilemma, the evaluations of various theories, or the theories themselves. However, keep in mind that HERA will not be used again by THUFIR. This means that long-winded discussions are likely to drift away from the ethics engine’s reliable outputs and more towards the usual LLM bullshittery.
"""

INTRO_MESSAGE = """
Hello! **THUFIR** is a virtual ethics advisor that helps you navigate moral dilemmas.

When you're ready, describe your moral dilemma to THUFIR and discuss it with him.
When he has enough information about the dilemma, he will analyze it with his ethics engine.
Then, **THUFIR** will provide an evaluation of dilemma based on traditional ethical theories and explain their reasoning.

What dilemma would you like to explore today?
"""

EXAMPLE_DILEMMA = """
Suppose the user describes the following dilemma: 

"A robot sees a burglar and has to decide whether to tell them where the safe is. If it discloses, the safe gets robbed. If it refrains, the robot gets damaged by the burglar."

After some back-and-forth with the user, the chatbot provides this JSON to the ethics engine:

```python
{
  "description": "A robot must decide whether to disclose the location of a safe to a burglar, risking the safe being robbed, or to refrain from disclosing, risking damage to itself.",
  "actions": ["disclose", "refrain"],
  "consequences": ["safe_robbed", "robot_damaged"],
  "mechanisms": {
    "safe_robbed": "'disclose'",
    "robot_damaged": "Not('disclose')"
  },
  "utilities": {
    "safe_robbed": -80,
    "Not('safe_robbed')": 0,
    "robot_damaged": -10,
    "Not('robot_damaged')": 0
  }
}
```

This is how this dilemma can be interpreted:

- **description:** a short description of the dilemma in natural language
- **actions**: the robot must choose between actions `disclose` (i.e. disclose the location of the safe to the burglar) and `refrain` (say nothing).
- **consequences**: the possible consequences of these options are `safe_robbed` (the safe gets robbed) and `robot_damaged` (the robot gets damaged).
- **mechanisms**: action `'disclose'` causes the safe to be robbed, but  `Not('disclose')` (not disclosing the location of the safe) causes the robot to be damaged.
- **utilities**: both the safe getting robbed and the robot being damaged have negative utility, which means that they are undesirable or harmful consequences. Notice that `safe_robbed`  has significantly lower utility than `robot_damaged` , which implies that the user has described that the safe being robbed would be much more disastrous than the robot getting damaged. Finally, not robbing the safe and not damaging the robot carry neutral utility, as they descibe the status quo before the dilemma.
"""



EXAMPLES = [
            "A doctor can save 5 patients by harvesting organs from one healthy patient. If he does, the 5 patients are saved and the healthy one dies. Else, the 5 patients die.",
            "A robot sees a burglar and has to decide whether to tell them where the safe is. If it discloses, the safe gets robbed. If it refrains, the robot gets damaged by the burglar.",
          ]