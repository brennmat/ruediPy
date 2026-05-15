from unittest.mock import MagicMock, patch

import pytest

from ruedipy.rgams_SRS import rgams_SRS


def _make_serial_mock(id_response=None):
	ser = MagicMock()
	ser.flushOutput = MagicMock()
	ser.flushInput = MagicMock()
	pending = {'data': b''}

	def in_waiting():
		return len(pending['data'])

	def read(size=1):
		if not pending['data']:
			return b''
		chunk = pending['data'][:size]
		pending['data'] = pending['data'][len(chunk):]
		return chunk

	def write(data):
		if data == b'ID?\r\n' and id_response is not None:
			pending['data'] = id_response

	ser.inWaiting = MagicMock(side_effect=in_waiting)
	ser.read = MagicMock(side_effect=read)
	ser.write = MagicMock(side_effect=write)
	return ser


@patch('ruedipy.rgams_SRS.misc.have_external_gui', return_value=True)
@patch('ruedipy.rgams_SRS.time.sleep', return_value=None)
@patch('ruedipy.rgams_SRS.serial.Serial')
def test_init_success_valid_id_reply(mock_serial, _mock_sleep, _mock_gui):
	ser = _make_serial_mock(id_response=b'RGA.SN1234567.Ver\r\n')
	mock_serial.return_value = ser

	ms = rgams_SRS(
		'/dev/ttyTEST',
		label='TESTMS',
		has_external_plot_window=True,
	)

	assert ms.get_serial_number() == '1234567'
	writes = [call.args[0] for call in ser.write.call_args_list]
	assert b'ID?\r\n' in writes


@patch('ruedipy.rgams_SRS.misc.have_external_gui', return_value=True)
@patch('ruedipy.rgams_SRS.time.sleep', return_value=None)
@patch('ruedipy.rgams_SRS.serial.Serial')
def test_init_raises_when_id_times_out(mock_serial, _mock_sleep, _mock_gui):
	ser = _make_serial_mock()
	mock_serial.return_value = ser

	with pytest.raises(RuntimeError, match='Could not determine instrument ID'):
		rgams_SRS(
			'/dev/ttyTEST',
			label='TESTMS',
			has_external_plot_window=True,
		)


@patch('ruedipy.rgams_SRS.misc.have_external_gui', return_value=True)
@patch('ruedipy.rgams_SRS.time.sleep', return_value=None)
@patch('ruedipy.rgams_SRS.serial.Serial')
def test_init_raises_on_malformed_id_reply(mock_serial, _mock_sleep, _mock_gui):
	ser = _make_serial_mock(id_response=b'garbage\r\n')
	mock_serial.return_value = ser

	with pytest.raises(RuntimeError, match='Could not determine instrument ID'):
		rgams_SRS(
			'/dev/ttyTEST',
			label='TESTMS',
			has_external_plot_window=True,
		)
