update ordering_scene set status = 'unavailable', note='Cannot currently process scenes which cross the international date line (due to interpolation of ozone, water vapor, and DEM aux data). Fix will be released in December 2015'  where status = 'error' and (select regexp_matches(log_file_contents, 'sample combination for the CMG\-related lookup tables')) is not null;


