# ECAO ( Echinobase Anatomy Ontology ) - Runbook (0.1)

This runbooks provides the steps to prepare the templates and the scripts involved in the ECAO generation. 
The github repo [ECAO](https://github.com/pellst/echinobase-anatomy-ontology/). 







## Getting Started

### Prerequisites

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running


```
finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain the purpose of these tests and why they are performed.

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system


# ROBOT is an OBO Tool

[![Build Status](https://travis-ci.org/ontodev/robot.svg?branch=master)](https://travis-ci.org/ontodev/robot)
[![Javadocs](https://www.javadoc.io/badge/org.obolibrary.robot/robot-core.svg)](https://www.javadoc.io/doc/org.obolibrary.robot/robot-core)


The integration tests are executed with `mvn verify`, which is run on all pull requests via Travis CI.

Embedded examples for testing must use Markdown [indented code blocks](https://github.github.com/gfm/#indented-code-blocks), where each line begins with four spaces. To provide code examples that *will not* be tested, use [fenced code blocks](https://github.github.com/gfm/#fenced-code-blocks) instead, beginning and ending with three backticks (\`\`\`).

robot-core/src/main/resources/Makefile-ROBOT
##   Currently the main purpose is to define some standard build targets, variables, and to provide a standard way
##   of obtaining the robot executable, e.g. for running in travis


util/release.sh
#!/usr/bin/env nix-shell
#! nix-shell -i bash -p git travis jq semver-tool
#
# This script helps to automate ROBOT releases.
step "Check Travis"
travis status --skip-version-check --exit-code --fail-pending

step "Check Jenkins"
curl --silent "https://build.obolibrary.io/job/ontodev/job/robot/job/master/lastBuild/api/json" | jq --exit-status '.result | test("SUCCESS")'





## Built With

* [ODK](https://github.com/INCATools/ontology-development-kit) - The language used
* [Robot](https://github.com/ontodev/robot) - The language used
* [Travis](https://travis-ci.org/ontodev/robot) - CI
* [zenodo](https://github.com/INCATools/ontology-development-kit) - The language used



## Contributing

Please read [CONTRIBUTING.md] for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 




## Authors

* **Echinobase Development Team** - *Initial work* - [Echinobase](https://Echinobase.org)

See also the list of [contributors](https://github.com/pellst/echinobase-anatomy-ontology/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Echinobase Development Team](http://www.Echinobase.org)
* Inspiration
* etc

