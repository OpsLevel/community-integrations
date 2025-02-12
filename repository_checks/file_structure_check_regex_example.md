# File structure check regex example

The regex parsing within OpsLevel only supports single line (not ```/m```).
I want to share an alternative. how you can do file structure checks with grouping.

## Example file structure
This .md contains only the headlines, I want to check for the structure. You could be as explicit, as you need to be.  
```
# **Service name**

_Include CircleCI status and SonarCloud badges for health check. 
_Include Tech Stack badges.

## **Description**

_Include a brief description of what the service does, its core functionality, and its main purpose.

## **Table of Contents**

1. [Software Architecture](#software-architecture)
2. [Prerequisites](#prerequisites)
...

## Software Architecture

<img src="/docs/diagram_example.jpg" alt="diagram" title="diagram example"/>
some explaining text

## **Prerequisites**

Before you begin, ensure you have the following installed:

[...]

## **Setup**

## **Testing**
[...]
```

## RegEx

The regex to validate the previous example .md file structure:

```\A#\s\*\*[a-zA-Z\s\-_.\*:]+\*\*\n(.*\n)*## \*\*Description\*\*\n(.*\n)*## \*\*Table of Contents\*\*\n(.*\n)*## Software Architecture\n(.*\n)*## \*\*Prerequisites\*\*\n(.*\n)*## \*\*Setup\*\*\n(.*\n)*## \*\*Testing\*\*\n(.*\n)*```

- Depending on what you expect, you can be more restrictive (like the first headline with the Service name), or allow any characters and linebreaks ```(.*\n)*```

## Usage

I'm using it within a ``Code & Configurations`` / ``Repo File``  check, where I set the ``File Contents: matches regex``.