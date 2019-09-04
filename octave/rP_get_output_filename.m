function name = rP_get_output_filename (use_zenity,label,extension)

% function name = rP_get_output_filename (use_zenity,label,extension)
% 
% Helper function to aks user for file name to be used for data output using the terminal or GUI/Zenity. Optional: make sure a specific file extension / type is used.
%
% INPUT:
% use_zenity: flag to indicate if terminal or GUI/Zenity is used.
% label: string to be used while prompting user
% extension (optional): file extension (type) to be used.
% 
% OUTPUT:
% name: file name including absolute path
%
% EXAMPLE 1:
% Get a file name using the terminal:
% name = rP_get_output_filename (0,'File name for example');
%
% EXAMPLE 2:
% Get a CSV file name using the GUI/Zenity:
% % name = rP_get_output_filename (1,'File name for example','CSV');

if nargin < 3
	extension = '';
end

% remove dots from extension (just in case):
extension = strrep (extension,".","");

do_file = true;

while do_file

	name = '';
	
	if use_zenity
		% ask for file name (Zenity will already ask to replace files):
		[status, name] = system (sprintf("zenity --file-selection --title='%s' --save --confirm-overwrite 2> /dev/null",label));
	else
		name = input (sprintf('%s: ',label),'s');
	end
	
	if isempty (name)
		% user didn't choose a file name, we are done.
		do_file = false;
	
	else

		name = strrep (name,"\n",""); % remove newlines (just in case)

		[DIR, NAME, EXT] = fileparts (name);
		EXT = strrep (EXT,'.','');

		% check for file extension:
		extension_added = false;
		if ~isempty (extension)
			if ~strcmp (toupper(EXT),toupper(extension))
				% add file extension:
				name = [ name '.' extension ];
				extension_added = true;
			end
		end % if ~isempty (...)

		% check if file already exists (even with Zenity, because the added extension changed things):
		if ~exist (name,'file')
			% file does not yet exist, we're done
			do_file = false;

		else
			% file already exists, ask what to do:

			msg = sprintf ('Do you want to overwrite the existing file %s',name);

			if use_zenity
				if extension_added
					% if extension was added to the file name, ask for overwrite:
					answer = system (sprintf("zenity --question --ellipsize --default-cancel --text=\"%s?\"",msg));
					yes = ( answer == 0);
				else
					yes = true;
				end
			else
				answer = input (sprintf('%s [Y/N]?',msg),'s');
				yes = strcmp (toupper(answer),'Y');
			end

			if yes
				% user wants to overwrite existing file, so we're done:
				do_file = false;
			end
		end % exist (...)

	end % if isempty (name)

end % while
