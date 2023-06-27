# Change log:

## General changes and notes:
- Update code to Python 3
- To make the functions of the bot work, starting with download-metadata, we first had to modify the test files dummy.py and pmc_doi

#### dummy.py 
- For dummy.py we tried different download files and fixed small errors
- added the links as variable to the function, complete the code so that it actually downloads the files instead of just "retrieving" them

#### pmc_doi.py
- Many small adjustments of the relations of the functions of the files to each other, adding arguments, often hiding optinoal parameters and arguments
- Adjusting the download structure same problem as with dummy.py with the "yielden" of contents
- adding download statements with the help of Carlin (external programming of WikiData)
- Often only the content was printed instead of saved


### File: oa-cache
  
#### 1. Type of change: import statements removed

What?

- The following modules were removed: gobject, pygst, gst
- Functions and classes that are no longer used have been removed: setup_all, create_all


#### 2. type of change: import statements updated / added

What?

- make_datestring from helpers was imported instead of importing the entire helpers module - functions and classes were updated to import from the according models
- sqlalchemy was added to create and link the database with sqllite

  

#### 3. Type of change: prints

What?

- stderr.write was replaced with print

#### 4. type of change: 'convert-media'.

What?

- materials was changed (no filters --> everything)
- path was removed (added os.path in some places)
- relative paths added
- lines 167 - 186 were added to do the conversion of the files with ffmpeg instead of gobject now
- link ffmpeg conversion to .ogg format with previous code

#### 5. Type of change: 'find-media'.

What?

- First part of the code was commented out, because the tool Elixir doesn't work on Python 3 anymore and so all variables with relations to these functions had to be disabled for now
- skip was commented out, this function did not work anymore with the existing code, this had a Python 3 or Elixir reason
- journal and artical.get_by were removed, contrib_authors was added as a separate variable
- get_by is an Elixir variable and therefore depreciated
- the code for category was removed first, because this caused problems with dependencies in the pipeline of the find-media function, instead the results are printed

### File: oa-get

#### 1. Type of change: Import statements added / changed.

What?

- sqlalchemy, model, urllib3, filetype, importlib, requests

#### 2. type of change: added a database engine and a session

What?

- a database engine and a session was added, as well as database tables
- for this sqllite is used via sqlalchemy to store metadata after format in dummy file

#### 3. type of change: path of source was added / try-except changed

What?

- Relative paths temporarily changed to absolute paths as each individual tried to solve file problems

#### 4. type of change: update a function check_mime_types

What?

- Rewrite of the function to fix problems in the pipeline

#### 5. Type of change: 'update-mimetypes'.

What?

- Beginning of if-else statement loops was deleted
- .all() was put in the parenthesis
- add a for-loop to control the file-path

#### 6. type of change: 'download-media'.

What?

- materials was added session and then printed, should check if content is added
- function download-media works when a PMC DOI is added in pmc_doi.py file, also works with a list

  

### File: model.py

#### 1. type of change: import statements added / changed

What?

- sqlalchemy, importlib, sys

#### 2. type of change: redefine function 'set_source'.

What?

- instead of sqllite use importlib to define the source_module.

#### 3. type of change: define new variables

What?
- engine --> to declare the SQL environment
- session --> to define a session in the botflow


#### 4. type of change: change in the class 'journal

What?

- other object, instead of Entity now Base, because problems with the call of the variable arose before the change
- add 'tablename', because data was not saved in correct format in sqllite server before
- because of this the variables in the class have to be changed, once at title not Field() is used anymore but Column() as an update from Python 2
- at articels relations of fields and keys have been changed

#### 5. Type of change: adding the variable 'article_category'.

What?

- An association table is now defined here with the name 'article_category'.
- so that articles and categories can be linked via the association table.
- a function in oa-get or oa-cache asked for this table although it didn't exist before, when switching to Python 3 variables must have been lost in some places which had to be added manually later by trial and error of the error messages for the functions, download-media, download-metadata, find-media and convert-media

#### 6. type of change: change in class 'Category', 'Article' & 'SupplementaryMaterial'

What?

- Again instead of Entity Base, as an adjustment to a new import. 

### File: config.py

Update to Python 3

#### 1. Type of change: Path change

What?

- Original path did not work on own laptops, everyone had to change it manually
- Later added a change with relative path
- Customization of User Config and extension with specific local variables

#### 2. type of change: adding to the function 'database_path'.

What?

- sqlite is needed at 'database_path' so that the respective command can create the individual databases.



## General changes and notes:
- For the functions of the bot to work, starting with download-metadata, we first had to modify the test files dummy.py and pmc_doi

#### dummy.py 
- For dummy.py we tried different download files and fixed small errors
- added the links as variable to the function, complete the code so that it actually downloads the files instead of just "retrieving" them, this may have worked in Python 2

#### pmc_doi.py
- Many small adjustments of the relations of the functions of the files to each other, adding arguments, often hiding optinoal parameters and arguments
- Adjusting the download structure same problem as with dummy.py with the "yielden" of contents
- adding download statements
- Often only the content was printed instead of saved