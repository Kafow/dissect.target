import textwrap
from io import BytesIO

from flow.record.fieldtypes import datetime as dt

from dissect.target.plugins.os.unix.history import CommandHistoryPlugin


def test_commandhistory_with_timestamps_1(target_unix_users, fs_unix):
    commandhistory_data = """
#1648598339
echo "this is a test"
echo "O no. A line without timestamp"
#1658578468
exit
    """

    fs_unix.map_file_fh(
        "/root/.bash_history",
        BytesIO(textwrap.dedent(commandhistory_data).encode()),
    )

    target_unix_users.add_plugin(CommandHistoryPlugin)

    results = list(target_unix_users.commandhistory())
    assert len(results) == 3

    assert results[0].ts == dt("2022-03-29T23:58:59")
    assert results[0].command == 'echo "this is a test"'
    assert results[0].source == "/root/.bash_history"

    assert results[1].ts is None
    assert results[1].command == 'echo "O no. A line without timestamp"'
    assert results[1].source == "/root/.bash_history"

    assert results[2].ts == dt("2022-07-23T12:14:28")
    assert results[2].command == "exit"
    assert results[2].source == "/root/.bash_history"


def test_commandhistory_without_timestamps(target_unix_users, fs_unix):
    commandhistory_data = """
echo "Test if basic commandhistory works" > /dev/null
exit
    """

    fs_unix.map_file_fh(
        "/root/.zsh_history",
        BytesIO(textwrap.dedent(commandhistory_data).encode()),
    )

    target_unix_users.add_plugin(CommandHistoryPlugin)

    results = list(target_unix_users.commandhistory())
    assert len(results) == 2

    assert results[0].ts is None
    assert results[0].command == 'echo "Test if basic commandhistory works" > /dev/null'
    assert results[0].source == "/root/.zsh_history"

    assert results[1].ts is None
    assert results[1].command == "exit"
    assert results[1].source == "/root/.zsh_history"
