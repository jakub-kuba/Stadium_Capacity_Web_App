An example of a web application created in Flask.

To run it, you must first create a database and an <b>.env</b> file containing its credentials in the main folder. Example:

DIALECT_DRIVER=postgresql
DBUSER=your_username
PASSWORD=your_password
HOST=localhost
DBNAME=your_database_name

Note that the <b>iframe</b> in the cap.html file contains a source that comes from the production version of the website available at: <b>https://data.jakub-kuba.com/capacity</b>. The chart was created in Looker Studio.

The application contains elements of webscraping and its operation depends on the operation of the website <b>http://stadiony.net/</b>. I do not know the authors of this website.
