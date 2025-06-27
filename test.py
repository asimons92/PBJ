import pytest
from unittest.mock import patch, MagicMock
from main import call_openai_function_call, match_id_with_name

##### Test the OpenAI API Call #####
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

##### Test The JSON name and database name matching exactly #####
def test_match_id_with_name_exact():
    record = MagicMock()
    record.student_name = 'Tony'

    student = MagicMock()
    student.name = 'Tony'
    student.id = 1

    session = MagicMock()
    session.query().filter_by().first.return_value = student

    result = match_id_with_name(record, session)

    assert result is True
    assert record.student_id == 1
    assert record.student_name == 'Tony'

##### Test User Selecting "Yes" For Fuzzy Matching #####
@patch("main.input", return_value="y")
@patch("main.process.extractOne")
def test_match_id_with_name_fuzzy_yes(mock_extract, mock_input):
    record = MagicMock()
    record.student_name = 'Tiny'

    session = MagicMock()
    session.query().filter_by().first.return_value = None

    student_mock = MagicMock()
    student_mock.name = "Tony"
    student_mock.id = 1
    session.query().all.return_value = [student_mock]

    mock_extract.return_value = ("Tony", 90)

    result = match_id_with_name(record, session)

    assert result is True
    assert record.student_name == "Tony"
    assert record.student_id == 1
