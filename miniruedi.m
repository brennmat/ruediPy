disp("");
disp("#################################");
disp("# MiniRuedi controls for Octave #");
disp("#################################");
disp("               Yama Tomonaga 2015");
disp("                tomonaga@eawag.ch");

pkg load instrument-control

# Opens serial port for VICI Acutator (default: 8-N-1)
s2 = serial("/dev/ttyUSB1", 9600);
set(s2,"bytesize", 8);

# Flush input and output buffers
srl_flush(s2);

disp("---------------------------------");
disp("SRS RGA200");
disp("---------------------------------");

disp("ID:");
rga_txt = python("rga_IO.py","ID?","1");
disp(rga_txt(1:length(rga_txt)-2));

disp("---------------------------------");
disp("VICI Acutator");
disp("---------------------------------");

disp("ID:");
srl_write(s2, "VR\n");
disp(char(readline(s2,"\r")));
disp(char(readline(s2,"\r")));

disp("Current port:");
srl_flush(s2);
srl_write(s2, "CP\n");
disp(char(readline(s2,"\r")));

# Close port connection
fclose(s2)

# Scan given range and output data to PDF
disp("---------------------------------");
disp("Execute scan:");
disp("---------------------------------");
# Get RGA200 parameters
rgatxt = python("rga_IO.py","MI?","1");
MI = str2num(rgatxt(1:length(rgatxt)-2)) # Initial mass [amu]
rgatxt = python("rga_IO.py","MF?","1");
MF = str2num(rgatxt(1:length(rgatxt)-2)) # Final mass [amu]
rgatxt = python("rga_IO.py","AP?","1");
AP = str2num(rgatxt(1:length(rgatxt)-2)) # Output data points
rgatxt = python("rga_IO.py","SA?","1");
SA = str2num(rgatxt(1:length(rgatxt)-1)) # Steps/amu
# Sart single scan
rgatxt = python("rga_IO.py","SC1",num2str(AP+1)); # NB: AP + 1 tot. pressure point
scantxt = str2num(rgatxt)
plot(MI:1/SA:MF,scantxt(1:length(scantxt)-1)*1E-16);
xlabel("Atomic mass [amu]");
ylabel("Ion signal [A]");
print scan.jpg
