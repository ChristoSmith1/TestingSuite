from typing import TypeVar


_T = TypeVar('_T')

def get_user_choice(
    choices: list[_T],
    prompt_message: str = f'Choose from the following',
    allow_multiple: bool = True,
    allow_empty: bool = True,
    verify: bool = True,
) -> list[_T]:
    """Prompt user to select a subset of given choices interactively at console.

    Args:
        choices (list[_T]): The valid choices to be selected from. Each entry should have a valid __str__() definition.
        prompt_message (str, optional): The prompt to show the user when selecting. Defaults to f'Choose from the following'.
        allow_multiple (bool, optional): Allow the user to select more than 1 entry. Defaults to True.
        allow_empty (bool, optional): Allow the user to select no entries. Will return an empty list. Defaults to True.
        verify (bool, optional): Present the user with the choices they made and ask them to verify correctness. Defaults to True.

    Returns:
        list[_T]: The subset of "choices" selected by the user
    """
    error_message = ''
    selected_choices: list
    while True:
        # Give the user their options
        print(f'\n{prompt_message}:')
        for index, choice in enumerate(choices):
            print(f'  {(index + 1):3}. {choice}')
        if error_message != '':
            print(f'[{error_message}] ', end='')
        if allow_empty:
            print(f'[Empty selection: ok] ', end='')
        else:
            print(f'[Empty selection: NOT OK] ', end='')
        if allow_multiple:
            print(f'[Multiple selection: ok]')
        else:
            print(f'[Multiple selection: NOT OK]')
        

        # Parse user index choices
        user_input_raw = input(f'Enter choice(s), separated by spaces. Blank to select nothing, "all" to select everything: ')
        if user_input_raw.strip() == '':
            selected_indexes = []
        elif user_input_raw.strip().strip('"\'').casefold() == 'all':
            selected_indexes = [x for x in range(len(choices))]
        else:
            try:
                selected_indexes = [int(x) - 1 for x in user_input_raw.split()]
            except Exception as exc:
                error_message = f'Error parsing user choice(s): {exc}. Please try again.'
                continue

        # Make sure number of selections is valid
        if (not allow_empty) and len(selected_indexes) == 0:
            error_message = f'You must select at least 1 option. You selected {len(selected_indexes)}. Please try again.'
            continue
        if (not allow_multiple) and len(selected_indexes) > 1:
            error_message = f'You must select exactly 1 option. You selected {len(selected_indexes)}. Please try again.'
            continue

        # Remove duplicates and sort in ascending order
        selected_indexes = list(set(selected_indexes))
        selected_indexes.sort()

        # Convert the indexes to a choice list
        selected_choices: list[_T] = []
        try:
            for index in selected_indexes:
                if index < 0:
                    # User input "0" becomes index -1
                    # Which is not an index error, usually.
                    # But we don't want to allow it.
                    raise IndexError
                selected_choices.append(choices[index])
        except IndexError:
            error_message = f'You selected an invalid index. Please try again.'
            continue

        # At this point, input is valid.
        # If we don't need to verify, we're done
        if not verify:
            break

        print(f'\nYou selected {len(selected_indexes)} choice(s):')
        for index in selected_indexes:
            print(f'  {(index + 1):3}. {choices[index]}')
        user_input_verify = input(f'Is this correct? (y/n): ').strip().strip('"\'').casefold()
        if user_input_verify == 'y' or user_input_verify == 'yes':
            break
        elif user_input_verify == 'n' or user_input_verify == 'no':
            error_message = f''
        else:
            error_message = f'Could not interpret yes/no input. Please try again.'

    return selected_choices

def get_user_choice_single(
    choices: list[_T],
    prompt_message: str = f'Choose from the following',
    verify: bool = True,
) -> _T:
    return get_user_choice(
        choices = choices,
        prompt_message = prompt_message,
        allow_multiple= False,
        allow_empty = False,
        verify = verify,
    )[0]
