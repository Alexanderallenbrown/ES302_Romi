# ES302_Romi

Romi control library for ES302 at Lafayette College

An instance of the Romi class can be spun up to control either a simulated romi or a real romi that uses a serial connection (bluetooth or wired) as long as that robot has the romi_interface firmware. The firmware is included with this library, and can be uploaded to the Romi using Arduino.

documentation available [here](https://alexanderallenbrown.github.io/ES302_Romi). The main function used inside the Romi class is update().

## Installation

This library is not packaged for global installation. clone or download/unzip this project into the folder where you'd like to use the library. Then, you can use it by calling, for example,

```python
from ES302_Romi.Romi import Romi

robot = Romi()
```

to create a Romi object. 
