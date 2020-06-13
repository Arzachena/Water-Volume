# Water-Volume
Measures water volume using ARCELI Waterproof Ultrasonic Distance Measuring Transducer.

Uses https://www.amazon.co.uk/ARCELI-Waterproof-Ultrasonic-Measuring-Transducer/dp/B07J2R2B92 to calculate the current water volume in a water cistern. The water cistern may be rectangular, or a vertical cylinder, or a horizontal cylinder with rounded ends.

Uses a Raspberry Pi and 3 Python modules to maintan an Sqlite database of measurements. 4th module uses Flask and Pygal to provide a web page showing zoomed and un-zoomed display of database contents.

1st module: Run by Cron every minute. Measures volume using GPIO in serial mode to interface with ultrasonic sensor. Stores volume readings in a table which uses triggers to make a FIFO queue.

2nd module: Run by Cron every hour. Calculates average volume during last hour. Stores average in a FIFO table.

3rd module: Run by Cron every day. Calculates average volume during last day. Stores average in a FIFO table.

4th module: uses Flask and Pygal to provide a web page showing zoomed and un-zoomed display of database contents. It also allows various parameters to be set (cistern shape, dimensions, etc)

There is also a module which updates DuckDNS with the current web address so that the graphs can be seen from outside the local network.

The whole project is a bit hack and slash i.e no exception handling, uses literals instead of constants.
