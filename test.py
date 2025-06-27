import pytest
from unittest.mock import patch, MagicMock
from main import call_openai_function_call

@pytest.mark.parametrize("note,mock_arguments,expected", [
    (
        "4th period history. John Doe was on task. Jane Smith was off task.",
        [
            '{"student_name": "John Doe", "behavior": "on task", "class_name": "4th Period History"}',
            '{"student_name": "Jane Smith", "behavior": "off task", "class_name": "4th Period History"}'
        ],
        [
            {"student_name": "John Doe", "behavior": "on task",  "class_name": "4th Period History"},
            {"student_name": "Jane Smith", "behavior": "off task",  "class_name": "4th Period History"}
        ]
    ),
])
def test_call_openai_function_call_multiple_students(note, mock_arguments, expected):
    # Mock tool calls based on the arguments list
    mock_tool_calls = []
    for args_json in mock_arguments:
        mock_tool_call = MagicMock()
        mock_tool_call.function.arguments = args_json
        mock_tool_calls.append(mock_tool_call)

    # Mock the response structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(tool_calls=mock_tool_calls))]

    # Patch the OpenAI API call
    with patch('main.client.chat.completions.create', return_value=mock_response):
        result = call_openai_function_call(note)
        assert isinstance(result, list)
        assert result == expected

