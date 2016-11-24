function X = rP_digest_step_RGA_SRS (RAW,MS_name,opt)

% function X = rP_digest_step_RGA_SRS (RAW,MS_name,opt)
% 
% Load raw data and process ("digest") PEAK and ZERO data from RGA_SRS mass spectrometer to obatin mean peak heights. This assumes that each datafile corresponds to a single "step" of analysis (i.e., a block of PEAK/ZERO readings corresponding to a given sample, calibration, or blank analyisis). Results can be printed on the terminal and plotted on screen.q
% 
% INPUT:
% RAW: raw data struct (see also OUTPUT of rP_read_datafile)
% MS_name: name / label of RGA_SRS mass spectrometer for which data should be digested (string)
% opt (optional): string or cellstring with keyword(s) to control various behaviours (use defauls if opt is empty). Multiple keywords can be combined in a cellstring.
%	opt = 'showplot' --> show plot(s) of the data (default: no plots are shown)
%	opt = 'printsummary' --> print results to STDOUT (default: don't print anything)
%	opt = 'userwait' --> same as 'printsummary', but wait for user to press a key after printing the results
% 
% OUTPUT:
% X: struct object with "digested" data from file:
%	X.type: analysis type (string; S, C, B, or X)
%	X.mz_det: mz/detector combination of the digested PEAK-ZERO data (cell string)
%	X.mean: means of PEAK-ZERO values (for each X.mz value)
%	X.mean_err: errors of X.inens.val data (errors of the means)
%	X.mean_unit: units of X.mean and X.mean_err (cell string)
%	X.mean_time: epoch time corresponding to X.mean (mean of PEAK timestamps)
% 	X.std: partial pressure(s) of the standard gas corresponding to each X.mz_det entry
% 	X.std_unit: unit of X.std (string)
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

if length(RAW) > 1
	error ('rP_digest_step_RGA_SRS: cannot process an array of multiple steps! Please try again with a single step struct...')
end

% init empty data containers for digested data:
X.type = '?';
X.mz_det = {};
X.mean = [];
X.mean_err = [];
X.mean_time = [];
X.std = [];
X.std_unit = {};

% default behaviour:
showplot = false;
printsummary = false;
userwait = false;

if exist('opt','var') % change defaults
	if ~iscellstr(opt)
		opt = {opt};
	end
	if any(strcmp(tolower(opt),'showplot'))
		showplot = true;
	end
	if any(strcmp (tolower(opt),'printsummary'))
		printsummary = true;
	end
	if any(strcmp (tolower(opt),'userwait'))
		userwait = true;
	end
end

% make sure hyphens are treaded correctly:
MS_name = strrep (MS_name,'-','_');

figr = 1;


% get data corresponding to MS_name:
if isfield (RAW,MS_name)
	MS  = getfield (RAW,MS_name);	% MS data
else
	error (sprintf('rP_digest_step_RGA_SRS: found no MS data for ''%s''.',MS_name))
end

% get PEAK and ZERO data:
if isfield (MS,'PEAK')
	P = MS.PEAK; NP = length (P);
else
	P = []; NP = 0;
	warning ('rP_digest_step_RGA_SRS: no PEAKs found!')
end

if isfield (MS,'ZERO')
	Z   = MS.ZERO; NZ = length (Z);	
else
	Z = []; NZ = 0;
	warning ('rP_digest_step_RGA_SRS: no ZEROs found!')
end

% determine PEAK values with associated timestamp, mz, and detector
PEAK_val = PEAK_time = PEAK_mz = [];
PEAK_unit = PEAK_det = {};
for i = 1:NP
    PEAK_time    = [ PEAK_time ; P(i).epochtime ];
    PEAK_mz      = [ PEAK_mz ; P(i).mz ];
    PEAK_val     = [ PEAK_val ; P(i).intensity.val ];
    PEAK_unit{i} = P(i).intensity.unit;
    PEAK_det{i}  = P(i).detector;
end

% determine ZERO values with associated timestamp, mz, and detector
ZERO_val = ZERO_time = ZERO_mz = [];
ZERO_unit = ZERO_det = {};
for i = 1:NZ
    ZERO_time    = [ ZERO_time ; Z(i).epochtime ];
    ZERO_mz      = [ ZERO_mz ; Z(i).mz ];
    ZERO_val     = [ ZERO_val ; Z(i).intensity.val ];
    ZERO_unit{i} = Z(i).intensity.unit;
    ZERO_det{i}  = Z(i).detector;
end

% determine PEAK-ZERO (net peak heights) and calculate mean and error-of-the-mean, for each mz and detector combination
M = unique ( PEAK_mz ); % list of all mz values in data
D = unique ( PEAK_det ); % list of all detectors in data

for iM = 1:length(M) % find all data with mz = M(iM) and process them
    pp = find (PEAK_mz == M(iM)); % index to PEAKs at current mz value
    zz = find (ZERO_mz == M(iM)); % index to ZEROs at current mz value
        
	for iD = 1:length(D) % find all data with detector = D(iD) and process them
		p = find (strcmp(PEAK_det(pp),D{iD})); p = pp(p); % p is index to PEAKs at current mz / detector combination
		z = find (strcmp(ZERO_det(zz),D{iD})); z = zz(z); % z is index to ZEROs at current mz / detector combination
		
		if any(p) % there is PEAK data available for the current mz / detector combination
			
			tp = PEAK_time(p)(:); peaks = PEAK_val(p)(:);
			tz = ZERO_time(z)(:); zeros = ZERO_val(z)(:);
						
			if any(zeros) % inerpolate ZERO values to PEAK timestamps and subtract from PEAK values
									
				[tp,k] = sort(tp); peaks = peaks(k);
				[tz,k] = sort(tz); zeros = zeros(k);				
				
				% keep original ZERO data for plotting
				ZZ = zeros;
				TZ = tz;
				
				% check if ZERO data needs padding for interpolation
				if tz(1) > tp(1)
					tz    = [ tp(1) ; tz ];
					zeros = [ zeros(1) ; zeros ];
				end
				if tz(end) < tp(end)
					tz    = [ tz ; tp(end) ];
					zeros = [ zeros ; zeros(end) ];
				end
	
				h = peaks - interp1(tz,zeros,tp); % peak height = PEAKs - ZEROs
				
			else % there are no ZEROs available, so assume ZERO = 0.0
				warning (sprintf('rP_digest_step_RGA_SRS: found no ZEROs for mz=%i and detector=%s, skipping baseline compensation...',M(iM),D{iD}))
				h = peaks;
			end
			
			% determine mean / error of the mean:
			if length(h) > 1
				e = std (h) / sqrt(length(h)-1);
			else
				warning (sprintf('rP_digest_step_RGA_SRS: found only single PEAK value for mz=%i and detector=%s, cannot determine standard deviation...',M(iM),D{iD}))
				e = NaN;
			end
						
			% store results:
			X.mean 		       = [ X.mean ; mean(h) ];
			X.mean_err 	       = [ X.mean_err ; e ];
			X.mean_unit{end+1} = PEAK_unit{p(1)};
			X.mean_time        = [ X.mean_time ; mean(tp) ] ;
			X.mz_det{end+1}    = sprintf('%i_%s',M(iM),D{iD});
			
			if printsummary % print digest summary			
				disp (sprintf('mz=%i, detector=%s: MEAN = %g +/- %g %s (%s UTC)',...
						M(iM),...
						D{iD},...
						X.mean(end),...
						X.mean_err(end),...
						X.mean_unit{end},...
						datestr(datenum (1970,1,1,0,0) + X.mean_time(end)/86400)))
			end
			
			if showplot	% plot results
				figure(figr); figr = figr+1;
				t1 = min([tp ; tz]);
				t2 = max([tp ; tz]);
				if t2 > t1
					dt = 0.1*(t2-t1);
				else
					dt = 0.1;
				end
				subplot (3,1,1);
				plot (tp-t1,peaks,'r.','markersize',12);
				axis ([-dt t2-t1+dt]);
				ylabel (sprintf('PEAK (%s)',X.mean_unit{end}))
				title (sprintf('PEAKs and ZEROs at mz=%i / detector=%s',M(iM),D{iD}))
				subplot (3,1,2);
				plot (TZ-t1,ZZ,'b.','markersize',12);
				axis ([-dt t2-t1+dt]);
				ylabel (sprintf('ZERO (%s)',X.mean_unit{end}))
				subplot (3,1,3);
				plot (tp-t1,h,'k.','markersize',12 , [-dt t2-t1+dt],[X.mean(end) X.mean(end)],'k-');
				axis ([-dt t2-t1+dt]);
				ylabel (sprintf('PEAK-ZERO (%s)',X.mean_unit{end}))
				xlabel ('Time (s)')
			end
			
		end % if any(p)
	end % for iD = ...
end % for iM = ...

% determine analysis type (SAMPLE, STANDARD, BLANK, UNKNOWN)
switch toupper(RAW.DATAFILE.ANALYSISTYPE.type)
	case { 'SAMPLE' 'S' }
		X.type = 'SAMPLE';
	case { 'STANDARD' 'STD' }
		X.type = 'STANDARD';
	case { 'BLANK' 'B' }
		X.type = 'BLANK';
	case { 'MISC' }
		X.type = 'MISC';
	otherwise
		X.type = 'UNKNOWN';
end % switch

% determine sample description / ID
[p,f,e] = fileparts(RAW.file);
X.file = [ f e ];
switch X.type
	case 'SAMPLE'
		if isfield (RAW.DATAFILE,'SAMPLENAME')
			X.name = RAW.DATAFILE.SAMPLENAME;
		else
			X.name = 'UNKNOWN SAMPLE';
		end
	case { 'STANDARD' 'BLANK' }
		X.name = datestr(rP_epochtime2datenum(mean(X.mean_time)),'yyyy-mm-dd_HH:MM:SS');
	otherwise
		X.name = 'UNKNOWN'
end % switch

% parse standard gas information (for calibrations)
X.standard.species = {};
X.standard.conc    = [];
X.standard.mz      = [];
if strcmp (X.type,'STANDARD')
	for i = 1:length(RAW.DATAFILE.STANDARD)
		X.standard.species{i} = RAW.DATAFILE.STANDARD(i).species;
		X.standard.conc       = [ X.standard.conc ; RAW.DATAFILE.STANDARD(i).concentration ];
		X.standard.mz         = [ X.standard.mz   ; RAW.DATAFILE.STANDARD(i).mz ];
	end
end
