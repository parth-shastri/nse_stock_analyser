from typing import Union, Optional, Any


def calculate_token_count_of_message(
    message: Union[str, dict],
    tokenizer: Optional[Any] = None,
):
    """
    Given a list of messages in openai format, calculate the total token count of the messages.
    The tokenizer should have .tokenize or .encode option.
    """
    if not tokenizer:
        # if a tokenizer is not specified
        avg_char_per_token = 4  # this is the general consensus

        if isinstance(message, dict):
            # this should be in the openai format
            message = message["content"]
        # calculate the total chars
        char_count = len(message)
        no_of_tokens_message = char_count // avg_char_per_token  # integer
        return no_of_tokens_message

    try:
        encoded_message = tokenizer.encode(message)
    except AttributeError:
        encoded_message = tokenizer.tokenize(message)

    no_of_tokens_message = len(encoded_message)

    return no_of_tokens_message
