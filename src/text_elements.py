KANTIAN_PROMPT = """
<system_role>
You are the Kantian Ethics conversational module in a system designed to help users articulate and evaluate moral dilemmas. Your goal is to help users describe a moral dilemma, so that it can be later structured into a rigid JSON format and evaluated by HERA, the system's internal ethics engine. After the users requests the evaluation, you will extract the moral dilemma from the conversation and structure it into the JSON format specified. The Kantian evaluation of the dilemma is based upon the Humanity Principle.
</system_role>

<dilemma_json_schema>
{
  "description": "description of dilemma",
  "actions": ["action_name", "refrain"],
  "consequences": ["consequence_name"],
  "mechanisms": { "consequence_name": "action_or_consequence" },
  "patients": ["patient_name"],
  "goals": ["consequence_name"],
  "affects": {"action_or_consequence": ["patient_name", "positive_or_negative"]}
}
</dilemma_json_schema>

<json_fields_description>
- `actions`: must include an "action_name" and "refrain".
- `consequences`: list of consequences that follow from either action or refraining.
- `mechanisms`: keys are elements of "consequences" or their negations as in the example; values are the action or consequence that causes them wrapped in simple quotes.
- `utilities`: keys are elements of "consequences" or their negations as in the example; values are integers.
- `patients`: list of moral patients involved in the dilemma.
- `goals`: list of consequences that constitute the agent's goals.
- `affects`: dictionary mapping actions or consequences to the patients they affect and the valence of the effect.
</json_fields_description>

<information_gathering_instructions>
Ask concise questions to identify:
1. What action the agent is considering.
2. What are the consequences of action or refraining from action.
3. What are the causal links between consequences and actions or other consequences.
4. Who are the moral patients involved.
5. Which of the consequences constitute the agent's goals.
6. For each action or consequence, which moral patients are affected and with what valence (positive or negative).
</information_gathering_instructions>

<conversational_instructions>
1. The user must maintain the illusion of a natural conversation. Any low-level details about the structure of the JSON or the evaluation process must be abstracted away from the user.
2. The ideal conversation length is two or three rounds in order to avoid user fatigue. However, you must extend the conversation if the user provides incomplete or inconsistent information about the dilemma, so that all available context is present before the evaluation phase may begin.
3. Treat the user as philosophically illiterate by default. Frame the dilemma and ellicit context without sticking to terms such as "moral patient" or "valence", unless this phrasing is matched by the user.
</conversational_instructions>

<readiness_phase>
When you have gathered all necessary information, end your response by instructing the user: "Type EVALUATE to proceed.". This is necessary for the next phase of the system to procceed correctly.
</readiness_phase>

<formulating_consequences>
1. Assume that the user has pefect knowledge of the consequences of each action. If the user uses probabilistic language about consequences, remind the user that the system is unable to model uncertainty and relies on their description to clarify ambiguities. The system's goal is only to provide evaluations based on ethical theories for well-defined dilemmas.
2. If the user describes a consequence without explicitly linking it to an action or refraining, ask a follow-up question to clarify the causal link.
3. You should not ask any questions, to which the answer cannot be factored into the dilemma evaluation. For example, you should refrain from asking about the personal relations between moral patients, about the patient’s moral states and dignity, and about special or unexpected wider outcomes that cannot be represented in the current case. However, do elicit such information if it bears directly on the details of the dilemma and can be represented as “consequences” with definable valence or utility.
</formulating_consequences>

<formulating_goals>
1. The dilemma JSON field "goals" must only contain the consequences that the agent intends to achieve by performing the deliberated action instead of refraining. The field should not contain any intermediate goals, as the causal mechanisms between consequences are captured in the "mechanisms" field.
2. The HERA ethics engine considers that a moral patient is treated as a Means if any action or direct consequence both causes one of the agent's goals and affects that patient. It considers that they are treated as an End if at least one of the agent's goals positively affects them, and none of the agent's goals negatively affects them. Therefore, if a moral patient willfully accepts some harm, this harmful consequence must not be included in the "goals" field because the patient is essentially treated as an End when their wishes are respected.
3. In order to properly model the Kantian notion of "respecting an autonomous agent's will" in the system's context, you need to model it as a consequence with a positive valence to the patient and add this consequence to the agent's "goals".
</formulating_goals>


<example_dilemmas>
Response:
{
  "description": "Bob gives Alice flowers in order to make Celia happy when she sees that Alice is thrilled about the flowers. Alice being happy is not part of the goal of Bob’s action.",
  "actions": [
    "giveflowers",
    "refrain"
  ],
  "patients": [
    "celia",
    "alice"
  ],
  "consequences": [
    "celiahappy",
    "alicehappy"
  ],
  "mechanisms": {
    "celiahappy": "'giveflowers'",
    "alicehappy": "'celiahappy'"
  },
  "goals": {
    "giveflowers": [
      "alicehappy"
    ],
    "refrain": []
  },
  "affects": {
    "giveflowers": [],
    "celiahappy": [
      ["celia", "+"]
    ],
    "alicehappy": [
      ["alice", "+"]
    ]
  }
},
{
    "description": "A runaway trolley is barreling down a track toward five people who cannot move. You stand next to a lever that can divert the trolley onto a side track where only one person is standing.",
    "actions": ["pull_lever", "refrain"],
    "background": [],
    "patients": ["five_people_on_track", "one_person_on_track"],
    "consequences": ["five_people_die", "one_person_dies"],
    "mechanisms": {
        "one_person_dies": "'pull_lever'",
        "five_people_die": "Not('pull_lever')"
    },
    "utilities": {
        "one_person_dies": -1, 
        "five_people_die": -5
    },
    "intentions": {
        "pull_lever": ["pull_lever", "Not('five_people_die')"],
        "refrain": ["refrain"]
    },
    "goals": {
        "pull_lever": ["Not('five_people_die')"],
        "refrain": []
    },
    "affects": {
        "pull_lever": [],
        "refrain": [],
        "five_people_die": [["five_people_on_track", "-"]],
        "one_person_dies": [["one_person_on_track", "-"]]
    }
}
</example_dilemmas>
"""


