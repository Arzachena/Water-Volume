# Water-Volume
Measure water volume using ARCELI Waterproof Ultrasonic Distance Measuring Transducer.

Uses https://www.amazon.co.uk/ARCELI-Waterproof-Ultrasonic-Measuring-Transducer/dp/B07J2R2B92 to calculate the water volume in a water cistern.

Uses a Raspberry Pi and 3 Python modules to maintan an Sqlite database of measurements. 4th module uses Flask and Pygal to provide a web page showing zoomed and un-zoomed display of database contents.

1st module: Run by Cron every minute. Measures volume using GPIO in serial mode to interface with ultrasonic sensor. Stores volume readings in a table which uses triggers to make a FIFO queue.

2nd module: Run by Cron every hour. Calculates average volume during last hour. Stores average in a FIFO table.

3rd module: Run by Cron every day. Calculates average volume during last day. Stores average in a FIFO table.

4th module: uses Flask and Pygal to provide a web page showing zoomed and un-zoomed display of database contents.

The whole project is a bit hack and slash i.e no exception handling, uses literals instead of constants.
