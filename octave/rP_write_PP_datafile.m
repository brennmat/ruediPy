function rP_write_PP_datafile ( samples, species, time, p_val, p_err, p_unit, sensors, file_path, file_name, use_zenity )

% function rP_write_PP_datafile ( samples, species, time, p_val, p_err, p_unit, sensors, file_path, file_name, use_zenity )
% 
% UNDER CONSTRUCTION!!!
%
% Write processed data from rP_calibrate_batch(...) to CSV data file.
%
% 
% INPUT:
% ...
% 
% OUPUT:
% ...
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
% Copyright (C) 2016, 2017, Matthias Brennwald (brennmat@gmail.com)
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
% Copyright 2023, Matthias Brennwald (brennmat@gmail.com)


	if isempty (name)
		name = rP_get_output_filename (use_zenity,'Data file for partial pressure data','CSV');
	end

	if isempty(name)
		disp ('rP_write_PP_datafile: no file name given, not writing data to file.')
	
	else
	
		% open ASCII file for writing:
		if length(path) == 0
			path = pwd;
		end
		if strcmp(path(end),filesep)
			path = path(1:end-1);
		end


		% open ASCII file for writing:
		[fid,msg] = fopen (name, 'wt');
		if fid == -1
			error (sprintf('rP_write_PP_datafile: could not open file for writing (%s).',msg))
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

					sns_unit = '???';
					k = 1;
					while k <= length(samples)
						if ischar(sensors{k}{j}.mean_unit)
							if ~strcmp(sensors{k}{j}.mean_unit,'NA')
								sns_unit = sensors{k}{j}.mean_unit;
								k = length(samples) + 1;
							end
						end
						k = k+1;
					end
					if strcmp (sns_unit,'???')
						warning (sprintf('rP_write_PP_datafile: could not determine units of %s sensor data.',sensors{1}{j}.sensor))
					end
					fprintf (fid,';%s TIME (EPOCH);%s (%s);%s ERR (%s)',sensors{1}{j}.sensor,sensors{1}{j}.sensor,sns_unit,sensors{1}{j}.sensor,sns_unit)

				end
			end
			
						
			% write data:
			for i = 1:length(samples)
				fprintf (fid,'\n');
				
				% sample name:
				fprintf (fid,'"%s"',samples{i});
				
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