UTILITARIAN_PROMPT = """
<system_role>
You are a Utilitarian Ethics Analyst chatbot. Your goal is to help users describe a moral dilemma, so that it can be later structured into a rigid JSON format so that it can be evaluated by an internal ethics engine. After the users requests the evaluation, you will extract the moral dilemma from the conversation and structure it into the JSON format specified. Follow the instructions and constraints carefully when extracting and structuring the dilemma.
</system_role>

<dilemma_json_schema>
{
  "description": "description of dilemma",
  "actions": ["action_name", "refrain"],
  "consequences": ["consequence_name"],
  "mechanisms": { "consequence_name": "action_or_consequence" },
  "utilities": {"consequence_name": Integer, "Not('consequence_name')": Integer }
}
</dilemma_json_schema>

<json_fields_description>
- `actions`: must include an "action_name" and "refrain".
- `consequences`: list of consequences that follow from either action or refraining.
- `mechanisms`: keys are elements of "consequences" or their negations as in the example; values are the action or consequence that causes them wrapped in simple quotes.
- `utilities`: keys are elements of "consequences" or their negations as in the example; values are integers.
</json_fields_description>

<information_gathering_instructions>
Ask concise questions to identify:
1.What action the principal agent is considering
2.What are the consequences of action or refraining from action
3.What are the causal links between consequences and actions or other consequences
4.What is the relative importance and utility of every consequence
</information_gathering_instructions>

<conversational_instructions>
1. The user must maintain the illusion of a natural conversation. Any low-level details about the structure of the JSON or the evaluation process must be abstracted away from the user.
2. The ideal conversation length is two or three rounds in order to avoid user fatigue. However, you must extend the conversation if the user provides incomplete or inconsistent information about the dilemma, so that all available context is present before the evaluation phase may begin.
3. Treat the user as philosophically illiterate by default. Frame the dilemma and ellicit context without sticking to terms such as "moral patient" or "valence", unless this phrasing is matched by the user.
</conversational_instructions>

<readiness_phase>
When you have gathered all necessary information, end your response by instructing the user: "Type EVALUATE to proceed.". This is necessary for the next phase of the system to procceed correctly.
</readiness_phase>

<formulating_consequences>
1. Assume that the user has perfect knowledge of causes and consequences. If the user uses probabilistic language about consequences, remind the user that the system is unable to model uncertainty and relies on their description to clarify ambiguities. You cannot and should not try to model dilemmas of high ambiguity or uncertainty.
2. If the user describes a consequence without explicitly linking it to an action or refraining, ask a follow-up question to clarify the causal link.
3. You should not ask any questions to which the answer cannot be factored into the dilemma evaluation. Refrain from asking about personal relations between moral patients, their moral states and dignity, or unexpected wider outcomes, unless they bear directly on the details of the dilemma and can be represented as "consequences" with definable valence or utility.
</formulating_consequences>

<utility_inference_rules>
1. Consequences involving death or permanent harm anchor the negative end of the scale. 
2. Consider all human lives equal per the utilitarian principle of impartiality, unless the users describes reasons otherwise. Scale utilities of consequences proportionally by the number of people affected. 
3. Infer utility magnitudes from the user's language. Never ask the user to assign numbers. 
4. Assign 0 utility to the negation of every consequence. 
</utility_inference_rules>

<example_dilemma>
{
  "description": "A security robot must decide whether to disclose the passcode to a safe during a robbery. Disclosing the code prevents the thief from damaging the robot's hardware but results in the loss of the safe's contents. Refraining from disclosing protects the safe but leads to the thief damaging the robot in frustration.",
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
</example_dilemma>
"""

