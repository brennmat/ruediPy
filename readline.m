function serialout = readline(serialport,termination)
i=0;
do
	i=i+1;
	serialout(i) = srl_read(serialport,1);
until serialout(i)==toascii("\r");
endfunction
