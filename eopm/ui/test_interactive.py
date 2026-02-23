"""Test interactive choices module."""

from eopm.ui.interactive import (
    Choice,
    ChoicePrompt,
    ChoiceType,
    parse_ai_choices,
    format_choices_for_ai,
)


def test_parse_choices():
    """Test parsing AI responses for choice prompts."""

    # Test single choice
    text = """
Here are some options:

@CHOICE:single
TITLE: What type of product?
1. Mobile app
2. Web app
3. Desktop app
@END_CHOICE
"""

    prompts = parse_ai_choices(text)
    assert len(prompts) == 1
    assert prompts[0].title == "What type of product?"
    assert prompts[0].prompt_type == ChoiceType.SINGLE
    assert len(prompts[0].choices) == 3
    print("✓ Single choice parsing works")

    # Test multiple choice
    text = """
@CHOICE:multiple
TITLE: Select features:
1. Feature A
2. Feature B
3. Feature C
OTHER:true
@END_CHOICE
"""

    prompts = parse_ai_choices(text)
    assert len(prompts) == 1
    assert prompts[0].prompt_type == ChoiceType.MULTIPLE
    assert prompts[0].other_option is True
    print("✓ Multiple choice parsing works")

    # Test lettered choices
    text = """
@CHOICE:single
TITLE: Choose framework:
a. React
b. Vue
c. Angular
@END_CHOICE
"""

    prompts = parse_ai_choices(text)
    assert len(prompts) == 1
    assert len(prompts[0].choices) == 3
    assert prompts[0].choices[0].key == "a"
    print("✓ Lettered choice parsing works")

    # Test confirm type
    text = """
@CHOICE:confirm
TITLE: Proceed to next stage?
1. Yes
2. No
@END_CHOICE
"""

    prompts = parse_ai_choices(text)
    assert len(prompts) == 1
    assert prompts[0].prompt_type == ChoiceType.CONFIRM
    print("✓ Confirm choice parsing works")


def test_choice_prompt_creation():
    """Test creating choice prompts manually."""

    prompt = ChoicePrompt(
        title="Select your target platform",
        prompt_type=ChoiceType.SINGLE,
        choices=[
            Choice(key="1", label="iOS", description="Apple's mobile platform"),
            Choice(key="2", label="Android", description="Google's mobile platform"),
            Choice(key="3", label="Web", description="Progressive Web App"),
        ],
        other_option=True,
    )

    assert prompt.title == "Select your target platform"
    assert len(prompt.choices) == 3
    assert prompt.other_option is True
    print("✓ ChoicePrompt creation works")


def test_format_choices_for_ai():
    """Test formatting choices for AI."""

    prompt = ChoicePrompt(
        title="Select platform",
        prompt_type=ChoiceType.SINGLE,
        choices=[
            Choice(key="1", label="iOS"),
        ],
    )

    formatted = format_choices_for_ai(prompt, "1. iOS")
    assert "Select platform" in formatted
    assert "User selected: 1. iOS" in formatted
    print("✓ Format choices for AI works")


if __name__ == "__main__":
    test_parse_choices()
    test_choice_prompt_creation()
    test_format_choices_for_ai()
    print("\n✅ All tests passed!")