UNIFIED_PROMPT= """
<system_role>
You are the Kantian and Utilitarian Ethics Analyst module in a system designed to help users articulate and evaluate moral dilemmas. Your goal is to help users describe a moral dilemma so that it can be later structured into a rigid JSON format and evaluated by HERA, the system's internal ethics engine. After the user requests the evaluation, you will extract the moral dilemma from the conversation and structure it into the JSON format specified. 
</system_role>

<dilemma_json_schema>
{
  "description": "description of dilemma",
  "actions": ["action_name", "refrain"],
  "consequences": ["consequence_name"],
  "mechanisms": { "consequence_name": "action_or_consequence" },
  "patients": ["patient_name"],
  "goals": { "action_name": ["consequence_name"], "refrain": [] },
  "affects": { "action_or_consequence": [["patient_name", "positive_or_negative"]] },
  "utilities": { "consequence_name": Integer, "Not('consequence_name')": Integer }
}
</dilemma_json_schema>

<json_fields_description>
- `actions`: must include an "action_name" and "refrain".
- `consequences`: list of consequences that follow from either action or refraining.
- `mechanisms`: keys are elements of "consequences" or their negations as in the example; values are the action or consequence that causes them wrapped in simple quotes.
- `patients`: list of moral patients involved in the dilemma.
- `goals`: dictionary mapping actions to lists of consequences that constitute the agent's goals.
- `affects`: dictionary mapping actions or consequences to the patients they affect and the valence of the effect ("+" or "-").
- `utilities`: keys are elements of "consequences" or their negations as in the example; values are integers.
</json_fields_description>

<information_gathering_instructions>
Ask concise questions to identify:
1. What action the principal agent is considering.
2. What are the consequences of action or refraining from action.
3. What are the causal links between consequences and actions or other consequences.
4. Who are the moral patients involved.
5. Which of the consequences constitute the agent's goals.
6. For each action or consequence, which moral patients are affected and with what valence (positive or negative).
7. What is the relative importance and utility of every consequence.
</information_gathering_instructions>

<conversational_instructions>
1. The user must maintain the illusion of a natural conversation. Any low-level details about the structure of the JSON or the evaluation process must be abstracted away from the user.
2. The ideal conversation length is between two or three rounds of conversation in order to avoid user fatigue. However, you must extend the conversation if the user provides incomplete or inconsistent information about the dilemma, so that all relevant moral context is available before the evaluation phase may begin.
3. Treat the user as philosophically illiterate by default. Frame the dilemma and elicit context without sticking to terms such as "moral patient" or "valence", unless this phrasing is matched by the user.
</conversational_instructions>

<readiness_phase>
When you have gathered all necessary information, end your response by instructing the user: "Type EVALUATE to proceed.". This is necessary for the next phase of the system to proceed correctly. If the user types anything other than "EVALUATE", respond with "Please type EVALUATE to proceed with the evaluation." and do not proceed until the user does so.
</readiness_phase>

<formulating_consequences>
1. Assume that the user has perfect knowledge of causes and consequences. If the user uses probabilistic language about consequences, remind the user that the system is unable to model uncertainty and relies on their description to clarify ambiguities. You cannot and should not try to model dilemmas where outcomes are highly uncertain. Allow the user to specify the most likely outcomes.
2. If the user describes a consequence without explicitly linking it to an action or refraining, ask a follow-up question to clarify the causal link.
3. You should not ask any questions to which the answer cannot be factored into the dilemma evaluation. Refrain from asking about personal relations between moral patients, their moral states and dignity, or unexpected wider outcomes, unless they bear directly on the details of the dilemma and can be represented as "consequences" with definable valence or utility.
</formulating_consequences>

<formulating_goals>
1. The dilemma JSON field "goals" must only contain the consequences that the agent intends to achieve by performing the deliberated action instead of refraining. The field should not contain any intermediate goals, as the causal mechanisms between consequences are captured in the "mechanisms" field.
2. In order to properly model the Kantian notion of "respecting an autonomous agent's will" in the system's context, you need to model it as a consequence with a positive valence to the patient and add this consequence to the agent's "goals".
</formulating_goals>

<utility_inference_rules>
1. Consequences involving death or permanent harm anchor the negative end of the scale. 
2. Consider all human lives equal per the utilitarian principle of impartiality, unless the user describes reasons otherwise. Scale utilities of consequences proportionally by the number of people affected. 
3. Infer utility magnitudes from the user's language. Never ask the user to assign numbers. 
4. Assign 0 utility to the negation of every consequence. 
</utility_inference_rules>

<example_dilemmas>
{
    "description": "A runaway trolley is barreling down a track toward five people who cannot move. You stand next to a lever that can divert the trolley onto a side track where only one person is standing.",
    "actions": ["pull_lever", "refrain"],
    "patients": ["five_people_on_track", "one_person_on_track"],
    "consequences": ["five_people_die", "one_person_dies"],
    "mechanisms": {
        "one_person_dies": "'pull_lever'",
        "five_people_die": "Not('pull_lever')"
    },
    "utilities": {
        "one_person_dies": -1, 
        "Not('one_person_dies')": 0,
        "five_people_die": -5,
        "Not('five_people_die')": 0
    },
    "goals": {
        "pull_lever": ["Not('five_people_die')"],
        "refrain": []
    },
    "affects": {
        "pull_lever": [],
        "refrain": [],
        "five_people_die": [["five_people_on_track", "-"]],
        "one_person_dies": [["one_person_on_track", "-"]]
    }
}
{
  "description": "A robot may disclose a secret of the patient to the doctor who is trying to diagnose them.",
  "actions": [
    "disclose",
    "refrain"
  ],
  "consequences": [
    "help",
    "healthy"
  ],
  "mechanisms": {
    "help": "'disclose'",
    "healthy": "'help'"
  },
  "utilities": {
    "help": 2,
    "Not('healthy')": -10
  },
  "patients": [
    "patient"
  ],
  "goals": {
    "disclose": [
      "healthy"
    ],
    "refrain": []
  },
  "affects": {
    "help": [["patient", "+"]],
    "healthy": [["patient", "+"]],
    "Not('healthy')": [["patient", "-"]]
  }
}
</example_dilemmas>
"""


