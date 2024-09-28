import mysql.connector
from datetime import datetime
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="2408",
    database = "testdatabase"
    )
mycursor = db.cursor()

# mycursor.execute("CREATE TABLE Test (name varchar(50), created datetime NOT NULL, gender ENUM('M','F','O') NOT NULL, id int PRIMARY KEY NOT NULL AUTO_INCREMENT)")
# mycursor.execute("INSERT INTO Test (name,created, gender) VALUE (%s,%s,%s)",("Joey",datetime.now(),"F"))
# mycursor.execute("SELECT id, name FROM Test where gender = 'M' ORDER BY id DESC")

# mycursor.execute("ALTER TABLE Test ADD COLUMN food varchar(50) NOT NULL")
# mycursor.execute("ALTER TABLE Test DROP food")
mycursor.execute("ALTER TABLE Test CHANGE first_name first_name VARCHAR(4)")
mycursor.execute("DESCRIBE Test")
for x in mycursor:
    print(x)

# db.commit()