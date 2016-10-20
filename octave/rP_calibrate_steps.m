function X = rP_calibrate_steps (data,MS_name)

% function X = rP_calibrate_steps (data,MS_name)
% 
% Calibrate ruediPy data by combining data from samples, calibrations, and blanks.
%
%
%
% *** THIS IS JUST A PLACEHOLDER FILE, WHICH DOES NOT YET CONTAIN ANY USEFUL CODE ****
% 
% APROACH:
% * GET RAW DATA:
% 	- Load raw data from all files / analysis steps
% 	- DIGEST RAW DATA: Determine mean peak heights for all steps, at all mz-detector combinations in the data set
% 	- Determine all combinations of mz values and detector types in the data set
% * PROCESS CALIBRATION DATA (STANDARDS, BLANKS):
% 	- Plot peak heights for steps of type STANDARD and BLANK (to identify potential outliers etc.)
% 	- Subtract mean BLANK peak heights for all peak heights for all mz-detector combinations
% 	- Determine gas partial pressures in STANDARD gas analyses from standard gas concentrations (as given in the data file) and the total gas pressure at the gas inlet (use TOTALGASPRESSURE value if available, or ask user for a total gas pressure value)
% 	- Determine sensitivities for all steps of type 'STANDARD', at all mz-detector combinations in the data set
% 	  (sensitivity = blank-corrected detector signal / partial pressure at gas inlet)
% * PROCESS SAMPLE DATA:
% 	- Interpolate sensitivities to SAMPLE analysis times (to compensate sensitivity drifts)
% 	- Determine SAMPLE partial pressures by multiplying SAMPLE peak heights (blank-corrected) with sensitivites
% 	- (optional?) Normalise SAMPLE partial pressures such that sum of all partial pressures is equal to TOTALGASPRESSURE reading taken from sample
% 
%
%
% 
% INPUT:
% data: vector of raw data structures or data file names, or pattern matching list of data files (see also rP_read_datafile)
% MS_name: name / label of mass spectrometer for which data should be digested (string)
% 
% OUPUT:
% ...(not yet defined)...
% ...(will likely be a time series of calibrated data / partial pressures at different mz values)...
%
% DISCLAIMER:
% This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
% 
% ruediPy is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% ruediPy is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with ruediPy.  If not, see <http://www.gnu.org/licenses/>.
% 
% ruediPy: toolbox for operation of RUEDI mass spectrometer systems
% Copyright (C) 2016  Matthias Brennwald
% 
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <http://www.gnu.org/licenses/>.
% 
% Copyright 2016, Matthias Brennwald (brennmat@gmail.com)


% ************************************
% ************************************
%helper functions:
% ************************************
% ************************************

function [val,err,t] = __filter_by_MZ_DET (steps,mz_det)
	% return time series of data measured on specified mz/detector combination (value, error, and datetime)
	val = err = t = [];
	for j = 1:length(steps)
		k = find(strcmp(steps(j).mz_det,mz_det)); % find index to specified mz_det combination
		if isempty(k)
			warning (sprintf('rP_calibrate_steps: there are no data for %s!',mz_det))
			val = NA;
			err = NA;
			t   = NA;
		else
			val = [ val , steps(j).mean(k)      ];
			err = [ err , steps(j).mean_err(k)  ];
			t   = [ t   , steps(j).mean_time(k) ];
		end % if isempty(k)
	end % for	
endfunction





% ************************************
% ************************************
% main function:
% ************************************
% ************************************




warning('rP_calibrate_steps: NOT YET IMPLEMENTED!')




% ************************************
% Load and digest raw data from files:
% ************************************

% load raw data from files:
RAW = rP_read_datafile (data);

% digest data and store results in array (X):
X = [];
for i = 1:length(RAW)
	u = rP_digest_step (RAW{i},MS_name);
	if ~isempty(u) % only append if digesting data was successful
		X = [ X ; u ];
	end % if
end % for



% *************************************************
% Process calibrations data (standards and blanks):
% *************************************************

% sort out samples, standards, blanks; and determine list of unique mz/detector combinations:
iSTANDARD = iBLANK = iSAMPLE = [];
mz_det = {};
for i = 1:length(X)
	switch X(i).type
		case 'STANDARD'
			iSTANDARD = [ iSTANDARD , i ];
		case 'BLANK'
			iBLANK    = [ iBLANK , i ];
		case 'SAMPLE'
			iSAMPLE   = [ iSAMPLE , i ];
		otherwise
			warning (sprintf("rP_calibrate_steps: unknown analysis type \'%s\' in file %s. Ignoring this step...",X(i).type,RAW(i).file))
	end % switch
	mz_det = unique ( { mz_det{:} X(i).mz_det{:} } );