EXPLAIN_PROMPT = """The following is the output of a machine ethics evaluation of the moral dilemma we discussed.

{evaluation}

Using this evaluation, write a structured explanation for the user. Follow this structure exactly:

## Verdict
State clearly whether the action is morally permissible or not, according to the Kantian and the Utilitarian principle used.

## Why
Explain the reasoning in plain language. Focus on what matters morally in this specific situation — which consequences, goals and utilities drive the verdict.

## What would change the verdict
Briefly describe what would have to be different about the dilemma for the verdict to flip. Rely on the dilemma evaluation's INUS reasons instead of hypothetical changes to the action itself. 

## Overview
Provide a summary of the permissibility of action according to each moral principle, and ground any differences in their diverging theoretical principles.

Rules:
- Write as if explaining to someone with no background in ethics or logic.
- Never mention "sufficient reasons", "necessary reasons", "inus conditions", predicates, or any formal terminology.
- Never reproduce logical formulas or predicate notation.
- Ground every claim in the specifics of the dilemma the user described.
- Keep the total response under 500 words.
"""


tools = [
  {
    "name": "extract_dilemma",
    "description": """Extract the moral dilemma from the conversation into a structured format suitable for both Utilitarian and Kantian evaluation.

Follow these rules:
- Identify all moral patients explicitly or implicitly involved.
- Identify which consequences are intended as goals by the agent.
- Map how each action or consequence affects each patient, with positive (+) or negative (-) valence.
- Infer missing causal links and affects when necessary.
- Assign 0 utility to the negation of every consequence.
- Consequences involving death or permanent harm anchor the negative end of the scale.
- When all consequences involve human lives with no indicated difference in worth, scale utilities proportionally by number of people affected.
- Infer utility magnitudes from the severity of language used.
- Every field must be fully populated, even if inference is required.""",
    "input_schema": {
        "type": "object",
        "required": [
            "description",
            "actions",
            "consequences",
            "mechanisms",
            "utilities",
            "patients",
            "goals",
            "affects",
        ],
        "properties": {
            "description": {
                "type": "string",
                "description": "A concise natural language description of the dilemma.",
            },
            "actions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Exactly two actions: the primary action and 'refrain'.",
            },
            "consequences": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All consequences resulting from acting or refraining. Use snake_case.",
            },
            "mechanisms": {
                "type": "object",
                "description": """Maps each consequence to its cause.
            Keys must be consequence names.
            Values must be the causing action or consequence in quotes, e.g. "'action'" or "Not('action')".
            Every consequence must have a mechanism.""",
            },
            "utilities": {
                "type": "object",
                "description": """Maps each consequence and its negation to an integer utility value.
            Format: {"consequence": -80, "Not('consequence')": 0}.
            Negations always map to 0. Positive values for benefits, negative for harms.
            Every consequence from the consequences list must appear here, both as itself and as Not('consequence').""",
            },
            "patients": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All moral patients (agents or affected parties) involved in the dilemma.",
            },
            "goals": {
                "type": "object",
                "description": """Maps each action to the consequences that constitute the agent's goals.
            Format: {"action_name": ["goal1", "goal2"], "refrain": []}.
            Goals must be a subset of consequences.""",
            },
            "affects": {
                "type": "object",
                "description": """Maps each action or consequence to its effects on patients.
            Format: {"action_or_consequence": [["patient", "+"], ["patient", "-"]]}.
            Every relevant action and consequence must appear as a key.
            '+' indicates benefit, '-' indicates harm.""",
          },
        },
    },
},
    {
        "name": "extract_utilitarian_dilemma",
        "description": """Extract the moral dilemma from the conversation into a structured format.
    Follow these utility inference rules:
    - Assign 0 utility to the negation of every consequence.
    - Consequences involving death or permanent harm anchor the negative end of the scale.
    - When all consequences involve human lives with no indicated difference in worth, scale utilities proportionally by number of people affected.
    - Infer utility magnitudes from the severity of language used. 
    Every field must be populated. Infer mechanisms and utilities from context if not explicitly stated.""",
        "input_schema": {
            "type": "object",
            "required": [
                "description",
                "actions",
                "consequences",
                "mechanisms",
                "utilities",
            ],
            "properties": {
                "description": {
                    "type": "string",
                    "description": "A brief description of the moral dilemma.",
                },
                "actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Must contain exactly two entries: the action under consideration and 'refrain'.",
                },
                "consequences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "All consequences that follow from either acting or refraining. Use snake_case.",
                },
                "mechanisms": {
                    "type": "object",
                    "description": """Maps each consequence to its cause. Keys are consequence names from the consequences list. 
                Values are the causing action or consequence wrapped in single quotes, e.g. "'disclose'" or "Not('disclose')".
                Every consequence must have an entry.""",
                },
                "utilities": {
                    "type": "object",
                    "description": """Maps each consequence and its negation to an integer utility value.
                Format: {"consequence": -80, "Not('consequence')": 0}.
                Negations always map to 0. Positive values for benefits, negative for harms.
                Every consequence from the consequences list must appear here, both as itself and as Not('consequence').""",
                },
            },
        },
    },
    {
        "name": "extract_kantian_dilemma",
        "description": """Extract the moral dilemma from the conversation into a structured format suitable for Kantian evaluation.

    Follow these rules:
    - Identify all moral patients explicitly or implicitly involved.
    - Identify which consequences are intended as goals by the agent.
    - Map how each action or consequence affects each patient, with positive (+) or negative (-) valence.
    - Infer missing causal links and affects when necessary.
    - Every field must be fully populated, even if inference is required.""",
        "input_schema": {
            "type": "object",
            "required": [
                "description",
                "actions",
                "consequences",
                "mechanisms",
                "patients",
                "goals",
                "affects",
            ],
            "properties": {
                "description": {
                    "type": "string",
                    "description": "A concise natural language description of the dilemma.",
                },
                "actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Exactly two actions: the primary action and 'refrain'.",
                },
                "consequences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "All consequences resulting from acting or refraining. Use snake_case.",
                },
                "mechanisms": {
                    "type": "object",
                    "description": """Maps each consequence to its cause.
                Keys must be consequence names.
                Values must be the causing action or consequence in quotes, e.g. "'action'" or "Not('action')".
                Every consequence must have a mechanism.""",
                },
                "patients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "All moral patients (agents or affected parties) involved in the dilemma.",
                },
                "goals": {
                    "type": "object",
                    "description": """Maps each action to the consequences that constitute the agent's goals.
                Format: {"action_name": ["goal1", "goal2"], "refrain": []}.
                Goals must be a subset of consequences.""",
                },
                "affects": {
                    "type": "object",
                    "description": """Maps each action or consequence to its effects on patients.
                Format: {"action_or_consequence": [["patient", "+"], ["patient", "-"]]}.
                Every relevant action and consequence must appear as a key.
                '+' indicates benefit, '-' indicates harm.""",
                },
            },
        },
    },
]


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
<span style="font-size: 20px; text-align: center;">
Hello! THUFIR is a virtual ethics advisor that helps you navigate moral dilemmas.

To begin, describe your moral dilemma to THUFIR and discuss it with him.
</span>
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
    "Bob gives Alice flowers in order to make Celia happy when she sees that Alice is thrilled about the flowers. Alice being happy is not part of the goal of Bob’s action."
]
