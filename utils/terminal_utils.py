import time
import blessed

def up_down_selection(choices):
    """
        The user moves with Up and Down arrow keys to view options,
        & hits enter to return selection
    :param choices:
    :return: choice
    """

    def render_options(curr_options):
        term = blessed.Terminal()
        print(term.home + term.clear)
        print(
            f"Label as ...:{term.white_on_black}[ ^ ]{term.normal}{term.black_on_white}[ {curr_options[1]} ]{term.normal}{term.white_on_black}[ v ]{term.normal}",
            flush=True, end="")

        val = None
        with term.cbreak():
            while val is None or val == '':
                val = term.inkey(timeout=3)
                if val.is_sequence and val.code == 259:  # UP key
                    popped = curr_options.pop()
                    curr_options = [popped] + curr_options
                    print(term.clear_bol, term.move_x(-1), flush=True, end="")
                    return render_options(curr_options)

                elif val.is_sequence and val.code == 258:  # DOWN key
                    popped = curr_options.pop(0)
                    curr_options = curr_options + [popped]
                    print(term.clear_bol, term.move_x(-1), flush=True, end="")

                    return render_options(curr_options)

                elif val.is_sequence and val.code == 343:  # ENTER key
                    print(term.home + term.clear)
                    print(
                        f"Label as ...:{term.white_on_green}[ ^ ]{term.normal}{term.green_on_white}[ {curr_options[1]} ]{term.normal}{term.white_on_green}[ v ]{term.normal}",
                        flush=True, end="")
                    time.sleep(0.6)
                    print(term.home + term.clear)

                    print("Loading next", end="")
                    time.sleep(0.5)
                    print(".", end="")
                    time.sleep(0.2)
                    print(".", end="")
                    time.sleep(0.2)

                    print(term.home + term.clear)
                    return curr_options[1]
                else:
                    pass

    choice = render_options(choices)
    return choice


