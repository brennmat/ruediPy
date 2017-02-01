function [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch(data,MS_names,SENSOR_names,varargin)

% function [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch (data,MS_names,PRESS_names,TEMP_names,options)
% 
% Calibrate a batch of ruediPy analysis steps by combining data from samples, calibrations, and blanks.
%
% INPUT:
% data: files to be processed (string with file/path pattern)
% MS_names: names / labels of mass spectrometers for which data should be processed (cellstring)
% SENSOR_names: names / labels of sensors (e.g., pressure, temperature, etc.) for which data should be processed (cellstring).
%	If there is no pressure or temperature data in the data file, use PRESS_names = {} or TEMP_names = {}. Pressure / temperature values will then be set to N/A.
% 
% OUTPUT:
% P_val: partial pressures of samples (matrix)
% P_err: uncertainties of partial pressures, taking into account ONLY the counting statistics of the data, not the overall reproducibility of the measurements (matrix)
% SPECIES: species names (cell string)
% SAMPLES: sample names (cell string)
% TIME: sample time stamps (epoch times as returned by rP_digest_RGA_SRS_step) (matrix)
% options: optional parameters:
%	- 'no_peak_zero_plot': don't plot PEAK and ZERO values
%	- 'no_sensitivity_plot': don't plot sensitivities
%	- 'no_partialpressure_plot': don't plot partial pressures
%	- 'no_plots','noplots': don't plot anything
%	- 'standardgas_pressure',X,unit: use this gas inlet pressure for all standard analyses (X: number, unit: string)
%	- 'wait_exit': wait for key press by user before exiting this function (useful for interactive use from shell scripts)
%
% EXAMPLE:
% Process 'ruediMS' data in *.txt files stored in 'mydata' directory, don't plot PEAK and ZERO data, and assume 970 hPa inlet pressure for all standard analyses:
% > [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch ("mydata/*.txt","ruediMS","no_peak_zero_plot","standardgas_pressure",970,"hPa")
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
% main function:
% ************************************
% ************************************

if ~iscellstr(MS_names)
	MS_names = cellstr (MS_names);
end
if ~iscellstr(SENSOR_names)
	SENSOR_names = cellstr (SENSOR_names);
end

% option defaults (plotting etc.):
flag_plot_peak_zero = true;
flag_plot_sensitivity = true;
flag_plot_partialpressure = true;
MS = 12; % default marker size
standardgas_pressure_val = NA;
standardgas_pressure_unit = '?';
wait_exit = false;

% parse options:
i = 0;
while i < length(varargin) % parse options
	i = i+1;
	switch tolower(varargin{i})
	
		% plotting options:
		case 'no_peak_zero_plot'
			flag_plot_peak_zero = false;
			disp ('rP_calibrate_batch: plotting of PEAK and ZERO data turned off.')
		case 'no_sensitivity_plot'
			flag_plot_peak_zero = false;
			disp ('rP_calibrate_batch: plotting of sensitivities turned off.')
		case 'no_partialpressure_plot'
			flag_plot_partialpressure = false;
			disp ('rP_calibrate_batch: plotting of partialpressures turned off.')
		case {'no_plots','noplots'}
			flag_plot_peak_zero = false;
			flag_plot_sensitivity = false;
			flag_plot_partialpressure = false;
			disp ('rP_calibrate_batch: plotting turned off.')
		
		% other options:
		case 'standardgas_pressure'
			standardgas_pressure_val = varargin{i+1};
			standardgas_pressure_unit = varargin{i+2};
			i = i+2;
			disp (sprintf('rP_calibrate_batch: using %g %s as inlet pressure for all STANDARDs.',standardgas_pressure_val,standardgas_pressure_unit))
			
		case 'wait_exit'
			disp ('rP_calibrate_batch: will wait for user confirmation after completion.')
			wait_exit = true;
		
		otherwise
			warning (sprintf("rP_calibrate_batch: unknown option '%s'. Ignoring...",varargin{i}))
	end
end


% ************************************
% Load and digest raw data from files:
% ************************************

% load raw data from files:
RAW = rP_read_datafile (data);

% digest data and store results in array (X):
X = [];
for i = 1:length(RAW)

	disp (sprintf('rP_calibrate_batch: parsing file %s...',RAW{i}.file))

	info = rP_digest_step_DATAFILEINFO(RAW{i});
	
	ms = {};
	sens = {};

	% digest MS data (abort if not available):
	for k = 1:length(MS_names)
		u = rP_digest_step_RGA_SRS (RAW{i},MS_names{k}); % digest RGA_SRS data
		if ~isempty(u.mean) % only keep data if digesting was successful
			ms{length(ms)+1} = u;
		end
	end
	if length(ms) > 1
		warning ("rP_calibrate_batch: there are data from different mass spectrometers. Skipping this file...")
		ms = {};
	elseif length(ms) == 0
		warning ("rP_calibrate_batch: found no mass spectrometer data for specified RGA_SRS names. Skipping this file...")
		ms = {};
	else
		ms = ms{1};
	end
	
	if ~isempty(ms) % otherwise skip parsing the rest of this file
		% digest SENSORs data:
		for k = 1:length(SENSOR_names)
			sens{k} = rP_digest_step_SENSOR (RAW{i},SENSOR_names{k});
		end
		
		xx.INFO        = info;
		xx.MS          = ms;
		xx.SENSORS     = sens;
	    X = [ X ; xx ];
	end
	
%	if ~isempty(ms) % otherwise skip parsing the rest of this file
%			% find pressure data from specified sensors
%			for k = 1:length(PRESS_names)
%				u = rP_digest_step_PRESSURESENSOR_WIKA (RAW{i},PRESS_names{k}); % digest PRESSURESENSOR_WIKA data
%				if ~isempty(u.mean) % only keep data if digesting was successful
%					p{length(p)+1} = u;
%				end
%			end
%			if length(p) > 1
%				error ("rP_calibrate_batch: there are data from different pressure sensors in the same step. Don't know how to handle this...")
%			elseif length(p) == 0
%				keyboard
%				error ("rP_calibrate_batch: found no pressure sensor data for specified PRESSURE_WIKA names...")
%			else
%				p = p{1};
%			end
%			if length(p) >= 1	% there is data from at least one pressure sensor
%				
%			end
%		end
%
%
%		% digest TEMPERATURE data:
%		if isempty(TEMP_names) % no temperature sensors specified, use t.mean = []
%			t.mean = [];
%			t.mean_unit = '--';
%		else % find temperature data from specified sensors
%			for k = 1:length(TEMP_names)
%				u = rP_digest_step_TEMPERATURESENSOR_MAXIM (RAW{i},TEMP_names{k}); % digest TEMPERATURESENSOR_MAXIM data
%				if ~isempty(u.mean) % only keep data if digesting was successful
%					t{length(t)+1} = u;
%				end
%			end
%			if length(t) > 1
%				error ("rP_calibrate_batch: there are data from different temperature sensors in the same step. Don't know how to handle this...")
%%%%			elseif length(t) == 0
%%%%				error ("rP_calibrate_batch: found no temperature sensor data for specified TEMPERATURESENSOR_MAXIM names...")
%			else
%				t = t{1};
%			end
%		end
%
%		clear u;
%
%		xx.INFO        = info;
%		xx.MS          = ms;
%		xx.PRESSURE    = p;
%		xx.TEMPERATURE = t;
%	
%		X = [ X ; xx ];
%	
%	end % ~isempty(ms)

end % for


% *************************************************
% Process calibrations data (standards and blanks):
% *************************************************

% sort out samples, standards, blanks; and determine list of unique mz/detector combinations:
iSTANDARD = iBLANK = iSAMPLE = [];
mz_det = {};	% list of all mz/detector combinations in the data set
for i = 1:length(X)
	switch X(i).INFO.type
		case 'STANDARD'
			iSTANDARD = [ iSTANDARD , i ];
		case 'BLANK'
			iBLANK    = [ iBLANK , i ];
		case 'SAMPLE'
			iSAMPLE   = [ iSAMPLE , i ];
		otherwise
			warning (sprintf("rP_calibrate_batch: unknown analysis type \'%s\' in file %s. Ignoring this step...",X(i).type,RAW(i).file))
	end % switch

	mz_det = { mz_det{:} X(i).MS.mz_det{:} };
	
end % for
	
mz_det = unique ( mz_det );

% Determine sample names:
for i = 1:length(iSAMPLE)
	SAMPLES{i} = X(iSAMPLE(i)).INFO.name.name;
end % for i = ...

% make sure we've got STANDARDs and BLANKs:
if isempty(iSTANDARD)
	error ('rP_calibrate_batch: there are no STANDARDs! Aborting...')
elseif isempty(iBLANK)
	error ('rP_calibrate_batch: there are no BLANKs! Aborting...')
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
if flag_plot_peak_zero
	t1 = min ([ t_standard(:) ; t_blank(:) ; t_sample(:) ]);
	t2 = max ([ t_standard(:) ; t_blank(:) ; t_sample(:) ]);
	dt = (t2-t1)/20; t1 = t1-dt; t2 = t2+dt;
	
	for i = 1:length(mz_det)
		figure()
		subplot (3,1,1)
		plot (t_standard(i,:),v_standard(i,:),'r.-','markersize',MS); axis ([t1 t2]);
		title (sprintf('STANDARDs: %s peak heights',strrep(mz_det{i},'_','\_')))
		set (gca,'xticklabel','')
		subplot (3,1,2)
		plot (t_blank(i,:),v_blank(i,:),'b.','markersize',MS , [t1 t2],[Bmean(i) Bmean(i)],'b-' ); axis ([t1 t2]);
		title (sprintf('BLANKs: %s peak heights',strrep(mz_det{i},'_','\_')))
		set (gca,'xticklabel','')
		subplot (3,1,3)
		plot (t_standard(i,:),V_standard(i,:),'k.-','markersize',MS); axis ([t1 t2]);
		title (sprintf('STANDARDs - mean BLANK: %s peak heights',strrep(mz_det{i},'_','\_')))
	end % for
end


PRESS_standard = repmat(standardgas_pressure_val,size(iSTANDARD));
unit = standardgas_pressure_unit;


% get standard gas info for STANDARDs and determine sensitivities:
S_val = S_err = repmat (NA,length(mz_det),length(iSTANDARD)); % matrices with sensitivities (and their uncertainties) of all mz_det combinations for all STANDARD steps (each row corresponds to one step)
SPECIES = cellstr(repmat('?',length(mz_det),1));
for i = 1:length(mz_det) % determine sensitivities S_val(i,:) / S_err(i,:) for all mz_det cominations
	u   = strsplit(mz_det{i},'_');
	MZ  = str2num(u{1});
	DET = u{2};	
	for j = 1:length(iSTANDARD) % determine sensitivity S_val(i,j) and S_err(i,j) for mz_det{i} in step iSTANDARD(j)
		k = find ( X(iSTANDARD(j)).INFO.standard.mz == MZ );
		if ~isempty(k) % there is (at least) one standard entry for this MZ value
			if length(k) > 1 % don't know how to treat this...
				error (sprintf('rP_calibrate_batch: there are multiple STANDARD entries for the same mz value in STANDARD step %s. Aborting...',X(j).INFO.name))
			else
				SPECIES{i} = [ X(iSTANDARD(j)).INFO.standard.species{k} , ' (' , mz_det{i} , ')' ];
				l = find(strcmp( X(iSTANDARD(j)).MS.mz_det , mz_det{i})); % l is index to mz_det{i} combination in current step/measurement.
				if any(l) % skip if l is empty
					pi = PRESS_standard(j) * X(iSTANDARD(j)).INFO.standard.conc(k); % partial pressure
					S_val(i,j) = X(iSTANDARD(j)).MS.mean(l) / pi;
					S_err(i,j) = X(iSTANDARD(j)).MS.mean_err(l) / pi;
				end % if l = ...
			end % if length(k) > 1
		end % if ~isempty(k)
	end % for j = ...	
end % for i = ...


% plot sensitivities (S_val) vs. time:
if flag_plot_sensitivity
	figure()
	tt = rP_epochtime2datenum (t_standard);
	tt1 = min(min(tt));
	tt2 = max(max(tt));
	dtt = (tt2-tt1)/20; tt1 = tt1-dtt; tt2 = tt2+dtt;

	if size(S_val,2) == 1
		y = [ S_val repmat(NA,size(S_val)) ];
		m = S_val;
		x = [ tt repmat(NA,size(tt)) ];
	else
		y = S_val;
		m = mean(S_val')';
		x = tt;
	end
	k = find (m<0);
	expon = round(log10(abs(m))); scal = repmat (10.^expon,1,size(S_val,2)); scal(k,:) = -scal(k,:);
	plot (x',y'./scal','.-','markersize',MS);
	datetick;
	xlabel ('Time (UTC)');
	ylabel (sprintf('Sensitivity (A/%s)',unit))
	leg = strrep(SPECIES,'_','');
	for i = 1:length(leg)
		if ( expon(i) ~= 0 )
			if ( expon(i) == 1 )
				leg{i} = sprintf('%s x 10',leg{i});
			else
				leg{i} = sprintf('%s x 10^{%i}',leg{i},expon(i));
			end
		end
	end
	legend (leg,'location','northoutside','orientation','horizontal');
end


% convert SAMPLEs peak heights to partial pressures using the S_val and S_err (interpolate in time):
P_val = P_err = repmat (NA,length(mz_det),length(iSAMPLE)); % matrices with sample partial pressures (and their uncertainties) of all mz_det combinations (each row corresponds to one step)
for i = 1:length(mz_det)
	
	tS = t_standard(i,:);
	Sv  = S_val(i,:);
	Se  = S_err(i,:);
	k = find (~isnan(Sv)); tS = tS(k); Sv = Sv(k); Se = Se(k); % remove NA and NaN entries
	if length(Sv) == 0
		warning (sprintf('rP_calibrate_batch: no valid STANDARDs data for %s. Skipping...',mz_det{i}))
	else
		[tS,k] = sort(tS); Sv = Sv(k); Se = Se(k);
		% If necessary, add 'fake' STANDARD steps before first SAMPLE and after last SAMPLE to allow interpolation / bracketing:
		if tS(1) > min(t_sample(i,:))
			tS = [ min(t_sample(i,:))-1 , tS ];
			Sv  = [ Sv(1) , Sv ];
			Se  = [ Se(1) , Se ];
		end % if min() ...
		if tS(end) < max(t_sample(i,:))
			tS = [ tS , max(t_sample(i,:))+1 ];
			Sv  = [ Sv , Sv(end) ];
			Se  = [ Se , Se(end) ];
		end % if min() ...
		
		% sensitivities at SAMPLE analysis times:
		S_smpl_val = interp1 ( tS , Sv , t_sample(i,:) );
		S_smpl_err = interp1 ( tS , Se , t_sample(i,:) );
	
		% sample partial pressures:	
		P_val(i,:) = v_sample(i,:) ./ S_smpl_val ;
		P_err(i,:) = sqrt ( (e_sample(i,:)./v_sample(i,:)).^2 + (S_smpl_err./S_smpl_val).^2 ) .* P_val(i,:) ; % error from counting statistics (NOT overall reproducibility of analyses!)

	end
end % for i = ...

TIME = t_sample;


% *************************************************
% Plot SAMPLE results vs. time
% *************************************************

if flag_plot_partialpressure
	figure()
	tt = rP_epochtime2datenum (TIME);
	tt1 = min(min(tt));
	tt2 = max(max(tt));
	dtt = (tt2-tt1)/20; tt1 = tt1-dtt; tt2 = tt2+dtt;
	
	if size(P_val,2) == 1
		y = [ P_val repmat(NA,size(P_val)) ];
		m = P_val;
		x = [ tt repmat(NA,size(tt)) ];
	else
		y = P_val;
		m = mean(P_val')';
		x = tt;
	end
	k = find (m<0);
	expon = round(log10(abs(m))); scal = repmat (10.^expon,1,size(P_val,2)); scal(k,:) = -scal(k,:);
	plot (x',y'./scal','.-','markersize',MS);
	datetick;
	xlabel ('Time (UTC)');
	ylabel (sprintf('Partial pressure (%s)',unit));
	leg = strrep(SPECIES,'_','');
	for i = 1:length(leg)
		if ( expon(i) ~= 0 )
			if ( expon(i) == 1 )
				leg{i} = sprintf('%s x 10',leg{i});
			else
				leg{i} = sprintf('%s x 10^{%i}',leg{i},expon(i));
			end
		end
	end
	legend (leg,'location','northoutside','orientation','horizontal');
end

% update plots / figures:
drawnow




% *************************************************
% Write SAMPLE results to data file
% *************************************************


PARTIALPRESSURES.species = SPECIES;
PARTIALPRESSURES.val     = P_val;
PARTIALPRESSURES.err     = P_err;
PARTIALPRESSURES.time    = TIME;
PARTIALPRESSURES.unit    = unit;

% S1.name = 'Wika pressure thingy';
% S1.unit = 'bar';
% S1.time  = repmat (123456789.01,length(SAMPLES),1);;
% S1.val  = repmat (123456789.01,length(SAMPLES),1);;
% S1.err  = repmat (0.123,length(SAMPLES),1);;
% S2.name = 'Maxim temperature thingy';
% S2.unit = 'deg.C';
% S2.time  = repmat (123456789.01,length(SAMPLES),1);;
% S2.val  = repmat (123456789.01,length(SAMPLES),1);;
% S2.err  = repmat (0.123,length(SAMPLES),1);;

% SENSORS{1} = S1;
% SENSORS{2} = S2;


% SENSORS data from samples:
SENSORS = {};
for i = 1:length(iSAMPLE)
	SENSORS{i} = X(iSAMPLE(i)).SENSORS; 
end


__write_datafile (...
	SAMPLES,...
	PARTIALPRESSURES,...
	SENSORS,...
	fileparts(data)...
	)

if wait_exit
	input ("Processing complete! Press ENTER to exit...", "s");
else
	disp ("Processing complete!")
end



endfunction % main function




% ************************************************************************************************************************************************




% ************************************
% ************************************
% helper functions:
% ************************************
% ************************************

function [val,err,t] = __filter_by_MZ_DET (steps,mz_det)
% return time series of data measured on specified mz/detector combination (value, error, and datetime)
	val = err = t = [];
	for j = 1:length(steps)
		k = find(strcmp(steps(j).MS.mz_det,mz_det)); % find index to specified mz_det combination
		if isempty(k)
			warning (sprintf('rP_calibrate_batch: there are no data for %s in file %s!',mz_det,steps(j).INFO.file))
			val = [ val , NA ];
			err = [ err , NA ];
			t   = [ t   , NA ];
		else
			val = [ val , steps(j).MS.mean(k)      ];
			err = [ err , steps(j).MS.mean_err(k)  ];
			t   = [ t   , steps(j).MS.mean_time(k) ];
		end % if isempty(k)
	end % for	
endfunction


%%% function [p,unit] = __get_totalpressure (steps,do_not_ask)
%%% % return total gas pressure from steps (TOTALPRESSUE field value, or ask user if TOTALPRESSURE is not available)
%%% 	default_p = 1013.25;
%%% 	p = repmat (NA,1,length(steps));
%%% 	
%%% 	for j = 1:length(steps)
%%% 		
%%% 		% ...check for TOTALPRESSURE field/value in steps(i) here (not yet implemented)...
%%% 		
%%% 		if ~isempty(steps(j).PRESSURE.mean)
%%% 			p(j) = steps(j).PRESSURE.mean;
%%% 			unit = steps(j).PRESSURE.mean_unit;
%%% 			
%%% 		else % if no pressure sensors were specified, or pressure data were not available for specified sensor(s)
%%% 		
%%% 			if ~do_not_ask % ask user for pressure:
%%% 				unit = 'hPa';
%%% 				u = input ( sprintf( 'Enter total gas pressure in %s at capillary inlet for step %s [or leave empty to use %g %s]:' , unit , steps(j).INFO.file , default_p , unit ));
%%% 				if isempty (u) % use default value
%%% 					u = default_p;
%%% 				else % use u value for next default
%%% 					default_p = u;
%%% 				end
%%% 				p(j) = u;
%%% 
%%% 			else % we don't know the pressure
%%% 				p(j) = NA;
%%% 				unit = '--';
%%% 				
%%% 			end % if ~do_not_ask
%%% 			
%%% 		end % ~isempty
%%% 		
%%% 	end % for
%%% 
%%% endfunction


%%% function [t,unit] = __get_temperature (steps,do_not_ask)
%%% % return temperature from steps (e.g., water temperature for GE-MIMS)
%%% 	default_t = 10;
%%% 	t = repmat (NA,1,length(steps));
%%% 	
%%% 	for j = 1:length(steps)
%%% 				
%%% 		if ~isempty(steps(j).TEMPERATURE.mean)
%%% 			t(j) = steps(j).TEMPERATURE.mean;
%%% 			unit = steps(j).TEMPERATURE.mean_unit;
%%% 			
%%% 		else % if no temperature sensors were specified, or temperature data were not available for specified sensor(s)
%%% 		
%%% 			if ~do_not_ask % ask user for temperature:
%%% 				unit = 'deg.C';
%%% 				u = input ( sprintf( 'Enter temperature in %s for step %s [or leave empty to use %g %s]:' , unit , steps(j).INFO.file , default_t , unit ));
%%% 				if isempty (u) % use default value
%%% 					u = default_t;
%%% 				else % use u value for next default
%%% 					default_t = u;
%%% 				end
%%% 				t(j) = u;
%%% 
%%% 			else % we don't know the temperature
%%% 				t(j) = NA;
%%% 				unit = '--';
%%% 				
%%% 			end % if ~do_not_ask
%%% 			
%%% 		end % ~isempty
%%% 		
%%% 	end % for
%%% 
%%% endfunction


function __write_datafile (samples,partialpressures,sensors,path)
% write processed data to CSV data file

	species = partialpressures.species;
	p_val   = partialpressures.val;
	p_err   = partialpressures.err;
	time    = partialpressures.time;
	p_unit  = partialpressures.unit;
	
	name = input ('Enter file name for processed data (or leave empty to skip): ','s');
	
	if isempty(name)
		disp ('rP_calibrate_batch: no file name given, not writing data to file.')
	
	else	
		% open ASCII file for writing:
		if strcmp(path(end),filesep)
			path = path(1:end-1);
		end
		[p,n,e] = fileparts (name);
		if ~strcmp(e,'.csv')
			name = [ name '.csv' ];
		end
		path = sprintf ('%s%s%s',path,filesep,name);
		[fid,msg] = fopen (path, 'wt');
		if fid == -1
			error (sprintf('rP_calibrate_batch: could not open file for writing (%s).',msg))
		else
		
			disp (sprintf('Writing data to %s...',path))
			
			% write header:
			fprintf (fid,'SAMPLE')
			for j = 1:length(species)
				fprintf (fid,';%s TIME (EPOCH);%s PARTIALPRESSURE (%s);%s PARTIALPRESSURE ERR (%s)',species{j},species{j},p_unit,species{j},p_unit)
			end	
			if ~isempty(sensors)
				nsens = length(sensors{1});
				for j = 1:nsens
					fprintf (fid,';%s TIME (EPOCH);%s (%s);%s ERR (%s)',sensors{1}{j}.sensor,sensors{1}{j}.sensor,sensors{1}{j}.mean_unit,sensors{1}{j}.sensor,sensors{1}{j}.mean_unit)
				end
			end
			
						
			% write data:
			for i = 1:length(samples)
				fprintf (fid,'\n');
				
				% sample name:
				fprintf (fid,'%s',samples{i});
				
				% gas partial pressures:
				for j = 1:length(species)				
					fprintf (fid,';%.2f;%g;%g',time(j,i),p_val(j,i),abs(p_err(j,i)))
				end

				% sensor data (if any):
				if ~isempty(sensors)
					for j = 1:nsens					
						fprintf (fid,';%.2f;%g;%g',sensors{i}{j}.mean_time,sensors{i}{j}.mean,sensors{i}{j}.mean_err)
					end
				end

			end % for i = 

			fclose (fid);

		end % if fid == -1
	end % if isempty(name)
	
endfunction