end % for

if isempty(iSTANDARD)
	error ('rP_calibrate_steps: there are no STANDARDs! Aborting...')
elseif isempty(iBLANK)
	error ('rP_calibrate_steps: there are no BLANKs! Aborting...')
end

% sort out digested values for all mz/detector combinations
v_standard = v_blank = v_sample = []; % mean values
e_standard = e_blank = e_sample = []; % error-of-the mean values
t_standard = t_blank = t_sample = []; % time stamps

for i = 1:length(mz_det)

	% standards:
	[v,e,t]    = __filter_by_MZ_DET ( X(iSTANDARD) , mz_det{i} );
	v_standard = [ v_standard ; v ];
	e_standard = [ e_standard ; e ];
	t_standard = [ t_standard ; t ];
	
	% blanks:
	[v,e,t]    = __filter_by_MZ_DET ( X(iBLANK)    , mz_det{i} );
	v_blank    = [ v_blank ; v ];
	e_blank    = [ e_blank ; e ];
	t_blank    = [ t_blank ; t ];
   
	% samples:
	[v,e,t]    = __filter_by_MZ_DET ( X(iSAMPLE)   , mz_det{i} );
	v_sample   = [ v_sample ; v ];
	e_sample   = [ e_sample ; e ];
	t_sample   = [ t_sample ; t ];
	
end % for

% determine mean blanks and subtract from STANDARDs and SAMPLEs:
Bmean = Berr = repmat (0,length(mz_det),1);
for i = 1:length(mz_det)
	Bmean(i) = mean (v_blank(i,:));							% mean blank
	Berr(i)  = std (v_blank(i,:)) / sqrt(length(mz_det)-1);	% uncertainty of the mean blank
	
	% blank-corrected standards:
	V_standard(i,:) = v_standard(i,:) - Bmean(i);
	E_standard(i,:) = sqrt ( e_standard(i,:).^2 + Berr(i).^2 );

	% blank-corrected samples:
	V_sample(i,:) = v_sample(i,:) - Bmean(i);
	E_sample(i,:) = sqrt ( e_sample(i,:).^2 + Berr(i).^2 );
	
end

% plot STANDARD and BLANK data:
MS = 12;
t1 = min ([ t_standard(:) ; t_blank(:) ; t_sample(:) ]);
t2 = max ([ t_standard(:) ; t_blank(:) ; t_sample(:) ]);
dt = (t2-t1)/20; t1 = t1-dt; t2 = t2+dt;

for i = 1:length(mz_det)
	figure(i)
	subplot (3,1,1)
	plot (t_standard(i,:),v_standard(i,:),'r.-','markersize',MS); axis ([t1 t2]);
	title (sprintf('STANDARDs: %s peak heights',mz_det{i}))
	subplot (3,1,2)
	plot (t_blank(i,:),v_blank(i,:),'b.','markersize',MS , [min(t_blank(i,:)) max(t_blank(i,:))],[Bmean(i) Bmean(i)],'b-' ); axis ([t1 t2]);
	title (sprintf('BLANKs: %s peak heights',mz_det{i}))
	subplot (3,1,3)
	plot (t_standard(i,:),V_standard(i,:),'k.-','markersize',MS); axis ([t1 t2]);
	title (sprintf('STANDARDs - mean BLANK: %s peak heights',mz_det{i}))
end % for

disp ('NEED TO ADD GAS CONCENTRATIONS AND TOTAL GAS PRESSURE IN STANDARD GAS ANALYSES, THEN DETERMINE PARTIAL PRESSURES VS. PEAK HEIGHT.')
disp ('THEN DETERMINE SENSITIVITIES = BLANK-CORRECTED PEAK HEIGHTS / PARTIAL PRESSURES')

% * PROCESS CALIBRATION DATA (STANDARDS, BLANKS):
% 	- Determine gas partial pressures in STANDARD gas analyses from standard gas concentrations (as given in the data file) and the total gas pressure at the gas inlet (use TOTALGASPRESSURE value if available, or ask user for a total gas pressure value)
% 	- Determine sensitivities for all steps of type 'STANDARD', at all mz-detector combinations in the data set
% 	  (sensitivity = blank-corrected detector signal / partial pressure at gas inlet)


endfunction % main function