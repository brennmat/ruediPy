from unittest.mock import MagicMock, patch

import pytest

from ruedipy.selectorvalve_VICI import selectorvalve_VICI


def _make_serial_mock(np_response=None, cp_response=None):
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
		if data == b'NP\r\n' and np_response is not None:
			pending['data'] = np_response
		elif data == b'CP\r\n' and cp_response is not None:
			pending['data'] = cp_response

	ser.inWaiting = MagicMock(side_effect=in_waiting)
	ser.read = MagicMock(side_effect=read)
	ser.write = MagicMock(side_effect=write)
	return ser


@patch('ruedipy.selectorvalve_VICI.time.sleep', return_value=None)
@patch('ruedipy.selectorvalve_VICI.serial.Serial')
def test_init_sends_legacy_before_np(mock_serial, _mock_sleep):
	ser = _make_serial_mock(np_response=b'NP = 6\r\n')
	mock_serial.return_value = ser

	valve = selectorvalve_VICI('/dev/ttyTEST', label='TESTVALVE')

	assert valve.getnumpos() == 6
	writes = [call.args[0] for call in ser.write.call_args_list]
	assert writes.index(b'LG1\r\n') < writes.index(b'NP\r\n')
	assert ser.flushInput.call_count >= 2


@patch('ruedipy.selectorvalve_VICI.time.sleep', return_value=None)
@patch('ruedipy.selectorvalve_VICI.serial.Serial')
def test_init_raises_when_np_times_out(mock_serial, _mock_sleep):
	ser = _make_serial_mock()
	mock_serial.return_value = ser

	with pytest.raises(RuntimeError, match='Could not determine number of valve positions'):
		selectorvalve_VICI('/dev/ttyTEST', label='TESTVALVE')


@patch('ruedipy.selectorvalve_VICI.time.sleep', return_value=None)
@patch('ruedipy.selectorvalve_VICI.serial.Serial')
def test_init_raises_on_non_legacy_np_reply(mock_serial, _mock_sleep):
	ser = _make_serial_mock(np_response=b'NP6\r\n')
	mock_serial.return_value = ser

	with pytest.raises(RuntimeError, match='Could not determine number of valve positions'):
		selectorvalve_VICI('/dev/ttyTEST', label='TESTVALVE')


@patch('ruedipy.selectorvalve_VICI.time.sleep', return_value=None)
@patch('ruedipy.selectorvalve_VICI.serial.Serial')
def test_setpos_skips_go_when_position_out_of_range(mock_serial, _mock_sleep):
	ser = _make_serial_mock(np_response=b'NP = 2\r\n')
	mock_serial.return_value = ser

	valve = selectorvalve_VICI('/dev/ttyTEST', label='TESTVALVE')
	ser.write.reset_mock()

	valve.setpos(5, 'nofile')

	writes = [call.args[0] for call in ser.write.call_args_list]
	assert b'GO5\r\n' not in writes


@patch('ruedipy.selectorvalve_VICI.time.sleep', return_value=None)
@patch('ruedipy.selectorvalve_VICI.serial.Serial')
def test_set_legacy_flushes_after_lg1(mock_serial, _mock_sleep):
	ser = _make_serial_mock(np_response=b'NP = 6\r\n')
	mock_serial.return_value = ser

	valve = selectorvalve_VICI('/dev/ttyTEST', label='TESTVALVE')
	ser.flushInput.reset_mock()
	ser.write.reset_mock()

	valve.set_legacy()

	assert ser.write.call_args_list[-1].args[0] == b'LG1\r\n'
	assert ser.flushInput.called
