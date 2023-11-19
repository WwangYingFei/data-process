# data-process

The link to the TREC2014 dataset is as follows: https://trec.nist.gov/data/session2014.html

TREC2014 is a processed subset of data samples.

For example:

460	798	SUNY	[2270, 2271, 4088, 2256, 2287, 4083, 4357, 4927, 2297, 4880]	['suny edu   The State University of New York', 'SUNY ESF  SUNY College of Environmental Science and Forestry', 'SUNY Upstate Medical University', 'SUNY Geneseo   SUNY Geneseo', 'Welcome   SUNY Fredonia', 'The College at Brockport  State University of New York', 'Welcome to the State University of New York at New Paltz ', 'Welcome to SUNY Potsdam   SUNY Potsdam', 'State University of New York at Oswego', 'SUNY Canton']	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

460 is sid.

798 is query id.

SUNY is user query.

[2270, 2271, 4088, 2256, 2287, 4083, 4357, 4927, 2297, 4880] is a list of document id.

['suny edu The State University of New York', 'SUNY ESF SUNY College of Environmental Science and Forestry', 'SUNY Upstate Medical University', 'SUNY Geneseo SUNY Geneseo', 'Welcome SUNY Fredonia', 'The College at Brockport State University of New York', 'Welcome to the State University of New York at New Paltz', 'Welcome to SUNY Potsdam SUNY Potsdam', 'State University of New York at Oswego', 'SUNY Canton'] is a list of 10 document titles.

[1, 1, 1, 1, 1, 1, 1, 1, 1, 1] represents the vertical type, where 0 represents non-vertical results, and 1 represents vertical results.

[0, 0, 0, 0, 0, 0, 0, 0, 0, 0] represents user clicks, where 0 indicates no click and 1 indicates a click.

