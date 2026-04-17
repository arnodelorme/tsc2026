# Execution Plan: Conference History Archive

## Overview
Create one HTML page per conference year in `past/`, then update `about.html` with links.

## Steps

### Step 1: Create archive pages for each conference year
Each page follows a consistent template with: edition, title, dates, location, description, and links to available materials (abstracts PDF, program, external sites).

| File | Year | Edition | Location | Materials Available |
|------|------|---------|----------|-------------------|
| 1994.html | 1994 | TSC 1 | Tucson, AZ | No link |
| 1995.html | 1995 | TSC 2 | Ischia, Italy | No link |
| 1996.html | 1996 | TSC 3 | Tucson, AZ | No link |
| 1997.html | 1997 | TSC 4 | Elsinore, Denmark | No link |
| 1998.html | 1998 | TSC 5 | Tucson, AZ | No link |
| 1999.html | 1999 | TSC 6 | Tokyo, Japan | No link |
| 2000.html | 2000 | TSC 7 | Tucson, AZ | No link |
| 2001.html | 2001 | TSC 8 | Skövde, Sweden | No link |
| 2002.html | 2002 | TSC 9 | Tucson, AZ | No link |
| 2003.html | 2003 | TSC 10 | Prague, Czech Republic | No link |
| 2004.html | 2004 | TSC 11 | Tucson, AZ | No link |
| 2005.html | 2005 | TSC 12 | Copenhagen, Denmark | No link |
| 2006.html | 2006 | TSC 13 | Tucson, AZ | No link |
| 2007.html | 2007 | TSC 14 | Budapest, Hungary | No link |
| 2008.html | 2008 | TSC 15 | Tucson, AZ | No link |
| 2009.html | 2009 | TSC 16 | Hong Kong, China | No link |
| 2010.html | 2010 | TSC 17 | Tucson, AZ | No link |
| 2011.html | 2011 | TSC 18 | Stockholm, Sweden | No link |
| 2012.html | 2012 | TSC 19 | Tucson, AZ | No link |
| 2013.html | 2013 | TSC 20 | Agra, India | No link |
| 2014.html | 2014 | TSC 21 | Tucson, AZ | Abstracts PDF |
| 2015.html | 2015 | TSC 22 | Helsinki, Finland | Scribd abstracts |
| 2016.html | 2016 | TSC 23 | Tucson, AZ | Abstracts PDF |
| 2017.html | 2017 | TSC 24 | San Diego, CA | Abstracts PDF |
| 2018.html | 2018 | TSC 25 | Tucson, AZ | Abstracts PDF |
| 2019.html | 2019 | TSC 26 | Interlaken, Switzerland | Abstracts PDF |
| 2020.html | 2020 | TSC 27 | Virtual (Tucson) | Abstract database |
| 2021.html | 2021 | Webinar | Virtual | YouTube, program |
| 2022.html | 2022 | TSC 28 | Tucson, AZ (hybrid) | Book PDF |
| 2023.html | 2023 | TSC 29 | Taormina, Sicily | External site |
| 2023-symposium.html | 2023 | Symposium | Encinitas, CA | Documents |
| 2024.html | 2024 | TSC 30 | Tucson, AZ | Conference page |
| 2025.html | 2025 | TSC 31 | Barcelona, Spain | Program PDF |

### Step 2: Generate all HTML files
- Use a consistent template matching the site's existing style (nav, footer, page-header)
- Each file is self-contained with embedded CSS
- Include all known metadata and links to materials

### Step 3: Update about.html
- Add a "Past Conferences" section with a chronological table linking to each year page

### Step 4: Validation
- Verify all files created
- Verify all external links preserved exactly as found
- Verify about.html links resolve correctly
