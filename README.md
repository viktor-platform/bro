![](https://img.shields.io/badge/release-vX.Y.Z-green)

# BRO
This package can access the REST API from the [BRO](https://www.broloket.nl/ondergrondgegevens). Currently, this package provides
functionality to request CPTs from the BRO when you provide a region of interest. The format is based on the REST API of the BRO, which is described [here](https://publiek.broservices.nl/sr/cpt/v1/swagger-ui/#/default/) for CPTs.

Current options include retrieval of the following objects: 
1. CPTs (format: bytes, dict)

The package also allows export of the retrieved data in GeoJSON format. 

**Note 1**: The BRO is only available for the Netherlands, other locations are not supported.

**Note 2**: The API of the BRO is limited and requesting large amounts of data may result in instability.

## Installation

```python
pip install bro
```

## Use
Example usage to retrieve CPTs from the BRO as dictionaries. 
```python
from datetime import datetime

import Envelope
import Point
import get_cpt_characteristics_and_return_cpt_objects

begin_date = datetime(2015, 1, 1).strftime("%Y-%m-%d")
end_date = datetime(2023, 3, 3).strftime("%Y-%m-%d")

# Define small square area that returns 5 valid cpts
lower_corner = Point(51.92269686635185, 4.469594207611851)
upper_corner = Point(51.923034432171065, 4.470094707426648)

area = Envelope(lower_corner, upper_corner)
cpts = get_cpt_characteristics_and_return_cpt_objects(begin_date, end_date, area, as_dict= True)


```

## LICENSE

```
MIT License

Copyright (c) 2023 VIKTOR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

## Publish
- update changelog with version number
- update `bro/__version__.py`
- tag with version number