from unittest.mock import Mock, patch

from yaru import main


@patch("yaru.import_module", Mock())
def test_main() -> None:
    mock_set_as_cli = Mock()
    mock_add_supbarsers = Mock()
    mock_parse_args = Mock()
    mock_parser = Mock(add_subparsers=mock_add_supbarsers, parse_args=mock_parse_args)

    with (
        patch("yaru.Command.registry", return_value={Mock(set_as_cli=mock_set_as_cli)}),
        patch(
            "yaru.argparse.ArgumentParser", return_value=mock_parser
        ) as mock_argument_parser,
    ):
        main()
        mock_argument_parser.assert_called_once_with(
            description="Project's development commands"
        )
        mock_add_supbarsers.assert_called_once_with(dest="command", required=True)
        mock_set_as_cli.assert_called_once_with(mock_add_supbarsers.return_value)
        mock_parse_args.assert_called_once()
